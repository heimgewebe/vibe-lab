# Artifact Drift Matrix

Documents known drift edges between Lenskit artifacts — pairs that can become inconsistent when one is updated without regenerating the other.

---

## Active Drift Edges (Producer exists)

| Source | Target | Trigger | Notes |
|---|---|---|---|
| `canonical_md` | `chunk_index_jsonl` | content change | chunk boundaries depend on source text |
| `canonical_md` | `derived_manifest_json` | structure change | manifest reflects document structure |
| `chunk_index_jsonl` | `sqlite_index` | index update | SQLite cache is built from chunk index |
| `derived_manifest_json` | `bundle_manifest` | manifest update | bundle manifest reflects derived manifest |

---

## Planned Drift Edges (Producer not yet implemented)

The edges below become relevant once a `citation_map_jsonl` Producer exists. They are documented here for architectural completeness. **This PR does not implement or activate these edges.**

| Source | Target | Trigger | Notes |
|---|---|---|---|
| `canonical_md` | `citation_map_jsonl` | content change | citation addresses derived from source positions |
| `chunk_index_jsonl` | `citation_map_jsonl` | chunk re-index | citation map depends on chunk boundaries |
| `bundle_manifest` | `citation_map_jsonl` | manifest update | manifest must register the role once emitted |

These edges will be activated in the Citation-Map-Producer PR.

---

## Non-Edges (by design)

| Pair | Reason |
|---|---|
| `citation_map_jsonl` ↔ `canonical_md` | `citation_map_jsonl` does not replace or substitute `canonical_md` |
| `citation_map_jsonl` ↔ `sqlite_index` | different authority tiers; no direct dependency |
