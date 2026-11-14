# Navigation: Cecil048 gegenüber Build018/020

Stand14.11.2026; ausschließlich Offline-Quellen-/Archivaudit ab`61ddb505`.
Claim: dieser neue bereinigte Bericht und der zugehörige neue Vergleichsplan.
Keine Implementierung, Tests, Builds, Prozess-/Display-/Frida-/Netzaktion.
Die vom Nutzer ausdrücklich relativierte schlechtere Bewegung ist eine
subjektive Beobachtung, **keine nachgewiesene Regression**. Ein kontrollierter
Red-Station-Vergleich048↔018↔020 fehlt.

## Frisch gegengeprüfte Herkunft

Alle47 manifestierten Gamequellen und28 Overlays je Build wurden gegen die
tatsächlich vorhandenen Dateien gehasht, ohne Abweichung. Das Overlay gehört
zur Herkunft; ein Gitcommit allein beschreibt nicht alle Buildbytes.

| Build unter`/srv/` | Quellcommit | DLL-SHA256 / Bytes | Manifest-SHA256 |
|---|---|---|---|
|`tse-cecil-full-build-048-20261109`|`4d04ab4ad190a0f6cd078d96f5416e0eea9e1da0`|`ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530` /393216|`6df71192b0654667740effc7e80e93e8dc0b2775597d0911e0516ee3e56704cf`|
|`tse-milestone-a-build-018-20261112`|`1802fb3f0720b53feb032abfe2c2a83407bfea6e`|`6db89204e33dc7d76ecdfed68055d2b75bde4950475793a57101fd0cefcb8e4a` /428544|`f4212443317b58b04808bd42d084e6a3286e458af2c0dbcfb276aa3bca931c2e`|
|`tse-milestone-a-build-020-20261114`|`e5f7a65502fbea683014ef8fcc95ecdd2a927b6a`|`094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0` /431104|`3099a0be953be1ff8047289de056b6cddf931cac9a4791f2520d3898357950c6`|

048→018 verändert zehn Gamequelldateien: BotDriver.cpp, BotSupplyNative.h,
BotCecilItems.h, Game.cpp, bot_aim.h, bot_human.h, bot_loadout.h, bot_profile.h,
cecil_motion.h undcecil_nav_data.h.018→020 verändert **nur BotSupplyNative.h**.
Keine gleichnamigen historischen Cecil-Build018/020 mit Milestone-Builds
verwechseln. Build019 ist die Zwischenstufe mit lokaler Supplykonkurrenzpräferenz;
020 ergänzt den engen Terminalwatchdog.

## Aktive Devbaseline und gemeinsame Daten

Root stellte die ursprünglichen Botpayloads wieder her. Die gespeicherte
Quittung`postrestore-result.json` unter
`/srv/tse-cecil-full-20261107/.codex/evidence/restart-fleet-20261111-user-baseline-20261114-171100`
hat SHA256`89df264b12648bd718fbc6496668569730740841cc707da99416e8b234c18d43`.
Dev048:92,820571s gemeinsames Flottenfenster,37 Devqueries,8eigene Bots und
1zusätzlicher Teilnehmer, alle8 mit tatsächlicher SameLife-Bewegung>1m,
7positive eigene Queryfragzuwächse,10beobachtete Respawnänderungen,
0neue Sync-/Disconnect-/CRC-/Crash-/Invalid-Action-/Joinfehler. Dies ist ein
kurzer Betriebsbeleg, keine vollständige Navigation oder dauerhafte Syncheilung.
Root dokumentierte bereits nach einem früheren048-Rollback weitereBADs;
deshalb ist weder018-spezifische Ursache noch048-Syncfehlerfreiheit bewiesen.

Dev-Botkonfigurationen wurden aus tatsächlich vorhandenen Dateien gelesen:
A-SHA`3f4e70818632bbbf72ed8f350228ecb9e5f14b4bd56b5e4e3d9f9ab3d217a8c5`,
B-SHA`81382adf3c3fb5c612ba3f83fff1e38659f0c05c82373a1d5b40c856db9a9f2a`.
HumanAI/AutoCombat/SupplyNavigation/ObstacleAvoidance=1, Diagnostics=0,
Profile0–3=7, Profilseed2026110750, MoveFactor1, YawSpeed45,20FPS,
StrafeScale0,5,FirePeriod1,FireTicks3, LogEvery200, BPS6000–100000.
Die geparsten Kampfwerte des020-Labkanonicals stimmen damit überein;
RosterOffset unterscheidet die beiden eigenen Vierergruppen. Bytehashes
von semantischer Konfiguration unterscheiden, Leerraum nicht als Verhalten deuten.
Konkrete aktive Quellen:`/srv/tse-development-live-20261107/bot{A,B}/Scripts/Integrated.ini`:
Zeilen6–9 LogEvery/Diagnostics/HumanAI/AutoCombat,15 RosterOffset,16–19
Profile0–3,20 Seed,30 SupplyNavigation. Der gepinnte Vorrollout-A-Backup
unter`/srv/tse-cecil-full-20261107/.codex/evidence/restart-fleet-20261111-build018-20261114/development/botA-backup/Scripts/Integrated.ini`
hat denselben oben genannten048-A-Hash.020-Vergleichsdatei ist
`/srv/tse-a4-build020-hard-ordered-memory-clean-final-20261114/canonical.ini`;
SHA256`9f2dfea816c3bd4d3ca0de9f3d09c2e457c208a3b50e5765575c9d0c888e465a`.

Dev048 und020-Lab besitzen identische Red-Station-Assets:

| Asset | SHA256 |
|---|---|
|`RedStation_5AF1A276.nav`|`70e2839587b0f14c024ef978579133e84eed594a3cbbd0fa1f1db98d99aa37c6`|
|`maps.txt`|`a98c865c4b4aee3adc8a10b79dfd3bcc011d20df1a339921271d243921ee9c78`|
|`settings.txt`(`preset2`)|`997ba93194bb1ae76632819184effdbb5e894636ccf57940beca4b09ba6b287a`|

Vollständige Basispfade der obigen drei Assets:
`/srv/tse-development-live-20261107/botA/Scripts/Cecil/` und
`/srv/tse-arena-isolated-20261111/botA/Scripts/Cecil/`.
`maps.txt:7` bindet RedStation,`settings.txt:2` wählt preset2.
Beide tatsächlichen Clientlogs melden`CecilLoad ready=1 nodes=193`,
Map-CRC`ff3776e0`, Nav-CRC`e4571656`. Das belegt die Graphbindung,
keinen erfolgreichen Weg. Die initialen Rolloutbelege018 verwenden denselben
Cecilpayload; fehlende Public-Navdaten vor diesem Rollout sind ein weiterer
Grund, PublicGen2 nicht als Ersatz für Dev048 zu verwenden.

Wichtiger semantischer Unterschied trotz gleicher Profilnummer7:
048 loggt`BOT-Expert-Rifle`, tier5, marksman;018/020 migriert zu`DEMON`,
tier3, duelist/arena-v1. Die nachfolgende konkrete Quellenkette zeigt die
Migration bei gleicher Seedableitung. Unterschiedliche Aim-/Reaktions-/
Target-/Waffenpolicy kann Kampf-/Supplyunterbrechungen beeinflussen;
der konkrete Einfluss auf das beobachtete Spiel ist nicht isoliert gemessen.
Der gewünschte Vergleich ist folglich ein Vergleich der Gesamtbotkandidaten,
kein isolierter Beweis einer einzelnen Wegfindungsänderung.

| Tatsächliche Datei unter`/srv/` | Konkrete Definition/Verdrahtung |
|---|---|
|`tse-cecil-full-build-048-20261109/Sources/Game/BotDriver.cpp:789`|`profile_index=*_apiProfileSlot[iLP]`;793 ruft BuildRosterProfile ohne Arenaoverride;801–803 loggen Ergebnis|
|`tse-cecil-full-build-048-20261109/Sources/Game/bot_profile.h:400`|nullbasierte8er-Rosterliste; Index7 bei408=`{5,4,"BOT-Expert-Rifle"}`; Persona4 ist marksman bei93|
|`tse-cecil-full-build-048-20261109/Sources/Game/bot_profile.h:424`|Seed aus unverändertem Legacy-Tier/Persona;425 übergibt e.tier/e.persona/e.name direkt an BuildProfile|
|`tse-milestone-a-build-018-20261112/Sources/Game/BotDriver.cpp:89`|ArenaTierstandard0=migrate roster;822 liest expliziten Slotindex,826 übergibt ihn mit diesem Override;837 loggt model=arena-v1|
|`tse-milestone-a-build-018-20261112/Sources/Game/bot_profile.h:410`|Legacy-Index7 bleibt `{5,4,"BOT-Expert-Rifle"}`;419 bildet Legacy5→Arena3;421 benennt3 DEMON|
|`tse-milestone-a-build-018-20261112/Sources/Game/bot_profile.h:451`|gleiche Legacyseedableitung;452 Migration,453 BuildProfile(tier,2,seed,ArenaTierName),454 arena=true,455 ArenaSkill;Persona2 ist duelist bei92|

BotDriver.cpp undbot_profile.h sind in020 **bytegleich** zu018 laut den
frisch geprüften Buildquellpins. Die Aussage wird zusätzlich durch die oben
genannten tatsächlichen BotHuman-Logformen corroboriert, nicht aus einer
gleichnamigen Konfigurationsoption allein abgeleitet.

Die Dev-Dedicated-DLL bleibt die getrennte Powerupvariante
`fe4a77bd1eae15a25cfeb67cf5dfdd6643cba59661f2ca3e99467a9fb15b06e0`.
Die bisherigen020-Privatgates benutzen den Original-Dedicated-GameMP
`1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208`.
Diese Bedingungen nicht in eine gemeinsame Ergebnisreihe mischen. Der
unten vorgeschlagene Originalserververgleich prüft alle drei Bot-DLLs unter
gleichen Bedingungen; er ist keine exakte Reproduktion der Devpowerupumgebung.

## Konkrete Funktionsänderungen und belegte Grenzen

- 048→018 behält die Grundgraphsuche bei, ergänzt aber validierte
  Successor-/Flugfortsetzung sowie Red-Bouncerbindungen. Die gewöhnliche
  Close-Combat-Abgabe bei Gegnerdistanz<8 bleibt; nur die validierte aktive
  Flugaktion darf begrenzt fortbestehen. Item-/Kampfbesitz nicht allein aus
  einem gesetzten Goal oder Firewunsch folgern.
- 018 ergänzt für erweiterte gewöhnliche Intermediate-Itemwege den passiven
 10s-/0,75m-Fortschrittswatchdog mit bestehender30s-Itemablehnung. Er gewährt
  keine neue Bewegung. Er reagiert auf Zielannäherung, nicht auf aufsummierte
  Wegstrecke.048 hatte diese Begrenzung nicht.
- 019/020 bevorzugt bei ersten Waffen eine zulässige Alternative, wenn ein
  näherer lebender lokaler Slot dasselbe Item bereits verfolgt. Vier lokale
  Slots, gemeinsame Frischeuhr,0,25s Frische/5s Eigentümerstillstand;
  blockierte Alternativen behalten den ursprünglichen erreichbaren Fallback.
  Keine Reservierung zwischen Botprozessen, keine Garantie gegen Doppelwahl.
- 020 erweitert ausschließlich den gewöhnlichen gemappten ersten
  Waffen-Endpunkt; gleiche10s/0,75m/30s, keine Flags/Locks/USE/Spezialaktion,
  kein brauchbarer Waffenbesitz. Die vorhandenen nativen positiven
  ItemTransitEnd-Ereignisse waren Intermediatefälle. Im unten geprüften
 020-Hard-Red-Fenster gibt es0ItemTransitEnd-Zeilen: **keinen positiven
  nativen Wirksamkeitsbeleg dieses neuen Terminalzweigs behaupten**.

## Vorhandene Runtimebelege, getrennte Nenner

| Kandidat / archivierter Kontext | Beleg | Grenze |
|---|---|---|
|048 Red, Supplyv21|10vollständige Cases/10Epochen;10/10 erste beobachtete Waffenziele mit Eigentumsgewinn; erste sinnvolle Waffenaufnahme Median5,075s/P9517,65s|`NUMERIC_SUPPLY_CRITERIA_MET_NATIVE_REVIEW_REQUIRED`; Einzelbot-/Supplyprotokoll, kein vollständiger8-Bot-Redvergleich|
|048 Hole600s|81Health-Tod/Respawnpaare, max unerklärter Stillstand2,023s; dennoch44s Itemziel,43/45Proben gleicher Hop,139,66m Weg in6,70×2,84×7,73m|Bewegung kann eine räumliche Schleife sein; Item endet Timeout, keine zusätzlichen Schüsse|
|048 Skulls600s|71Healthpaare,max Stillstand5,046s; dennoch25s gleicher Itemhop, nächste gemessene Annäherung11,69m|Kein funktionaler Erfolg trotz Aktivität; andere Map|
|018 Red→Red→Red,Serious3|23/24Slotphasen; ein Slot8inventarbeobachtete Leben ohne nützliche Zusatzwaffe|FAIL bleibt; lokale Itemkonkurrenz sechsfach konkret zugeordnet, keine globale Navregression daraus|
|019 Quiet,Serious3|23/24; ProblemB0 erstes Leben bereits nützlich bewaffnet, spätereLeben ohneNachschub;111→175Terminal14Diagnosen ohne rechtzeitigen Fortschrittsabbruch|FAIL; fehlender erster Pickup linkszensiert, nicht als„nie bewaffnet“ umdeuten|
|020 Redreset,V2,Serious3|24/24Slotphasen,432,397s, keine neuen Schlusslogfehler|Begrenzter Reset-/Versorgungsbeleg, kein Hard-/048-Vergleich|
|020 HardRed,V3|600,129s, alle8Bewegung/Inventargewinne/gebundene Feuerflags;179Serverkills; max dokumentierte stationäre Lebendphase9,050552s;0neue Schlusslogfehler|`PASS_LIMITED_A4_OBSERVATION_FUNCTIONAL_REVIEW_REQUIRED`, kein048-Vergleich, keine vollständige Übergangs-/Recovery-/A-/Langzeitabnahme|

048-Supplyaudit-SHA`b63d8fd128cdafa24ddbc73d309d3bc4960544cc8d990b915cb305674072b545`,
Datei`/srv/tse-cecil-supply013-20261109/evidence/supply048-v21-audit.json`.
020-Hardresult-SHA`fb668f2a42e51b809ba528aa6d6a3682ab699521e99ace054cdea6e3ccb1db1e`,
Archiv`/srv/tse-milestone-a-evidence-20261111/a4-020-hard-ordered-redstation-20261114-131207`.
Die048-Qualifikationsmetrik`max_unexplained_stationary_s` und die020-
Inventarmetrik`max_stationary_alive_game_seconds` haben unterschiedliche
Ausnahme-/Lückenbehandlung und Abtastraten. Ihre obigen Maxima werden
ausdrücklich **nicht** als gleich definierter direkter Leistungsvergleich benutzt.
Keine Rohspieleridentitäten, Peers oder NAVkoordinaten werden veröffentlicht.

Die048-Funktionsprobleme und Quellen sind bereits im
[Itemtransitbericht](2026-11-11-item-transit-recovery.md) dokumentiert;
018-Konkurrenz im[Supplybericht](2026-11-14-a4-local-supply-contention.md),
019-Endkante im[Terminalbericht](2026-11-14-build019-terminal-first-weapon-watchdog.md).
Der020-[Hardbericht](2026-11-14-a4-ordered-hard-redstation-checkpoint.md)
trennt tatsächliche Inventargewinne von bloßem Besitz/Links-Zensierung.
Die109:33 gegenGen2 aus dem[alten Kampfvergleich](2026-11-12-build018-six-window-comparison.md)
ersetzen weder048-Navigation noch einen menschlichen Spielniveauvergleich.

Ergebnis: gleiche Navdatei, veränderte Policies, echte bekannte Fehler auf
beiden Seiten, aber keine belegt schlechtere oder bessere Rednavigation
gegen048. [Nächster begrenzter Vergleichsplan](../superpowers/plans/2026-11-14-navigation-baseline-comparison.md)
ist nur Vorbereitung; kein weiterer Rollout und keine gestartete Probe.
