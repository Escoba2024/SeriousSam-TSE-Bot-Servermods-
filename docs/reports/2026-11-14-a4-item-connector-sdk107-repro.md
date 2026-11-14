# A4: echter SDK107-Reproducer für verlorenen Itemconnector

Status: **RED_REPRODUCED, kein Produktionsfix**. Ausschließlich portabler
Bridgeharness; keine DLL, Engine-/Wine-/Fridaruntime, kein Display und keine
Liveänderung. A1-Finalstand und andere Worktrees bleiben unangetastet.

## Beleg und Grenze

Der geschlossene020-Nav20Arm
`nav20-020-root-redstation-20261114-191457` enthält für botA:2/global3 ein
beobachtetes Leben mit owned3 und rund45.739s zwischen erster und letzter
lebender kanonischer Beobachtung. Zwei Waffenversuche enden unavailable;
deren genauer Read-/Typedneedgrund ist bei Diagnostics0 unbekannt. Danach
folgen Health285 und287 am gewöhnlichen Navpunkt55 mit Radius2; beide Items
liegen ungefähr6m vom Navpunkt entfernt. Der erste Healthversuch endet nach
seinem unveränderten gewöhnlichen12sPolicytimeout, der zweite durch Tod.

Quelle/Privatdiagnose:
`/srv/tse-cecil-rollout-evidence-20261114/navigation-comparison20-long-unarmed-diagnosis.json`,
SHA256 `2251fd95b3608059830d97c264468d8a5727ff81906ac0347b8f8c67484cb756`.
Resultat SHA256 `4e5f096529e31f4c13efb44ccc32da71af924a0308df27dcdeaeb2be87ca5d66`;
botA.log SHA256 `88f1b4a23c8427b847b3b107f312af4c554343031cefb42a342a3487f32dc54b`.
Keine Rohspieleridentität wird hier veröffentlicht.

Die Sourcebeobachtungen bei Tick6860/6900/6920/6960 sowie7060/7100/7160/7180 zeigen wechselnde
terminalArrival-/Navtravelzustände und Abstände innerhalb/außerhalb der2mSphäre.
Source tick bezeichnet hier den gedruckten Tickwert, nicht die Dateizeilennummer.
Policyzeit wird nicht aus tick/20 mit nativer GameTime gleichgesetzt.
Der entity-/generationsgebundene HopCheckpoint in Logzeile4960 ist zu beachten:
Policytime349.000, source56→hop55/goal55, anchor55, seit343.050, best_distance
0.507084 und current_distance2.179545. Danach bleibt dasselbe Healthziel bis
Timeout; der Checkpoint ist kein nachgewiesener Recoveryerfolg.

HP steigt im geschlossenen Leben zeitweise10→12→13→14. Deshalb lautet der
Befund nicht „kein Pickup überhaupt“. Identität und Ursache dieser Healthgewinne
sind unbewiesen. Der Connectorbefund erklärt außerdem weder die vorherigen
Weapon-unavailable-Enden noch allein den gesamten nativen Verlauf.

## Reproducer am unveränderten Produktionskörper

Der bestehende `test_cecil_native_bridge.py` extrahiert die tatsächlichen
BotSupplyNative.h-Körper und verwendet den echten CecilNavigator. Ausgeschlossen
bleiben wie bisher nur Plattformloader und native Itemdekodierung; World/Rays
sind vorhandene deterministische Stubs. Keine zweite Implementierung des
Navigators oder der Supplyentscheidung wurde geschrieben.

Baseline vor Testergänzung: **2920Checks,0FAIL**.
Neue Fixture `itemConnectorRadiusContinuity` setzt einen bereits behaltenen
gewöhnlichen Healthversuch, explizites goalKindHealth, HP10, Node55 mit echten
Koordinaten/Radius2 und die beiden ungefähr6m entfernten Itempositionen.
Nur die Spielerposition wird von Test zu Test vorgegeben; derselbe Navigator
wird zwischen diesen aufeinanderfolgenden BotSupplyTick-Aufrufen nicht resettiert.
Yaw zeigt in der Fixture jeweils zum Item. Das ist keine Enginephysik- oder
Pickupsimulation und reproduziert nicht den gesamten nativen Anmarsch56→55.

| Abstand zum Navpunkt | nav_travel | forward | Ergebnis beider Healthziele |
|---|---:|---:|---|
|1.500m|0|+1|Bewegung zum Item|
|1.900m|0|+1|Bewegung zum Item|
|2.125m|1|−1|Rückbewegung zum Navpunkt, RED|
|3.000m|1|−1|Rückbewegung zum Navpunkt, RED|
|4.500m|1|−1|Rückbewegung zum Navpunkt, RED|

Alle zehn Zustandsprüfungen halten dabei Ziel55, denselben lebenden Healthgegenstand,
aktive Bewegung und null GoalEndereignisse fest. Die beiden unabhängigen
Cold-outside-Kontrollen verlangen weiterhin normale Navannäherung: bloße
Nähe zum Item darf ohne vorherige Ankunft keinen Direktconnector freigeben.

Finaler Command:

```
python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
```

Ergebnis: **2942Checks,6FAIL**, Exit1. Genau die sechs neuen warmen
Kontinuitätsprüfungen scheitern; alle übrigen2936Checks inklusive Coldkontrollen
und unveränderter Parenttests bestehen. Kein GREEN und keine Regressionabnahme
behauptet. Die nachfolgende private Pinquittung hatte zunächst einen falsch
konstruierten SDK-Includepfad; nur dieser Belegpfad wurde korrigiert, kein
Test/Gate geändert oder dadurch erneut ausgeführt.

Private vollständige Commands/Hashes/Output:
`/srv/tse-a4-item-connector-repro-20261114/.codex/evidence/item-connector-sdk107-repro/receipt.json`.

| Unveränderter Beleg | SHA256 |
|---|---|
|BotSupplyNative.h|585dd66439d9c9fcb375acbaab3d43939da706ae38c6e24b32e947c0abf6f121|
|cecil_motion.h|0b25686cff2d6df541b50c1a12917ad4c284998b105ddbcf2de9ad0f54a31241|
|BotDriver.cpp|75cf99356b70ec1150e3af1316c8bae2d989c37b1608f2d0e64ec056e5e71551|
|SDK107 Player.es|85c92933fa5b0cc726be7b42a3bc82d4c95b255507ec8b1fffe2666fcf3888af|
|SDK107 WorldRayCasting.h|0865f54625b1b5da413c775c25589b3cd0d420fee3c131036bf6066ff82837b2|

Produktionskörper sind bytegleich zu Branchbasis und Build020-Overlay. SDK107
pinnt PLACT_USE32/PLACT_SNIPER_USE4096 sowie PASSABLE2048/SHOOTTHRU16 und
COLLISIONBOX2. Portable Konstantenbelege ersetzen keine Retailkollision.

## Konkreter Mechanismus und enger späterer Fixentwurf

BotSupplyNative.h1580–1588 erzeugt in jedem Tick einen neuen Motioninput zur
Navzielposition. CecilNavigator.Update in cecil_motion.h81–83 prüft Reached
jedes Mal neu und meldet arrived nur innerhalb der ursprünglichen Kugeln.
BotSupplyNative.h1632–1647 steuert den eigentlichen Itemconnector nur im
jeweiligen move.arrived-Tick. Nach eigenem Fortschritt aus der Kugel wird daher
derselbe behaltene Itemversuch wieder Navtravel zum unveränderten Navpunkt.
Ein einmal erreichter Punkt bedeutet gegenwärtig keine fortbestehende
Itemconnectorphase. Der neue Test zeigt exakt diese Zustandsdiskontinuität.

Vorschlag zur Rootentscheidung, noch nicht implementiert: eine kleine explizite
gewöhnliche terminale Itemconnectorphase nur nach echter move.arrived-Ankunft
und erfolgreich frisch geprüftem Itemconnector behalten. Für den ersten Fix
Scope auf den bewiesenen gewöhnlichen Healthfall begrenzen; Weapon-/Special-
Verhalten erhält zunächst unverändert seine bestehenden Gates/Watchdogs.
Ein warmer Tick darf denselben frischen Connector danach verwenden, ohne erneut
in die2mSphäre zurückzumüssen. Keine Navdatenänderung, erfundene Ankunft oder
Item-/Engine-/Replicated-Statewrites; kein neuer Pickup oder neuer Raypfad.

Für einen späteren Produktionspatch sind vor dessen GREEN nötig:

- Echte Ankunft plus getesteter Connector erzeugen die Phase; hop==goal,
  coldPose, ein gesetztes Ziel oder ein alter Anchor allein tun dies nicht.
- Phase exakt an World/Map, Player/Generation, Item, Navziel, ursprünglichen
  Versuchsbeginn/-deadline und Gravity binden. ClearGoal, Death/Rejoin,
  Map-/World-/Generation-/Goalwechsel, expliziter Navigatorreset/Relocation,
  rückläufige Zeit oder abgelaufener unveränderter Versuch löschen sie.
- Vor jedem Bewegungsangebot vorhandenes native Itemread und Typedneed erneuern;
  verschwundenes/abgewiesenes/nicht mehr benötigtes Item bleibt der bisherige
  GoalEnd-/Rejectpfad. Kein Lifecycle-/Pickedmask-/Readfehlerfallback.
- Maximal8mItemdistanz,3mGravityhöhe, bestehender LOS-Cast und reservierte letzte
  zwei Rays bleiben exakt. Budget<=2 bedeutet neutral warten ohne zusätzliche
  Casts oder behauptete Unreachableursache; feste Deadline läuft weiter.
- Follow, Important/Lock/Nextchain, Specialflags/-flug, Liquid und andere
  Bewegungseigentümer erhalten keine neue Berechtigung. UrgentHealth behält
  ausschließlich seine vorhandene Closecombatpriorität. Finaler physischer
  Bewegungscheck darf nicht umgangen oder um eine neue Floorfreigabe ergänzt werden.
- Ehrliche Telemetrie muss Itemconnector von erneuter Navtravel unterscheiden;
  kein synthetisches move.arrived und kein behaupteter Recoveryerfolg.
- Gewöhnliche12sHealthdeadline,30sRejectbackoff sowie Weaponterminalwatchdog
  mit seinen10s/.75m-Kriterien bleiben unverändert. Keine Verlängerung zum
  Kaschieren eines Stalls; nach Erfolg keine fiktive Waffenausrüstung.

Parent enthält bereits getrennte Death-/World-/Map-/Goal-/Special-/Flight-/
Weapontransit-/Budget-/Connector-/Cold-/Physikguards. Ein späterer neuer
Phasenzustand benötigt dafür eigene adversariale Reset-/Abbruchtests am echten
Bridgekörper; die unveränderten2920Parentchecks allein beweisen seine Sicherheit
nicht. Erst nach Rootentscheidung darf ein Produktionspatch diese REDs grün machen.
