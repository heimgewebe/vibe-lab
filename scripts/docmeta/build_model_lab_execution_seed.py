#!/usr/bin/env python3
"""Validate or materialize the canonical Run-004 execution seed."""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

import validate_model_lab_execution_readiness as readiness

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_MANIFEST = (
    REPO_ROOT
    / "experiments/2026-05-31_model-lab-replication-series/artifacts/"
    / "run-004-execution-seed/seed-manifest.yml"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_manifest(manifest_path: Path, repo_root: Path) -> tuple[dict | None, list[str]]:
    try:
        manifest_path = manifest_path.resolve(strict=True)
        manifest_path.relative_to(repo_root.resolve())
    except (OSError, RuntimeError, ValueError):
        return None, ["manifest must be a safe existing repository file"]
    problems = readiness._seed_manifest_errors(
        manifest_path.relative_to(repo_root.resolve()).as_posix(),
        _sha256(manifest_path),
        repo_root,
        readiness._is_fixture_candidate(manifest_path, repo_root),
    )
    if problems:
        return None, problems
    try:
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        return None, [f"manifest is invalid or unreadable: {exc}"]
    return data, []


def materialize(manifest_path: Path, output: Path, repo_root: Path) -> dict:
    data, problems = validate_manifest(manifest_path, repo_root)
    if problems or data is None:
        raise ValueError("; ".join(problems))
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{output.name}.", dir=str(output.parent)))
    try:
        if data["seed_kind"] == "file_manifest":
            root = readiness.resolve_repo_relative_path(data["root_ref"], repo_root, must_exist=True)[0]
            if root is None:
                raise ValueError("seed root is unavailable")
            for entry in data["files"]:
                source = readiness.resolve_repo_relative_path(entry["path"], repo_root, must_exist=True)[0]
                if source is None:
                    raise ValueError(f"seed source unavailable: {entry['path']}")
                relative = source.relative_to(root)
                target = temporary / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
        actual_files = sorted(item for item in temporary.rglob("*") if item.is_file())
        actual_entries = [
            {
                "path": item.relative_to(temporary).as_posix(),
                "sha256": _sha256(item),
            }
            for item in actual_files
        ]
        if data["seed_kind"] == "empty_directory":
            expected_hash = readiness._bundle_content_hash([])
        else:
            root = readiness.resolve_repo_relative_path(data["root_ref"], repo_root, must_exist=True)[0]
            expected_entries = []
            for entry in data["files"]:
                source = readiness.resolve_repo_relative_path(entry["path"], repo_root, must_exist=True)[0]
                expected_entries.append(
                    {
                        "path": source.relative_to(root).as_posix(),
                        "sha256": entry["sha256"],
                    }
                )
            expected_hash = readiness._bundle_content_hash(expected_entries)
        actual_hash = readiness._bundle_content_hash(actual_entries)
        if actual_hash != expected_hash or data["content_sha256"] != readiness._bundle_content_hash(data["files"]):
            raise ValueError("materialized seed content hash mismatch")
        os.replace(temporary, output)
        return {
            "seed_id": data["seed_id"],
            "seed_kind": data["seed_kind"],
            "content_sha256": data["content_sha256"],
            "file_count": len(actual_entries),
            "output": str(output),
        }
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    data, problems = validate_manifest(args.manifest, REPO_ROOT)
    if problems or data is None:
        for problem in problems:
            print(f"ERROR: {problem}")
        return 1
    if args.output is None:
        print(
            f"OK seed_id={data['seed_id']} seed_kind={data['seed_kind']} "
            f"content_sha256={data['content_sha256']} files={len(data['files'])}"
        )
        return 0
    try:
        report = materialize(args.manifest, args.output, REPO_ROOT)
    except (FileExistsError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"OK materialized seed_id={report['seed_id']} seed_kind={report['seed_kind']} "
        f"files={report['file_count']} output={report['output']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
