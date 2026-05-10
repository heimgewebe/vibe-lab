# Artifact Inventory

Registry of all known Lenskit ArtifactRoles with their semantic properties.

---

## Roles

### `canonical_md`

| Property | Value |
|---|---|
| Authority | `canonical_content` |
| Canonicality | `content_source` |
| Regenerable | false |
| Status | active, emitted |

The primary Markdown source of truth for a document. Not replaceable by derived artifacts.

---

### `chunk_index_jsonl`

| Property | Value |
|---|---|
| Authority | `navigation_index` |
| Canonicality | `derived` |
| Regenerable | true |
| Status | active, emitted |

Derived chunk-level index over `canonical_md`. Used for navigation and retrieval. Not a substitute for the canonical source.

---

### `derived_manifest_json`

| Property | Value |
|---|---|
| Authority | `navigation_index` |
| Canonicality | `derived` |
| Regenerable | true |
| Status | active, emitted |

Derived structural manifest produced from the bundle contents.

---

### `dump_index_json`

| Property | Value |
|---|---|
| Authority | `navigation_index` |
| Canonicality | `derived` |
| Regenerable | true |
| Status | active, emitted |

Dump-level index artifact.

---

### `index_sidecar_json`

| Property | Value |
|---|---|
| Authority | `navigation_index` |
| Canonicality | `derived` |
| Regenerable | true |
| Status | active, emitted |

Sidecar index companion to the primary document.

---

### `sqlite_index`

| Property | Value |
|---|---|
| Authority | `runtime_cache` |
| Canonicality | `cache` |
| Regenerable | true |
| Status | active, emitted |

Runtime SQLite cache built from derived indexes. Not canonical; must not be treated as source of truth.

---

### `citation_map_jsonl`

| Property | Value |
|---|---|
| Authority | `navigation_index` |
| Canonicality | `derived` |
| Regenerable | true |
| Staleness-sensitive | true |
| Contract | `citation-map.v1` |
| Status | **allowed/planned — not yet emitted** |

NDJSON artifact mapping chunk positions to citation addresses. Derived from `canonical_md` and `chunk_index_jsonl`; does not replace either.

**Constraints enforced in `bundle-manifest.v1.schema.json`:**
- Must have `authority: navigation_index` — not `canonical_content`, not `runtime_cache`.
- Must have `canonicality: derived` — not `content_source`, not `cache`.

**Not yet emitted.** The Bundle Manifest Schema recognises `citation_map_jsonl` as a valid optional role as of this PR. A Producer does not yet exist. Bundles without `citation_map_jsonl` remain fully valid.
