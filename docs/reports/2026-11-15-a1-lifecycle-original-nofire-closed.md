# A1: Original-NoFire mit Lifecyclezuordnung geschlossen, Pitchkalibrierung FAIL

Der einzelne isolierte Originallauf vom 15.11.2026, Start 00:56:28 UTC, bleibt
**FAIL**: `opposite pitch gain does not reproduce`. Der horizontale Prüfschritt
bestand in diesem Fall; der vertikale Gegenversuch lieferte unterschiedliche
Verstärkung. Das ist weder ein dauerhafter Gainfix noch eine A1-Schadensabnahme.
Kein Schuss und kein normaler fremder Treffer wurden in diesem Fall nachgewiesen.

## Fall und unveränderte Grenzen

Private Evidenz: `/srv/tse-milestone-a-evidence-20261111/a1-xres-lifecycle-root-20261115-005628`.
Resultat-SHA256: `3e4398c98b2518b4dc44882243d4218d4f3f4678b8a1d36f0c34accaf6035e35`.
Rootmanifest: `e9cb52a1135ea3046570fdaaac6e2f37ac2117535b8d4c312239f39d7cbec90c`.
Der vorab unabhängig geprüfte Freeze verwendete den tatsächlichen eigenen
Lifecyclemethodenbeleg `1642b145…`. Eingabeprogramm, FPS, CP85/Runner90,
ACK2 und Held350ms sowie Gain-Toleranz blieben unverändert. Es gab keinen Retry.

Sechs Phasen enthielten acht Einzelrequests. Die gemessenen sechs
Hold-/Releasezeiten lagen zwischen 0,124862 und 0,265492 Sekunden, unter 350 ms.
Die vollständige kausale Pitchauswertung bleibt eine separate offene Aufgabe;
die JS-Actioninstrumentierung liefert keinen eigenen Raw-Pitchwert.

## Neue Messzuordnung, keine nachträgliche Umdeutung

Der passive Collector schloss `PASS_PASSIVE_XRECORD_DIAGNOSTIC_ONLY` mit
310 Records/175124 Bytes, 310 Freigaben, null malformed/drop/error/cleanup-error.
Die vier vom unveränderten Core unbekannten, im Adapter typisierten
Nicht-Cursor-XTestrecords bleiben ausdrücklich sichtbar. Raw-SHA256:
`6e85404f7c6c414567b3797438b92d7bfa746e5e25e4b3f44375a5e23e16f54f`.

Genau zwei akzeptierte XRes-Snapshots benötigten 28 PIDqueries. Beide
Clientarrays und alle 28 IDarrays wurden freigegeben. Die vollständige
Lifecycle-/Rohdatenauswertung bindet 238 aktuelle Query-/Warprecords an den
eigenen Originalprozess und belässt zwölf Records unbekannt. Eine im Stream
veränderte Verbindungsbase wird konservativ verworfen. Root reproduzierte die
Attribution vollständig und exakt. Historische U-Records bleiben UNKNOWN;
außerhalb dieses Recordfensters ist keine durchgängige Lebensdauer bewiesen.

## Schließen, Wiederherstellung und Ressourcen

Alle drei gestarteten Spielrollen schlossen regulär; `botA` war hier ebenfalls
ein unveränderter Originalclient, kein KI-Bot. Die drei geschlossenen Logs
enthielten keine neuen Ereignisse der sechs geprüften Fehlerklassen.
Der lesende Collectorprozess wurde mit SIGTERM beendet und reapte mit −15;
dies ist kein normaler Exit0. Originalbytes wurden verifiziert wiederhergestellt.

Root prüfte um 00:59:07 UTC unabhängig 664 Dateien, neun Abwesenheiten,
drei geschlossene Loghashes, Prozessgenerationen, Units, beide Displayabwesenheiten
und verfügbare Sperren: `PASS_RESTORE`. Geprüft wurden Inhalt/UID/GID/Modus und
Dateimengen; eine exakte Fixture-Mtimewiederherstellung wird nicht behauptet.

Der äußere Hostbeobachter behält wegen Kind-Exit1 den Status
`FAIL_HOST_OBSERVATION`. In 50 Proben betrugen maximale Lücke 1,002115 s,
CPUmaximum 71,246819 %, minimal verfügbarer RAM 2745843712 Bytes und freier
Datenträger 9267519488 Bytes. Es gab keine Ressourcenverletzung, Signale oder
Wiederholung durch diesen Beobachter. Das ist keine formale Budgetabnahme.

Die Vorbereitungen sind vollständig in Delta059 extern gesichert. Die neuen
geschlossenen Rohdaten brauchen noch das nächste rückgelesene Delta060.
Live bleibt Dev048/RedGen2/vier Public018 erhalten. A offen; B nicht begonnen.
