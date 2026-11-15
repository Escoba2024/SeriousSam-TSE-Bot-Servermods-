#030 B0/g11: Movement-Submit ist noch keine Action-/Physikkette

Reine fokussierte geschlossene Source-/Beleganalyse, keine C++-/Harnessänderung,
Tests, Native oder neue Vollauswertung. Vorhandener030-Auditstatus bleibt gleich.
Die konkrete Stillstandsursache bleibt **UNKNOWN**.

Slot5/B0/g11 besitzt Usefulwaffen. Der übernommene kanonische Nenner enthält
60Beobachtungen mit exakt gleicherPosition/Nulltranslation über7.7504730224609375s
(native161.25523376464844..169.00570678710938). Zwei ganze native Dezimalintervalle
binden Safety2 und nichtneutrale Submitargumente an diese Episode: Source3260/
native161.905273438 und3340/165.905517578. Keine SourceTick/20-Interpolation.

## Was zusätzlich tatsächlich eingegrenzt ist

Die beiden `CecilPlayerObserve`-Zeilen lesen native `desired!=0`, aber
`currentVelocity==0`. Playerflags525 enthalten INITIALIZED/JUMPALLOWED/SYNCWEAPON/
LEVELSTARTED, weder AUTOMOVEMENTS noch NOTCONNECTED. Kein Kamera-/Actionmarker.
Der SDK107-generierte Statetabelleneintrag019100a6 heißt `Main_03`, nicht
`DoAutoActions`; das ist keine neue Binärqualifikation aller Handler.
APPLIEDACTION fehlt an dieser Beobachtungsstelle erwartbar auch nach normalem
`PostMoving`, das dieses Bit löscht. Sein Fehlen beweist keine verlorene Action.
Die beobachteten Physicsflags0x40000287 enthalten MOVABLE und Gravitation sowie
ONBLOCK_CLIMBORSLIDE; derselbe Supportpointer bleibt vorhanden. Das beweist keine
freie Playerkollision oder gelungene Step-/Slidebewegung.

Besonders wichtig: `action_rotation` im Playerobserver wird aus dem übergebenen
lokalen `pa` geloggt, nicht aus dem native zuletzt angewandten Actionpacket.
Die nach `SetAction` geloggte Sourcezeile ist daher kein ApplyAction-Leave.
`CecilState.last_pitch` liest dagegen native `m_aLastRotation(2)`:

|SourceTick|composedPitch|nativeLastPitch|desired(x,z)|
|---|---:|---:|---|
|3260|5.3484392|14.5231276|(5.3954,0.2227)|
|3340|10.0435629|10.0435629|(3.7229,-3.7229)|

3260 kann deshalb nicht als nachgewiesener ACK genau des gerade geloggten
vollständigen Inputs gelten.3340 ist numerisch mit Submit×1.3(Knife)×1.35(DM)
innerhalb der vorhandenen4-Dezimal-Ausgabeintervalle vereinbar. Gleichheit eines
Wertes ist trotzdem keine Packet-/Callidentität. Auch weitere mögliche
Playertransformationen und vorherige identische Inputs bleiben zu berücksichtigen.

Zwischen diesen Punkten sind andere1Hz-Samples neutral:3280/3300 zeigen reale
Floor-Probe-Rejections `UnsupportedNormal` mit Support0.3976;3320/3360/3380/3400
haben ebenfalls Safety0. Der gesamte Stillstand ist also kein kontinuierlicher
Nachweis eines durchgehend nichtneutralen endgültigen Inputs. Safety2 quittiert
unter anderem einen durch den bestehenden Punkt-Ray/Flooradapter geprüften
Escapevorschlag, keine erfolgreiche vollständige Playerkörper-Physik.

## Exakte Source-/Retailgrenze und nächster Messschritt

Der Driver bindet `localInput` über `CEntity::GetPlayerEntity` und `player` über
`GetLocalPlayerEntity`; die Baseline prüft gleiche ID/World, nicht Pointergleichheit.
Die beiden tatsächlichen Pointer und ihre Predictionflags fehlen diesem Fall.
Ein Unterschied der Objektkopien ist somit nicht bewiesen oder ausgeschlossen.
`SetAction` und `CecilDriverFinalSubmit` belegen lokale Übergabe; der030-Beleg
enthält weder den gestempelten `pa_llCreated` noch eine zugehörige serverseitige
ApplyAction-/Physik-Callkette.

Die bestehende FirstState-Quelle liest bereits das echte48-Byte-Actionargument in
ApplyAction. SDK107 ordnet Translation/Rotation/View bei0/12/24, Buttons36 und
`pa_llCreated`40 ein. Vorhandene Originalguardbindungen für ProcessGameTick
(EngineRVA0xe6140), ApplyAction(EntitiesRVA0xee900) und PostMoving(0xec320) können
für einen **separat reviewten** fokussierten passiven Beleg wiederverwendet werden.
Der frühere Originalnachweis für EngineSetDesiredTranslation(RVA0x157f60) zeigt
nur Wunschkopie nach Entity+0xec und Aufnahme in Movers, nicht tatsächliche
Bewegung; siehe `2026-11-11-native009-bouncer-repeat-up.md`.

Der kleinste entscheidende neue Kettenbeleg wäre derselbe gestempelte vollständige
Input beim Client-Submit und beim autoritativen ApplyAction-Enter, dessen Leave
samt Desiredwert und anschließend phasengleich gebundene Bewegung/PostMoving
unter derselben Tick-/Actor-/Life-/Worldidentität. Er trennt fehlende/veränderte
Action von einer tatsächlich konsumierten, physisch nicht ausgeführten Bewegung.
Für eine anschließende konkrete Kollisionsursache fehlen intended/move/applied-
Translation und tatsächlicher Clip-/Step-/Supportentscheid. Diese Felder existieren
im107-Header; neue Nativeoffset-/Callbackqualifikation ist vor zusätzlichen Reads
nötig. Kein Callback aus Engine1.10 ersetzen, keine zusätzlichen Casts, keine
Radius-/Floor-/Recoveryfreigabe oder Speicherreparatur vorschlagen.

Root muss eine solche begrenzte Messung mit passender Kontrolle/Overhead und
Source-/ABIreview zuerst gesondert beschließen. Kein neuer nativer Blindversuch
oder einfacher Snapshotvergleich qualifiziert diesen Pfad.

Private reproduzierbare Quittung:
`.codex/evidence/build030-stationary-action/{analyze-v2.py,receipt-v2.json}` im
Autorenworktree; enthält zwei Driverzeugen,16kleine Sourcezeilen, WholeClockchecks,
Read-Prefixhash, Original-/Sourcepins. Kein Inventoryrawreplay, keine Navreads.
