# A4: kumulative Rotationsbasis und Lücken der Phasenbeobachtung

Status: Quellkorrektur zur unabhängigen Prüfung vorbereitet; keine neue DLL und kein nativer Lauf durch diesen Worker. Der Versuch `a4-reset015-lowrender-readable-20261112-092421` bleibt FAIL.

## Abgrenzung und Ausgangsstand

Arbeitsbasis ist `0e7deda04b06571a83da1342b7f13d10347eda74` im isolierten Branch `codex/20261112-a4-phase-activity`. Die geprüfte Build015-Überlagerung und die bisherige Driver-Datei dieser Basis sind textgleich. Build015 stammt von `b6b776ddbc761ee96049e6626edd5af4895cb3af`; seine DLL hat SHA-256 `10015f213c05b2faefc312e11a310dae63d64eda1c7173601c6ffd4386a70313`, der bisherige Driver `cf021bb098088bbeb63a2488012a6262be1a5fb2d630994b23860d8f990c7fff`.

Der vorhandene Versuch belegt tatsächliche Ausführung der Begin-Skripte 1/2/3 und effektive Zeitlimits 1/1/0. Alle vier Rollen wurden normal geschlossen; die finalen Logs wurden akzeptiert und 648 Sicherungseinträge wiederhergestellt. Das Ressourcenmaximum betrug 56,4334 Prozent CPU, die kleinste freie verfügbare Speichermenge 2.276.880.384 Byte. Diese Teilnachweise ändern den fehlgeschlagenen Aktivitätsnachweis nicht.

## Konkreter Fehler im Produktionspfad

`SBotState::bs_aHeading/bs_aPitch` sind kumulative eigene Sollwinkel. Der bisherige neue-PlayerSource-Pfad setzt sie zurück. `BotHumanAttach`, der Reset der Navigation und der Wechsel der Spielerentity setzen dagegen nur Profil-, AI-, Waffen- beziehungsweise Navigationszustand zurück. Bleibt die PlayerSource über eine Map erhalten, kann der vorherige Sollwinkel die neue Entity erreichen.

Die tatsächlichen Compose-Zeilen ziehen `localInput->m_aLocalRotation` vom Sollwinkel ab. Der normale Composer addiert diese Differenz anschließend wieder zur nativen lokalen Rotation. Ein alter Soll-Pitch von 173,4698792 Grad und eine frische native Basis von null ergeben deshalb wieder einen absoluten Input von 173,4698792 Grad. Der offline reproduzierte Fehler liegt im eigenen gewünschten Winkel, nicht in einem notwendigen Nullsetzen nativer Felder.

Der Datenpfad ist unter dem bestehenden `ga_csNetwork`-Lock eingebaut. Ein neuer Helper übernimmt beim Attach, Wechsel der Mapserial, Wechsel der originalen lokalen Inputentity oder Entity-ID den endlichen `m_aLastRotation`-Wert in die beiden eigenen Sollwinkel. Entscheidungsspieler und originale Inputentity müssen dieselbe positive Entity-ID und dieselbe nicht leere World besitzen. Fehlende oder widersprüchliche Beobachtungen bleiben neutral und können später erneut gültig gebunden werden. Ein transienter Predictor-Wechsel allein ist keine neue Grenze.

Ein normaler Respawn derselben Entity löst keine solche Übernahme aus. Die kumulative Basis kann dabei ungleich null bleiben. Es gibt keine direkten Schreibzugriffe auf native View-, LocalRotation- oder LastRotation-Felder und keine Änderung von Gain, FOV, Zielwahl oder Feuerlogik.

## Native Beobachtungen und Aussagegrenze

Die Zeilen stammen aus den getrennten unveränderten Phasenlogs des Versuches; Tick ist der lokale kumulative Driver-Tick, keine globale gemeinsame Spielzeit.

| Beobachtung | Entity | Driver-Tick | View-Pitch | Local/Compose/Last-Pitch | kumulative Feueraktionen |
| --- | ---: | ---: | ---: | ---: | ---: |
| Letzte lebende A0-Zeile in Phase 1 | 560 | 3060 | 0 | 173,4698792 | 172 |
| Erste A0-Zeile in Phase 2 | 559 | 3560 | 90 | 173,4698792 | 172 |
| A0 nach gewöhnlichem Respawn in Phase 2 | 559 | 4200 | 0 | 173,4698792 | 172 |
| A0 am Ende von Phase 2 | 559 | 5040 | 0 | 228,9070129 | 182 |

A0 bleibt in seiner ersten beobachteten Phase-2-Lebensperiode auf View-Pitch 90. Der Körper-Pitch allein wäre hierfür kein Blicknachweis; die vorliegenden Zeilen enthalten ausdrücklich den View-Pitch. Der gewöhnliche Respawn zeigt die wichtige Gegenprobe: View null bei erhaltener kumulativer Basis 173,4698792.

Der offline Test beweist die Übernahme des alten Sollwinkels durch die tatsächlichen Attach-/Entity-/Compose-Anweisungen. Die bisherigen nativen Samples beginnen erst nach ersten Aktionen. Sie rekonstruieren weder die erste native Action-Queue noch den exakten ersten View-Schritt. Die gesamte native 90-Grad-Abweichung und ihre Auswirkungen auf Kampf/Navigation gelten deshalb erst nach einem neuen begrenzten Lauf als behoben.

Eine neue Diagnosezeile `[BotRotationBaseline]` wird nur bei tatsächlicher Basisübernahme und aktiviertem bestehendem Diagnoseflag ausgegeben. Sie erfasst Mapserial, Slot, Entity/World, bisherigen Sollwinkel, native Last-/Local-Winkel, View und Spawnclock **vor** der Änderung des eigenen Sollwinkels. Sie verändert keine Entscheidung und ersetzt keinen Nachweis des ersten Simulationszustandes.

## Aktivität: Messlücke und tatsächlich fehlendes Verhalten

Die neun Spieler umfassende Inventarerfassung beginnt nach dem Observer-Rejoin in Phase 1 erst bei Spielsekunde 19,949981689453125, in Phase 2 erst bei 15,1000394821167. Das bisherige `run-mapreset.py` erstellt den neuen `InventoryReader` erst nach `protocol.ready`. Der blockierende Start des neuen Original-Observers läuft davor. Die Phasenlogs erfassen dagegen bereits frühere Botaktionen.

| Phase / Bot | vorhandene Beobachtung | Bedeutung für die offene Abnahme |
| --- | --- | --- |
| 0 / alle acht | Je Bot alle geforderten Aktivitätsfelder vorhanden | Phase 0 besteht diese Teilprüfung. |
| 1 / A2 | Gesamter Phasenlog: nur zwei Aufnahmen von Double Colt (Masken 3→7), Feuerzähler 118→140, kein protokollierter brauchbarer Fernwaffenzugang | Diese Lücke ist nicht allein durch den späten Reader erklärt. |
| 1 / B0 | Shotgun-Aufnahme bei Tick 2583, im nativen Inventar um Spielsekunde 44,7; Zähler 216→222 bereits früh, danach keine weitere Zunahme | Späte Waffenverfügbarkeit und fehlendes späteres Feuer bleiben ein tatsächlicher begrenzter Aktivitätsbefund. |
| 1 / B1 | Cannon-Aufnahme bei Tick 1744; beim ersten Inventarsample bereits vorhanden; native Feuerproben vorhanden | Der Vorher/Nachher-Pickup liegt vor der Inventarerfassung. Erstbesitz darf nicht als beobachteter Pickup umgedeutet werden. |
| 1 / B2 | Shotgun-Aufnahme Tick 1753, weitere Waffe Tick 1920; beim ersten Inventarsample schon vorhanden; native Feuerprobe vorhanden | Gleiche linke Beobachtungsgrenze. |
| 2 / A0 | Cannon-Aufnahme Tick 3622 vor Inventarstart; 75 1-Hz-Zeilen mit fire=0, aber Feuerzähler 172→182 | Ein null gesetzter Momentanstatus beweist keine ausbleibenden Inputs. Die späteren zehn Aktionen betreffen Colt; native brauchbare Fernwaffenfeuerprobe fehlt weiterhin. |
| 2 / A2 | Shotgun-Aufnahme Tick 3656; tatsächliche Shotgun-Inputs um Tick 3680–3720 vor Inventarstart; Zähler insgesamt 140→178 | Frühe Aktionsbelege sind vorhanden; nativer Feuerbeleg und beobachteter Inventarzuwachs werden durch späte Samples verpasst. |

Alle Bots haben Ready-/Bewegungszeilen; die größte beobachtete stationäre Zeit liegt bei etwa 2,4 Sekunden. Das allein schließt Umwege oder Schleifen nicht aus. Es wird kein längerer Versuch allein aufgrund dieser Werte als erfolgreich angenommen.

Die separate minimale Beobachtungskorrektur soll bereits nach frisch gebundenen Map-/NAV-Logs und tatsächlicher Acht-Bot-Zuordnung native Inventarproben sammeln, einschließlich der vorhandenen begrenzten Warteoperationen des Observer-Neustarts. Die spätere Neun-Spieler-Registry muss dieselben acht Entity-/World-Zuordnungen bestätigen. Persistente Prozessidentitäten, Originalmodul-Pins, frische Loggrenzen, native Zeitfolge und bestehende Lebensschlüssel bleiben bindend. Alte Proben und bloßer Erstbesitz dürfen keine Pickup-Transition erzeugen. Die bisherigen 300 Sekunden, 50 Sekunden Übergang, 19 Sekunden Observer-Schließgrenze und alle Aktivitäts-/Ressourcenanforderungen bleiben bestehen. Der Beobachtungspatch wird separat geprüft; er ist kein Bestandteil dieser C++-Korrektur.

## Enger RedStation-Whitelistbefund

Für die gepinnte Original-RedStation-Welt `66e1309ee6eeeda8c564574df65df87a8406f4079b78ad508e77c82d19971111` liegt nach dem bestehenden Entitybefund kein Teleport- oder PlayerActionMarker-Objekt vor. Node 12 ist Bouncer 234; Node 34 gehört zum Minigun-WeaponItem 243. Das NAV-Bit TELEPORT ist kein Beleg für einen physischen Teleporter. Eine echte Teleporter-Funktionsprüfung ist für diese konkrete Welt deshalb nicht anwendbar.

Die vorhandenen Bouncer-Berichte enthalten einen nativen erfolgreichen Start an Bouncer 234 mit anschließendem Minigunzugang und spätere Original-Funktionsaufzeichnungen. Build015 zeigt in der aktuellen Phase 2 für A3/Entity 570 eine zusammenhängende 12→34-Flugroute und bei Tick 5040 den Inventarzuwachs 1043→1107 (Minigun-Bit 64). Das ist konkrete Routen-/Itemevidenz; die aktuelle Spur enthält jedoch keinen neuen Hookbeleg des exakten nativen Kontaktereignisses.

Die offen bleibende RedStation-Frage ist somit nicht das abstrakte Fehlen aller denkbaren Mapfunktionen. Offen sind die Aktivitätsanforderungen für alle acht Bots nach den tatsächlichen Reloads und die native Wirkung der jetzt korrigierten Sollwinkelübernahme. Bouncer-/Item- und korrekte Reloadbefunde können unabhängig anerkannt werden; eine vollständige Kandidatenqualifikation folgt daraus noch nicht. Für andere Welten und Flüssigkeitsnavigation wird keine Übertragbarkeit behauptet.

Quellen im Repository: `2026-11-11-redstation-node12-bouncer.md`, `2026-11-12-bouncer012-arrival-up.md`, `milestone-a-20261111/native-bouncer-v3-control-and-observation.json`, `2026-11-12-arena-zoom-residual.md`. Letzterer hält die direkt disassemblierte Retail-ApplyAction-Differenz-/LastRotation-Semantik fest; SDK-Compose-/Respawn-Code dient ergänzend der Erklärung, nicht als alleiniger Retail-Beweis.

## Reproduzierbare Prüfung

Der neue `test_rotation_epoch_native.py` extrahiert tatsächlich `SBotState`, `BotHumanAttach`, den Entity-Grenzblock und die beiden Compose-Anweisungen aus `BotDriver.cpp`. Native Felder werden durch kleine SDK-förmige Testobjekte bereitgestellt. Der ursprüngliche Test kompiliert auch ohne den neuen Helper.

Root führte vor der Änderung denselben direkten Test aus: Kompilierung erfolgreich, 18 Prüfungen, acht Verhaltensfehler, Exit 1. Mit der Quellkorrektur bestehen dieselben 18 Prüfungen. Der erweiterte Test ergänzt ungültige Identity-/World-/Winkelbeobachtungen, gültige Wiederholung, unabhängige Mapserial, Originalobjekt-/Predictor-Unterscheidung sowie sparsame, rein beobachtende Diagnose. Root hat den erweiterten Test mit ASan/UBSan ausgeführt: 47 Prüfungen, null Fehler, Exit 0 in 0,84 Sekunden. Der bestehende Test der tatsächlichen Driver-Aktionsguards besteht ebenfalls mit ASan/UBSan, Exit 0 in 1,05 Sekunden. Driver-, Regression- und SDK-SHA sowie die Root-Quittung sind in `milestone-a-20261111/a4-rotation-epoch-source.json` festgehalten.

```bash
python3 poc/candidates/redstation-supply-20261107/test_rotation_epoch_native.py --sanitize
python3 poc/candidates/redstation-supply-20261107/test_cecil_action_native.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
```

Die RED-Quittung liegt privat unter `/srv/tse-milestone-a-continuation-evidence-20261112/a4-rotation-epoch-red.log`. Root besitzt Review, Commit-/Integrationsprüfung, gegebenenfalls DLL-Build und einen neuen namentlich getrennten nativen Versuch. Kein bestehender FAIL, keine alte Controllerquelle und kein bisheriges Beweispaket wurde umgeschrieben.
