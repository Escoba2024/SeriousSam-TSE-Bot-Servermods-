# Eigene Capturebindung über den JSON-Prozessübergang

**Goal:** Den konkret fehlgeschlagenen Setupvergleich korrekt typisieren,
ohne Port-/PID-/Namespace-/Datei- oder Capturegrenzen zu lockern.
**Architecture:** Der Rollendatensatz besitzt bereits an seiner Quelle eine
JSON-stabile Darstellung; Parent und frischer Exec-Helfer vergleichen dieselbe
vollständige Bindung. Root allein friert ein und startet.

Ausgang: eigener Versuch145119 FAIL vor Release und vor tcpdump,
Result`ae048d5fc51fa6bd564d7cf891a5681c16a644366bdb77b956394765e454fd75`.
`observe_roles` liefert `ports` als Liste von Tupeln; JSON erzeugt Listen von
Listen. Der bisherige Mocktest bildet diese tatsächliche Übergabe nicht ab.
Alle vier Rollen normal geschlossen, Root640Dateien/4Loghashes/Metadaten/PIDs/
DisplayRestorePASS. PCAP0Bytes; kein Spiel-/Capture-/Syncnachweis.

- [ ] In getrenntem Worktree einen roten Test mit dem tatsächlichen
  FD-/UDP-Fixturleser und JSON-Schreiben/Lesen bis zum Setupvergleich ergänzen.
- [ ] An `observe_roles` die Portpaare als Listen von Listen ausgeben.
  `socket_rows`-Parsing, Werte, Reihenfolge und alle Guards unverändert.
- [ ] Derselbe Test muss grün werden; geänderte Ports/Inodes/PID/Namespace
  nach JSON bleiben harte Fehler. Bestehende35gezielteFälle erhalten.
- [ ] Frischen deaktivierten Fork vom bisherigen Autorenpaket erzeugen;
  alten Rootfreeze und FAIL unverändert aufbewahren. Nur neue Sourcepins,
  keine Eingaben, Observer-/Aktivitäts-/Budget-/Capturegrenzen ändern.
- [ ] Root reviewt, friert neu ein, sichert/publiziert und startet nach
  frischem Preflight höchstens einen festen600s-Versuch. Kein Auto-Retry.

Ein Erfolg dieses Transporttests ist keine Runtime- oder Capabilitiesabnahme.
