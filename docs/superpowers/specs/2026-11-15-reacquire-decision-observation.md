# Minimaler passiver Reacquire-Entscheidungsbeleg

**Status:** Designvorschlag zur Rootprüfung, noch kein Code/Test/Native.
**Quelle:** geschlossener Skulls024-Audit;242.491s NoUseful, Watchdogabbruch
129→248, danach unverankerte Recovery. Exakte Reacquireursache UNKNOWN.

## Einziger vorgesehener Ansatz

Eine feste lokale Diagnoseaufzeichnung im bestehenden `BotCecilReacquire`
mit genau einem expliziten Abschluss an jedem vorhandenen Return/Loopende.
Neue kleine Struktur/Emitter unmittelbar im bestehenden `BotSupplyNative.h`,
kein zweiter Selector, kein BotDriverrefactor und keine neue Hook-/Reader-
Architektur. Eine RAII-Ausgabe wird vermieden: der Emitter soll ausschließlich
an bekannten normalen Returnstellen laufen, nicht bei ungeklärtem Unwinding.

Ein neuer `diagReacquireLast`-Zeitstempel in `SSupplyState` dient nur der neuen
Lograte. `bot_bDiagnostics=0` führt zu keinem neuen Log, Getter oder Statewrite.
Bei1 höchstens eine neue Zeile pro Slot/Policysekunde im aktuellen State-
Lebenszyklus. Nichtfinite/rückläufige Zeit unterdrückt Ausgabe; Rücklauf darf
keine Burstserie freigeben. `Reset()`/frischer Mapstate initialisiert nur diesen
Diagnosestempel, `ClearGoal`/Scan-/Hint-/Deathwechsel öffnen keine neue Rate.
Bestehende Supportlogs bleiben unverändert, auch ihre bisherige eigene Rate.

## Aufzeichnung und Aussagegrenzen

- Identität: vorhandene Entity/Generation, Policyzeit, tatsächlich einmal am
  Abschluss gelesenes `_pNetwork->GetGameTime()` mit `native_time_valid`.
  Gleiches bestehendes Retailmuster wie `BotDriver.cpp`/CecilPlayerObserve.
  Nullnetwork/ungültiger Wert bleibt UNKNOWN; kein Ersatz durch Tick/20.
- Eingänge/vorhandene lokale Ergebnisse: Kontext-only, Liquid/Air, Groundeligible,
  Shape/Metadata-valid, tatsächlicher Supportzweig und dessen Ergebnis,
  Anchor/Goal/Hint/Rejected/Retry/Since vor/nach, Budget ein/aus.
  Fehlende noch nicht berechnete Felder haben Knownbits, keine Nullannahme.
- Geometrie: tatsächliches `localPoint` samt `local_geometry_checked`, `farHint`,
  bis drei endgültige ausgewählte Slots mit bereits berechneter Distanz/Height,
  und pro Slot selected/unattempted/probeUnknown/blocked/clear/planarShort/accepted.
  Keine neue Graphpassage oder Kandidatensuche. Vorhandene Skips dürfen nur dort
  gezählt werden, wo der Originalzweig tatsächlich ausgeführt wurde.
- LOS ausschließlich vorhandener `BotSupplyClear`-Aufruf. Dessen bereits
  verfügbare optionale `validProbe`/`SCecilSupplyCastDetail` liefern bei gültigem
  positivem Segment einen tatsächlichen Castbeleg. FALSE allein ist kein
  Blockadenbeweis: ungültige oder deferred Probes bleiben UNKNOWN. Ein leeres
  Segment ist `empty_segment`, kein Nativecast. Ein nach internem Cast
  ungültiges Ergebnis ohne vorhandenen Probenbeleg bleibt ebenfalls UNKNOWN;
  es wird dafür keine PhysicalCast-API verändert.
- Accepted bedeutet ursprünglicher Reacquire-Bewegungsvorschlag. Kein neuer
  Anchor, kein Radius-/Arrival-/Floorstempel und keine SafeMotion-Erfolgsbehauptung.

Der Logdatensatz ist fest: maximal3Hintrecords, kein Heap/Containerwachstum,
keine RNG-/Such-/Castwiederholung. Eine Zeile bleibt nach Worst-case-Formatprüfung
unter dem vorhandenen2048Byte-BotLogpuffer; kurze feste Enums und begrenzte
wissenschaftliche Darstellung für Distanz/Height, Nativezeit mit9Nachkommastellen.
Ausgabe nennt `proposal=1` ausschließlich beim tatsächlich akzeptierten Vorschlag.
Throttling kann andere Entscheidungen derselben Sekunde verpassen: Abwesenheit
oder Rand zwischen zwei Zeilen bleibt UNKNOWN, keine vollständige Branchabnahme.

## Tatsächliche Returnklassen

| Originalstelle | Neuer passiver Grund; bestehende Wirkung bleibt |
|---|---|
| NULLref, Budget<4 | support_budget_deferred; Support UNKNOWN, kein Cast |
| State/Gravityflag/vertikaleSpeed ungültig | support_motion_guard; ursprüngliches ClearScan |
| ungültiges/leeres Supportsegment | support_segment_unknown; ursprüngliches ClearScan |
| PhysicalCast liefertfalse | support_probe_unknown; kein erfundener physischer Reject |
| tatsächliche Hit/Polygon/Distancebedingungen false | support_geometry_rejected mit vorhandenen Ergebnissen |
| tatsächlicher Normalguard false | support_normal_rejected |
| graphShapeValid false | graph_shape_invalid |
| contextOnly | context_only, nach unveränderter Support-/Groundbeobachtung |
| slots[0]<0 | no_candidate_after_filters; originales ClearScan |
| LOSloop endet bei Budget≤2 mit unversuchtenSlots | hint_budget_deferred, bisherige Ergebnisse behalten |
| alle ausgewählten Slots bearbeitet, keiner angenommen | hints_exhausted; einzeln bekannte/unknown Ergebnisse |
| bestehendes out.active=true | accepted_proposal, keine finale Safetyfreigabe |

`no_candidate_after_filters` ist nicht pauschal „keine Geometrie“: vorhandene
tried-/Backoff-/Lockfilter können die Auswahl leeren. Nur tatsächlich geprüfte
`localPoint=false` darf lokale Geometrieabwesenheit belegen; farHint und der
noch vorhandene freie Graph sind keine LOSgarantie. Metadata-invalid erzeugt
keinen neuen Return, wo der Originalcode weiterlaufen würde.

## Unverhandelbare Grenzen und nächste Entscheidung

Keine Änderung an Supportcast.25–.30/Normal>.5, Speed.1, Nearest12m/Height3,
Reacquire32m/Height8, farHintbedingung, Bitmaps,3Slots, LOSbudget>2/Reserve2,
Retention6s/Reject6s, Scanreset.75m/Gravity, Locks/Floor/Radius/Deadlines oder
Steuerung. Kein Retailbuild/Freeze/Native aus diesem Design. Rootreview entscheidet
zuerst, ob die folgende enge TDD-Umsetzung begonnen wird. Nativeursache bleibt
bis einer tatsächlich passenden Messung oder einem belegten SDKrepro offen.
