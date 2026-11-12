# Ausführungsplan – kompensierter Original-Inputvergleich

Owner /root/review_names_transaction. Exklusiver Claim: `/srv/tse-a1-colt-pitch-analysis-20261112/worktree-claim.json`. Basis des eigenen isolierten Worktrees 5ede10f5b169b91184d7c1191932214e713e1cec. Rootintegration, Native und Build bleiben ausschließlich Root vorbehalten.

Spec: `COMPARISON-SPEC.md`. Geschlossene Kausalanalyse: `/srv/tse-a1-colt-pitch-analysis-20261112/ANALYSIS.md`.

- [x] Alte Pakete/Frozen/Native vollständig vorab pinnen; reale sechsteilige Inputfolge und alle Reads ableiten.
- [x] Faktor 2 auf lokale Kumulativstufe eingrenzen; fehlenden Pointer-/GetInput-Trace offen erhalten.
- [x] Originale Symbole, 0,25-Skalierung, Setter und normalen PersistentSymbols-Ladepfad statisch binden.
- [x] Root-Ruling umsetzen: genau AllowMouseAcceleration 1→0 und MouseSensitivity 1→0,25; gleicher Grundfaktor, keine anderen Eingabeparameteränderungen.
- [x] Gezielte RED-Fälle vor Implementierung; reale Konfigurations-/Reader-/Controllerfunktionen anschließend GREEN.
- [x] Vollständige 240er private Regression und 32 vorhandene Readertests; keine Nativequalifikation aus Tests.
- [x] 54 AST-identische Schutzfunktionen und zwölf bytegleiche Kern-/Transport-/Policydateien vergleichen.
- [x] Finale Closure, Docscommit, Pins und Reviewhandoff erstellt; Abschlussquittung und Commit stehen im HANDOFF.json.

Ruling: Der genaue alte Ursprung ist unbewiesen. Der neue Entwurf ist deshalb ein ausdrücklich autorisierter kontrollierter Vergleich und kein behaupteter Bugfix. Eine falsche Hypothese kostet höchstens den einen separaten Root-Versuch; unveränderte Abbruch-/Restoregrenzen verhindern eine automatische Ausweitung.

Ruling: Die bisherige Testfunktion mit dem Namen actual_inputs wird im Offlineadapter gegen fünf verifizierte statische Originalbilder ausgeführt. Dies verhindert aktuelle Labreads und ersetzt keine frische echte Root-Pinprüfung. Kein Test wird übersprungen.

Nach Autorhandoff bleibt der Worker idle. Root beauftragt den unabhängigen Reviewer und entscheidet anschließend über einen getrennten Freeze.

Privater eingefrorener Entwurf: /srv/tse-a1-colt-noaccel-completion-20261112. Die finale Closure und Testquittung werden dort getrennt von diesem reinen Dokumentationscommit gepinnt.
