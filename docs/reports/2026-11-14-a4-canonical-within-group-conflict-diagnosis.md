# Gleicher Sessiontick identifiziert keine eindeutige Speicherbeobachtung

Der geschlossene Lauf `a4-020-hard-groups-redstation-20261114-120936` bleibt **FAIL**. Sein Ergebnis-SHA256 ist `935f6d88c1741bd2a37d6b5c076a7b409db2abf604c394b38fb5ed8c1763cc29`. Root meldete 600,098s Gameplay, vier normal geschlossene Rollen und unabhängig bestandenen Dateirestore. Diese Diagnose verändert weder Controller, V2-Kern, Gates noch das historische Ergebnis.

## Vollständiger Konfliktbefund

Der einmalige geschlossene Archivscan verglich sämtliche Gesamtrows für gleiche physische Identität, World, Spawnclock und Sessiontick. Er fand 13.627 aktive Samples: 4.541 `botA_actual`, 4.538 `botB_actual`, 4.548 Overlap. Es gibt neun ungleiche Rowpaare insgesamt: sechs zwischen Gruppen und genau **drei innerhalb der kanonischen Gruppe**. Dazu kommen 128 gleiche kanonische Rowpaare. Im restlichen gesamten 600-s-Archiv findet sich kein weiterer kanonischer Gesamtrowkonflikt.

Alle drei liegen zwischen denselben `botA_actual`-Samples in Inventoryzeilen 7 und 10, mit identischem Epoch, Serverprozess und Vertragsdigest. Alle drei gehören zum ersten beobachteten Leben; Spawnclock und Sessiontick betragen jeweils exakt `0.9000001549720764`.

| Physischer eigener Slot | Slotnummer | Y vorher → nachher | Heading vorher → nachher |
|---|---:|---|---|
| botA:1 | 2 | 0,10750000178813934 → 0,032499998807907104 | −180 → 179,99998474121094 |
| botA:2 | 3 | 0,29499998688697815 → 0,2199999839067459 | unverändert |
| botA:3 | 4 | 0,29499998688697815 → 0,2199999839067459 | 102,5 → 102,50000762939453 |

In allen drei Rows wechselt `physics_flags` exakt von `0x40000287` auf `0x40000284`; die Höhenänderung beträgt jeweils `−0.07500000298023224`. Die gelesene Translation bleibt dabei `(0,0,0)`. HP, Armor, physische Slotzuordnung, Entity-/Worldidentität, Spawnclock, Waffenidentität, vollständiges Inventar, Ammo, Fire-/Buttonwerte und übrige Rowfelder sind innerhalb jedes Paars gleich. Die [bereinigte vollständige Ausgabe](a4-canonical-within-group-20261114/three-conflicts.json) listet sämtliche Unterschiede, ohne Rohidentitäten oder Retailbytes.

Die gemeinsame Loopzeit des früheren Reads ist `0.12447293801233172s`, die des späteren `0.15796421491540968s`: 33,491276903ms Abstand der Loopmarkierungen. Die jeweiligen Readaufrufe dauern 4,344677087ms und 3,866225947ms. Das sind keine individuell gemessenen Callback- oder Readstart-/Readendzeiten; die Loopzeit wird vor den separaten Gruppenreads erhoben. Exakte absolute Phasengrenzen lassen sich daraus nicht rekonstruieren.

## Anfangszustand und belegte Grenze

Die pausierten Smokes stehen bei Sessiontick `0.7000001072883606` und zeigen noch ungespawnte Spieler. Der erste aktive botA-Read in Zeile4 liegt bei `0.8000001311302185`, ebenfalls ungespawnt. Zeile7 ist der erste botA-Read mit lebenden Spielern. Bereits der unmittelbar folgende Overlap-Read in Zeile9 sieht für die überlappenden Slots die späteren Werte; der nächste kanonische botA-Read in Zeile10 bestätigt diese. Eine falsche feste Quellzuordnung ist damit keine Erklärung für das kanonische Zeilenpaar.

Zusätzlich sieht Zeile7 bei botA:0 bereits HP100, aber noch Spawnclock0; Zeilen9/10 sehen die positive Spawnclock0,9. Diese Row gehörte nicht zu den drei V2-Konflikten, weil der unveränderte Kern nichtpositive Spawnclocks überspringt. Das ist ein weiterer Befund zum beobachteten Übergang, keine nachträgliche Begründung, andere Anfangsrows zu verwerfen.

Der tatsächlich verwendete Reader bezeichnet sein Ergebnis ausdrücklich als `two_equal_reads_not_atomic`. `retail_inventory_readonly.py:37` liest die Felder nacheinander, vergleicht danach alle gelesenen Speicherbereiche erneut und prüft den Sessiontick nochmals. Sein Vertrag verspricht gleiche Lesepässe pro Aufruf, keine Atomizität und keine eindeutige gesamte Weltrow für diesen Tick. Die beiden neuen kanonischen Reads erfüllten denselben Vertrag, liefern aber unterschiedliche Gesamtrows.

Das qualifizierte SDK107-Feld `CSessionState::ses_tmLastProcessedTick` ist in `SessionState.h:70` als letzter Tick verarbeiteter Aktionen beschrieben. Es ist kein dokumentierter Sequenzzähler, der jeden physischen Zustandswechsel kennzeichnet. Die SDK107-Physikflags ordnen den beiden entfernten Bits die Gravitationseinflüsse auf Orientierung und Translation zu (`Entity.h:116–117`). Daraus folgt **kein** Nachweis, welcher Originalpfad oder Thread die konkreten Werte schrieb. Die zuständige Retailfunktion, Mutexphase und Gleichzeitigkeit anderer Writer sind weiterhin nicht gemessen. Es wurde keine neue Ghidra-Dekompilation durchgeführt und kein Engine1.10-Ablauf übertragen.

## Bewertung des Messdatentyps, ohne Implementierung

Der Schlüssel `(Spawnclock, Sessiontick)` identifiziert nach diesen Daten auch innerhalb einer festen Gruppe keine einzelne Speicherbeobachtung. Die bisherige Whole-row-Gleichheitsannahme für diesen Schlüssel ist empirisch widerlegt. Der historische Test bleibt deshalb fehlgeschlagen; beliebiges Weglassen der ersten Rows, Feldvergleiche anstelle ganzer Rows, EPS, Best-row-Auswahl oder Crossgroup-Ersatz würden den Befund nicht beheben.

Roots vorgeschlagener prospektiver Datentyp ist sachgerecht: sämtliche kanonischen Rows als streng geordnete `MemoryObservation` erhalten, mit eigener Identität aus PID/Start, Epoch, Gruppe und vor dem Read vergebener monotoner Readserial. Readstart/-ende und fehlgeschlagene Readversuche müssen vorab mit der bestehenden begrenzten Lesehülle archiviert werden. Eine abweichende Gesamthülle unter derselben Beobachtungs-ID bleibt harter Fehler. Gleiche Sessionticks sind dann mehrere verschieden identifizierte Beobachtungen, keine Dubletten einer behaupteten atomaren Simulationaufnahme.

Die exakte Source-/Generation-/Lifebindung und Decimal-Zeitrundung dürfen dadurch nicht geändert werden. Inventargewinn darf weiterhin nur bei strikt zunehmendem Sessiontick belegt werden. Bei Same-tick-Übergängen müssen alle Rows in tatsächlicher Readreihenfolge erhalten bleiben; es darf kein günstiger Vorgänger oder Nachfolger ausgewählt werden. Zählwerte müssen Speicherbeobachtungen benennen, keine Zahl tatsächlicher Schüsse oder Simulationsereignisse.

Diese Identitätskorrektur macht den Reader weiterhin **nicht atomar**. Zwei gleiche Readpässe garantieren keinen gemeinsamen Zeitpunkt aller FIRE-/Waffen-/Buttonfelder und keinen tatsächlichen Waffenfunktionsaufruf. Für die begrenzte Aussage „native Flags innerhalb des dokumentierten Leseintervalls, mit Sourcewachstum im gebundenen Leben“ ist der Datentyp passend. Ein Anspruch auf ein präzise phasengebundenes serverseitiges FIRE-Ereignis benötigt dagegen zusätzlich einen qualifizierten Ereignismessweg. A1-Erstzustandschaden und A3-Tierstärke bleiben unabhängige native Schadens-/Vergleichsabnahmen.

Ein möglicher passiver Ereignismessweg müsste zuerst am unveränderten Original die tatsächliche Action-/Waffenfunktion oder abgeschlossene Tickphase nachweisen. Der SDK107 nennt `ProcessGameTick`, `HandleMovers` und `HandleTimers`, belegt aber weder deren konkretes Original-RVA noch Writerexklusivität. Ein bloßer Hook auf einen vermuteten Return ist deshalb noch kein Atomizitätsbeweis. Erforderlich wären Originalhash-/ABI-/Caller-/Thread-/Sessionbindung, ausdrückliche Ereignis-ID und Eintritt-/Austrittsphase, nachgewiesene Zuständigkeit der relevanten Writer sowie die vorhandenen Bounds, Quieszenz und vollständige Originalbytewiederherstellung. Zuvor muss die getrennte eigene IA32-Instruktionsmethodenprobe bestanden sein. Hier wurde kein solcher Hook geplant implementiert oder gestartet.

## Reproduktion und Handoff

Isolierter Diagnoseworktree: `/srv/tse-a4-canonical-conflict-diagnosis-20261114`, Basis `e5a6ba4dc9dd88a7b90be0df884e8c774fff9f7c`. Keine fremde Änderung im Rootworktree wurde verändert.

Privater reproduzierbarer Scan: `/srv/tse-a4-canonical-conflict-scan-20261114/scan.py`; Aufruf `python3 /srv/tse-a4-canonical-conflict-scan-20261114/scan.py`. Dort liegen `receipt.json`, die bereinigte Ausgabe und eine nur private vollständige Rohkonfliktkopie. Acht Archivdateihashes waren vor/nach der Analyse identisch. Keine nativen Prozesse, Attachments, Compiler oder Tests wurden durch diese Diagnose gestartet. Der Scanner ist beendet; keine Aufgabe läuft weiter.

Nächster Schritt ist ein unabhängig prüfbarer Rootplan für den korrekten Messdatentyp beziehungsweise erforderliche Ereignismessung. Hier wurden ausdrücklich keine Produktions-/Gateänderung und kein weiterer nativer Versuch vorgenommen.
