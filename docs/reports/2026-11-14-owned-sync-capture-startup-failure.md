# Eigene Syncaufzeichnung: Setupfehler vor Gameplay

**FAIL**, kein600s-/Sync-/WAN-Nachweis. Versuch
`own-sync018-yodeller-root-20261114-145119`, Ergebnis-SHA256
`ae048d5fc51fa6bd564d7cf891a5681c16a644366bdb77b956394765e454fd75`.

Vier eigene Rollen erreichten die pausierte Neunerbarriere. Der frische
Capture-Exec-Helfer brach an `roles changed before capture exec` ab, bevor
tcpdump oder ein unpausiertes Beobachtungsfenster begann. Die PCAP ist0Bytes.
Fehlende Statistik und nicht parsebarer Header sind als Fehler erhalten.

Die gespeicherte vollständige Rollenbindung enthält unveränderte tatsächliche
Ports/Inodes, PID-/Startidentitäten, Rollen-CWDs, Cgroups und eigene NetNS.
Der Quellcode liefert Portpaare als Tupel; über die JSON-Konfiguration werden
daraus Listen. Der exakte Vergleich zwischen neu gelesenen Tupeln und
JSON-Listen schlägt damit schon bei gleichen Werten fehl. Ein eigener Test
des tatsächlichen Prozessübergangs muss diesen Befund vor Korrektur belegen;
keine Ableitung einer tcpdump-/NetNS-Capability aus diesem Fehlstart.

Alle vier Spielrollen normal geschlossen, vollständige Schlusslogs erhalten.
Root verifizierte unabhängig640Dateien mit Metadaten, vier Loghashes,
Prozessstartidentitäten und Displayende: `PASS_RESTORE`. Capture-Supervisor
mit Exit1 beendet; kein eigener Capturekind-PID wurde vor Exec angelegt.
Kein Rollen- oder Flottenprozess wurde forciert beendet.

Nächster Schritt gemäß [enger Korrekturplan](../superpowers/plans/2026-11-14-owned-capture-json-binding.md):
JSON-stabile Darstellung an der Quelle, tatsächlicher Übergabetest,
unveränderte Guards und frischer deaktivierter Fork. Kein automatischer Retry.
