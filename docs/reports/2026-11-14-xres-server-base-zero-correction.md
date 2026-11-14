# XRes: belegter Hintergrundclient0 und enge Policykorrektur

Der erste eigene XRes-Methodenlauf blieb FAIL. Die sechs echten Resource-/Base-
PIDantworten waren korrekt und vollständig freigegeben; die pure Policy verwarf
vor ihrer Zielprüfung die zusätzliche Serverrange Base0/Mask2097151. Das war
meine zu enge Validierungsannahme. Die Korrektur betrifft ausschließlich zwei
Policyzeilen; Worker, Controller, Builder, Zeitlimits und alle alten Pakete bleiben
unverändert. Kein neuer Nativefall, Display, Compiler oder Input wurde gestartet.

## Tatsächlicher geschlossener Beleg

Privates Originalresultat:
`/srv/tse-cecil-rollout-evidence-20261114/own-xres-pid-method-root-20261114/method-result.json`,
SHA256 `47e10306c99bcc7e01cd2fb2f7e50596daaca6d25eb5199ee41da211b15b7edd`.
Ein echter Snapshot, fünf Ranges einschließlich Server0 und vier positiven
Clientranges; genau sechs erfolgreiche Einzelqueries mit richtiger eigener PID,
Success0, Maske2 und Länge4. QueryClientsarray1/1, IDarrays6/6 freigegeben.
Alle vier eigenen Rollen normal beendet/reaped, Exit0, kein Force und keine
Rollenfehler, Display167 abwesend.

Die nachfolgende Closeprüfung erwartete den vollständigen Zweierablauf mit
12IDarrays und meldete deshalb einen zweiten Fehler. Dies ist kein belegtes
Speicherleck: die vorhandene Nativeclosequittung zeigt ein Snapshot und6/6Frees.
Diese sekundäre Diagnose wird hier nur richtig eingeordnet; Cleanupcode und
MethodenPASS-Prädikat bleiben unverändert. Ein sauberer Abbruch ist kein
bestandener Zweiersnapshot-Methodenfall.

## Primärquelle und Vertrag

Das [offizielle Xorg-Server21.1.11-Quellarchiv](https://www.x.org/releases/individual/xserver/xorg-server-21.1.11.tar.xz)
belegt: `dix/main.c:159` initialisiert serverClient mit Index0, Zeile163 setzt
clients[0]; `dix/dispatch.c:3586` berechnet clientAsMask aus dem Index.
`Xext/xres.c:229` iteriert QueryClients ab Index0 und Zeilen253–254 geben
clientAsMask und RESOURCE_ID_MASK zurück. Damit ist die0-Hintergrundrange
reguläres Serververhalten. Dies ist eine Quellsemantikgegenprüfung, kein neuer
Buildnachweis für die genaue gepinnte Host-Xvfb-Binärdatei.

Das vorhandene Protokoll `resproto.txt:64–78` definiert Base/Mask als CARD32 und
die Maskierung zur Clientidentifikation; es fordert kein positives Basefeld für
jede Listenrow. `resproto.txt:110–124` beschreibt dagegen CLIENTIDSPEC0 als
Wildcard. Deshalb wird keine Query auf Base0 hinzugefügt.

ArchiveSHA256:
`1d3dadbd57fb86b16a018e9f5f957aeeadf744f56c0553f55737628d06d326ef`;
Xext/xres.c:
`2fa908ddb4b3083aa0c5c7c1c6f3c816cf65807a2b4911dca863e2153dd12880`.
Private Quellen und weitere Datei-/Provenienzpins liegen in der Quittung unten.

Der neue enge Vertrag erlaubt Base0 ausschließlich als gültige Hintergrundrow.
Keine Row wird ausgeschnitten. Uint-/Boolprüfungen, positive Masken,
BaseMaskdisjunktheit, Duplikatverbote und eindeutiges Zielmatching bleiben.
Nach eindeutiger Zuordnung muss die eigene Zielbase weiterhin ausdrücklich>3
sein. Alle sechs Resource-/Basequeries und ihre PID-/Masken-/Status-/Längen-/
Prozessgenerationprüfungen bleiben gleich. Auch eine passend erfundene PID kann
keine eigene Ressource auf Server0 umdeuten; ambige Hintergrundranges scheitern.

## RED/GREEN und Grenzen

Drei neue fokussierte Tests prüfen realistische0-Listenrow, neun ungültige/
doppelte/ambige Varianten und eine adversariale eigene Ressource in Server0.
Der erste RED zeigt die tatsächliche ValueError-Kante; ein zusätzlicher RED
formuliert denselben Befund als explizite Assertion. Beide sind gespeichert.
Danach 3neue+28vorhandene=31Tests PASS, 0Skips, 2,255s. Nur pure Policy,
Fake-C-/Kindtests, Offlinepaketpins und geerbte OwnChildregressionen.

Der unveränderte erste Originalsnapshot besteht die korrigierte Einzelpolicy
im reinen Archivreplay. Das alte Result bleibt unverändert FAIL; auch die
Methodenpolicy gibt für das Originalresult weiter FAIL. Zweiter echter Snapshot,
Methodenqualifikation und alle A1-/Lifetime-/Retailnachweise bleiben offen.
Alte Verbindung U bleibt UNKNOWN.

Private0700/0600-Belege:
`/srv/tse-xres-server-base-zero-evidence-20261114/`.
`offline-receipt.json` SHA256:
`54e932a2bb165b03b25ce033e54d7897768fcbb012fcfbb0b03ddf2f03e19db1`.
GREEN `green-range-and-regressions.log`:
`cfea1d8cd6c9d9158e685ae892e5deabfa217e6942d1564e148787b9fdfd69c1`.
RED `red-realistic-server-zero-explicit-assertion.log`:
`1442aaaed4f7161f43a15a57a6f98bb564a877bdf79300f808591cb7ba9b433c`.

```sh
cd /srv/tse-xres-server-base-zero-20261114/tools
python3 -B -m unittest test_xres_pid_method test_xres_pid_lifecycle test_xrecord_core_process -v
```

Root entscheidet nach unabhängigem Review über ein neues deaktiviertes Paket,
einen separaten Freeze und gegebenenfalls einen neuen begrenzten Methodenfall.
Es wurde kein Retry ausgelöst und kein altes Paket überschrieben.
