"""Tests for bundle-manifest.v1.schema.json — role constraints and backward compatibility."""
import json
import pathlib

import jsonschema
import pytest

SCHEMA_PATH = (
    pathlib.Path(__file__).parent.parent / "contracts" / "bundle-manifest.v1.schema.json"
)

with SCHEMA_PATH.open() as f:
    SCHEMA = json.load(f)

VALIDATOR = jsonschema.Draft202012Validator(SCHEMA)


def _minimal_manifest(**overrides):
    base = {
        "schema_version": "1.0.0",
        "contract": "bundle-manifest",
        "bundle_id": "test-bundle-001",
        "created_at": "2026-05-10T00:00:00Z",
        "artifacts": [],
    }
    base.update(overrides)
    return base


def _citation_artifact(**overrides):
    base = {
        "role": "citation_map_jsonl",
        "content_type": "application/x-ndjson",
        "authority": "navigation_index",
        "canonicality": "derived",
        "regenerable": True,
        "staleness_sensitive": True,
        "contract": {"id": "citation-map", "version": "v1"},
    }
    base.update(overrides)
    return base


# --- Case 1: valid bundle WITH citation_map_jsonl ---

def test_valid_manifest_with_citation_map():
    doc = _minimal_manifest(artifacts=[_citation_artifact()])
    errors = list(VALIDATOR.iter_errors(doc))
    assert errors == [], [e.message for e in errors]


# --- Case 2: old bundle WITHOUT citation_map_jsonl remains valid ---

def test_valid_manifest_without_citation_map():
    doc = _minimal_manifest(artifacts=[
        {
            "role": "canonical_md",
            "content_type": "text/markdown",
            "authority": "canonical_content",
            "canonicality": "content_source",
        }
    ])
    errors = list(VALIDATOR.iter_errors(doc))
    assert errors == [], [e.message for e in errors]


def test_empty_artifacts_list_is_valid():
    doc = _minimal_manifest()
    errors = list(VALIDATOR.iter_errors(doc))
    assert errors == [], [e.message for e in errors]


# --- Case 3 & 4: citation_map_jsonl with wrong authority is rejected ---

@pytest.mark.parametrize("bad_authority", ["canonical_content", "runtime_cache"])
def test_citation_map_wrong_authority_rejected(bad_authority):
    doc = _minimal_manifest(artifacts=[_citation_artifact(authority=bad_authority)])
    errors = list(VALIDATOR.iter_errors(doc))
    assert errors, f"Expected validation error for authority={bad_authority!r} but schema accepted it"


# --- Case 5 & 6: citation_map_jsonl with wrong canonicality is rejected ---

@pytest.mark.parametrize("bad_canonicality", ["content_source", "cache"])
def test_citation_map_wrong_canonicality_rejected(bad_canonicality):
    doc = _minimal_manifest(artifacts=[_citation_artifact(canonicality=bad_canonicality)])
    errors = list(VALIDATOR.iter_errors(doc))
    assert errors, f"Expected validation error for canonicality={bad_canonicality!r} but schema accepted it"


# --- Other roles are not affected by citation_map_jsonl constraints ---

def test_other_roles_unaffected_by_citation_map_constraints():
    doc = _minimal_manifest(artifacts=[
        {
            "role": "chunk_index_jsonl",
            "content_type": "application/x-ndjson",
            "authority": "navigation_index",
            "canonicality": "derived",
        },
        {
            "role": "sqlite_index",
            "content_type": "application/vnd.sqlite3",
            "authority": "runtime_cache",
            "canonicality": "cache",
        },
    ])
    errors = list(VALIDATOR.iter_errors(doc))
    assert errors == [], [e.message for e in errors]
