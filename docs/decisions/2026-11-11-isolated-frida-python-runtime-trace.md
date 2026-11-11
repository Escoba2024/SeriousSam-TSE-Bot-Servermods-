# Isolierte Frida-Python-Qualifikation für die Bouncer-Diagnose

Stand:11.11.2026, nach dem lokalen ELF32-Selbsttest. Gilt ausschließlich für eigene temporäre Prozesse und die bestehende isolierte Arena-Kopie, nicht für die produktiven Server.

## Anlass und tatsächliche Verfügbarkeit

Die Original-Welt ordnet Nav12→34 dem Bouncer234 und Minigun243 zu. Wiederholte langsame oder fehlgeschlagene Waffenaufnahme trotz freier Connectoren ist in den uninstrumentierten Original-Retail/Wine-Fenstern006/007 belegt. Die vorhandenen Stichproben unterscheiden einen übersprungenen Kontakt nicht sicher von einem kurz erfolgten Launch. Statische Zuordnung und aktuelle Detailgrenzen stehen im [Bouncer-Bericht](../reports/2026-11-11-redstation-node12-bouncer.md).

Die tatsächlich verfügbaren Werkzeugmetadaten enthalten hier keinen Frida-/Ghidra-/REA-MCP-Aufruf. Python-Frida war lokal nicht installiert. Deshalb wurde ausschließlich eine neue virtuelle Python-Umgebung `/srv/tse-frida-probe-20261111` angelegt und das öffentlich verfügbare Paket `frida==17.26.2` installiert. Version wurde an der tatsächlichen PyPI-Metadatenantwort geprüft. Keine Dienste oder qualifizierten Retail-Dateien geändert, kein globales ptrace-/Kernelrecht umgestellt und kein historischer Shadow-Nachweis als lokale Freigabe übernommen. Dies ist **kein Frida-MCP-Smoke**.

## Tatsächlich bestandene Qualifikation

Ein selbst gebautes dynamisch gegen die vorhandene32-Bit-libc gelinktes ELF-i386-Wegwerfprogramm berechnet einen einfachen Aufruf und prüft selbst dessen unverändertes Ergebnis. Uninstrumentierte Kontrolle: normaler Exit0 nach4,0832s. Passive Frida-Interceptor-Probe: tatsächliche Architektur `ia32`, Pointergröße4,197 erfasste Aufrufe,0 falsche Ergebnisse, erfolgreicher Detach und normaler Exit0 nach4,1052s. Programm-SHA256 `8008ba3ee5a8e428565cbaf3a536bf6e3dec3906f015313ec539e0fc6e381b2b`. Die Zeitwerte sind keine belastbare CPU-Overheadstudie.

Ein vorheriger statisch gelinkter freestanding-i386-Versuch bestand nur die Kontrolle. Der instrumentierte Versuch wurde wegen eines Wartetimeouts nicht vollständig protokolliert; die konkrete vorherige Exception ging durch den Fehler im Wegwerf-Harness verloren. Nachprüfung fand keinen verbliebenen eigenen Testprozess. Dies bleibt fehlgeschlagene Qualifikation und wird durch den späteren dynamischen PASS nicht umetikettiert.

## Nächste Schranke

Zuerst nur Metadata-Attach/Detach an einem durch PID/Startzeit/CWD/Namespace/Originalhashes und eigener Population gebundenen, pausierten Arena-Server. Noch kein Game-Interceptor. Pausefelder, Tick und PRNG müssen vor/nach gleich sein; anschließend normale Spiel-/Sync-/Cleanup-Kontrolle. Ein solcher Smoke beweist noch keinen brauchbaren Retail-Hook. Bei anderer Zielarchitektur den vorbereiteten i386-Hook nicht verwenden.

Erst danach gegebenenfalls ein zeitlich begrenzter passiver Bouncer-Hook: Originalfunktion und echte Relokationen exakt prüfen, nur den eigenen Bouncer und die neun eigenen Spieler beobachten, begrenzte Warteschlange/Verlustzähler, keine Argument-/Return-/Spielzustandsänderung und keine aufgerufene Simulationsfunktion. Uninstrumentiertes007-Fenster bleibt Vergleichsbasis. Aufwand, Tick-/CPU-/Speicherverhalten, Sync und rückstandsfreier Detach müssen gesondert erfasst werden. Unbekannte/fremde Spieler und produktive Prozesse sind ausgeschlossen. Bei Scheitern keine Sicherheitsumgehung; passive Quellen-/Logdiagnose fortsetzen.

Offizielle Schnittstellenreferenzen: [Frida-Installation](https://frida.re/docs/installation/), [JavaScript-API und Interceptor](https://frida.re/docs/javascript-api/). Diese beschreiben die API, belegen aber keinen lokalen Test. Private Quellen, Testprogramme, Prozessidentitäten und Rohbelege liegen im bestehenden Milestone-Evidence-Verzeichnis und gehören in den nächsten privaten Backup-Nachtrag.

## Nachtrag: Wine-Metadaten-Schranke tatsächlich bestanden

Der eigene pausierte Original-Retail/Wine-Server wurde inzwischen ausschließlich für Metadaten angebunden: tatsächlicheArchitektur ia32/Pointer4,0Game-Interceptor, erfolgreicheEntladung/Detach, Pause/Tick/PRNG vor/nach exaktgleich. Anschließendes15,6398s-Spiel-/Syncfenster0BAD/Disconnect, allevierRollen regulärgeschlossen. Sanitisiert `../reports/milestone-a-20261111/frida-wine-metadata-smoke.json`. Dies ist weiterhin kein TSE-Game-Hooknachweis.

Vor Einsatz des vorbereiteten passiven Bouncer-Hooks fand Root bei der unabhängigen Prüfung einen Metadatenfehler: Der Entwurf hatte Cecil-Pfad-Hash5af1a276 alsMap-CRC bezeichnet. TatsächlicheWeltbytes erneut aus dem privaten GRO gelesen:901715Bytes, SHA66e1309ee6eeeda8c564574df65df87a8406f4079b78ad508e77c82d19971111, CRCff3776e0. Schema/Validator müssen diese Werte getrennt führen und die Vertauschung ablehnen. Bis zur korrigierten Quelle und erneutem Review kein Hook-Arm.


## Tatsächlicher erster Game-Hook, 22:12–22:14 UTC

Das private Fenster `arena007hook-checked-swap0-trial-1-221254` ist beendet: 60,0507s Spielbeobachtung, null SYNCBAD/Disconnects, alle vier Rollen normal geschlossen. Ein vollständiges Bouncer234-Ereignis, null Drops/Lesefehler, erfolgreicher Detach und exakter restaurierter123-Byte-Funktionskörper einschließlich beider echten Relokationen. Der Aufruf gehört jedoch zum alten048-BotA/local0 (Server-Slot0, Entity565); `CecilState` und Inventar stimmen überein. Vorheriger Support234 wird nach dem normalen Originalaufruf null; die Geschwindigkeit ändert sich von(-13,37; -6,19; -0,12) auf(59,78; 63,71; -80,10). Dies beweist genau diesen normalen Launch, keine erfolgreiche neue007-Botroute. Sanitisiert: [Erstbeobachtung](../reports/milestone-a-20261111/frida-bouncer-first-observation.json).

Der erste Controller speichert Frida-`message.type=error`, wertet diese aber noch nicht automatisch als Fehler. Unabhängiger Review fand diesen wichtigen Gatefehler; im gespeicherten konkreten Lauf gibt es keine solche Meldung. Die Akzeptanz oben enthält eine explizite Nachprüfung des Fehlerkanals. Der nächste Controller muss diese Meldungen unmittelbar in `errors` übernehmen und beim Abschluss ablehnen. Außerdem beginnt TTL beim Arm vor Pausefreigabe: 60s TTL sind keine lückenlose Abdeckung des60,0507s-Spielzeitfensters. Ein nächster begrenzter Entwurf erfasst Arm-/Ablaufzeit und alle Aufrufzähler vor dem Filter ohne unbekannte Pointer zu dereferenzieren.

Die erste schnelle Zuordnung `group=observer` wurde vor Veröffentlichung korrigiert: Gruppenlabels benennen nur überlappende Vierer-Lesebündel. Slot0 ist BotA/local0, der Vanilla-Observer ist Slot1/Entity563. Eigentum muss aus tatsächlicher Client-Entity-ID und Server-Slot abgeleitet werden. Der007-Vollbericht führt BotA bereits korrekt mit Slots0/2/3/4; seine Zahlen wurden nicht anhand des irreführenden Labels gebildet.
