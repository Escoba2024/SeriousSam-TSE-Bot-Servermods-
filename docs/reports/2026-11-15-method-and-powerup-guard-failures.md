# Zwei geschlossene Prüfkonflikte – 15.11.2026

Kein Livewechsel. A bleibt offen, B nicht begonnen. Beide Tests sind FAIL;
Aufbau, erste Messpakete und wiederhergestellte Dateien ersetzen keine Abnahme.

## First-State-Methodenfenster060723

Case `a1-first-state-getter-boundary-root-trace-20261115-060723`,
ResultSHA256 `aeffa6a7040b155cae6a49e30b5960c4e182db7c0fe605f4d40b35136f7e4753`.
Nach dem bereits portabel geprüften Getterboundaryfix erreichte der Trace
OBSERVING. Erstes Paket:21abgeschlosseneCalls/42Events, Getter1, Fault0,
Drop0, AbortedLeave0; ProcessGameTick/ApplyAction/PostMoving/CastRay. Strikter
Validator akzeptierte dieses Paket, nicht den ganzen Test.

Anschließend prüfte der alte periodische InventoryReader vollständige originale
Colt-Instruktionen, obwohl derselbe Methodenbeobachter FireColt absichtlich
abgefangen hatte: `loaded Colt Original instructions differ: FireColt parameters
clip decrement`. Das ist ein widersprüchlicher Prüfvertrag. Danach enthält der
Nachlauf64Events mitQueueoverflow/1Drop/1AbortedLeave; FAIL bleibt erhalten.

Rootrestore06:10:25UTC:664Dateien,9Abwesenheiten,3Abschlusslogs, Prozesse,
Units, Displays undvierSperren geprüft. Zusätzlich alle38vollständigen
Originalbereiche gemäßunveränderterHIGHLOW-Policy vor/nachgleich,
Identitätgleich, Unload/Detach erfolgreich. Alle drei Spielrollen regulär
beendet, eigenerWorker erst danach beendet. Outer43Samples: CPUmax73,5369%,
RAMmin2806599680B, Diskmin10733805568B; maximaleLücke1,00215s. Keine gemessene
Ressourcenverletzung, dennoch Child1/FAIL_HOST_OBSERVATION.

Nächster enger Scope: aktive Methodenüberwachung mit bestehenden Host-, Log-,
Identitäts-, Display-, Window- und Queryguards statt der fremden alten
Input-/Coltgeometry-Stichprobe. Prearm-Paare und volleOriginalprüfungen vor
Arm/nachUnload bleiben. Das beweist keine aktiveInventory-/Aim-/fixedLife-
Kontinuität. Neuer passender uninstrumentierterControl nötig. VorRuntime muss
derDrainplan qualifiziert werden: beobachteterGesamtpoll159,6ms, davon23msIPC;
64Eventqueue hat keine belegte Reserve. KeineQueue-/TTL-/Schema-/Toleranzweitung.

## PowerupOFF061540

Case `powerup-048-offon0-root-redstation-20261115-061540`,
ResultSHA256 `a216c955abf56bf22a1741f9936302f8e0fdd83dfc4748c1e737219423891a02`.
FAIL vorCensus/Release an `A4 native fire V2: sample Original module hashes`.
InventoryReader war bereits für den vorgesehenen Dedicatedfe4 gepinnt,
der nachgelagerte Fireobserver erwartete dagegen noch OriginalGameMP1c41.
Keine600s-, Sync- oder Filterursachenaussage; ON wurde nicht gestartet.

Rootrestore06:24:21UTC:640Dateien,4Abschlusslogs, allevierRollen/Units/PIDs,
Display undvierSperren geprüft. Outer64Samples: CPUmax57,3604%,
RAMmin2737885184B, Diskmin10699644928B, maximaleLücke1,00107s; Child1 bedeutet
FAIL_HOST_OBSERVATION. Rollenstrikte Korrektur muss fe4 ausschließlich als
gepinntenServer zulassen und OriginalEngine/Entities/Bot/Vanillaguards behalten.
Neue deaktiviertePakete, echteMismatch-/Negativtests undRootreview sind nötig.

Private vollständigeRohdaten bleiben außerhalb des öffentlichenRepository.
Es wurde keinFehler alsbestanden umetikettiert, keinGrenzwertgelockert und kein
unveränderterTest erneutgestartet. Quelle081/Delta072 sichern dieVorbereitung;
die neuen abgeschlossenenRohdaten gehen inDelta073.
