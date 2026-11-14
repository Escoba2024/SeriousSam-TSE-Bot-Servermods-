# Prospektiver Feuerobserver-V2-Lauf: Ressourcen-FAIL

Der eigene Lauf `a4-fire020-v2-20261114-100455` endete am14.11.2026 um10:06:27UTC mit **FAIL**: Host-CPU80,095923% überschritt die unveränderte75%-Grenze. Er scheiterte vor Abschluss der ersten120-Sekunden-Slotphase; keine neue24/24-Abnahme und keine Nativefreigabe für Build020 oder den V2-Abschlussbeobachter.

Build020 blieb unverändert094ec8ed…/431104Bytes. Eingefrorenes Manifest2b55f08482586b73d08e6e88fd607603b5687b1789937e5bb6161b980274cdd4.31Ressourcenproben: Mindest-RAM2829295616Bytes, Mindest-Disk11095818240Bytes, Gameplayprobenlücke höchstens1,103414s; die getrennte Startlücke47,230136s ist kein Gameplaygap. Der CPU-Spitzenzeitpunkt lässt sich aus dem gemeinsamen Linux-Monotonic-Clock ungefähr auf10:06:13UTC abbilden.

Root veröffentlichte während dieses Fensters Quellen über den GitHub-Connector und startete dafür mehrere parallele kurzlebige Python-Dateileser. Diese eigene Arbeit überlappte das Gameplayfenster. Es liegen keine vollständigen zeitgleichen PID-CPU-Deltas vor; eine alleinige kausale Zuordnung der Spitze wird deshalb nicht behauptet. Diese Lastbedingung war vermeidbar. Vor einem weiteren getrennten Fenster müssen auch Root-Veröffentlichungen, parallele Leser und Sicherungen beendet sein; sämtliche Kriterien bleiben unverändert. Keine automatische Wiederholung.

Alle vier eigenen Spielrollen wurden regulär geschlossen, vier Schlusslogs ohne neue Sync-/Disconnect-/Crash-/InvalidAction-/Joinfehler akzeptiert. Root prüfte unabhängig643Dateihashes samt Modus/UID/GID, fünf ursprüngliche Abwesenheiten und vier Schlussloghashes; alle passenden Spiel-PIDs sind beendet. Ergebnis-SHA256762713c0a1c0e688008e641bda62813c850a7f49beaf3ff9be8e1a5b0ce41f4b. Frischer Originalpreflight10:09:06UTC bestätigt vier freie Rollen, beide Displays frei, beide Locks erwerbbar, CPU36,88%, verfügbarerRAM3657043968Bytes und Disk11080667136Bytes.

Keine020-Liveübernahme: sechs Instanzen bleiben Build018, Hard2nurDev/Red. A1, A3/A4 und formale Dauerprüfungen bleiben offen, B unimplementiert. Die geschlossenen neuen Rohbelege benötigen den nächsten privaten Sicherungsnachtrag.
