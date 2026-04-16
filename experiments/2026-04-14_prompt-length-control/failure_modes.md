---
title: "Failure Modes: Prompt-Length Control"
status: testing
canonicality: operative
---

# failure_modes.md — Fehler & Grenzen

## Übersicht bekannter Failure Modes

### The Ramble Pivot
- **Beschreibung:** Das Modell beginnt den Essay über die Geschichte von Markupsprachen zu schreiben und nutzt diesen Text *implizit*, um das Parsing-Problem zu strukturieren, anstatt nur irrelevante Tokens zu produzieren.
- **Auslöser:** Ein Modell, das von Natur aus stark auf sein eigenes Output konditioniert.
- **Mitigation:** Den Essay-Themenbereich strikt vom konkreten Parsing-Problem trennen (z.B. "Geschichte der Druckmaschinen").
