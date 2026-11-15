# Normales Original-Respawn/Festziel030 – separate deaktivierte Bedingung

Rootruling nach Trouble031-CLOSED15:49:50: DEAD_READY darf den vorhandenen
Basisreader ohne optionale Live-Colt-Muzzlegeometrie benutzen. Alter Coltreader,
inputfreier MethodWindow, Observerbody/Schema/Validator/18Sites und vier Coredateien
bleiben bytegleich. Keine Runtime/Builds/Original-/Livewrites durch den Autor.

Exakt zwei Actors, Originalopfer global0 und nach tatsächlicher lokaler Ownership
gebundener030Bot global1; unveränderter OriginalDedicated und Originalclient.
Gepinnte neue Config unterscheidet sich ausschließlich TestTarget-1→0; bestehende
FirePeriod1/FireTicks3/Move1/Yaw45/Nav/Settings unverändert. Normale Bot-Actions
müssen realen Originaltod vor Arm bewirken; ohne Tod bis bestehender Frist FAIL.
Kein HP-/Pose-/Winkelwrite, künstlicher Schaden, Ersatzspawn oder automatischer Retry.

DEAD_READY: frische übereinstimmende Doppelreads health≤0,MayRespawn2,neutrales
Fire,nicht gelöscht/nicht Predictor, exakt Actor/World/Slot/PID/start/Spawn/NS.
Vorhandenes NativeContext.input_frame liefert die gepinnten Retailreadinessfelder;
kein neuer ABIoffset. Alte optionale Animator-/Coltgeometrie wird nicht gelockert.

Nach Arm und TLS genau ein normaler FireDown/Up an das eigene Originalfenster,
gewünschterHold.1s, tatsächliche Zeiten/Returns/Fehler/Neutralität archivieren.
Keine100ms-ACKgarantie. Vor Down≥2.35s Restreserve; hardHold.35s,ACK2s,
.2s/8Frameattempts,max48Aktionen/96Nativeattempts unverändert. Release wird auch
bei Down-/Metadatenfehler genau einmal versucht, Flush/Neutrality unabhängig.
Nur kausal beobachteter EEnd/DeathHandler/Init erlaubt den erwarteten Lifewechsel;
andere Actor-/World-/Prozessänderungen fatal. Normalinput ist keine Aimkalibrierung.

Native10s einschließlich Input/ACK,TTL15s,Queue64/native16384/order8192/damage1024,
TLS2s256,Parent85/Runner90,alleHost-/Roharchiv-/S/F-/38Restore-/Cleanupgrenzen bleiben.
Keine neue Beobachtungszeit nach Input und kein Clockreset nach Vorbereitung.

Tracepositiv nur mit tatsächlicher nach Arm gebundener Release→EEnd→DeathHandler→
Init→erstem validen GameTick sowie normalem und fatalem Schaden am Original mit
vollständiger registrierter Bot-Colt→Bullet→Cast→Direct→Receive-Kette vorS.
UnbekannteOwner/explicit chain_boundfalse/fehlendeLeaves/Drop oder fehlende
Beispiele bleiben INCOMPLETE. Control bestätigt nur eigene normale Vorbereitung/
Transport/Release, keine Hookketten. Kein allgemeiner A1-/Botopfer-/Fire-/Gainpass.

Claim: nur neue a1_original_respawn_policy.py,a1_original_respawn_method.py,
prepare_a1_original_respawn.py und je eigene Tests/Spec/Plan/Report. Eigener
vorhandener WT /srv/tse-build030-skulls-closed-audit-20261115. Parent D-v3
/srv/tse-a1-registered-first-state-damage-v1-v3-disabled-20261115 Manifest
1b58376cc824a597fd16be43fb8f7a956467dc05dfa1300c364a5fa37d92809b.
Keine Parent-/Frozenänderung; spätere frische Kopie main/instrumentation disabled.
