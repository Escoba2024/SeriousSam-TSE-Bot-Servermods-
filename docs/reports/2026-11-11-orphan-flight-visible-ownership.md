# Sichtbarer Gegner während des begrenzten Flugabschlusses

Der abgeschlossene native005-Gegenlauf belegt einen verbleibenden Fehler:
BotA/local2/gen7 verliert Laser 267 bei Tick 3772 während 84→86. Ein neu sichtbarer
Gegner übernimmt bei 3773 die Bewegung. Im nächsten Tick endet der Flugabschluss
mit `context`; danach folgen erneute Node 86-Akquisitionen und eine erste
Fernkampfaufnahme erst 50,6 s nach Spawn. Der vollständige Befund steht im
[Vergleichsbericht](2026-11-11-native005-tier1-crossover.md).

Der Driver erkennt den Flugabschluss nach Ende des Itemziels bislang nicht als
eigenständigen Bewegungsgrund. `goalEntity=0` ist dabei korrekt: Das Item ist
verschwunden. Bei sichtbarem Gegner wird `supplyActive=false`; die abschließende
Sicherheitsprüfung löscht folgerichtig die vorherige NAV-Annahme. Die folgende
Frischeprüfung verwirft dann auch die noch gültige physische Kante.

`SCecilMove.flightGoal` kennzeichnet jetzt ausschließlich diesen bereits
begonnenen, weiterhin gültigen Flugabschluss. Der Planner setzt es erst nach
aktueller Identitäts-/Fristprüfung, aktualisierten Sperren und Prüfung derselben
gebundenen Kante. Nur dieser Fall überspringt das gewöhnliche Nachgeben bei
Gegnerabstand unter 8 m. Der Driver erhält darüber Bewegungszuständigkeit auch bei
einem sichtbaren Gegner. Item-/Urgency-/USE-Semantik bleiben unverändert.

Ankunft, Bodenkontakt, abgelaufene Frist, veraltete Daten, geänderte Identität,
gesperrte oder geänderte Kante und fehlgeschlagene finale Sicherheit behalten
ihre bisherigen Abbruchbedingungen. Nach einem solchen Abbruch gibt es kein
Flugsignal mehr. Die finale Wand-/Bodenprüfung und vorhandene Ausweichprüfung
laufen unverändert. Weder andere FALL-Zustände noch gewöhnliche Gesundheitsziele
bekommen diese Priorität. Eine neue Item-/Follow-Auswahl bleibt während des
gültigen Abschlusses aufgeschoben.

RED: Der aus dem tatsächlichen Driver extrahierte Ownership-Ausdruck scheiterte
an der neuen Bewegungszuständigkeit. Die mehrtaktige Kette aus tatsächlichem
`BotSupplyTick`, tatsächlicher Driver-Bedingung und `BotCecilSafeMotion` hatte
zehn fehlgeschlagene Assertions für Sichtwechsel auf 84→86 und 86→176.
GREEN: 1552 native-bridge Prüfungen sowie die tatsächlichen Driver-Action-Tests
und Item-/Ammo-Adapterprüfungen bestehen. Die Tests decken Sichtbarkeit bereits
beim Itemverlust oder einen Tick später, 6 m/15 m Abstand, Ankunft/Frist/Reset,
gewöhnliches Gesundheitsziel, ausbleibende neue Ziel-/Follow-Auswahl und gleiche
vorhandene Ray-/Lookup-/RNG-Arbeit gegenüber dem Fall ohne Sichtkontakt ab.
Auch der SDK-gestützte ASan/UBSan-Lauf besteht mit 1552 Prüfungen und null
Fehlern. Die unabhängige Prüfung fand keinen wichtigen oder kritischen Defekt;
dies ist eine Quellcodeprüfung, keine native Abnahme.

```sh
python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py
python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sanitize --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
python3 poc/candidates/redstation-supply-20261107/test_cecil_action_native.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
python3 poc/candidates/redstation-supply-20261107/test_cecil_items_native.py
```

Diese Änderung berührt `BotSupplyClear` nicht; die separat untersuchte
Segmentendebegrenzung bleibt unabhängig. Keine Runtime-Dateien wurden verändert.
Ein neuer Build und native Wiederholung des Sichtwechsel-/Itemverlustfalls sind
weiter erforderlich. Die fehlgeschlagenen native005-Leben bleiben als Fehlschläge
erhalten; A3, schnelle Waffenaufnahme und die vollständige A-Abnahme sind offen.
