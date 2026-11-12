# Enger V2-Fix: bereits gelesene optionale Globals bleiben fatal

Owner /root/review_names_transaction, eigener bestehender Git-Worktree ab d3d4683. Root besitzt Runtime/Build/Integration. V1, Originalautor, Root-Freeze und geschlossenes 171044-Fenster bleiben anhand vollständiger Inventare unverändert.

## Abnahme

- [x] Exakten Reviewer-RED in eigener Kopie gegen unveränderte V1 reproduzieren.
- [x] Zusätzliche unmittelbar betroffene Gegenfälle: erster falscher Wert plus Tickwechsel, Änderung im zweiten Read plus früherer Statefehler, Rohwerte im tatsächlichen Attemptstream; korrekter Wert plus reiner Tickwechsel bleibt transient.
- [x] Nur Reader-Fehlerpriorität und Übernahme der Fehlrohwerte korrigieren; keine zusätzlichen Reads, Inputs oder Retry-/Zeit-/Gain-/Transportänderung.
- [x] Konkrete Fälle GREEN sowie betroffene vorhandene Reader-/Attemptregression, kein optionaler Vollausbau.
- [x] Unveränderte Setter-/Seal-/Start-/Restorequellen mit bestehenden V1-Quittungen binden. Eigene Gates false; genau zwei Runtimequelldeltas plus eindeutige V2-Prefixkennung.
- [x] Exakte Closure, Diff, Testquittung, Altbestandsvergleich, Dokumentationsfolgecommit und Handoff. Danach idle für unabhängiges Review.

Der Fehler liegt vor jedem neuen Nativeversuch. Falsche optionale Werte dürfen nicht durch ein generisches state/tick changed zum erlaubten Wiederlesen werden. Erfolgreiche Profile bleiben unverändert doppelt konsistent gelesen. Der alte native Pitch-FAIL und dessen offene Ursache werden nicht umgewertet.

Abgeschlossen: konkrete RED→GREEN, 64 betroffene Tests, exakte Closure/Altprüfung und Dokumentationsfolgecommit. Kein weiterer Native- oder Offlineauftrag aktiv; nach Handoff idle.

Privates Paket: /srv/tse-a1-colt-noaccel-v2-completion-20261112
