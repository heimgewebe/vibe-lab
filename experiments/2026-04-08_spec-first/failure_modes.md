---
title: "Failure Modes — Spec-First Vibe-Coding"
status: adopted
canonicality: operative
document_role: experiment
---

# Failure Modes — Spec-First Vibe-Coding

## Wann funktioniert diese Praxis NICHT?

- **Hochgradig explorative Tasks:** Wenn das Problem noch nicht verstanden ist, produziert eine Spec zu früh eine falsche Schiene. Der LLM folgt dann der falschen Spec anstatt die Domäne zu erkunden.
- **Sehr kurze Tasks (< 5 Minuten):** Der Spec-Schritt kostet 5–10 Minuten; bei trivialen Tasks überwiegt der Overhead.
- **Wenn Spec und Implementierung nicht synchron gehalten werden:** Veraltete Specs führen zu Verweigerung nützlicher Abweichungen durch den LLM.

## Bekannte Fehlannahmen

- **„Die Spec ist vollständig":** Die Spec wird in der Regel auf Basis unvollständigen Wissens geschrieben. Fehlende Edge Cases in der Spec fehlen dann auch im Output.
- **„Konsistenz = Korrektheit":** Spec-First erhöht die interne Konsistenz, nicht notwendigerweise die fachliche Korrektheit. Ein konsistent falsches Ergebnis ist kein Erfolg.
- **„Der Effekt ist modellunabhängig":** Alle Tests wurden mit GPT-4o in GitHub Copilot durchgeführt. Andere Modelle (Claude, Gemini, lokale LLMs) wurden nicht getestet.

## Grenzen der Evidenz

- **Stichprobengröße:** 3 Tasks, je 2 Varianten (Spec-First vs. Direkt). Zu klein für statistische Signifikanz.
- **Single-Author-Bias:** Alle Tasks wurden von derselben Person durchgeführt. Kein unabhängiger Replikationstest.
- **Kontext-Abhängigkeit:** Nur TypeScript/Node.js/Express getestet. REST-API-Kontext. Andere Sprachen oder Paradigmen unbekannt.
- **Zeitpunkt:** Kein Langzeiteffekt gemessen (lernt der Entwickler die Praxis? Nimmt der Nutzen zu oder ab?).

## Risiko einer Fehlanwendung

Wenn Spec-First pauschal als „Best Practice" für alle LLM-Coding-Tasks gilt, droht:
- Überplanung in explorativen Phasen (Analysis Paralysis durch frühe Spezifikation)
- Erhöhter kognitiver Overhead in Kontexten, wo Direktheit effizienter wäre
- Falsche Sicherheit: gut strukturierter Output wird nicht mehr kritisch geprüft
