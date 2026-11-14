# Capturebindung bei verschwindenden fremden Dateideskriptoren

**Goal:** Die konkret fehlgeschlagene `/proc/PID/fd`-Beobachtung robust
machen, ohne verschwundene/geänderte eigene UDP-Sockets zu akzeptieren.
**Architecture:** Nur ENOENT beim bereits vorhandenen einzelnen readlink
bedeutet, dass dieser aufgelistete Deskriptor inzwischen geschlossen wurde.
Die unveränderte zweite FD-Menge, UDP-Tabelle, Rollen-/Port-/Inodebindung
und PID-/Namespaceguards entscheiden weiterhin strikt. Keine Wiederholung,
kein zusätzlicher Scan und kein Rebaseline.

Ausgang: Lauf150433 FAIL75eb5fa3333f7962463f58df98030336f3e5538e038094689b20f14cd783880e
vor600s an verschwundenem botB-FD46. Capture normalExit0,58088Pakete,
0KernelDrops; alle drei Paare je456matching sampled syncchecks,0Differenzen,
0Missing/Unsupported/Fragments/Konflikte. Voller Versuch bleibtFAIL.
Alle4Rollen normalclosed, Root640Dateien/4Loghashes/Metadaten/PIDs/DisplayRestorePASS.

- [ ] Tatsächlichen FD-/UDP-Fixturleser im ersten und zweiten vorhandenen
  Durchlauf einen aufgelisteten Nicht-UDP-FD verlieren lassen: RED belegen.
- [ ] Nur `FileNotFoundError` des einzelnen readlink überspringen.
  Alle anderen Fehler bleiben Fehler. Keine weiteren Prozessreads/Sleeps.
- [ ] Verschwundener/ausgetauschter erwarteter UDP-Inode, Port, PID oder
  Namespace muss weiterhin vor Capture/bei Guard scheitern; zwei bestehende
  Durchläufe und vollständiger JSON-stabiler Bindungsvergleich bleiben.
- [ ] Gezielte alte37Fälle plus neue Churn-/Socketverlustgegenfälle prüfen.
  Alten FAIL/Freeze unverändert lassen; frischen deaktivierten Fork erstellen.
- [ ] Root reviewt und entscheidet den nächsten tatsächlich nötigen nativen
  Diagnoseversuch. Keine automatische Wiederholung der600s allein aus diesem
  Offlinefix;456verifizierte Vergleichszeitpunkte bleiben begrenzte Evidenz.

Dies ist eine Beobachtungsfehlerkorrektur, keine Syncursachenbehebung.
