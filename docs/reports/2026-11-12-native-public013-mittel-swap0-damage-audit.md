# Kandidat013 MITTEL, Swap0: ungünstiges Ergebnis und vollständige Nenner

Im abgeschlossenen120,055-s-Fenster `arena013public-damage-checked-swap0-trial-1-031704` liegt Kandidat013 MITTEL deutlich hinter Public7fc: **801,410 gegen3307,855 tatsächlich beobachteter, auf Vorhit-HP begrenzter Fremdschaden**, acht gegen28 tödliche Fremdaufrufe. Der bessere STARK-Befund ersetzt dieses Ergebnis nicht. [Vollständige42 Lebensdatensätze und Belege](2026-11-12-native-public013-mittel-swap0-damage-audit.json) bleiben erhalten; kein Gesamturteil über MITTEL ohne getrennte Gegenrichtung und keine vorschnelle Tuningänderung.

PublicA belegt tatsächliche Slots0/2/3/4, KandidatB5–8, VanillaSlot1. Alle neun Entity-/Pointerbindungen wurden gegen jede native Inventarprobe geprüft, Initialpolicy/Referenz exakt wiederholt und beide kanonischen Konfigurationen bytegenau neu erzeugt. CecilSpawn/Death/Pickup des Kandidaten passen pro Leben zum nativen Inventar. Alle vier Closed-Logs/Identitäten/Originalhashs und endgültige Restore-/Coveragebelege stimmen; Fehlerlisten leer. Kein eigener Runtimeaufruf.

| Vollständiger Nenner | Public7fc | Kandidat013 MITTEL |
|---|---:|---:|
| Beobachtete Leben |28|13|
| Tod / Fensterzensierung |25 /3|10 /3|
| Nützlicher Besitz (`0x3df8`) |4|9|
| Beendet ohne nützlichen Besitz |21|3|
| Zensiert ohne nützlichen Besitz |3|1|
| Nützliche aktuelle/besessene Waffe |1|9|
| Nützliche aktuelle Waffe mit Fire-Request |1|6|
| Erstbesitz-Median, nur erfolgreiche Leben (s) |5,300|11,350|
| Spätester Erstbesitz (s) |8,950|18,750|
| Letzter Query-Fragdelta |+27|+8|

Vanilla hat zusätzlich ein beobachtetes Leben, einen Tod, keinen Erwerb. Es gibt keine ausschließlich als Leiche beobachteten Leben. Die drei statt vier Fensterzensierungen je Botkohorte sind korrekt: jeweils ein Bot ist am Ende bereits tot und hat noch kein neues beobachtetes Leben. Alle ersten Public-Leben bleiben unbewaffnet; erste Kandidatenaufnahmen nach4,300/3,500/11,350/10,350 s. Erwerb ist erster lebender Besitz, keine garantierte sofortige Auswahl oder Verwendung. Alle Zeitangaben verwenden native Spieluhren.

Der Hooknenner **189 =140 lebende bekannte Fremdaufrufe+44 Leichenaufrufe+5 unzuordenbare Inflictors**, ohne Selbstaufruf oder außerhalb des Fensters liegenden Record, ist vollständig. Kandidat38 Fremdaufrufe/8 tödlich; Public102/28. Alle36 Fremdkillmeldungen des am Fensterende gespeicherten Originalserverlogs stimmen für jedes Schütze-/Opfer-Slotpaar mit den tödlichen Hookrecords überein. Die ursprüngliche HP-Summe einschließlich Overkill ist Kandidat1669,342/Public3838,542; für den Vergleich wird Overkill nicht als zusätzlicher lebender Schaden gewertet. Bekannte Fremdtreffer umfassen auch andere Bots derselben KI-Kohorte; es sind keine Teams.

Kandidat-DamageType:14 BULLET,14 BURNING,8 PROJECTILE,1 EXPLOSION,1 CANNONBALL; Public101 BULLET und1 IMPACT. Enumwerte sind im Retail107-Header `Engine/Classes/BaseEvents.h:108–120` belegt. Es wird daher nicht behauptet, jeder Public-Aufruf sei ein normaler Bullet-Treffer oder jeder Kandidatenaufruf ein eigener Schuss. TLS/Hauptthread, keine Überlappung, positive gleiche Spawnclock, gleicher CurrentTick, Victimpointer und fortlaufende Sequenzen wurden erneut geprüft. Keine Faults/Drops/unknown-victim/non-main/in-flight/detach-errors; volle Hookdeckung und beide Originalkörperrestaurierungen sind endgültig archiviert. SameSpawnTick-HP weiterhin0; FirstProcessedStatefalse.

## Waffen vorhanden, aber weniger Feuer — noch kein eindeutiger Mechanismus

In lebenden SameLife-Probenintervallen mit maximal0,5 s Lücke umfasst MITTEL461,961 beobachtete Spieler-Sekunden, davon314,906 mit nützlichem Besitz. STARK derselben physischen Startseite hatte459,061/338,007. Die nützliche aktuelle Waffe trägt bei MITTEL nur für7,450 solcher Sekunden einen Fire-Request, bei STARK26,901. Das sind Stichprobenintervalle, keine exakten Schussdauern. Die kumulativen final ausgegebenen Combat-Fire-Inputcounter steigen zwischen erster/letzter CecilState-Probe bei MITTEL insgesamt193, bei STARK589. `BotDriver.cpp:1543` zählt hierbei Respawninput ausdrücklich nicht. Eingabecounter sind keine Projektil-/Treffer-/Genauigkeitsrate.

Nachweisbare Auswahlverläufe sind im JSON vollständig für vier auffällige Leben enthalten:

- **Local0/gen7:** Granatenwerferbesitz259 nach18,750 s, erster nützlicher Current9 erst nach44,699 s; erster nützlicher Fire-Request53,899 s. In28 erhaltenen Useful+Knife-States sind28 NAV-aktiv und0 Ziele sichtbar. Quellen-/Hopfolge wechselt durch zahlreiche Knoten. Das belegt Reisen ohne aktuelle Sicht, keinen durchgehenden Stillstand und keinen bewiesenen WeaponInput-Fehler.
- **Local1/gen7:** Sniperbesitz4099 nach17,551 s, Current13 nach26,352 s, bis Tod41,553 s kein nützlicher Fire-Request beobachtet.14 Useful+Knife-States, davon13 NAV-aktiv/13 ohne Sicht; ein sichtbarer Übergang bleibt ohne vollständige20Hz-Triggerhistorie.
- **Local2/gen6:** Kanonenbesitz8195 nach11,350 s, Current14 nach12,200 s, erster nützlicher Fire-Request37,650 s.22 erhaltene sichtbare Useful-States enthalten nur einen finalen Fire-State; Waffen-/Messerwechsel bleiben nachvollziehbar erhalten.
- **Local3/gen6:** Sniper nach10,350 s, Current13 nach21,600 s, bis Tod43,550 s kein nützlicher Fire-Request. Alle11 Useful+Knife-States sind NAV-aktiv ohne Sicht.15 sichtbare Useful-States zeigen kein finales Feuer.

Der konkrete Reisemesserpfad liegt in `BotDriver.cpp:1399–1405` über `CecilTravelKnife` und `ResolveSupplyWeapon`; er ist nicht mit einem Fehler des nachfolgenden originalen Waffenwechsels gleichzusetzen. `has_ammo=1` in diesen Übergangsproben beschreibt die aktuelle Waffe, nicht eine isolierte Munitionserlaubnis jeder besessenen Waffe. Keine erfundene Ammo-Ursache.

Kein langer Stillstand ist im definierten Maß belegt: maximale lebende1-m-Ankerresidenz bei Probenlücken≤0,5 s für Kandidatslots5/6/7/8 nur0,50/0,60/1,45/1,45 s. Das schließt Routenineffizienz oder wiederholte weite Wege nicht aus. GoalEnd-Gründe:26 unavailable,4 timeout,4 connector,7 death. Diese Ereigniszahlen sind nicht automatisch26/4/4 zusätzliche Lebensfehlschläge oder Fehlerbeweise.

## Tatsächlich aktiver MITTEL-Pfad

Alle vier nativen Initlogs melden `profile=MITTEL tier=1 model=arena-v1`. Quellstand`5ce974c296240be4ece76386654ecd7e666d1aa4`, DLL`3a8d84c9…`; relevante Overlaydateien wurden erneut gegen das Buildmanifest gehasht.

| Parameter | MITTEL | STARK |
|---|---:|---:|
| Reaktion (s) |0,20|0,10|
| Aim-Sigma (Grad) |0,9|0,45|
| Drehgeschwindigkeit (Grad/s) |300|420|
| Drehbeschleunigung (Grad/s²) |1000|1600|
| Trackingverstärkung (1/s) |10|14|
| Kontinuierliche Ausrichtung vor Feuer (s) |0,10|0,05|
| Projektilvorhaltfaktor |0,75|0,9|

`bot_profile.h:423–438` setzt diese Parameter, gemeinsame Feuerwinkeltoleranz1,5°, gleiche Sicht-/Waffen-/Bewegungsfähigkeiten. `BotDriver.cpp:789–808` baut das angeforderte Arena-Profil; `bot_human.h:94–112` begrenzt Cecils nachträgliche Überschreibungen auf **Nicht-Arena**. MITTEL-Werte werden deshalb nicht stillschweigend zu einem Cecil-Default. `bot_aim.h:128–155` verwendet Trackinggain mit weiter bestehenden Dreh-/Beschleunigungsgrenzen. `bot_human.h:303–322` verlangt Sicht, tatsächlich aktuelle gewünschte Waffe, sicheren Bereich, residual≤1,5° und aufeinanderfolgende ausgerichtete Samples; Zielwechsel/Verlust setzt den Trigger zurück. Spätere Supply-Arbitrierung kann Bewegungs-/Feuerhoheit übernehmen.

Die vorhandene Detailmessung begrenzt die Diagnose: `bot_iLogEvery=200` liefert nur47 BotHuman-Commandzeilen im120-s-Fenster, elf davon mit sichtbarem Ziel. Zehn dieser elf Residualfehler liegen über1,5°, eine Zeile feuert. Es gibt keinen protokollierten Fall HumanFiretrue→FinalFirefalse in den47 gleichzeitigen Human-/Cecil-Proben. Das belegt einzelne Winkelsperren, aber **keine kontinuierliche Tracking-/Settlingursache für das gesamte schlechte Ergebnis**. Die Kombination aus langsamerem Tracking, Rauschen und enger kontinuierlicher Ausrichtung ist eine prüfbare Hypothese, kein bereits belegter Bug.

Nächste enge Unterscheidung: zuerst die getrennte gekreuzte MITTEL-Probe auswerten. Falls das Muster bleibt, unveränderte013 in einem klar begrenzten eigenen Diagnosefenster mit dichterem **bereits vorhandenem** `bot_iLogEvery` beobachten, damit tatsächliche Ziel-/Waffen-/Residual-/HumanFire-/FinalFireübergänge zeitlich zusammenpassen. Kein zusätzlicher Hookpunkt, kein Radius-/Physik-/Feuertoleranzfix aus diesem Einzelbefund. Logkosten und uninstrumentierte Kontrolle bleiben zu beachten.

Privater Parserstand: `/srv/tse-combat-a3-mittel-audit-20261112`; alle Auswertungen unter CPUQuota25%/Nice10, keine Liveänderung. Vollständige Lebens-/Schadens-/Kosten-/Hashdaten im JSON. A3gesamt, Kandidatenqualifikation und A1-Erstzustand bleiben offen.
