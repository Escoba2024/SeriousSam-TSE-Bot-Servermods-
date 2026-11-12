# Retail-Schadensbeobachtung im isolierten Labor

Die erste eigene TSE-Ausführung des privaten Damage-v2-Beobachters ist als
begrenzter Werkzeugnachweis bestanden. **A1 ist damit nicht abgenommen.**
Frida-MCP war hier nicht erreichbar; verwendet wurde das zuvor am eigenen
ELF32-Prozess geprüfte lokale Frida-Python 17.26.2. Kein produktiver Prozess und
kein fremder Spieler wurde instrumentiert.

Der Hauptagent hielt den exklusiven Lock des privaten Labors mit eigenem
Netzwerk-Namespace, vier Prozessrollen, eigenen Wine-Präfixen und neun eigenen
Spielerentitäten. Originalserver und Vanilla verwendeten GameMP `1c41da35…`,
Engine `b79bf8bb…` und EntitiesMP `7f595f2a…`; die Botkohorten verwendeten
Kandidat011 `4184df65…` und Cecil048 `ec820d04…`. Die effektive Session setzte
Spawn-Unverwundbarkeit auf 0. Die Serverdatei blieb bytegleich. Frida Interceptor leitete die zwei unten
genannten Stellen vorübergehend für die Beobachtung um und restaurierte sie
anschließend; der instrumentierte Prozess ist keine unveränderte Kontrolle.

Vor dem Hook lief dieselbe kontrollierte Konfiguration ohne Instrumentierung
30,071 Sekunden. Danach lief die instrumentierte Probe 30,087 Sekunden. Beide
endeten ohne beobachtete Sync-/Crash-/Joinfehler; alle vier Rollen wurden normal
geschlossen und ihre danach archivierten Logs geprüft. Es handelt sich um zwei
natürlich ablaufende Partien, keine identische Action-Aufzeichnung.

Der v2-Script-SHA256 lautet
`767a013ae896aa507d536e16f34ee3ed9bcc73121b41970ea329478f59381787`.
ReceiveDamage liegt in der unveränderten EntitiesMP bei RVA `0xed380`, der
ursprüngliche Körper umfasst 1395 Bytes. Der kurze TLS-Bindungsbeobachter sitzt
am ursprünglichen CurrentTick-Getter der Engine, RVA `0x2c1af`; der vollständige
Getter umfasst 22 Bytes. Ein Getter-Aufruf band den tatsächlichen TLS-Block des
Spielhauptthreads. Danach war dieser Getter bereits wiederhergestellt.

Ergebnis: 52 gesamte und 52 zugeordnete Damage-Aufrufe,52 vollständig empfangene
Records, 0 unbekannte Opfer,0 fremde Threads, 0 Drops, 0 Faults und keine
Detachfehler. Beim Ende liefen keine erfassten Aufrufe mehr. Der Listener
überdeckte das gesamte beobachtete Spielfenster. Nach Stop, Unload und Detach
stimmten beide vollständigen Originalfunktionskörper einschließlich ihrer
geprüften HIGHLOW-Anpassungen wieder bytegenau. Es gab keine Spielzustands-
Schreibzugriffe, NativeFunction-Aufrufe oder Änderungen von Schaden/HP/Timern.

Die Probe erfasste 22 direkte HP-Abnahmen, aber keine im exakt gleichen
Spawn-Tick. Ein normaler Fremdtreffer war bereits ungefähr 1,05 native Sekunden
nach einem Botspawn sichtbar; seine vollständige DamageType-/Originalpfad-
Zuordnung und die verlangte wiederholte erste-Tick-Abnahme bleiben offen.
Umwelt-, Selbst- und besondere Schadensarten dürfen nicht als normaler
Fremdtreffer ausgegeben werden. Auch ein gleichzeitiger Spawn-/TLS-Tick würde
keine atomare Aussage über den allerersten verarbeiteten Zustand begründen.

Beobachtete Kosten: Server 3,525 gegenüber 3,889 Prozent eines CPU-Kerns;
Server-RSS am Ende 48,97 gegenüber 101,18 MiB; Frida-Setup 0,322 Sekunden.
Die unterschiedlichen Partien und der nicht mitgemessene Hostcontroller
verhindern einen kausalen Overheadwert. Die Instrumentierung ist insbesondere
wegen des zusätzlichen Speicherbedarfs kein Produktions- oder Dauertestwerkzeug.

Bereinigter Beleg mit Logprüfsummen und vollständiger Ergebnisabgrenzung:
[erste native Schadensbeobachtung](../reports/milestone-a-20261111/a1-first-native-damage-observation.json).
Die Rohrecords, privaten Guards mit Originalbytes und vollständigen Registry-
Pfade bleiben außerhalb des öffentlichen Repository. Weitere Proben erhalten
eigene Zeitfenster und dieselben Restore-/Post-Close-Gates.
