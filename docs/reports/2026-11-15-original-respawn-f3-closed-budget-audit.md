# F3-Originalrespawn030: geschlossener Budget-FAIL und Festzielpfad

Claim ausschließlich dieser neue Bericht und private begrenzte Auditdateien;
keine Adapter-/Paket-/Gameplayänderung.

Der F3-Control bleibt FAIL, ohne Originalinput. Ein einziger begrenzter Lesepass
umfasste das Resultat und84 tatsächliche Ownershipquittungen:85Dateien,
2311559Bytes. Keine anderen Roh-/Logdateien, Laufzeitzugriffe oder Tests.
Alle Handles sind geschlossen. Die private Auswertung inklusive ausführbarer
Readerquelle belegt jeden Eingangsdateihash und bleibt unter512KiB Output.

84Readinessversuche enthalten83 vollständige gültige Frames und einen durch das
Ownershipbudget abgewiesenen Versuch. Der Initialframe und83 Folgecaptures
ergaben84 erfolgreiche Ownershipbelege; der nächste Capture (Serial85) wurde
vor Ausführung verhindert. Das ist nicht gleichbedeutend mit85 gespeicherten
Ownershipquittungen.

In allen83 vollständigen Readinessframes: Original HP100, MayRespawn0,
neutrales Fire, identische Actor/Life/Spawnbindung. Kein beobachteter HP-Abfall,
Tod oder DEAD_READY. Sichtbares Host-Monotonicfenster23,721479s; letzter Frame
bei Parentelapsed52,102143s. Ein Zustand zwischen oder nach den Frames wird
nicht interpoliert. Der Bot hatte ebenfalls HP100; elf von83 Serverframes
zeigten sein Firebit, die übrigen72 nicht. Firebit ist kein Bullet-/Hitbeweis.

Die84 Belege beanspruchten1592539Bytes; Einzelgrößen11500 bis27013Bytes.
Nicht-Log-Felder sind vollständig gleich, Logtexte wachsen ausschließlich als
fortgesetzte Präfixe. Exakte Byteentfernung des Felds log_text reduziert alle
Belege zusammen um1397659Bytes (einschließlich jeweiliger JSON-Trennzeichen,
keine additive Feldpartition). Konstante GMS-Hexdarstellung trägt je1451Bytes
bei. Dominierend ist wiederholt gespeicherter Logtext, kein einzelner Ausreißer.

Vom3MiB-Gesamtbudget waren1553189Bytes frei. Der konservativ erforderliche
vollständige Einzelvorbehalt1572864Bytes fehlte damit um19675Bytes. Der Guard
arbeitete wie definiert. Ein höheres Budget beweist keinen erreichbaren Tod und
wird hier nicht empfohlen. Ownershipzeiten0,028359–0,061017s;
Framezeiten0,134001–0,188113s. Daraus folgt kein CPU-/Trefferkausalitätsbeweis.

25 gespeicherte CecilState-Zeilen zeigen current/wanted2, target-1,vis0 und
shots0; einige fire1/buttons32769. Die anschließende schmale Sourceprüfung
klärt die Bedeutung, ohne neue Rawdaten zu lesen:

- Gepinnter Build030 BotDriver.cpp:1178–1187 setzt bei TestTarget0 ausdrücklich
  automatic=false. targetVisible startet FALSE. Die aktive Config hat trotzdem
  AutoCombat1/HumanAI1/SupplyNavigation1; der feste Zielindex hat hier Vorrang.
- :1202–1426 ist Perception/LOS/profilgesteuerte Zielwahl einschließlich
  bs_iCombatTarget-Zuweisung ausschließlich automatic. target-1 und vis0
  beweisen im festen Zweig daher weder fehlendes Ziel noch tatsächliches LOSfalse.
- :1427–1441 richtet den Bot auf die Liveposition des Zielspielers aus;
  Aimfehler müssen beide unter3° liegen. Bewegung bleibt0, bis das erfüllt ist,
  sowie unter8mDistanz. Sonst gibt es direkten Vorwärtswunsch, keinen Navpfad.
- :1451,1479,1491,1550 schließen SupplyNav, WeaponPoll, Hindernisnavigation und
  SafeMotion hier über automatic aus. Dies ist keine verworfene Naventscheidung.
- :1529–1543 erzeugt den periodischen3Tick-Firepuls, begrenzt durch geometrisches
  AimReady; :1621 setzt Colt. Der feste Zweig prüft dafür keine Sichtlinie.
  :1671 erhöht shots nur bei automatic. Fire trotzvis0 undshots0 ist damit
  statisch erklärbar; tatsächliche Bullets, Hindernisse oder Treffer bleiben offen.

Die bestehende Spec verlangt echten Tod durch normale Botaktionen vor Arm,
sonst FAIL. Sie definiert ausschließlich ein Original-FireDownUp nach Arm/TLS,
keine zusätzliche Originalbewegung vor Arm und keine Map-/Spawnvariation.
Normaler unveränderter Red-Join/Spawn bleibt bestehen. Eine künftig explizite
normale Originalbewegungs-/Aufstellungsvorbereitung mit tatsächlicher Geometrie-
und Sichtliniencustody wäre eine neue Bedingung; sie ist kein stiller Teil
aktueller zwei Inputs. Keine HP-/Pose-/Winkelwrites, kein einfacher F4-Retry.
Konkrete Episodeursache (Wand, Aimtransport, Bullet oder Treffer) nicht bewiesen.

Provenienz: Build030 Driver SHA
7af47d87aaaf4c51ebaca6f65d628cfec3c2544419be07e39b65e52b370eb386;
aktive Config SHA cdf68caf9ff559de56b2808f2db12acefb8c87c8d002187aaf29adb674bb3261.
Beide mit explizitem resolve/NOATIME/NOFOLLOW geprüft; nur zwei Driverfragmente.
Geschlossenes Resultat SHA
93a34af1a3729e352ffb6efef57b59daa1d2d736b76ea0aee59b6613bf3f8934.
Private Belege unter `/srv/tse-original-respawn-f3-budget-audit-evidence-20261115`:
final-receipt.json SHA9de8657358900959596a741a4c85e99bda71ce84361f7da6d02bab9c2071ab6a;
fixedtarget030-static-source-note.json SHA6fcde29e3bd5fb4a4e604ad5900f9528f63d9cede0c9091e656bddf48b4bcef0.
Keine Implementierung, Budget-/Toleranzänderung oder Nativeabnahme.
