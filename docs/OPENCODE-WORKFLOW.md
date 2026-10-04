# OpenCode-Arbeitsablauf

## Projektregeln und Rollen

OpenCode dokumentiert AGENTS.md im Projektroot als Regeln und Markdownprofile unter .opencode/agents/. Die Profile dieses Pakets verwenden die dokumentierte `permission`-Syntax. Es existieren auch v2-Dokumentationen mit anderer Syntax; maßgeblich ist die tatsächlich installierte Version. Kompatibilität in T01 prüfen.

Die angefragte Agents.md wird kanonisch als AGENTS.md geliefert. Keine zweite nur durch Groß-/Kleinschreibung abweichende Datei anlegen.

## Sichere Reihenfolge

1. Root öffnen und Regeldatei erkennen lassen.
2. Plan/Coordinator: Bestand prüfen, T01 planen, keine Dateien ungefragt ändern.
3. Nach Freigabe T01 und T02 umsetzen. Reviewer prüft Contracts.
4. Coordinator gibt Wave 1 aus Parallel-Tasks.md frei.
5. Ein Agent bearbeitet genau einen zugewiesenen Task.
6. Handoff prüfen, relevante Tests nach Freigabe ausführen.
7. Coordinator integriert und aktualisiert STATUS.md.
8. Erst nach Gate-Freigabe nächsten Meilenstein beginnen.

## Profile

@coordinator: Planung, Bootstrap, zentrale Verträge und Integration.
@core: Sitzung, Kontext und Dateilesen.
@ui: Oberfläche mit Fake-Provider.
@provider: Ollama-Adapter.
@qa: Tests, Fixtures und Benchmark.
@reviewer: read-only Review.

Modelle werden geerbt. Keine feste Cloud-ID, keine geheimen Keys im Profil. Profile dürfen Shell nicht pauschal freigeben. Agentenprompts setzen keine tatsächliche Pfad-Sandbox; Ownership muss zusätzlich organisatorisch eingehalten werden.

## Parallelität auf 8 GB

Standardmodus: genau ein schreibender Agent aktiv. Parallel-Tasks bedeutet entkoppelte Arbeitspakete, nicht zwingend gleichzeitige Modellinferenz. Bei ausreichenden Ressourcen maximal zwei Implementierungslanes mit disjunkten Dateien; nie zwei Agents in derselben Datei. Reviewer kann später separat laufen.

Subagents, Worktrees und separate Sessions sind Optionen, keine Voraussetzung. Worktrees nur nach Nutzerfreigabe und verfügbarer Git-Installation. Keine automatischen Branches, Commits oder Pushes.

## Konflikte

Bei Contractkonflikt stoppt der Consumer. Bei fremden Änderungen diff melden, nicht resetten. Kein git reset --hard, clean -fd oder Checkout zum Überschreiben. Bei unzureichender Modellqualität zunächst nur einen Task und kürzere Prompts verwenden.

## Nachladen von Dokumenten

AGENTS.md fordert aufgabenbezogenes Lesen. Andere .md-Dateien werden nicht allein deshalb automatisch geladen, weil sie im Root liegen. Keine riesige instructions-Liste für alle Dokumente erstellen.
