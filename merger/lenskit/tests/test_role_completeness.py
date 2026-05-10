"""Tests for drift between constants.py role list and bundle-manifest.v1.schema.json enum."""
import json
import pathlib

from merger.lenskit.core.constants import (
    ARTIFACT_ROLES,
    AUTHORITY_VALUES,
    CANONICALITY_VALUES,
    ROLE_CONSTRAINTS,
)

SCHEMA_PATH = (
    pathlib.Path(__file__).parent.parent / "contracts" / "bundle-manifest.v1.schema.json"
)

with SCHEMA_PATH.open() as f:
    _SCHEMA = json.load(f)

_SCHEMA_ROLES = _SCHEMA["$defs"]["ArtifactRole"]["enum"]
_SCHEMA_AUTHORITIES = _SCHEMA["$defs"]["Authority"]["enum"]
_SCHEMA_CANONICALITIES = _SCHEMA["$defs"]["Canonicality"]["enum"]


def test_citation_map_jsonl_in_constants():
    assert "citation_map_jsonl" in ARTIFACT_ROLES


def test_citation_map_jsonl_in_schema_enum():
    assert "citation_map_jsonl" in _SCHEMA_ROLES


def test_constants_roles_subset_of_schema():
    """Every role declared in constants must appear in the schema enum."""
    missing = set(ARTIFACT_ROLES) - set(_SCHEMA_ROLES)
    assert not missing, f"Roles in constants but not in schema: {missing}"


def test_schema_roles_subset_of_constants():
    """Every role in the schema enum must appear in constants (no silent schema additions)."""
    missing = set(_SCHEMA_ROLES) - set(ARTIFACT_ROLES)
    assert not missing, f"Roles in schema but not in constants: {missing}"


def test_authority_values_match():
    missing_in_schema = set(AUTHORITY_VALUES) - set(_SCHEMA_AUTHORITIES)
    missing_in_constants = set(_SCHEMA_AUTHORITIES) - set(AUTHORITY_VALUES)
    assert not missing_in_schema, f"Authority values in constants but not schema: {missing_in_schema}"
    assert not missing_in_constants, f"Authority values in schema but not constants: {missing_in_constants}"


def test_canonicality_values_match():
    missing_in_schema = set(CANONICALITY_VALUES) - set(_SCHEMA_CANONICALITIES)
    missing_in_constants = set(_SCHEMA_CANONICALITIES) - set(CANONICALITY_VALUES)
    assert not missing_in_schema, f"Canonicality values in constants but not schema: {missing_in_schema}"
    assert not missing_in_constants, f"Canonicality values in schema but not constants: {missing_in_constants}"


def test_citation_map_constraints_in_role_constraints():
    assert "citation_map_jsonl" in ROLE_CONSTRAINTS
    c = ROLE_CONSTRAINTS["citation_map_jsonl"]
    assert c["authority"] == "navigation_index"
    assert c["canonicality"] == "derived"
    assert c["regenerable"] is True
    assert c["staleness_sensitive"] is True
    assert c["contract_id"] == "citation-map"
    assert c["contract_version"] == "v1"
