# Build024 Little Trouble: geschlossene Zehn-Minuten-Beobachtung

Alle acht eigenen DEMON-Bots zeigten Bewegung, native Fernfeuerflags und
beobachtete Zusatzwaffengewinne. Der isolierte Fall lief 600,173441590 Sekunden
mit Hard2, Original-Dedicated und eigenem unverändertem Originalclient bei
20 FPS. Die beiden Botgruppen mit je vier Spielern luden ausschließlich die
geprüfte Build024-DLL. Die öffentlichen Server wurden nicht verändert.

Das ursprüngliche Resultat bleibt unverändert
`PASS_LIMITED_A4_OBSERVATION_FUNCTIONAL_REVIEW_REQUIRED`, `qualified=false`
und `functional_pass=false`. Dieses Fenster ersetzt weder Übergangs-/Resettests
noch Dauerabnahme, direkten Buildvergleich oder den offenen Skulls-Fix.

## Bindung und vollständige Nenner

- Quellcommit im Buildmanifest: `100bda43eb46c7d671d71b7a50fae673a9e4406e`.
- DLL: `192169fe8396bfe1fb9c49419657b9146120c64eb3ac15095ac50a6f8659753c`.
- Rootmanifest: `58faf8c7aed63abda0c6c96ef7c27d78219fd76a27b4a5199b9c0d5def70c99c`.
- Resultat: `dc01c2d8cf9c26121f1469870b8140123039c2f63e7921a35fa975401d865093`.
- Private Rohbelege: `/srv/tse-milestone-a-evidence-20261111/nav20-024-trouble-root-trouble-20261115-014819`.

Die unveränderte geordnete V3-Lifeauswertung akzeptierte alle 13956
Leseversuche einschließlich 376 gespeicherter Fehlversuche. Sie zählt 279
beobachtete Leben, davon drei reine Leichenzustände, 188 linkszensierte und
acht rechtszensierte Leben sowie vier mehrdeutige HP-Reihenfolgen. In 137
Leben wurde eine brauchbare Zusatzwaffe beobachtet; 184 tatsächliche
Inventargewinne sind belegt. 271 Leben endeten mit beobachtetem Tod.
Die 236 serverseitigen Fremdabschusszeilen sind ein Gesamtfensterbefund,
kein Nachweis einzelner Schadenspfade oder eines Vorteils gegenüber Build018.

| Botgruppe/Local | Leben | Leben mit Zusatzwaffe | Zusatzwaffengewinne | Bewegungsaktionen | Fernfeuerflagproben | längster stationärer Abschnitt (s) |
|---|---:|---:|---:|---:|---:|---:|
| A/0 | 37 | 22 | 30 | 523 | 537 | 1,650 |
| A/1 | 37 | 16 | 25 | 521 | 316 | 2,100 |
| A/2 | 40 | 17 | 23 | 525 | 369 | 2,199 |
| A/3 | 38 | 17 | 20 | 525 | 352 | 1,450 |
| B/0 | 23 | 13 | 18 | 547 | 646 | 1,950 |
| B/1 | 32 | 18 | 25 | 532 | 460 | 3,800 |
| B/2 | 34 | 14 | 18 | 527 | 324 | 3,099 |
| B/3 | 38 | 20 | 25 | 525 | 377 | 2,150 |

Die stationären Werte stammen aus dem vorhandenen Active-Evidence-Verfahren;
sie sind kein lückenloser Bewegungsbeweis. Native Fernfeuerflags beweisen
keinen einzelnen ursprünglichen Waffenfunktionsaufruf. Fehlende Aktivitäts-
slots und widersprüchliche Sourcegenerationen wurden dort nicht gemeldet.

Der längste beobachtete lebende Abschnitt eines Lebens ohne jemals beobachtete
Zusatzwaffe betrug 33,391845703 Sekunden: Slot7, Spawnclock421,320648193,
lebend beobachtet bis454,712493896, danach Tod454,962432861. Dieser Abschnitt
ist nicht linkszensiert; maximaler Leseabstand0,299926758 Sekunden. Der nächste
Gegenbefund beträgt30,892456055 Sekunden bei Slot8 und ist linkszensiert.
Bei einem später bewaffneten Leben betrug der größte obere Alterswert bis zur
ersten beobachteten Zusatzwaffe35,141418457 Sekunden. Diese Werte erklären
keinen Item-/Routenpfad und dürfen nicht als Erfolg aller Spawnphasen gelten.

## Navigation und Grenzen

Ein tatsächlicher `CecilGroundReplan` steht im geschlossenen Bot-A-Log,
Zeile6632: Local2/Entity686, Tick7437, Source16, Hop18, neuer Anker99,
Höhen8,496805 und Ziel22. Der letzte vorherige Snapshot, Tick7420,
hatte bereits Anker99; danach zeigt Tick7440 Hop99 und Bewegung.
Das belegt einen ausgeführten Replan, aber nicht die neue Stale-Anchor-
Verzweigung: der unmittelbare alte Anker am Reset wird noch nicht protokolliert.
Kein kausaler Waffenbeschaffungserfolg aus diesem Marker wird behauptet.

World-/Navbindung und aktive Konfiguration wurden im tatsächlichen Fall
geprüft. Sprünge, Teleporter, Gefahren, Kartenwechsel und Entityreset sind durch
diesen einzelnen gewöhnlichen Kampffall nicht vollständig abgenommen.

## Close, Wiederherstellung und Ressourcen

Alle vier Rollen schlossen regulär. Die vier vollständig geschlossenen Logs
enthalten keine neuen Ereignisse der sechs geprüften Sync-/CRC-/Crash-/Action-/
Joinfehlerklassen. Root prüfte02:00:03 UTC unabhängig640Dateien, vier Loghashes,
Prozessgenerationen, Units, Display154-Abwesenheit und vier freie Sperren:
`PASS_RESTORE`. Geprüft sind Inhalt, UID, GID, Modus und Dateimengen; keine
exakte Fixture-Mtime wird behauptet. Die Restorequittung enthält den absoluten
`case_result`-Pfad und seinen Hash für den nächsten isolierten Kartenfall.

Der äußere Hostbeobachter schloss `PASS_HOST_OBSERVATION_ONLY`:697Proben,
maximaler Abstand1,003213597 Sekunden, gemessenes CPUmaximum64,467005%,
minimal verfügbarer RAM2555777024Bytes und freier Datenträger9415987200Bytes.
Keine Budgetverletzung, kein Signal oder Retry, KindExit0/reaped und identischer
Quellenhash vor/nach dem Fall. Das ist keine formale B-Kapazitätsqualifikation.

Nächste Schritte: geschlossene Rohdaten als nächsten Delta sichern; Hole und
Yodeller einzeln prüfen; Skulls-Recoveryursache mit passivem Entscheidungsbeleg
isolieren. A bleibt offen, B nicht begonnen; Live bleibt der bestätigte Stand.
