# Filter-ON: vollständiges Beobachtungsfenster, Abschlussprüfung fehlgeschlagen

Case `powerup-048-offon1-modulev2-root-redstation-20261115-071200`, ResultSHA256
`f4ef09e27abb4e4fa00cb1020d4c7c5faa236723d9e3d8a132cc0f6e54356ded`.
600,0495s RedStation/Hard2, acht048ExpertRifle/Tier5/Marksman,
Originalobserver20FPS/Diagnose0, bestehende Dedicatedfe4 mit Filterflag1.
Der Census vor Freigabe und am Ende belegt zwei entfernte Powerups
(Unsichtbarkeit/Schaden); bei OFF blieben dieselben Typen vorhanden.
Keine Liveänderung. Kein CRC-Ursachenbeleg.

**Gesamtergebnis FAIL**, kein erfolgreicher ON-Abschluss: Im Servercleanup trat
`FileNotFoundError` auf; anschließend fehlte die normale Closeattestierung.
Drei vollständige Bot-/Original-Abschlusslogs sind fehlerfrei archiviert.
Das Serverfinal-Log wurde ausdrücklich VOR dem Close kopiert: 2158SYNCOK,
0SYNCBAD/0Sync-Disconnect; SHA256
`d4a1a050e5c0956063fde413f004c4e968bc6f24fa97cbf63e58fe583db86600`.
Ein Server-Abschlusslog darf daraus nicht konstruiert werden. Die vier Rollen
meldeten im vollständigen Beobachtungsfenster jeweils 0BAD/0Sync-Disconnect.
Systemd meldete den Serverprozess um07:23:17 erfolgreich beendet; die genaue
fehlerwerfende Dateizugriffsstelle ist mangels Traceback noch nicht bewiesen.
Ein Procfs-/Cgroup-Exit-Rennen ist eine zu prüfende Hypothese.

Root prüfte um07:26:02 alle vier Rollen/Units/Präfixe auf Quieszenz, 640Dateien
mit Hash und Eigentümer/Gruppe/Mode sowie vier exklusive Sperren: PASS_RESTORE.
Das wegen fehlender Closeattestierung verbliebene eigene Display154
(PID1630404/Start135312151, exakte Cmdline/Unit geprüft) wurde erst danach
gezielt mit SIGTERM beendet. Fremde Displays blieben unberührt. Parent1630386/
Start135311871 und Exec16732 sind beendet/reaped1; kein Retry oder Folgejob.
Die ursprünglichen Result-/Cleanupfehler bleiben unverändert.

Erhaltene Auswertung: alle acht Aktivitätsprädikate, 70serverseitige Fremdkillzeilen,
86AILeben/70mitbrauchbarerWaffe/79beobachteteTode; 13593Rohstichproben,
9060kanonischeGruppenstichproben,390fehlgeschlagene Leseversuche. Nichtatomare
Reads und zensierte Leben bleiben sichtbar. Erster ungebundener Serverread:
1922B/Mode0600, SHA256
`7a83f0a934045d73b31d893413d712eea63c209d48541432aee78485bbfe15e4`,
exakte Server-PID-/Modulbindung vor der Folgeverarbeitung. Keine erneute volle
Frameauswertung, keine Waffenfunktions-/A4-/Erstzustandsschadensabnahme.

Outer681Samples: CPUmax64,05063%, RAMmin2500562944B,
Diskmin10134179840B, Maxlücke1,00348s. Wegen Childexit1 bleibt Outer FAIL.
InnerStartup-Lücke46,0596s, Gameplaylücke1,2669s: kein formales A5-Ressourcengate.
Der Originalobserver erhielt keine Gameplayeingaben und blieb nach seinem Tod
passiv. Beide kurzen Filterfenster erklären den früheren aktiven externen
Live-Syncfehler nicht. Keine allgemeine Filterfreigabe, keine erneute Liveverteilung.

Nächste Arbeit: Abschluss-/Cgroup-Rennen eng reproduzieren und beheben, ohne
alte FAILs umzuwerten; A1-Methodenmonitor mit autonomem begrenztem Drain und
A3/A4-Endaktionsdiagnose isoliert fertigstellen. A bleibt offen, B nicht begonnen.
