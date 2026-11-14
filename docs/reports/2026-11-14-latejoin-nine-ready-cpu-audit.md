# Spätjoin175329: CPU-FAIL, Verursacher nicht gemessen

Nur Read-only-Diagnose von geschlossenem Archiv/Quellen ab`a308756`.
Keine Runtime, Tests, Builds, Displays, Frida, Netz oder Code-/Gateänderung.
Root führt Navigationadapter und A1-Recorder getrennt weiter; hier nur dieser
neue Bericht. Keine reproduzierte portable Fehlfunktion rechtfertigt einen Fix.

Archiv`/srv/tse-milestone-a-evidence-20261111/own-latejoin018-nine-ready-root-20261114-175329`;
Result-SHA`0360a76e9e691ea501df8414e255f0a284ea69980c06735d476e39c68f8a00ac`.
Controllerquelle-SHA`0f0bc72c6c21bb834e49a3f2517666dc8da4acac4313796a467ed1d597847509`.
Der Lauf bleibt FAIL:77,2839506%>75%. Capture meldet folgerichtig keinen
abgeschlossenen600s-Bereich. Erfolgreiche0,498948s-Admission mit zwei vollen
progressiven Neunerrunden und gespeicherten Originalreads ist ein getrennter
Teilbeleg. Vier normale Closes/640Dateien+4Closedlogs-RestorePASS sind Rootbelege.

## Tatsächliche Zeit-/Lastdaten

48Hostproben über49,907581s einschließlich Startup;12Gameplayproben nach
Postjoinstart1305246,278731488. Letzte Probe1305257,848047942, also11,569316s
nach diesem Start. Gameplay-CPUwerte:75,00;67,49;70,44;49,87;51,33;53,02;
51,34;54,61;53,73;53,62;62,88;77,28%. Ein später Spike ist belegt, kein
über das ganze Fenster konstant überlasteter Controller.

124Sessionzeilen bis11,548395s,372Inventarversuche/363Erfolge/9Changed-
Discards. Gemessene gesamte Reader-Wallzeit1,781773s, Maximum11,234ms je
Versuch; maximaler Gameplay-Samplegap0,177304s. Readerzeit ist realer
Controlleraufwand, aber **keine gemessene CPUzeit** und keine alleinige
Ursache des letzten Hostspikes. Die ersten2s haben den bestehenden kürzeren
Sleep0,015 statt0,1s; auch das ist kein neuer Defekt des Readinessfixes.

Letztes globales Diskfree-Delta41.717.760Bytes in1,047894s, davor7.405.568Bytes.
Gesamte am Ende vorhandene reguläre Archivdateien einschließlich Restore- und
Closedlogs:8.342.322Bytes; PCAP887.539Bytes/2548Pakete/0Drops, Inventory
1.515.724Bytes, Session1.140.299Bytes, finale Botlogs zusammen448.898Bytes.
Diese Endgrößen erklären den globalen Diskfree-Sprung nicht. Sie sind aber
kein Write-/Block-/temporärer Dateiallokationszähler und schließen eigene
Wine-/Labdateien, andere Prozesse oder temporäre Schreiblast nicht aus.

## Quellenprüfung der vermuteten Lasttreiber

Pfadpräfix der eingefrorenen Quellen:
`/srv/tse-owned-sync018-latejoin-nine-ready-root-frozen-20261114/`.

| Quelle/Zeilen | Belegter Aufwand; Grenze der Aussage |
|---|---|
|`strict_backend.py:75–85`,`:87–91`|Volle DLL-SHA beim ursprünglichen pin_modules; verify_modules im laufenden Guard prüft PID/maps/Dateisignatur, **keine Vollhashes jede1s**. Drei DLLstat-/Mappingprüfungen je Rolle bleiben.|
|`run-a4.py:242–248`, Backend`:13–20`,`:67–74`|Je1s vier eigene systemctl-Identitysubprozesse und Mapping-/Namespacechecks, eine nsenter/iproute-Prüfung; je2s eigener Python-Querychild. Keine Dauerstatistik ihrer CPU-/Startkosten gespeichert.|
|`owned_sync_capture.py:70–103`,`:235–246`|Jeder Captureguard liest bei vier Rollen insgesamt acht FDlisten, vier IPv4- und vier IPv6-Netztabellen samt PID/CWD/cgroup/NSguards. Keine systemweite PIDsuche in diesem Pfad; zusätzliche Captureguardkosten sind plausibel, aber ungemessen.|
|`strict_backend.py:35–66`|Globale Quieszenzsuche gehört zu Startup/Cleanup/privatem Prestart, nicht in den gewöhnlichen1s-Gameplayguard.|
|`run-a4.py:54–64`,`:207–231`|JeHostprobe werden Hosthistorie und Gesamtresultat neu serialisiert/geschrieben, Inventar/Session/Attemptstreams fortlaufend geflusht. Reale IO-/JSONarbeit, keine gespeicherten Kosten-/Writezähler; kein aus den Quellen erkennbarer plötzlicher40MB-Anhang.|

Der externe gepinnte Reader
`/srv/tse-milestone-a-20261111/tools/retail_inventory_readonly.py:154–165`
hasht nur beim Pinaufbau; check_file prüft anschließend die Signatur.
`:233–270` liest/mapsprüft vor/nach jedem Sample und führt die passiven
zweifachen Speicherreads aus. Sessionreader
`/srv/tse-milestone-a-evidence-20261111/session-readonly.py:6–10` cached den
Enginehash anhand der Dateisignatur; kein Enginevollhash pro Snapshot.

## Fehlender entscheidender Beleg

Nur controller_usage_start ist gespeichert:2,149185user/2,168223system-Sekunden
kumuliert vorGameplay. Endwerte und eigene Rollen-Usage-Endwerte fehlen,
weil`run-a4.py:255–258` erst nach erfolgreichem600s-Ende erreicht wird.
Es fehlen zeitgebundene PID-/Child-CPU-/IOdelta und guard-/save-/reader-
Einzelkosten für das letzte1,048s-Intervall. Hostprozentsatz und Diskfree
allein erlauben keine Prozess- oder Funktionsattribution.

Die bestehenden Grenzen bleiben unverändert. Keine Guardauslassung,
Hash-/FD-/Namespaceausnahme, geringere Samplerate oder automatische
Wiederholung aus dieser Diagnose ableiten. Kleinster weiterer Beleg wäre
nach eigenem Rootplan ein begrenzter passiver Kosten-/CPU-/IOledger der
bereits eigenen Controller-/Child-/Rollenidentitäten einschließlich
Fehlerfinally, mit unveränderten Gates und ohne Gameplayhook. Zuerst vorhandene
Rootzeitbelege auf parallele eigene Arbeit prüfen; deren Abwesenheit hier
ist kein Beweis, dass fremde oder eigene Nebenlast ausgeschlossen war.
