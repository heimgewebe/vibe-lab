#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
SCRIPT = HERE / "build_model_lab_execution_seed.py"
spec = importlib.util.spec_from_file_location("seed_builder", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bundle_hash(entries: list[dict]) -> str:
    digest = hashlib.sha256()
    for entry in sorted(entries, key=lambda item: item["path"]):
        digest.update(entry["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(entry["sha256"].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


class SeedBuilderTests(unittest.TestCase):
    def test_real_manifest_validates(self):
        data, problems = module.validate_manifest(module.DEFAULT_MANIFEST, REPO_ROOT)
        self.assertEqual([], problems)
        self.assertEqual("empty_directory", data["seed_kind"])
        self.assertEqual([], data["files"])

    def test_empty_seed_materializes_empty_directory(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "workspace"
            report = module.materialize(module.DEFAULT_MANIFEST, output, REPO_ROOT)
            self.assertTrue(output.is_dir())
            self.assertEqual([], list(output.iterdir()))
            self.assertEqual(0, report["file_count"])

    def test_existing_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "workspace"
            output.mkdir()
            with self.assertRaises(FileExistsError):
                module.materialize(module.DEFAULT_MANIFEST, output, REPO_ROOT)

    def test_wrong_empty_hash_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as td:
            path = Path(td) / "seed.yml"
            data = yaml.safe_load(module.DEFAULT_MANIFEST.read_text(encoding="utf-8"))
            data["content_sha256"] = "0" * 64
            path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            _, problems = module.validate_manifest(path, REPO_ROOT)
            self.assertTrue(any("content_sha256 mismatch" in item for item in problems), problems)

    def test_empty_seed_with_file_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as td:
            root = Path(td)
            payload = root / "payload.txt"
            payload.write_text("x\n", encoding="utf-8")
            path = root / "seed.yml"
            data = yaml.safe_load(module.DEFAULT_MANIFEST.read_text(encoding="utf-8"))
            data["files"] = [{"path": payload.relative_to(REPO_ROOT).as_posix(), "sha256": sha(payload)}]
            data["content_sha256"] = bundle_hash(data["files"])
            path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            _, problems = module.validate_manifest(path, REPO_ROOT)
            self.assertTrue(problems)

    def test_file_manifest_materializes_declared_bytes(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as td, tempfile.TemporaryDirectory() as out_td:
            root = Path(td)
            source_root = root / "root"
            source_root.mkdir()
            payload = source_root / "a.txt"
            payload.write_text("hello\n", encoding="utf-8")
            entry = {"path": payload.relative_to(REPO_ROOT).as_posix(), "sha256": sha(payload)}
            manifest = root / "seed.yml"
            data = {
                "schema_version": "v1",
                "artifact_type": "model_lab_execution_seed_manifest",
                "seed_id": "fixture-file-seed",
                "seed_kind": "file_manifest",
                "synthetic_fixture": False,
                "root_ref": source_root.relative_to(REPO_ROOT).as_posix(),
                "content_hash_algorithm": "sha256(sorted(repo_relative_path + NUL + file_sha256 + LF) over files)",
                "content_sha256": bundle_hash([entry]),
                "files": [entry],
            }
            manifest.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            output = Path(out_td) / "workspace"
            report = module.materialize(manifest, output, REPO_ROOT)
            self.assertEqual("hello\n", (output / "a.txt").read_text(encoding="utf-8"))
            self.assertEqual(1, report["file_count"])

    def test_file_manifest_omission_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as td:
            root = Path(td)
            source_root = root / "root"
            source_root.mkdir()
            (source_root / "omitted.txt").write_text("x\n", encoding="utf-8")
            manifest = root / "seed.yml"
            data = {
                "schema_version": "v1",
                "artifact_type": "model_lab_execution_seed_manifest",
                "seed_id": "fixture-file-seed",
                "seed_kind": "file_manifest",
                "synthetic_fixture": False,
                "root_ref": source_root.relative_to(REPO_ROOT).as_posix(),
                "content_hash_algorithm": "sha256(sorted(repo_relative_path + NUL + file_sha256 + LF) over files)",
                "content_sha256": bundle_hash([]),
                "files": [],
            }
            manifest.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            _, problems = module.validate_manifest(manifest, REPO_ROOT)
            self.assertTrue(problems)

    def test_cli_check_succeeds(self):
        self.assertEqual(0, module.main([]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
