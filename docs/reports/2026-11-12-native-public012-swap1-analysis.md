# Public012 MITTEL: Swap1 und tatsächlicher Startplatztausch

Das abgeschlossene Fenster `arena012public-v4-checked-swap1-trial-1-004059` (240,037 s) bestätigt einen Vorteil beim beobachteten Waffenbesitz und diesmal auch bei den Frags. Es bleiben Erwerbsausfälle und Wartezeiten über30 s. **Keine A3-Gesamtfreigabe.** Originalserver/Vanilla, keine Frida-Instrumentierung; ausschließlich nachträgliche Dateianalyse.

Tatsächliche Attach-Zuordnung: Kandidat012/e0495577 jetzt `botA`, lokale0–3 → globaleSlots0/2/3/4, Entity565–568; Legacy7fc94a39 jetzt `botB`, Slots5–8, Entity569–572. Vanilla bleibtSlot1. Die vorherige inerte Bootstrapinstanz gehört nicht zur Messkohorte.

| Beobachtung | Kandidat012 | Legacy7fc |
|---|---:|---:|
| Beobachtete Leben | 28 | 46 |
| Beobachteter Tod / Fensterzensierung | 24 / 4 | 42 / 4 |
| Nützlicher Besitz (`0x3df8`) | 21 | 2 |
| Abgeschlossene Leben ohne nützlichen Besitz | 5 | 41 |
| Zensierte Leben ohne nützlichen Besitz | 2 | 3 |
| Nützliche aktuelle Waffe | 21 | 2 |
| Nützliche aktuelle/besessene Waffe mit Fire-Request | 18 | 0 |
| Erstbesitz-Median, **nur erfolgreiche Leben** | 11,201 s | 7,400 s |
| Spätester beobachteter Erstbesitz | 33,452 s | 13,651 s |
| Letzter Query-Fragdelta | +42 | +19 |

Die [kompakten Lebensdaten](2026-11-12-native-public012-swap1-analysis.json) enthalten alle74 Leben, Quellzeilen, native Spawn-/Todesuhren, Zensierungen und Erwerbsbelege. Kandidaten-CecilSpawn28/Death24 und erste nützliche Pickups stimmen je Leben mit dem Originalserver-Inventar überein. Minigunbesitz wurde nicht beobachtet. Der letzte Query bei239,756 s ergibt lokale Frags `[21,3,8,10]` bzw.`[4,2,5,8]`; Vanilla0. Fire-Requests sind keine Projektile/Treffer, Frags keine vollständige Schadensrekonstruktion.

Die fünf erfolglos abgeschlossenen Kandidatenleben: local1/Leben2 (3,650 s), local1/Leben3 (5,350 s), local2/Leben3 (22,250 s), local2/Leben8 (5,450 s), local3/Leben3 (3,250 s). Weitere erfolglose Leben sind nach24,101 bzw.7,250 s zensiert. Langsamste erfolgreiche Erwerbe: local0/Leben5 nach33,452 s und local3/Leben2 nach31,502 s. Der Median erfolgreicher Leben blendet diese erfolglosen Leben aus und ist ausdrücklich kein All-Life-Leistungsmaß.

Sieben FlightFinish-Episoden: sechs enden mit`arrived`, eine mit`context`; jede ursprüngliche Deadline bleibt unverändert. Sechs betreffen86→176, eine84→86. Fünf der sechs86→176-Episoden zeigen angrenzend Besitz2051; local3/Generation6 erreicht die Kante, bleibt zunächstBesitz3 und fällt später wieder von der erhöhten Fläche. Local1/Generation11 erreicht84→86 und späterSupport338, bleibt aber bis FensterendeBesitz3. Kantenankunft ist damit kein Waffenerwerbsnachweis. Drei Goal-Timeouts sind erhalten. Keine Approach-Zeilen, somit kein neuer gemessener8→12-/11→12-Übergang und kein Hook234-Nachweis.

Als reine Bewegungsbeschreibung beträgt die längste beobachtete Residenz innerhalb1 m, ohne Probenlücke über0,5 s, beim Kandidaten2,050 s und bei Legacy13,901 s. Das schließt Routenschleifen nicht aus. `CecilState liquid` enthält die PlayerState-Enum;156 lebendeFALL-Zeilen sind kein Wasserbeweis. KeineSWIM/DIVE-Zeilen, keine daraus abgeleitete Hazard-Abnahme.

Alle vier nach normalem Close archivierten Logs wurden erneut auf exakte Bytes/SHA und Syncbad/Disconnect/CRC/Crash/InvalidAction/Joinfehler geprüft: keine Treffer. Attach-Mapping, Launch-/Close-Identitäten, Originalkomponentenpins jeder Inventarprobe und beide neu erzeugten Kohortenkonfigurationen stimmen. Vollständiger Initial-Policy-Replay reproduziert unveränderte raw-first/first-neutral-Archive und pending_errors{}. Alle neun neutralen Positionen einschließlichYaw entsprechen exakt der Referenz. Raw Slots2/3/5/6/7/8 zeigen zunächstPhysics287, später ersteNeutral284; kein Position-basiertes Ersetzen und **kein erster Simulationszustandsnachweis**.

5901 gültige doppelte Reads,147 veränderte Reads verworfen; weiterhin nicht atomar. Readerzeit24,610 s insgesamt/maximal12,058 ms jeProbe ist keine kausale Overheadmessung. Positive beobachtete, auf0 begrenzte HP-Abnahmen ohne Spawnclock-Proben: Kandidat2662,543/Legacy4286; Armor150/0. Dies sind Zustandsverlust-Untergrenzen ohne Schützenattribution, keine exakten Damage-Summen. Nicht beobachtete Zwischenzustände können nicht ausgeschlossen werden.

## Vergleich mit Swap0

Die [Zweifenstersumme](2026-11-12-native-public012-mittel-crossover.json) ergänzt den [Swap0-Bericht](2026-11-12-native-public012-swap0-analysis.md). Alle neun neutralen XYZ/Yaw/Physics sind zwischen beiden Fenstern exakt gleich. Dieselben DLLs wechseln die physischen Gruppen. Kanonische Quellen/Referenz sind bytegleich; gekreuzte Konfigurationen unterscheiden sich **ausschließlich** im Rosteroffset4↔0. Innerhalb jedes Fensters gemeinsame positive Spawnclock:0,9 bzw.0,8 s; keine Behauptung identischer absoluter Weltzeit, vollständigen Weltzustands oder RNG-Verlaufs zwischen Fenstern.

Deskriptiv zusammen: Kandidat40/51 Leben mit nützlichem Besitz,7 abgeschlossene+4 zensierte ohne; Legacy9/84,68 abgeschlossene+7 zensierte ohne. Frags Kandidat20+42=62, Legacy26+19=45. Die Fragführung kehrt sich zwischen den Fenstern um. Es sind zwei MITTEL-Fenster, keine drei Gegenproben, keine Signifikanzbehauptung und keine allgemeine Abnahme.

Private Reproduktion: `/srv/tse-nav-public012-swap1-review-20261112/{analyze,enrich,finalize,paired,publish_compact}.py`; Eingabe-/Analyseskript- und vollständige private Auswertungshashs sind im JSON festgehalten. Keine Rohlogs, Adressen, GUIDs oder Konfigurationsinhalte im Commit. Keine Runtime wurde durch diese Auswertung gestartet oder verändert.
