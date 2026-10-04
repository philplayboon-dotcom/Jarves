# Parallel-Tasks — entkoppelte Arbeitspakete

## Ressourcenregel

Auf dem 8-GB-Laptop zunächst sequenziell: ein aktiver schreibender Agent. Diese Datei ermöglicht saubere Übergaben und spätere Parallelität, sie fordert keine gleichzeitigen lokalen Modellinstanzen. Maximal zwei Schreib-Lanes nur nach Ressourcencheck; niemals dieselbe Datei gleichzeitig.

## Rollen und Ownership

| Rolle | Eigene Bereiche | Nicht ohne Coordinator ändern |
|---|---|---|
| coordinator | pyproject.toml, domain/, app.py, application/controller.py, config/logging, globale Dokumente | Nutzerentscheidungen |
| core | application/session.py, context_builder.py, filesystem/, später capture/ocr | domain/, app.py, pyproject.toml |
| ui | ui/, später extensions/vscode/ | domain/, Provider, app.py, pyproject.toml |
| provider | infrastructure/providers/ | domain/, UI, app.py, pyproject.toml |
| qa | tests/security/, fixtures/, scripts/benchmark.py | Adapter/Domain ohne abgestimmten Bugfix |
| reviewer | read-only | alle Schreibaktionen |

Feature-Agent besitzt seine fokussierten Unit-/Adapter-/UI-Tests. QA verändert nicht gleichzeitig dieselben Testdateien. README/STATUS/Roadmap/Contracts nur durch Coordinator pflegen. Neue Dependency per Handoff melden.

## Waves

| Wave | Freigabe | Lane A | Lane B | Integration |
|---|---|---|---|---|
| 0 | Nutzerfreigabe | T01 dann T02 | keine | G0/Contract Freeze |
| 1 | T02 | UI T04 | core T05; provider T03 sequenziell dazu | T06,T07 |
| 2 | T02 | provider T08,T09 | core T12,T13 | UI T10,T14; Coordinator T11 |
| 3 | T12,T13 | QA T15 | UI T14 | T16 |
| 4 | T16 | core T17 | QA T18; UI T19 separat | T20,T21 |
| 5 | T21 | QA T22,T23 | kein lokaler Parallelstress | T24/Nutzermessung |
| 6 | G5 Go | core T25,T26,T27 | UI erst T28 | G6 |
| 7 | G5 Go | Coordinator T29 | keine während Contractänderung | T30 und T31 danach |

Die Tabelle ist ein Lane-Vorschlag. Abhängigkeiten aus Roadmap.md gelten immer. T11 benötigt T07/T09/T10; T14 benötigt T04/T12/T13. Aufgaben nicht nur wegen freier Lane vorziehen.

## Taskregister

| Task | Phase | Owner | Dependencies | Größe | Status |
|---|---|---|---|---|---|
| T01 | M0 | coordinator | — | S | TODO |
| T02 | M0 | coordinator | T01 | M | TODO |
| T03 | M1 | provider | T02 | S | TODO |
| T04 | M1 | ui | T02 | M | TODO |
| T05 | M1 | core | T02 | S | TODO |
| T06 | M1 | ui | T03,T04,T05 | M | TODO |
| T07 | M1 | coordinator | T06 | S | TODO |
| T08 | M2 | provider | T02 | M | TODO |
| T09 | M2 | provider | T08 | M | TODO |
| T10 | M2 | ui | T04,T08 | S | TODO |
| T11 | M2 | coordinator | T07,T09,T10 | S | TODO |
| T12 | M3 | core | T02 | M | TODO |
| T13 | M3 | core | T02 | M | TODO |
| T14 | M3 | ui | T04,T12,T13 | M | TODO |
| T15 | M3 | qa | T12,T13 | S | TODO |
| T16 | M3 | coordinator | T11,T14,T15 | M | TODO |
| T17 | M4 | core | T05,T13 | S | TODO |
| T18 | M4 | qa | T09,T16 | M | TODO |
| T19 | M4 | ui | T06,T16,T17 | S | TODO |
| T20 | M4 | coordinator | T17,T18,T19 | S | TODO |
| T21 | M4 | coordinator | T20 | S | TODO |
| T22 | M5 | qa | T21 | M | TODO |
| T23 | M5 | qa | T22 | S | TODO |
| T24 | M5 | coordinator | T23 | M | TODO |
| T25 | M6 | core | T24 + Go | S | TODO |
| T26 | M6 | core | T25 | M | TODO |
| T27 | M6 | core | T25,T26 | M | TODO |
| T28 | M6 | ui | T14,T27 | M | TODO |
| T29 | M7 | coordinator | T24 + Go | S | TODO |
| T30 | M7 | ui | T29 | L | TODO |
| T31 | M7 | provider | T29 | S | TODO |
| T32 | M8 | coordinator | T24 + Nutzerentscheidung | S | TODO |

## Startprotokoll

Vor Beginn ID reservieren; eigene Dateien benennen; Contractstand 0.1 bestätigen; vorhandenen diff prüfen. Keine stillen Shared-File-Edits. Bei parallel laufenden Sessions Übergaben außerhalb gemeinsamer Quelltexte koordinieren.

## Handoff und Integration

HANDOFF-TEMPLATE.md als Bericht verwenden. Implementierungsagent meldet Änderungen und Testnachweise; Coordinator prüft Diff, führt Integrationsprüfungen nach Freigabe aus und aktualisiert STATUS.md. Reviewer kann read-only Befunde ergänzen. Erst danach DONE.

## Konfliktregel

Vertragsänderung zuerst melden, Consumer nicht selbst umdefinieren lassen. Bei überlappenden Dateien Aufgaben sequenziell ausführen. Worktrees nur optional nach ausdrücklicher Freigabe. Kein automatisches Merge, Commit, Reset oder Push.
