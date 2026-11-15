# Lokale statische Prüfung der Retail-Serverzustandsgrenze

Für A1 fehlt die originale autoritative Reihenfolge nach Respawn. Die bestehende
Richtlinie priorisiert dafür REA/GhidraMCP. Frische Toolprüfung auf diesem
Ubuntu-Host: kein Ghidra-/REA-/Frida-Analysebackend in den verbundenen Tools,
keine Programme `ghidra`, `ghidraRun`, `analyzeHeadless` oder `pyghidra` im PATH.
`/usr/bin/objdump` ist vorhanden. Das ist keine Änderung des historischen
Shadow-Qualifikationsstands und kein Beleg einer dortigen aktuellen Verbindung.
RDC wird wegen des bekannten Kontingentblocks nicht erneut aufgerufen.

Root verwendet für die unabhängige Vorbereitung ausschließlich lesende lokale
PE-Exportauflösung und begrenzte Disassemblierung der vorhandenen legalen
Originalkopie. Engine-SHA256 frisch bestätigt:
`b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f`.
Die Retail-Exports nennen getrennt ProcessGameTick und ProcessPredictedGameTick.
Aus Exportnamen oder SDK-Deklarationen wird kein Feldoffset oder Hookvertrag
geschätzt. Reicht die begrenzte Originalanalyse nicht, bleibt der konkrete
Binärvertrag offen; eine spätere Ghidra-Gegenprüfung wird nicht als erledigt
ausgegeben. Keine neue Installation, kein Prozessattach, keine Runtimeänderung.

Private Disassembly und Originalbytes bleiben außerhalb des öffentlichen Git.
Bereinigte Erkenntnisse benötigen Adresse, Originalhash, Werkzeugversion,
vollständige Aufruf-/Feldgegenprüfung und ausdrücklich benannte Restunsicherheit.
Ein abgeleiteter Hook erfordert anschließend eigenen begrenzten Entwurf und
Qualifikation; dieser Read-only-Schritt erteilt keine Runtimefreigabe.
