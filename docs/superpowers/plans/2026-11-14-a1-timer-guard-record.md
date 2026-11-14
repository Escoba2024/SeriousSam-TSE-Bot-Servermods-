# A1: fehlende Action-Kette passiv eingrenzen

Root besitzt Runtime/Integration. Dieser isolierte Branch verändert keine alten Pakete und startet weder Prozesse noch Hooks.

Ziel: Die vorhandenen GetInput-Datensätze um die tatsächlichen beobachteten Game-/Pause-/Vtablewerte ergänzen. Keine Fokusänderung auf Verdacht; kein neuer Hook, Input, Wait, Retry, keine Lockerung oder neue Gameplayfunktion.

- [x] Geschlossene Control-/Tracefehler getrennt auswerten; tatsächliche geschlossene Originalbedingung bleibt unbekannt.
- [x] Original-Timercaller, virtuelle Controls-Tabelle, getter-exportierte Funktionen und IAT gegen SDK107/archivierte Disassemblierung und hashgeprüfte Originaldateien abgleichen.
- [x] Toolgrenze erfassen: kein REA/Ghidra-MCP in ALL_TOOLS; keine ghidra/analyzeHeadless/java/rea-Kommandos im aktuellen PATH. Kein Ghidra-Aufruf/keine Dekompilation behauptet.
- [x] Bestehenden Inputrecord bei Entry/Return rein lesend ergänzen; ausdrücklich `actual_branch_proven=false`.
- [x] Statische Guards um fünf Originalregionen erweitern, weiterhin exakt sechs bestehende Hooks. Altes Metadatenschema vor Attach ablehnen.
- [x] Neue Fälle auf altem JS RED, danach neue Snapshotfälle und vorhandene Fehler-/Warmup-/Cleanupfälle GREEN. Ausschließlich nach Roots Ressourcenfreigabe.
- [x] Neue separate deaktivierte Library und Manifest erstellen; alte Library und Root-Freeze per Hash unverändert.
- [ ] Commit/Handoff und unabhängiger Review.
- [ ] Root erstellt bei Bedarf eine eigene neue Freeze-Kopie, aktualisiert transitive Pins und führt frischen Preflight aus.
- [ ] Tatsächliche Guardwerte, vollständige Action-Sequenz und Observerkosten erst in separat autorisiertem Root-Fenster messen; kein automatischer Retry.

Bericht: `docs/reports/2026-11-14-a1-missing-action-chain.md`.
