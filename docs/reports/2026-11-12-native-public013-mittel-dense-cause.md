# Native013 MITTEL: dichter Intent-/Action-Gegencheck

Im abgeschlossenen 30-s-Diagnosefenster entsteht die geringe FIRE-Zahl bereits in der HumanAI: **kein beobachtetes gesetztes Human-FIRE geht anschließend verloren**. Überwiegend liegt der protokollierte Zielrestfehler über der Feuergrenze; kurze passende Folgen erreichen oft den vorgesehenen Einschwingzeitraum nicht. Die Messung belegt weder die mechanische Ursache großer Restfehlerschwankungen noch einen berechtigten Tuningfix. Vollständige Nenner, alle15Leben,23Zielepisoden mit603Residualzeilen und27passende Einzelaktionen stehen im [bereinigten JSON](2026-11-12-native-public013-mittel-dense-cause.json).

## Beleg und Zeitabgrenzung

`arena013mittel-dense-checked-swap0-trial-1-035717`: 30.126844s, Candidate013 `3a8d84c9…`/MITTEL auf botB (lokal0–3→Slots5–8, Entities569–572), Public7fc auf botA (Slots0/2/3/4), Original-Vanilla Slot1. Instrumentation0, kein Frida. Vier normale Abschlüsse, vollständiger Restore, akzeptierte Closed-Logs; Hash/Bytezahlen und deren unveränderter aktiver Logprefix erneut geprüft. Tatsächliche Attach-Zuordnung, Originalserver-Inventarhashes/PID-Start, Controller-/Configpins, alle neun unveränderten Initialreferenzen sowie Raw/Neutral/Pending-Replay bestehen.

`botB.log` enthält2299 Human-Tickzeilen plus8Profilzeilen. `botB-closed.log` enthält2619 Human-Zeilen einschließlich Profilen und Cleanup und wird **nicht** als Aktionsnenner verwendet. 143gültige `CecilWeaponObserve.native_time`-Anker bestätigen `native_clock≈(tick−19)*0.05` mit maximal0.00016s FLOAT-Abweichung. Die konservative Verknüpfung ist auf die tatsächliche Serverproben-Spanne0.800000–30.749817s begrenzt:2291lebende Human/Combat/Input/FinalAction-Paare. Acht Randzeilen (Tick635/636) bleiben außerhalb dieses engen Nenners; sie sind im aktiven Log erhalten und enthalten zwei weitere Human-/Final-FIRE. Der vollständige aktive Log zählt somit10 statt8FIRE-Aktionen. Keine Gleichsetzung der verschiedenen Log-/Fenstergrenzen.

990der2291Aktionen haben eine Serverinventarprobe am selben quantisierten nativen Tick und in derselben Entity-/Lebensuhr-Epoche. Fehlende Waffen-/FIRE-Zustände werden nicht fortgeschrieben. Cliententscheidung und serverseitige Verarbeitung sind trotz Uhrzuordnung verschiedene Beobachtungspunkte: ein dort noch nicht gesetztes `fire_requested` beweist keinen Actionverlust.

## Vollständige Aktionsnenner

| Local | Lebende Humanzeilen | Kein gewähltes Ziel | Erinnert, nicht sichtbar | Sichtbar | Residual >1.5° | Human-/Final-FIRE |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 561 | 489 | 36 | 36 | 31 | 0 / 0 |
| 1 | 567 | 394 | 71 | 102 | 97 | 2 / 2 |
| 2 | 598 | 349 | 94 | 155 | 141 | 6 / 6 |
| 3 | 565 | 456 | 31 | 78 | 75 | 0 / 0 |
| Gesamt | 2291 | 1688 | 232 | 371 | 344 | 8 / 8 |

344/371sichtbare Zielproben liegen über1.5°, sichtbarer Median21.95°. Von27Proben innerhalb der Grenze feuern8; die19anderen haben bereits die passende aktuelle und gewünschte Waffe. Alle27passen zur äußerlich beobachteten Folge: erste/zweitaufeinanderfolgende passende Probe ohneFIRE, ab dritter mitFIRE. Dies stimmt mit MITTEL `settle_s=.10` bei20Hz überein. Die internen Einschwing-/Reaktionszähler wurden nicht gemessen; gerundete Residualwerte sind kein exakter Zustandsreplay.

81sichtbare Proben haben eine andere aktuelle als gewünschte Waffe; **alle81 haben zugleich Residual>1.5°**. Ein isolierter Waffenwechsel erklärt deshalb keinen der19passenden Nicht-FIRE-Fälle. 114gleichgetaktete1Hz-CecilState-Proben enthalten100NAV-Übernahmen; keine davon trägt vorherHuman-FIRE. Das schließt einen nachgeschalteten Verlust in den vollständigen2291FIRE-Paaren aus, aber erklärt nicht jede20Hz-Bewegungsentscheidung. `BotCombat.ready` liegt vor Supply-Arbitrierung; finaler `BotDriver.fire` wird nach SetAction protokolliert. `BotInput` zeigt komponiertes Vorwärts/UP, keinFIRE-Feld.

## Konkrete Folgen statt pauschaler Trackingdiagnose

- **Local2/entity571/generation5, IronCannon14, Zielslot1:** Tick363–412sind50durchgehend sichtbare Proben mit unverändertem Ziel und aktueller Waffe14. Residual schwankt zunächst9.52→25.57→2.43→14.48°. Tick380=1.43°,381=6.47°;385=1.40°,386=2.52°;387=1.45°,388=2.62°. Danach liegen die Werte überwiegend2–3°; keine Folge von drei passenden Proben, keinFIRE. Ab413ist das Ziel nicht mehr sichtbar; der folgende Restfehleranstieg ist deshalb kein Beleg für sichtbares Trackingversagen. Beleg: botB.log9916–12165, vollständige Episode im JSON.
- **Positives Gegenbeispiel derselben Entity/Life/Waffe, Zielslot0:** Tick604–615Residual45.81→…→1.57°.616/617=0.88/0.96° ohneFIRE,618=0.43° mitHuman-FIRE undFinal-FIRE;619–621ebenfallsFIRE.622=1.77° unterbricht.629=1.41°,630=1.52° unterbricht erneut;631/632=0.95/0.53° ohneFIRE,633/634=0.44/0.30° mitFIRE. Beleg16635–17454. Kein Waffenwechsel und kein Zielwechsel innerhalb dieser Folge.
- **Local3/entity572/generation5, Colt2, Zielslot4:** Tick537–548hat aktuelleWaffe2. Die Werte wechseln70.45/0.89/70.20/1.41/69.13/1.56/67.13/1.31/65.01/1.70°. Das Ziel bleibt sichtbar und gleich; die drei einzelnen passenden Werte erzeugen keine zusammenhängende Feuerfolge. Die vorherige Sniper13→Colt2-Umschaltung endet bei537, erklärt das anschließende Alternieren allein nicht. Beleg14555–15132. Ohne20Hz-Ziel-/Pose-/Bias-/komponierteRotationsmessung wird die Ursache dieses Alternierens nicht erfunden.
- **Local0/entity569/generation5, DoubleShotgun5:** Tick153–166Residual11.85→1.22°; aktuelleWaffe5erstab160.167verliertSicht, bevor drei passende sichtbare Proben entstehen. Später im Nahkampf mitSlot6liegen187/189/191/192teilweise unterGrenze, jedoch mit Unterbrechungen; Tod beendet das Leben. Local1/entity570/generation5 mit SingleShotgun4 erreicht dagegen189/190/191drei passende Proben und feuert191/192; beide finalenFIRE bleiben erhalten.

Die Waffen-IDs wurden mit dem Engine107-Header und der EntitiesMP-WeaponType-Deklaration abgeglichen:4SingleShotgun,5DoubleShotgun,11Flamer,12Laser,13Sniper,14IronCannon. Insbesondere ist14keineLaserwaffe. `has_ammo=0` allein wird hier nicht als Feuerverbot interpretiert; tatsächliche ausgegebeneFIRE und spätereServer-FIRE-Proben bleiben maßgeblich.

## Lebens- und Inventarbelege

15beobachteteLeben: Candidate7(3Tode/4rechtszensiert), Public7(3/4), Vanilla1(Tod); keine reinenLeichenepochen. Candidate6/7mit nützlichemBesitz,5/7mit nützlicherAuswahl,2/7mit nützlicherServer-FIRE-Anforderung; Public0/7inallen dreiKategorien. Alle siebenCandidate-Spawn-/Todes-/Pickup-Lebensabschnitte stimmen mit dem Serverinventar überein.

| Candidate Local/Generation | Beobachtetes Ende/Alter | Erste nützliche Aufnahme | Erste nützliche Auswahl | Erste Server-FIRE-Anforderung |
|---|---|---:|---:|---:|
| 0/5 | Tod7.850s | 3.900s | 4.200s | keine |
| 0/6 | zensiert20.200s | 12.300s | keine | keine |
| 1/5 | Tod8.100s | 3.750s | 4.100s | 7.850s |
| 1/6 | zensiert20.200s | 8.850s | 9.150s | keine |
| 2/5 | zensiert29.850s | 8.650s | 14.200s | 29.250s |
| 3/5 | Tod25.700s | 10.350s | 16.100s | keine |
| 3/6 | zensiert2.600s | keine | keine | keine |

ActualQuery-Fragdelta Public+6/Candidate+1. Die beobachteten HP-Abnahmen an noch lebenden Proben ergeben lediglich unattribuierte Untergrenzen: Public400.361, Candidate319.285, Vanilla80; CandidateArmor25. TödlicherOverkill wird nicht in diese Zahlen hineingerechnet. OhneDamagehook keine Schützenzuordnung, Treffer-/Schusszählung oder Kausalbehauptung aus diesen Werten.

827gültigeInventarbatches,13verworfeneÄnderungsproben, gesamteLeserzeit3.360s, maximal8.512ms; größteHauptlooplücke191.573ms. Dichtere Logs ändern Beobachtungskosten; ein30sEinzellauf ist weder ein kausaler Kostenvergleich noch A3-Freigabe. Private Skripte unter `/srv/tse-nav-a3-mittel-dense-audit-20261112`; alle Analysen unterCPUQuota25%. Rohlogs/Namen/GUIDs/Pointer bleiben privat. KeinGameplaycode geändert.
