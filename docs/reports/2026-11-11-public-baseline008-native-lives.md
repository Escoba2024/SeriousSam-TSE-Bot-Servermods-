# Public7fc gegen Kandidat008: Erstspawn und vollständige Waffenaufnahme

Der abgeschlossene eigene Retail-1.07-Lauf `arena008public-checked-swap0-trial-1-225500` belegt einen gemeinsamen automatischen Erstspawn und deutlich mehr beobachtete nützliche Waffenaufnahmen des Kandidaten in diesem einzelnen 120,114-s-Fenster. Er ist kein Drei-Tier-, Crossover- oder Langzeitnachweis. Die [JSON-Beilage](2026-11-11-public-baseline008-native-lives.json) enthält sämtliche 35 beobachteten Leben einschließlich Vanilla, Quellhashes, Zeilenbelege und private Positionsvektoren nur als Hashes.

## Tatsächlicher Baselinepfad und Zuordnung

Die letzte gestartete botA-DLL ist Public7fc (`7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835`); der frühere 048-Bootstrap wurde vor dem Beobachtungsfenster geschlossen. botB ist Kandidat008 MITTEL (`07113052dac65df7143f8418e5e2c3ef1c9f1ebd5acc96b6fba55c4166bffb4b`). Server und Vanilla verwenden die originale Game-DLL `1c41da35…4208`.

Die öffentliche Konfiguration wurde unabhängig gegen den protokollierten SHA256 geprüft: einzig der Roster-Offset wurde von 4 auf 0 geändert. HumanAI0, AutoCombat1, MoveFactor1, YawSpeed45, FirePeriod1 und FireTicks3 blieben erhalten. 450 BotCombat- und 141 BotNavigation-Zeilen belegen laufenden Legacy-Combat; die vier BotHuman-Zeilen sind ausschließlich Attach/Profile-Metadaten und kein Nachweis aktivierter HumanAI. Alte CecilSpawn-Ereignisse existieren nicht; Lebenszahlen kommen deshalb für beide Kohorten aus demselben nativen Inventarleser.

| Rolle | Lokale Spieler | Echte globale Slots | Entity-IDs |
|---|---|---|---|
| Public7fc/botA |0,1,2,3|0,2,3,4|565,566,567,568|
|008/botB|0,1,2,3|5,6,7,8|569,570,571,572|
|Vanilla|—|1|563|

Die Zuordnung folgt tatsächlichen BotDriver-Attachmeldungen (botA Zeilen 182/184/186/188, botB 183/196/200/204) und dem Join mit Inventar-Slot/Entity-ID. Messgruppen wie `physicalA` oder `observer` wurden nicht als Spielerzuordnung verwendet.

## Gemeinsamer Erstspawn und physische Startzustände

Alle neun Spieler erhalten den nativen Spawnzeitpunkt **0,7500001192s**. Die jeweils erste gültige lebende Inventarprobe liegt bereits bei demselben Spieltick: HP100, Armor0, Owned3, Current2 und Wanted2 bei allen neun. Inventarzeilen 12–14 decken alle Slots ab. Session-health Zeile 5 bestätigt den Spawnzeitpunkt und sämtliche per-Slot-Positionshashes unabhängig in allen vier Prozessansichten. Die vorherige nichtatomare Zeile 4 erfasst teilweise laufende Initialisierung und ist kein vollständiger Startzustand.

Dies belegt gleichzeitig initialisierte Spieler mit gleichem Inventar an ihren jeweiligen regulären Kartenpositionen. Es behauptet keine identischen Positionen zwischen Gegnern, keine gleichwertigen Spawnorte und keinen bereits durchgeführten Rollentausch. Die neun vollständigen Platzierungs- und Positionshashes bleiben in der JSON-Beilage prüfbar. Der Harness verwendete nur normale Pause-Eingaben; während der Beobachtung gab es keine periodischen Observer-Spielinputs oder Frida-Hooks.

## Alle Leben, einschließlich Fehlschlägen und Zensierung

| Kohorte | Beobachtete Leben | Nützliche Waffe erworben | Ohne Erwerb gestorben | Ohne Erwerb am Fensterende lebend | Erfolgs-only Median |
|---|---:|---:|---:|---:|---:|
|Public7fc|21|3|15|3|6,55s|
|008 MITTEL|13|10|2|1|9,10s|

Als nützlich gilt Owned-Maske `0x3df8`. Ein Leben wird nach tatsächlicher Entity-ID und nativem Spawnzeitpunkt getrennt, Messgruppen werden vereinigt, doppelte Messungen erzeugen keine zusätzlichen Leben. Erwerbsalter ist der erste beobachtete positive Owned-Bit-Nachweis im lebenden Zustand, somit ein Abtastungsoberwert und kein exakter Pickupzeitpunkt. Ein gesondertes JSON-Feld erfasst erstmals ausgewählte nützliche Waffen mit `has_ammo`; Besitz bedeutet weder Schuss noch Treffer.

Alle beendeten Leben besitzen eine direkt beobachtete gleichlebige HP≤0-Probe; kein Lebensende musste allein aus dem folgenden Spawn erschlossen werden. Der größte Abstand zwischen Spawn und erster lebender Inventarmessung beträgt 0,10001s. Die separate Vanilla-Lebensdauer bleibt aus den Botkennzahlen ausgeschlossen.

Die drei alten Erfolge lagen bei 1,15/6,55/12,40s. Die zehn neuen Erfolge lagen zwischen 2,50 und 14,50s. **Der niedrigere alte Erfolgs-only-Median ist kein Akquisitionsvorteil:** Er berücksichtigt nur 3 von 21 statt 10 von 13 Leben und blendet Fehlschläge/Zensierung aus.

Bei den ersten Leben starben alle vier alten Bots ohne nützliche Waffe (Alter 5,95/34,45/11,50/7,05s). Alle vier neuen Bots erwarben eine (Alter 3,80/3,55/5,70/10,20s für lokale 0–3). Am Fensterende noch ohne Erwerb lebende alte lokale 0/1/2 waren mindestens 11,45/17,70/29,95s alt; der neue lokale 1 mindestens 4,30s. Diese vier Fälle sind keine abgeschlossenen Erwerbszeiten.

## Nachweisgrenze

3027 Inventarproben wurden angenommen, 72 wegen veränderter Daten verworfen. Der Leser arbeitet mit übereinstimmenden Doppelablesungen, nicht mit einem atomaren Simulationssnapshot. Gemessene Gesamtlesedauer 12,445s, maximale Einzelablesung 0,01813s; daraus wird keine CPU- oder unbeeinflusste Kontrollgleichheit abgeleitet. Ergebnisreceipt: PASS_LIMITED, keine Fehler, alle vier Rollen geschlossen, jeweils 0 SYNCBAD und 0 Disconnects über 120,114s. Keine Prozess-, Konfigurations- oder Gameplayänderung wurde für diese nachträgliche Analyse ausgeführt.

Der Vergleich deckt erstmals den tatsächlichen öffentlichen HumanAI0/AutoCombat1-Pfad ab. Eine einzelne MITTEL-/Slotbelegung mit kurzen Beobachtungsgrenzen reicht nicht für die abschließende A3-Überlegenheit, STARK/DEMON oder die native Wirksamkeit des nachfolgenden 009-Fixes.
