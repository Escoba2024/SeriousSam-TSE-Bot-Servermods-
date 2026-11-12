# Public012 STARK, Swap0: Erwerbsnenner und native Grenzen

Das abgeschlossene Original-Retail-Fenster `arena012public-v4-checked-swap0-trial-2-005336` dauert240,014 s. Vier normale Close-Belege und nachgelagerte Logprüfung sind erhalten. Kandidat012/e0495577 läuft als STARK mit HumanAI/Supply1, Legacy7fc94a39 mit seiner kanonischen HumanAI0-Konfiguration. **Keine Gesamtfreigabe vor vollständigem Stufen-/Startplatzvergleich und Schadensnachweisen.** Keine Frida-Instrumentierung in diesem Fenster.

Tatsächliche Attach-Mappings: Legacy`botA` lokale0–3 → Slots0/2/3/4, Entity565–568; Kandidat`botB` → Slots5–8, Entity569–572; VanillaSlot1. Die [kompakten JSON-Daten](2026-11-12-native-public012-stark-swap0-analysis.json) enthalten alle85 beobachteten Leben, native Spawn-/Todesuhren, Zensierungen, Erstbesitz-/Current-/Fire-Request-Zeilen und Kandidatengenerationen.

| Beobachtung | Legacy7fc | Kandidat012 STARK |
|---|---:|---:|
| Leben | 53 | 32 |
| Beobachteter Tod / Fensterzensierung | 49 / 4 | 28 / 4 |
| Nützlicher Besitz, exakt`0x3df8` | 5 | 24 |
| Abgeschlossen ohne nützlichen Besitz | 45 | 6 |
| Zensiert ohne nützlichen Besitz | 3 | 2 |
| Nützliche aktuelle Waffe | 1 | 20 |
| Nützliche aktuelle/besessene Waffe mit Fire-Request | 0 | 17 |
| Erstbesitz-Median, **nur erfolgreiche Leben** | 1,150 s | 10,300 s |
| Spätester Erstbesitz | 5,700 s | **53,053 s** |
| Letzter Query-Fragdelta | +25 | **+47** |

Alle Leben beginnen im ersten lebenden Inventarsample mit Besitz3. Die vier ersten Legacy-Leben enden ohne nützlichen Besitz; beim Kandidaten liegt Erstbesitz nach3,850/3,950/11,300/10,350 s vor. Kandidatenspezifische CecilSpawn32/Death28 und Existenz erster nützlicher Pickups stimmen pro Leben mit dem Originalserver-Inventar überein. Legacy hat diese Cecil-Lebensmarker nicht. Erfolg-only-Mediane dürfen nicht als All-Life-Leistung oder Vorteil der Legacy-Erwerbsgeschwindigkeit gelesen werden.

Der letzte Query bei239,029978 s ergibt lokale Fragdeltas Legacy`[8,7,5,5]`, Kandidat`[13,12,13,9]`, Vanilla0. Der Kandidat liegt hier vorn; das ersetzt keinen vollständigen Stufenvergleich. Fire-Requests und Cecil-`shots` sind Eingabeanforderungen, keine Projektile/Treffer. Keine Schützenzuordnung aus HP-Verlusten.

## Konkrete Erwerbsfehler und ein Minigun-Einzelbeleg

Sechs abgeschlossene Kandidatenleben bleiben ohne nützlichen Besitz: local0/Leben5/Generation10 (13,401 s), local0/Leben7/gen12 (1,000 s), local2/Leben4/gen9 (10,750 s), local2/Leben8/gen13 (15,401 s), local3/Leben4/gen9 (11,401 s), local3/Leben7/gen12 (9,201 s). Erfolglos zensiert: local1/Leben5/gen10 (0,100 s) und local3/Leben9/gen14 (2,900 s). Die sehr kurze letzte Lebensbeobachtung wird ausdrücklich nicht als abgeschlossener Fehlschlag gezählt.

**Local1/Entity570/Generation8**: Spawnclock85,000587; erster nützlicher Besitz erst nach53,053230 s, Owned259/Weapon9. Aktuell wird die nützliche Waffe erst nach59,653633 s beobachtet; bis Tod nach77,754738 s kein nützlicher Fire-Request. Goal544 endet1779 als unavailable; Goal401 folgt1826 und endet2345 unavailable. Dazwischen zeigen native Cecil-Zeilen mehrere Aufenthalte auf Source0→Hop1 und später andere Kanten; danach eine Health-Zwischenwahl und erneutes Goal544 ab2420. Pickup2776 ist belegt (`botB.log`:2819). Das ist kein behaupteter durchgehender Stillstand und kein Goal-Timeout: die Folge benötigt eine eigene Routen-/Itemverfügbarkeitsanalyse, nicht eine erfundene Deadlinekorrektur.

**Local1/Generation7** ist das einzige beobachtete Minigun-Leben. Native Spawnclock10,600022; Erstbesitz67 nach33,749587 s, Minigun als aktuelle Waffe nach37,099536 s, nützlicher Fire-Request nach37,649528 s. CecilPickup905 bestätigt Owned67 am erhöhten Ziel (`botB.log`:1110). Diese Aufnahme ist funktionaler Einzelbeleg, keine generelle Bouncer-Abnahme.

Die erhaltene Actionepisode zeigt8→12: Ticks802/807/812 RawUP1→FinalUP0 mit realen Supports54/null/193. **Tick815** (`botB.log`:963) erreicht12 und wählt34: requested`(-0.650732,0.759307,0.000000)`, finaleAction`(3.796535,0.000000,6.507325)`, Position`(-47.520412,24.007755,63.040184)`, Velocity`(-17.548832,0,-0.202574)`, Support193. RawUP war bereits0. Damit **kein positiver Ausübungsnachweis der neuen012 Arrival12→34-UP-Unterdrückung**. Tick817 liegt bereits auf12→34 und zeigt RawUP1/FinalUP11 sowie Velocity`(52.300568,71.682266,-75.965965)`. Die Flugkurve und spätere Aufnahme belegen keinen direkt gemessenen234-Funktionsaufruf; Frida war aus.

Acht FlightFinish-Episoden: vier`arrived`, vier`context`; ursprüngliche Begin/Enddeadlines jeweils unverändert. Kanten: vier86→176, drei84→93, eine12→34. Die12→34-Episode905→907 beginnt beim Minigun-Pickup und endetcontext. Alle Ereignisse stehen im JSON. Ein Goal-Timeout: local1/tick4425/entity292. Keine pauschale Terminal-/Flugfreigabe aus dem Gesamtscore.

## Unabhängige Nachprüfung und Messgrenzen

Alle vier Closed-Logs stimmen in Länge/SHA mit ihren Receipts überein; erneut keine Syncbad/Disconnect/CRC/Crash/InvalidAction/Joinfehler, errors[]/final_evidence_reasons[]. Attach-Mapping, Launch-/Close-Identitäten und Originalkomponentenpins aller Inventarproben stimmen. Beide Kohortenkonfigurationen wurden aus den archivierten kanonischen Quellen erneut erzeugt und exakt verglichen.

Der vollständige Initial-Policy-Replay reproduziert raw-first/first-neutral und pending_errors{} exakt. Alle neun neutralen XYZ/Yaw entsprechen unveränderter Referenz. Slots5–8 wurden zuerstPhysics287, danach ersteNeutral284 beobachtet. Keine Position-basierte Ersetzung und **kein erster Simulationszustandsnachweis**.

5908 gültige doppelte Inventarreads,149 veränderte Reads verworfen; nicht atomar. Readerzeit insgesamt24,507 s/maximal15,697 ms jeProbe ist keine kausale Overheadmessung. Längste beschreibende1m-Residenz ohne Lücke>0,5 s: Legacy10,351 s, Kandidat1,600 s; keine automatische Stuck-Freigabe. Beobachtete positive, auf0 begrenzte HP-Abnahmen ohne Spawnclock-Proben: Legacy5064,622/Kandidat3093,387; Armor50/175. Nur Zustandsverlust-Untergrenzen ohne Schützenattribution, keine exakten Damage-Summen.

Rawlogs/Adressen/GUIDs/Konfigurationsinhalte bleiben privat. Dateianalyse und Reproduktion unter `/srv/tse-nav-public012-stark0-review-20261112/`; Eingabe-/Skripthashs im JSON. Kein eigener Runtime-Aufruf.
