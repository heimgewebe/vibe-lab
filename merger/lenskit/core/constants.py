ARTIFACT_ROLES = [
    "canonical_md",
    "chunk_index_jsonl",
    "derived_manifest_json",
    "dump_index_json",
    "index_sidecar_json",
    "sqlite_index",
    "citation_map_jsonl",
]

AUTHORITY_VALUES = [
    "canonical_content",
    "navigation_index",
    "runtime_cache",
]

CANONICALITY_VALUES = [
    "content_source",
    "derived",
    "cache",
]

# Per-role constraints enforced in bundle-manifest.v1.schema.json.
# authority and canonicality values must match the schema's if/then blocks.
ROLE_CONSTRAINTS = {
    "citation_map_jsonl": {
        "authority": "navigation_index",
        "canonicality": "derived",
        "regenerable": True,
        "staleness_sensitive": True,
        "contract_id": "citation-map",
        "contract_version": "v1",
    },
}
