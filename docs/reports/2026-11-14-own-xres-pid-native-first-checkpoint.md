# Eigene XRes-PID-Methode: erster Nativeversuch fehlgeschlagen

Am 14.11.2026 um23:35UTC wurde genau eine eigene Metadatenprobe ausgeführt.
Status **FAIL_METHOD_XRES_PID_EVIDENCE**, Resultat-SHA256
`47e10306c99bcc7e01cd2fb2f7e50596daaca6d25eb5199ee41da211b15b7edd`.
Keine TSE-/Wine-Instanz, kein RECORD und kein Input waren beteiligt.

XRes1.2 meldete fünf Ressourcenbereiche. Darunter war der Hintergrundbereich
Basis0/Maske2097151. Die reine Validierung verwarf diesen schon vor dem
Abgleich der drei eigenen Verbindungen als `invalid client range`.
Der gespeicherte erste Snapshot enthält sechs erfolgreiche QueryClientIds-
Antworten (Success0, ein PIDwert, Maske2, Länge4): zwei eigene Verbindungen
des Drivers und eine des Peers, jeweils über Ressource und tatsächliche Basis.
Die erwarteten eigenen PID-/Start-/Namespacewerte waren vor/nach der Abfrage
unverändert. Ein zweiter Snapshot wurde nicht ausgeführt. Das sind begrenzte
Einzeldaten, keine bestandene Methode oder kontinuierliche Lebenszeitbindung.

Der Controller meldete zusätzlich fehlende vollständige Zwei-Snapshot-
Abschlussbelege. Tatsächlich wurden im abgebrochenen Lauf eine Clientliste
und sechs ID-Arrays allokiert und genau einmal freigegeben; die Native-
Closequittungen enthalten keine Fehler. Root prüfte diese Zahlen unabhängig.
Die fehlgeschlagene Gesamtquittung bleibt unverändert erhalten.

Alle vier Rollen wurden regulär geschlossen und reaped, Exit0, ohne Force.
Die drei Fenster wurden zerstört, alle vier X-Verbindungen geschlossen und
die Fehlerhandler wiederhergestellt. Root prüfte anschließend die Abwesenheit
der exakten Prozessgenerationen, Display167/Socket/Lock und die Verfügbarkeit
der fünf technischen Zugriffssperren. Keine automatische Wiederholung.
Die Metadatenprobe dauerte0,216666s. Äußere Hostbeobachtung: zwei Proben,
maximal0,314924s Abstand, CPU48,3871%, verfügbarer RAM3531493376B,
Datenträger9890459648B; wegen ChildExit1 blieb auch ihr Gesamtstatus FAIL.
Keine Ressourcenabnahme für Gameplay.

Die folgende Korrektur muss die tatsächliche QueryClients-Protokollsemantik
an Primärquellen prüfen und ein realistisches Basis0-RED vorweisen. Eigene
Zielverbindungen müssen weiterhin positiv, eindeutig und PID-gebunden sein.
Keine Umdeutung historischer U-Verbindungen, keine Änderung an A1-Gain,
Toleranzen, Retailclient oder bestehendem Nativeergebnis.

Vorher vollständig verifiziert: Quellstand lokal6d07a9b, Remote
`7cced7dd26622b86fb42e0899fdaf07bf9bb82f2`, identischer Tree
`3573366f03d9d4035f651341660044bec867920f`; tatsächlicher Fetch/diff0.
Delta055:7097402B, SHA256
`06ad5e2685086f84191ebd398a705c758620d7189b2cb0ddf1c02c86db17e371`,
privat in Drive14VtEZjbDm2kf-5QH7gEA4BjWMBM6jG5J. Vollständig rückgelesen;
807 Dateiinhalte/UID/GID/Modus/mtime_ns zweimal geprüft. Der Lauf selbst
entstand danach und gehört in das nächste Delta.

Flottenabfrage23:36:34: alle sechs Instanzen mit je acht eigenen Bots;
Dev zusätzlich ein unbekannter Teilnehmer. Keine Liveänderung. A offen,
B nicht begonnen. Private Quittungen liegen unter
`/srv/tse-cecil-rollout-evidence-20261114/own-xres-pid-method-root-20261114`,
`xres-pid-method-root-cleanup.json` und
`own-host-around-xres-pid-method-root-20261114`.
