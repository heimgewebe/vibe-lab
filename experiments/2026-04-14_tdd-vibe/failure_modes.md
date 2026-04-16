---
title: "Failure Modes — TDD-Vibe"
status: testing
canonicality: operative
document_role: experiment
---

# Failure Modes — TDD-Vibe

## Wann funktioniert diese Praxis NICHT?

- **Wenn der Test-Generator dieselben blinden Flecken hat wie der Code-Generator:**
  Im vorliegenden Experiment kennt der Testschritt die 500-Fehlerklasse nicht
  explizit — also gibt es keinen 500-Test, und die Implementierung behandelt
  den Fall folgerichtig nur als globalen Handler. TDD-Vibe externalisiert
  nur das, was das Modell im Test-Schritt bereits bedenkt.
- **Wenn Tests Design-Zucker produzieren, der nie genutzt wird:**
  Das generierte `_resetStore()` ist eine plausibel klingende Abstraktion, die
  aber nirgendwo im Test aufgerufen wird (`grep -n beforeEach users.test.ts`
  liefert 0 Treffer). Die Folge: Die Tests sind reihenfolgenabhängig, 2 der 40
  Tests schlagen deshalb fehl. Ein "schön aussehender" Testlauf ersetzt kein
  funktionierendes Test-Setup.
- **Wenn die Implementierung an compilerseitigen Hürden scheitert, die Tests
  nicht sichtbar machen:** Die Express-5-Typing-Lücke (`req.params.id` als
  `string | string[]`) ist ein tsc-Problem, kein Test-Problem. Tests helfen
  hier nicht; sie laufen schlicht nicht erst an. Das begrenzt die Schutzwirkung
  von TDD-Vibe gegenüber systematischen Setup-Defekten.
- **Bei hochgradig explorativen Tasks:** Tests zementieren Annahmen zu früh,
  wenn die Domäne noch nicht verstanden ist — genauso wie bei Spec-First.

## Bekannte Fehlannahmen

- **„Test-First produziert weniger Nacharbeit":** Im Experiment widerlegt.
  Beide Ansätze brauchen dieselben 4 Patches, um überhaupt zu kompilieren.
- **„Exportierte Reset-Helper belegen Design-Gewinn":** Nur wenn sie auch
  benutzt werden. Die Existenz einer Funktion ist kein Qualitätsbeleg.
- **„Mehr Tests = robusteres Ergebnis":** Nur wenn die Tests unabhängig
  vom Code-Generator entstanden sind und das Test-Setup korrekt ist.
  Bei asymmetrischen Vergleichen (Kontrolle ohne Tests, Treatment mit Tests)
  ist "mehr Tests" keine aussagekräftige Metrik.
- **„Das Modell kennt alle Edge Cases, die es im Test nennt":** TDD-Vibe
  formalisiert nur das Gewusste. Unbekannte Unbekannte werden nicht
  automatisch aufgedeckt.

## Grenzen der Evidenz

- **Stichprobengröße:** 1 Benchmark-Task, je 1 Durchlauf pro Gruppe. Zu klein
  für statistische Aussagen.
- **Single-Agent-Bias:** Kontrolle und Treatment wurden vom selben LLM-Agent
  in derselben Session erzeugt. Kein unabhängiger Replikationstest.
- **Kontrollgruppe asymmetrisch:** Wurde explizit ohne Tests angewiesen — der
  Vergleich "Tests vs. keine Tests" ist konstruktionsbedingt, nicht
  methodeneffekt-getrieben.
- **Modellspezifisch:** Nur Claude claude-sonnet-4-6 getestet. Spec-First lief
  mit GPT-4o; ein sauberer Methodenvergleich würde gleiches Modell verlangen.
- **Run-Evidenz teilweise:** Der gepatchte Jest-Lauf liefert konkrete Zahlen
  (38/40 grün), aber der Patch ist nicht Teil des Original-LLM-Outputs — er
  ist eine Eingriffsmarkierung für Reproduzierbarkeit, keine Messung des
  Nacktoutputs.

## Risiko einer Fehlanwendung

- **Promotion ohne Replikation:** Ein LLM, das sich selbst Tests schreibt und
  sie dann besteht, ist kein unabhängiger Beweis für Methodentauglichkeit.
  Wer TDD-Vibe auf Basis dieses Experiments als catalog-tauglich einstuft,
  zementiert einen asymmetrischen Vergleich.
- **Falsche Sicherheit durch ausführbare Tests:** Eine grüne Test-Suite in
  TDD-Vibe bedeutet nicht, dass der Code korrekt ist — sondern, dass er die
  vom Modell selbst formulierten Tests besteht. Das ist ein schwacher
  Korrektheitsnachweis.
- **Overhead-Verschleierung:** 2 Prompts und 47 % mehr Code bei identischer
  Funktion sind reale Kosten, die in euphorischen Berichten leicht
  untergehen.
