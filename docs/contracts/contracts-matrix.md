# Contracts Matrix

Overview of all Lenskit contracts, their ArtifactRoles, and implementation status.

---

## Contracts

| Contract | ArtifactRole | Content-Type | Status | Producer | Consumers |
|---|---|---|---|---|---|
| `bundle-manifest.v1` | `bundle_manifest` | `application/json` | active | bundle assembler | all downstream |
| `citation-map.v1` | `citation_map_jsonl` | `application/x-ndjson` | **Contract ✓ · Manifest-Role ✓ · Producer ✗** | — | Query / Context / Agent Evidence Pack (planned) |

---

## `citation-map.v1` — Detail

**Schema:** `merger/lenskit/contracts/citation-map.v1.schema.json`
**ArtifactRole:** `citation_map_jsonl`
**Manifest-Role:** allowed as optional artifact in `bundle-manifest.v1`

**Current state:**
- `citation-map.v1.schema.json` defines the structure of individual JSONL entries. ✓
- `bundle-manifest.v1.schema.json` recognises `citation_map_jsonl` as a valid optional role. ✓
- No Producer exists. Bundles do not yet emit `citation_map_jsonl`. ✗

**Planned consumers (not yet implemented):**
- Query layer
- Context assembly
- Agent Evidence Pack

**Non-goal:** Claim evaluation, evidence scoring, or citation quality judgement are explicitly out of scope for this contract.
