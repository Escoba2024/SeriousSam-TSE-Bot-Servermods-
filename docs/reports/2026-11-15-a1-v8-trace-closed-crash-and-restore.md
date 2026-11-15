# A1 V8: neuer Control begrenzt bestanden, Trace fehlgeschlagen und separat wiederhergestellt

Stand15.11.2026,10:51UTC. **Aoffen/Bnichtbegonnen. KeineLiveänderung.**

Der zuvor am aggregiertenCPU-Limit gescheiterte Trace bleibtFAIL. V8 wurde
als getrennte neue Bedingung explizit angefordert und durch einen kaltenRPC
auf genau demselben Script bestätigt; das ist keine Feststellung, welche
Laufzeit der ältere Retailtrace tatsächlich verwendete. Drei vollständige
Quellinversen und der unabhängigeReview bestanden. KeineFristen, Guards,
TTL-, Queue- oderCPU-Limits wurden gelockert.

## Neue Nativefenster

- Control10:39:46:10,08348s,`PASS_LIMITED_UNINSTRUMENTED_TWO_ORIGINALS_ONLY`,
  keineFrida/Worker/Input. ResultSHA256
  `506d923f97f613aeacd9926b66a669a05479a6147293a8e77831389e1d4aa149`.
  Root10:40:46:664Dateien/SHA/UID/GID/mode/atimeNS/mtimeNS,9Abwesenheiten,
 3normaleAbschlusslogs undalleeigenenRollen/Units/Anzeigen/4LocksPASS; reaped0.
- Trace10:40:51: **FAIL bereitsSTARTING**, keine abgeschlossene10s-Beobachtung.
  ResultSHA256`ebf5a44645cb23911c25b78e1043ce54dd706d5b183ad1c68bf279e8a45c1ccb`.
  KalteQuittung bestätigtV8/erwartetePID/ia32/4. Drei vollständigeIPC-Antworten
  connect/load/arm sind gehasht unddekodiert; alle meldenOK, enthalten aber
  keineCaptures. Genau ein zusätzlicher roherDrain liegt nurimJournal vor:
  strictpacketgültig,0Events/Calls/Getter,keineTLS-Bindung. Er ist keiner
  vollständigenWire-Antwort zugeordnet. AchtSchedulerfehler bleiben erhalten,
  zunächst `script has been destroyed`, danach u.a. Deadline-/Cleanupfehler.
  KeinS/F,keinevolleCoverage undkeinOriginalregionen-Afterbeleg amverstorbenenProzess.

DieServerunit meldete `Result=core-dump`, `ExecMainCode=3`,Status11/SIGSEGV,
Zeit10:41:35. Wine meldete davor eine unbehandelte0x80000003-Ausnahme.
Der genaue Zusammenhang zwischen Hookfehler, Signal-/Abschlussablauf und
Crashursache ist **UNKNOWN**. Das ist keine bewiesene allgemeineV8-Ursache.
NormalerServerabschluss/Helper-Cleanup/Displaycleanup/Restore bestanden im
ursprünglichenFall nicht. DerTrace und alle sieben ursprünglichenFehler
bleiben unverändertFAIL; keinautomatischerRetry.

## Separate Rootwiederherstellung

Nach Ende desControllers wurden unter allen vier exklusivenSperren nur die
überCgroup,UID,PID/start und privatenWineprefix zugeordneten eigenen
Hilfsprozesse behandelt. EigenerWineDebugger bekamSIGTERM; nach bereits
fehlgeschlagenemNormalclose wurde nur der verifizierteeigeneWineprefix über
wineserver-k geschlossen. ErstnachleeremGamecgroup wurden dieeigenenbeiden
Xvfb-Anzeigen normal perSIGTERM beendet. Fremde Prozesse wurden nichtverändert.

RoheAbschlusslogs undUnitjournal sind privat erhalten. Root stellte danach
664Dateien und9Abwesenheiten ausdemfrischenSnapshot wiederher undprüfte
SHA/UID/GID/mode/beideSnapshotzeitstempel/Treeumfang undQuieszenz um10:45:03.
Dasist `PASS_ROOT_POST_CRASH_FILE_RESTORE_ONLY`, **keinNormalclose-/NativePASS**.
Der originaleResultHash blieb gleich; fehlenderAfterregionenbeleg wirdnicht ersetzt.

Ein neuer eigenerELF32-Gegenversuch unter explizitbestätigtemV8 reproduzierte
denFehler nicht:3Fälle×400Rückgabewertprüfungen mitnatürlichemExit0, darunter
Getter-Instruktionshook+15 undverschachtelteCalllistener; Getterbytes nach
Unload/Detach exakt gleich. Diese kleineFakeTLS-Probe enthältkeineRetail-/Wine-
oderFS-ABI-Bedingungen und erklärtdenNativecrashnicht.

## Passive CPU-Domänen und Grenzen

Der neue Helfer wurde nach unabhängigemQuellreview umexakteTyp-/Bereichsprüfungen
fürdev/ino ergänzt: neuerFakeFS-Test9SubfälleRED, danach7TestsPASS0,005s.
DieübrigenPID/start-,Readzeit-,Counter- undCgroupwechselprüfungen bleiben.
Control51/Trace75CPU-Samples deckendieController biszu derenReap ab,
0Bindungsfehler. Rohwerte/Fehler bleibenprivat. Ausgefallene/recycelteQuellen
sindUNKNOWN,keineNull; Prozess- undCgroupdomänen werdennichtaddiert.
DerneueTrace erreichtekeineMethodenbeobachtung. KeineMessung erklärt den
altenCPU-Fail oderbelegt einenPerformancevorteil.
AuditSHA256`a74dbd2931fae08ca9760d0ebd23eb2d90d5c9e29ce07d7de958a00d3cff0d66`.

## Live und nächster Schritt

FrischeRead-only-Prüfung10:47:01:alle18geladenenModul-/Konfigtargets weiter
Rollback051gleich; sechs×8eigeneBots, Skulls1ungeklärterZusatzteilnehmer,
sonst0. Dev048/RedGen2/Yodeller,Skulls,Trouble,Hole018. Dev09:37:02→10:47:03:
0neueBAD/0SyncDisconnect/10073OK; älterefehlgeschlageneIntervalle bleibenoffen.

V8-Paketnichtweiterverwenden. Crash-/Restoredaten vollständigexternsichern.
A4-ResetV3 wirddeaktiviert auf030retargeted; derbewaffneteStillstand wird
gezielt überfehlendeAction-/Physikphasenbindung untersucht. Keinneuer
ungezielterLanglauf, keineA-/B-/Produktionsfreigabe.
