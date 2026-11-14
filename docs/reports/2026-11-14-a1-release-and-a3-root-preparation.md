# A1-Eingabeabschluss und A3-Kampfvergleich: Rootvorbereitung

Noch kein neuer nativer Lauf und keine A-Abnahme.

Die A1-Korrektur aus Autorencommit `627e6b2606585b24399d0a0ea467b44c8044c4dd`
ist als `6f6e6b37508e6c45857dc120b3d95d89341f66f3` integriert. Root hat
die enge Änderung geprüft und 20 neue sowie 27 unveränderte historische
Action-/Request-/Postobserve-Regressionen erfolgreich ausgeführt. Für den
historischen Offline-Gatetest wurde ausschließlich das importierte Pythonmodul
auf false gesetzt; keine eingefrorene Datei wurde dabei geändert.
Der separat dokumentierte historische Vergleich gegen den zu alten Parent
bleibt FAIL. Die echten A1-Ergebnisse bleiben unverändert.

| Rootkopie | Manifest-SHA256 | Launcher-SHA256 | Pins |
|---|---|---|---|
| `/srv/tse-a1-release-deadline-root-frozen-20261114` | `2665517067a491e00607c7e4f88d5c3585739c66896f24c26b25eff672b7d136` | `a2d9fbe4ee9d5e86a60cc6a133d20242e2a302441e2841a29e7b5e5e829e4aa5` | 70 Runtime/61 Diagnose/14 Collector |
| `/srv/tse-a3-instruction-probe-root-frozen-20261114` | `272d04e3f82f270ecf52241da8fc66a2f516e7f9657215af08703044e6aad6a7` | `f9cb4c4991d101e096787c5ccd5ee26a552b0a34dc8f43e600e7f75f07a7433a` | 79 Runtime/109 Quellen |

Beide Rootkopien wurden separat gegen die deaktivierten Autorenpakete geprüft:
nur Ausführungsgates, eigene Dienst-/Evidencebezeichner und bei A1 der eigene
Collectorpfad sowie die zugehörigen Manifeste unterscheiden sich. Externe Pins,
Originalmodule, Grenzen, Eingaben, Hooklogik, Close und Restore sind gleich.
Das ist ein `PASS_SCOPE` für diese Ableitung, keine native Qualifikation.

Root führte außerdem die 59 gezielten A3-Fälle erfolgreich ohne Skips aus.
Ein erster Aufruf verwendete irrtümlich bereits gepatchte Hookbytes als
Eingabe für die historische Patchprüfung: sieben erwartete Hashablehnungen.
Mit der im Bericht vorgeschriebenen unveränderten Ausgangsfixture bestanden
dieselben 59 Fälle; keine Code- oder Grenzänderung. Beide Logs bleiben erhalten.

Nächster Schritt nach Ende aller Archiv-/Reader-/Agentenarbeit und frischem
Preflight: genau ein A1-Original-NoFire-Lauf mit unveränderten ACK-, Gain- und
350-ms-Grenzen. Danach Originalbytes, Unload/Detach, Workerende, normale
Rollencloses, Schlusslogs und unabhängigen Restore prüfen. Kein automatischer
Retry oder anschließender Firelauf. Der A3-Vergleich bleibt einzeln ausgewählt
mit 120 Sekunden, Hard2, Diagnostics0 und geprüften Original-Damage-Hooks.

Flottenprüfung 14:38:09 UTC: alle sechs Server je acht eigene Bots, null
zusätzliche Teilnehmer, Spawnwert0. Sechs Dedicated-Logpräfixe wurden gegen
13:51:58 UTC verifiziert; seitdem null neue Sync-, Disconnect-, Crash-, Join-
oder CRC-Fehlermeldungen. Red und Yodeller laden Gen2, übrige vier Build018.
Die Ursache der früheren externen Syncereignisse ist weiter unbekannt.
