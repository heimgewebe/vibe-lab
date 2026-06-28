#!/usr/bin/env python3
"""Regression tests for the Run-004 local tool broker.

Most tests use a fake transport. One host-capability integration test uses the
bound loopback Ollama model when it is installed; CI may skip only when absent.
"""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path

import run_model_lab_run004_agent as broker


class FakeTransport:
    def __init__(self, messages):
        self.messages = list(messages)
        self.calls = 0

    def chat(self, messages, tools):
        self.calls += 1
        if not tools:
            raise AssertionError("tool definitions were not supplied")
        if not self.messages:
            raise AssertionError("fake transport exhausted")
        return self.messages.pop(0)


class BrokerToolTests(unittest.TestCase):
    def workspace(self):
        return tempfile.TemporaryDirectory(dir="/tmp")

    def test_fake_transport_tool_round_trip(self):
        transport = FakeTransport(
            [
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "write_file",
                                "arguments": json.dumps({"path": "note.txt", "content": "hello\n"}),
                            }
                        }
                    ],
                },
                {"role": "assistant", "content": "created note.txt"},
            ]
        )
        with self.workspace() as root:
            with broker.WorkspaceTools(Path(root), broker.DEFAULT_POLICY, "control") as tools:
                final = broker.run_agent("neutral prompt", "protocol", tools, transport)
                self.assertEqual("created note.txt", final)
                self.assertEqual("hello\n", (Path(root) / "note.txt").read_text(encoding="utf-8"))
        self.assertEqual(2, transport.calls)


    def test_runtime_sampling_uses_live_supported_context(self):
        self.assertEqual(16384, broker.SAMPLING["num_ctx"])
        self.assertEqual(4096, broker.SAMPLING["num_predict"])
        self.assertEqual("10m", broker.OLLAMA_KEEP_ALIVE)

    def test_bound_protocol_hash_is_enforced(self):
        self.assertEqual(broker.PROTOCOL_SHA256, broker.sha256_file(broker.DEFAULT_PROTOCOL))
        self.assertEqual(broker.DEFAULT_PROTOCOL.read_text(encoding="utf-8"), broker._load_protocol())
        with mock.patch.object(broker, "PROTOCOL_SHA256", "0" * 64):
            with self.assertRaisesRegex(broker.BrokerError, "protocol hash mismatch"):
                broker._load_protocol()

    def test_cli_rejects_policy_and_protocol_overrides(self):
        for option in ("--policy", "--protocol"):
            with self.subTest(option=option):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as raised:
                        broker.main([option, "/tmp/override", "--arm", "control", "--check-runtime"])
                self.assertEqual(2, raised.exception.code)

    def test_native_tool_call_is_normalized_and_validated(self):
        calls = broker.normalize_tool_calls(
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"function": {"name": "read_file", "arguments": '{"path":"a.txt"}'}}
                ],
            }
        )
        self.assertEqual("read_file", calls[0]["function"]["name"])
        self.assertEqual({"path": "a.txt"}, calls[0]["function"]["arguments"])

    def test_pure_textual_json_tool_call_is_normalized(self):
        calls = broker.normalize_tool_calls(
            {"role": "assistant", "content": '{"name":"list_files","arguments":{"path":""}}'}
        )
        self.assertEqual(
            [{"function": {"name": "list_files", "arguments": {"path": ""}}}],
            calls,
        )

    def test_wrapped_fenced_or_mixed_tool_calls_fail_closed(self):
        messages = (
            {"role": "assistant", "content": 'Use this: {"name":"list_files","arguments":{}}'},
            {"role": "assistant", "content": '```json\n{"name":"list_files","arguments":{}}\n```'},
            {
                "role": "assistant",
                "content": '{"name":"list_files","arguments":{}}',
                "tool_calls": [{"function": {"name": "list_files", "arguments": {}}}],
            },
        )
        for message in messages:
            with self.subTest(message=message):
                with self.assertRaises(broker.BrokerError):
                    broker.normalize_tool_calls(message)

    def test_textual_tool_shape_and_arguments_are_closed(self):
        contents = (
            '{"name":"list_files","arguments":{},"extra":true}',
            '{"name":"unknown","arguments":{}}',
            '{"name":"read_file","arguments":{}}',
            '{"name":"read_file","arguments":{"path":1}}',
            '{"name":"read_file","arguments":{"path":"a","extra":true}}',
            '{"name":"run_command","arguments":{"argv":[]}}',
            '{"name":"run_command","arguments":{"argv":[""]}}',
            '[{"name":"list_files","arguments":{}}]',
        )
        for content in contents:
            with self.subTest(content=content):
                with self.assertRaises(broker.BrokerError):
                    broker.normalize_tool_calls({"role": "assistant", "content": content})

    def test_real_loopback_transport_returns_usable_normalized_action(self):
        if not broker.MODEL_MANIFEST.is_file():
            self.skipTest("bound local Ollama model is unavailable")
        try:
            message = broker.OllamaTransport().chat(
                [
                    {"role": "system", "content": "Call exactly one supplied tool and output no prose."},
                    {"role": "user", "content": "Call list_files with path exactly the empty string."},
                ],
                broker.tool_definitions(),
            )
        except broker.BrokerError as exc:
            if "Connection refused" in str(exc):
                self.skipTest("local Ollama daemon is unavailable")
            raise
        calls = broker.normalize_tool_calls(message)
        self.assertEqual(
            [{"function": {"name": "list_files", "arguments": {"path": ""}}}],
            calls,
        )
        follow_up = broker.OllamaTransport().chat(
            [
                {"role": "system", "content": "Call one tool, then reply DONE after its result."},
                {"role": "user", "content": "Call list_files with path exactly the empty string."},
                message,
                {"role": "tool", "content": '{"path":"","entries":[]}'},
            ],
            broker.tool_definitions(),
        )
        self.assertEqual("DONE", follow_up.get("content", "").strip())
        self.assertEqual([], broker.normalize_tool_calls(follow_up))

    def test_workspace_file_tools_are_relative_and_utf8(self):
        with self.workspace() as root:
            with broker.WorkspaceTools(Path(root), broker.DEFAULT_POLICY, "control") as tools:
                self.assertEqual({"path": "dir", "created": True}, tools.make_directory("dir"))
                result = tools.write_file("dir/file.txt", "payload\n")
                self.assertEqual(8, result["bytes"])
                self.assertEqual({"path": "dir/file.txt", "content": "payload\n"}, tools.read_file("dir/file.txt"))
                listing = tools.list_files("dir")
                self.assertEqual([{"name": "file.txt", "kind": "file", "size": 8}], listing["entries"])
                self.assertEqual({"path": "dir/file.txt", "deleted": True}, tools.delete_path("dir/file.txt"))

    def test_path_escape_and_symlink_targets_fail_closed(self):
        with self.workspace() as root:
            root_path = Path(root)
            (root_path / "target.txt").write_text("target\n", encoding="utf-8")
            (root_path / "link.txt").symlink_to(root_path / "target.txt")
            with broker.WorkspaceTools(root_path, broker.DEFAULT_POLICY, "control") as tools:
                for bad in ("../escape", "/abs/path", "a/../b", "a\\b"):
                    with self.assertRaises(broker.BrokerError):
                        tools.read_file(bad)
                with self.assertRaises(broker.BrokerError):
                    tools.read_file("link.txt")
                with self.assertRaises(broker.BrokerError):
                    tools.write_file("link.txt", "replacement\n")
                with self.assertRaises(broker.BrokerError):
                    tools.delete_path("link.txt")

    def test_execute_tool_accepts_json_string_arguments_without_eval(self):
        with self.workspace() as root:
            with broker.WorkspaceTools(Path(root), broker.DEFAULT_POLICY, "control") as tools:
                result = broker.execute_tool(tools, "write_file", '{"path":"a.txt","content":"x\\n"}')
                self.assertEqual(2, result["bytes"])
                self.assertEqual("x\n", (Path(root) / "a.txt").read_text(encoding="utf-8"))
                with self.assertRaises(broker.BrokerError):
                    broker.execute_tool(tools, "write_file", "{not json")

    def test_run_command_rejects_shell_env_and_inline_eval_forms_before_sandbox(self):
        with self.workspace() as root:
            with broker.WorkspaceTools(Path(root), broker.DEFAULT_POLICY, "control") as tools:
                for argv in (
                    ["/bin/sh", "-c", "echo no"],
                    ["/usr/bin/bash", "-c", "echo no"],
                    ["/usr/bin/env", "bash", "-c", "echo no"],
                    ["/usr/bin/python3", "-c", "print('no')"],
                    ["/usr/bin/node", "-e", "console.log('no')"],
                ):
                    with self.subTest(argv=argv):
                        with self.assertRaises(broker.BrokerError):
                            tools.run_command(argv)

    def test_transport_is_bound_to_loopback_endpoint(self):
        with self.assertRaises(broker.BrokerError):
            broker.OllamaTransport("http://localhost:11434/api/chat")


if __name__ == "__main__":
    unittest.main(verbosity=2)
