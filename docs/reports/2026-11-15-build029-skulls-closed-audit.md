# Skulls029: Finalaktion eingegrenzt, Versorgung weiter offen

Der geschlossene600,027142s-Diagnosefall zeigt238beobachtete Botleben und
116Useful-Maskengewinne. Die längste nieUseful beobachtete Lebensspanne bleibt
48,688110s. Ein konkreter Teilpfad lässt sich nun trennen: Zwei Nullaktionen
entstehen bereits im Navvorschlag und werden von Arbitration/SafeMotion nicht
verworfen. Danach beendet der vorhandene2s-Holdwatchdog das Waffenziel während
protokollierter deutlicher Höhenbewegung. Das ist eine enge Fixhypothese für
einen Source-Reproducer, noch kein nachgewiesener allgemeiner Verhaltensfehler
oder die Ursache aller48Sekunden ohne Aufnahme.

Originalstatus bleibt `PASS_LIMITED_REACQUIRE_DIAGNOSTIC_OBSERVATION_ONLY`,
`qualified=false`, `functional_pass=false`. Keine Runtime, kein neuer Build,
keine Liveänderung oder A4-Freigabe durch diesen Audit.

## Quelle, Bedingungen und Nenner

Privater Fall `nav20-029-skulls-root-skulls-20261115-083018`, Result
`9800b41c91373b8b89056ad96694f8ffcbcbc612bac189ebc0938f0670a63064`.
DLL `a043de1e0fc647d2805c20ea01e9f52eada3fdaa0b55caad8be6df5302ded971`,
451584Bytes, Buildquelle7dfda985fe547cf6496cc18aaa713568fafcc9fa.
Hard2, achtDEMON3/duelist, Profile7/Seed2026110750, Original20FPS, Diagnostics1.
Server und Original sind eigene unveränderte Originalrollen. Originalslot1
wird nicht als KI gezählt: BotA0/2/3/4, BotB5/6/7/8.

Gelesene Eingaben binden WorldSHA
1af9e22b8d0dba2b1cd4b0c9952ad97ee39c0aeb64317ea7c2156f7f8dd34ed5,
NavSHA6aafa5eb0f80826033ff23a75b1dc21138127719756d207614561bffd23ce874
und296Originalpunkte. Beide aktiven Kohortenkonfigurationen bleiben getrennt
gepinnt:11a7872c…/2e6444da…, kanonischeBasis9f2dfea8… .

Alle14058Readversuche wurden mit der unveränderten vollständigenV3-/Gruppen-/
Epoch-/Prozess-/Slot-/Entity-/Lifeprüfung ausgewertet:567Fehlversuche,
13491erfolgreicheGruppenreads einschließlich drei getrennten Pausensmokes.
KanonischesGameplay4496A/4502B;4490Overlapreads bleiben außerhalb dieses
Lebensnenners.238Leben,230beobachteteTode,158links-/8rechtszensiert,
dreiAlive-after-dead-mehrdeutigeLeben. Positive Reads nach erstem Tod
verlängern weder Leben noch Pickupnenner.97Leben mit Usefulbesitz,
116strikt spätereSame-Life-Gewinne.245Sourcegenerationen insgesamt;
alle238Nativeleben eindeutigSourcegebunden, sieben weitereSourcegenerationen
ohneNative-Lebenszeugen bleibenUNKNOWN.

| Slot | Leben | Usefulleben/Gewinne | NativeFernfeuerflagproben | längstes nieUseful (s) | maximale1m-Episode (s) |
|---|---:|---:|---:|---:|---:|
|0|28|9/11|156|48,688|2,199|
|2|31|10/11|181|46,539|2,200|
|3|23|10/12|332|32,750|2,550|
|4|34|15/20|539|27,843|2,700|
|5|38|12/15|472|38,491|2,650|
|6|28|13/15|378|33,392|2,699|
|7|29|14/17|778|17,946|2,550|
|8|27|14/15|467|41,553|2,600|

Flags sind Anforderungen, keineWeaponcalls/Treffer/Schäden.1m-Episoden benutzen
alle kanonischen lebenden Vor-Tod-Reads, ursprünglicheAnkersphäre und≤0,5s
nichtfallendeTickabstände; kein kontinuierlicherBeweis und keine neueAbnahmegrenze.

## Vollständiger neuer Finalentscheidungsnenner

5036`CecilDriverFinalV1`-Zeilen bleiben vollständig erhalten.4902 haben exakte
Cohort/local/tick/actor/identischeEntry+Exitgeneration und passendeSourceleben.
48haben keinen passendenSpawn,86nurSourcegeneration ohneNativeleben. Nur229
haben zusätzlich einen vorhandenenSameTick-Nativeclockzeugen, dessen GANZES
Decimal-Druckintervall im beobachteten Leben liegt. Andere Zeilen behalten
ihre konkreteSourcebindung, werden aber nicht in Nativezeit interpoliert.
AlleMapKnown0 bleibenUNKNOWN; gleicherGenerationswert beweist keineMapstabilität.

GeprüfteSourcepins: Driver7af47d87…, Formatter5286aaca…, SupplyHeader72cea9c2…
stimmen exakt zum029Stand.5036einzigartigeInvocationtokens; keine fehlenden
20Tick-Gelegenheiten erfunden. Die vollständigenFelder umfassen Vor-Supply-
Modus/Targetindex, Proposal, Arbitration, WeaponPollwanted/lastButtons,
FirePollcurrent/wanted, SafeMotionargumente/-status/-achsen und tatsächliche
SetActionargumente einschließlichRotation/View/Buttons. EinSubmit ist keinACK.

Im vollständigenSource liegen604Candidate- und414Selectionzeilen;
189bzw69mit qualifiziertemOwnerreceipt. Die emittierten Kosten-,Commonclock-
Frische- und getrenntenLocaltime-/Progress-/Deadlinebedingungen passen.
OwnerValid0 bedeutetUNKNOWN, nichtkeinMitbewerber. Item-Entity bleibt vom
Player-Actor getrennt.86Selections haben chosen0; keine erreichbareAlternative
wird daraus erfunden.160Closed-SourcePickupzeilen,156inNativegebundenen
Sourceleben,148mit vorhandenemMaskenwechselzeugen; keineItemcallback-/Aufnehmer-
oderlebensgenaueKillzuordnung.

## Längstes nieUseful-Leben: konkreter Nullwunschpfad

A0/Generation32, Spawn551,7388305664062, lebend bis600,4269409179688:
48,6881103515625s, nichtlinkszensiert, **rechtszensiert**. Owned bleibt3.
Eine spätereSourceDeath ist Closed-Nachlauf und kein beobachteterNativeTod.
Die gesamte beobachtete gesampeltePolyline beträgt≈824,97m; kein48sStillstand.

Erstes Ziel: W9/Nav0, zwei tatsächlich emittierte Kandidaten. W9Path212,291m/
Score395,270 gegenüber W8Path273,753m/Score530,628; beideuncontested. Es fehlt
hier kein durchContention bevorzugter näherer emittierterKandidat.

BotAClosedzeilen12953/13010/13021 zeigen tick11400/11420/11440:
Positionen(-6,522,-63,995,-44,309),(-6,499,-45,293,-56,082),
(-6,499,-10,643,-56,082). Source267→Hop112 bei den letzten zweiZeilen.
OriginalNav112=(-6,5,-64,-56),Radius2,Flags0;267=(-6,5,-64,-52),Radius1.
DriverFinalzeilen13009/13020 belegen für dieselben Aufrufe:
Proposalachsen0→Arbitration0→SafeMotionStatus1/unverändert0→Submittranslation0.
Kein nachgelagertes Safety-/Combatveto dieser beiden Wünsche.

Der passende vorhandeneSourcepfad ist `cecil_motion.h:143`: am horizontalen
Stay-on-point mit großemVertikalabstand bleibt der aktiveMove neutral.
`BotSupplyNative.h:1924` akkumuliert denselben neutralenTravelhop; ab2s führt
ein nicht erfolgreicherGroundedReplan zuGoalEnd/unreachable_hold,RejectItem und
ClearGoal. Genau dieserEndgrund steht bei tick11455/Closedzeile13043.
DerSourcepfad koppelt somit neutraleNavwünsche anAbbruch, ohne dort tatsächliche
Positionsbewegung zu prüfen. WelcherGuard den ursprünglichen Nullwunsch erzeugte,
ist ohne den folgendenSource-Reproducer keine separat gemesseneBranchtrace.

WichtigesFeldverständnis: `CecilState liquid=4` ist gemäßDriverargument und
SDK107Player.es:66 **PST_FALL**, keinWassernachweis. Die tatsächliche Ursache
derVertikalbewegung,Launcher-/Flug-/Routengültigkeit und günstigereZielalternative
bleibenoffen. WederVelocity nochInput werden alsPositionsfortschritt ausgegeben.

Danach W8→W12→W7→W9; dievierEnden meldenRender5/unavailable,AufnehmerUNKNOWN.
BeiW8 ist tatsächlich ein anderer lebenderlokalerOwner näher, aber nurdieser
eineKandidat ist emittiert, und derSelektor wählt ihn trotzdem: kein beobachteter
dauerhafterContention-Ausschluss. Von51Finalzeilen diesesSourcelebens zeigen45
nichtnullSubmit; vier sichtbareKampfunterbrechungen. Sie sind keine zeitlückenlose
Beschreibung desNativelebens. ZumSourceende W13/Death fehltNativeabdeckung.

## Bewaffneter Stillstand und Grenzen

B0/Generation23 mit Owned2051 besitzt die längste hier ausgewählte bewaffnete
1m-Episode254,260910–256,910797:2,649887s; davon2,399918s exaktePosition und
Nulltranslation. Current1 ist **Messer**, trotz vorhandenemUsefulbesitz.
Ein streng zeitgebundenerFinalcall tick5140 zeigt Navproposalforward≈1,
SafeMotionStatus2 undpostSafety(Forward≈0,Strafe≈0,4,Up0);
nachdemOriginalcomposer eingereichtwirdStrafe4. Das erklärt
dieSafeMotionänderung diesesCalls, beweist aber keineNativeaktionsannahme oder
Bewegungsursache der gesamtenEpisode. Kein pauschalesLockerndesSafetyguards.

702Reacquireentscheidungen,641streng imNativeleben,61Clock-/TailUNKNOWN;
154lebensgebundeneaccepted_proposals bleibenVorschläge. ZehngebundeneHop-
Checkpoints, einGroundReplan, viergebundeneItemTransitEnds; Closedgesamtfünf
ItemTransitEnds. KeinTerminal-Watchdog- oderRecoveryerfolg ausMarkern allein.
DieMaxima sind gegenüber026/027 rein deskriptiv: getrennteEinzelfenster,
keinegematchteVerbesserungs-/Regressionskausalität und keinA4-PASS.

## Wiederholung und Übergabe

Vier bisherqualifizierte027Reader mit byteexakterCase/Root/Result/DLL/Label-
Inverse einmal sequentiell wiederverwendet. Neue reineAuswertung
`tools/audit_build029_driver_final.py`; keineSpiel-/Controllerimports.
Private Vollbelege unter `/srv/tse-build029-skulls-closed-audit-evidence-20261115`:
`reader-adaptation.json`, vierReader/Logs und derenLebens-/Decision-/Followup-
Receipts, neues `driver-final-receipt-v2.json` undausführendesLog. AlleFehlreads,
Source-onlyTails undUnknowns erhalten; keinRawarchiv restauriert.
V2-ReceiptSHA256:
`618385d565307d447bf383edc0a0908171fd91c69303202b17de0d46af34f919`.
Vorheriger engerV1-Ausgabestand bleibt separat erhalten;V2 ergänzt nur die
bereits emittiertenOwnerreceipt-Konsistenzprüfungen, keineNative-/Gateänderung.

```sh
nice -n 15 python3 -B tools/audit_build029_driver_final.py \
  --case /srv/tse-milestone-a-evidence-20261111/nav20-029-skulls-root-skulls-20261115-083018 \
  --output /srv/tse-build029-skulls-closed-audit-evidence-20261115
```

Die exklusiveAusgabedatei muss vor einer unabhängigenWiederholung in einem
frischen eigenenOutputverzeichnis liegen; die vier qualifiziertenVorstufen
und derenOutputhashes sind Voraussetzung. KeinControllerimport oderNativecall.

Root bestätigt separat vier normaleCloses und640Dateien/vierClosedlogs/
PID-/Unit-/Display-/Lockrestore inklusive neuemTimestampvertrag. DieserAudit
führt keinenRestore erneut aus. Interne582Hostsampels, CPUmax54,476%,
MemAvailablemin2496372736B, Diskmin9624129536B; interneGameplaylücke1,212s,
`budget_pass_claim=false` bleibt erhalten. KeineDauer-/A5-/B-Kapazitätsfreigabe.

Nächster engerSchritt nachRootentscheidung: den tatsächlichen neutralenTravelhop-
Watchdog mit wechselnderPosition im bestehendenSDK107Bridge reproduzieren,
bevorVerhalten geändert wird.2s, fixeGoaldeadline, Topologie,Support undSafety
bleibenunverändert. Keine weitereDiagnose-DLL ist aus diesemBefund erforderlich.

## Engster bestehender Bridge-Anschluss, noch nicht ausgeführt

`poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py` bindet
den echtenHeader an SDK107-basierteWorld-/Player-/Raystubs. Vorhandene
`groundedAcquireHandshakeFixture`, `groundedReplanFixture`, `groundedReplanHold`
und `groundedRetainedAnchorGuards` rufen schon den echtenBotSupplyTick auf;
alleFALL-/Support-/Velocity-/Lock-/Budgetgegenfälle bleiben bestehen.
KeinneuesFramework undkeineÄnderungvonCecilMotion notwendigfürdenReproducer.

MinimalerMechanismusfall: echteNavpunkte267/112/0 mit unverändertenPositionen,
Radien/Flags und gerichtetenVerbindungen; normal pickbaresW9-Item1025 und
derselbe gehalteneWeaponattempt. Bottompose etabliert die echte267→112-Kante.
Danach bekannteaufeinanderfolgende Sourceposeanker(-6,499,-45,293,-56,082),
(-6,499,-10,643,-56,082) mitPST_FALL/Gravity(0,-1,0) verwenden. Für einen
20Hz-Mechanismustest wärenZwischenposen ausdrücklich synthetischeFixturewerte,
kein nachträglich rekonstruierter Nativeflug. ExaktmessbareTestfrage ist:
erzeugen unveränderteNavigator-/Tickpfade weiter neutraleMoves und danach
unreachable_hold, obwohl die tatsächlichenFixturepositionen fortschreiten?
Goaldeadline/goalSince,2s-Grenze, Topologie undCastbudgets dabei unverändert.

Pflichtgegenprobe: gleichePose eingefroren und nurVelocity/Intent hochsetzen
darf keinenPositionsfortschritt beweisen oderaltenHoldabbruch umgehen.
Umgekehrt bewegtePose mitVelocity0 trennt tatsächlichePositionsbeobachtung von
derGeschwindigkeitsmetadatei. FesterDeadlineablauf bleibt auchbeibewegterPose
Abbruch. Alte GroundedReplan-Tests verlangen weiterhin echteSTAND/CROUCH-
Supportauthority; FALL allein darf niemalsGroundreplan/Support/Safetyfreigabe
werden. Reproducer zunächstnurTest/Report, Produktivfix erstnachRootreview.
