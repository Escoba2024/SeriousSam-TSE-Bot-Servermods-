# Eigene XRes-/RECORD-Lifecycleprobe begrenzt bestanden

Die einzige eigene inputfreie Probe auf :167 endete um00:43:39UTC mit
`PASS_OWN_XRES_RECORD_LIFECYCLE_ONLY`. Resultat-SHA256:
`1642b145796b2a87a352b65e0de136b08decaf04d13195514139f7c44ad72a4c`.
Kein TSE/Wine/Frida oder Input. Damit ist diese neue Diagnosemethode für den
nachfolgenden isolierten Originalclient-NoFire-Fork belegt, keine A1-Abnahme.

Zwei tatsächliche Snapshots im aktiven RECORDintervall, insgesamt elf korrekte
PIDqueries; zwei Clientlisten und elf IDarrays allokiert und freigegeben.
Der vollständige Rawstream enthält sechs Records: Start, echter ClientStarted,
ein eigener QueryPointer-Request und seine gebundene Antwort, ClientDied, End.
Der stabile Driver wird über Window, Sequenz, Replywerte, PID/Startgeneration
und beide Snapshots zugeordnet. Die neu gestartete und regulär geschlossene
Peerverbindung bleibt wegen ihrer Lifecyclegrenzen für Intervallattribution
UNKNOWN. Keine erzwungene Base-Reuse und keine Zuordnung historischer U.

Alle sechs Records freigegeben, keine Malformed-/Drop-/Native-/Cleanupfehler.
Vier reguläre Closes/reapedExit0, keine Force. Root wiederholte unabhängig die
vollständige reine Attributions- und Methodenauswertung, prüfte die abwesenden
Prozessgenerationen, Display167 und alle fünf wieder verfügbaren Sperren.
Methodenzeit0,336880s. Äußerer Hostbeobachter: zwei Proben/maxGap0,465291s,
CPU48,9011%, mindestens3528163328B RAM und9382002688B Datenträger;
Childreaped0/Quellhash nachher gleich/keine Signale oder Retries.
Nur `PASS_HOST_OBSERVATION_ONLY`, keine Gameplayressourcenabnahme.

Vorher Delta058 vollständig aus Drive zurückgelesen:
15026184B/SHA256
`1a7ee050a3354500b1f26e4526d29c9a15a80d72065f31d6de4152e3e0107bc8`,
Drive `1-5ZiNjz5KpzhXhkDhRu1YZqrfrYObuuK`.
1279 reguläre Dateien/179972503B zweimal auf Inhalt, Eigentum, Modus und
mtime_ns geprüft. Die temporäre Rekonstruktion wurde erst danach entfernt.
Dies war kein nativer Start einer vollständig restaurierten Produktionsflotte.
Neue Methodenlaufdaten benötigen das nächste private Delta.

## Geerbte Collector-Metadaten korrigiert

Die erste deaktivierte A1-Kopie erbte `collector/source-manifest.json` mit
`runtime_reviewed=True`, während die neue Collectorquelle und alle obersten
Ausführungsgates bereits False waren. Es wurde kein Collector damit gestartet.
Ein gezielter zusätzlicher Test reproduzierte den Widerspruch (zwei Tests,
ein tatsächlicher FAIL). Commit `13bb029` setzt bei der neuen Kopie auch dieses
Manifestflag explizit False. Danach zwei Tests PASS/0Skips/1,489s; keine
Worker-/Core-/Input-/Zeit-/Fingerprintänderung und keine Methodenwiederholung.
Frühere Pakete und FAILlogs bleiben unverändert erhalten.

Die neue qualifizierte, weiterhin deaktivierte A1-V2-Kopie hat Manifest
`4dd80ca6a514c580e16b91032d5b0b4794f09a3f453a2ae40afd9dc026bed7c3`.
Rootfreeze für genau einen NoFire-Diagnosefall:
`e9cb52a1135ea3046570fdaaac6e2f37ac2117535b8d4c312239f39d7cbec90c`;
fünf Ausführungsgates/private Pfade und exakte Repins,104Runtime-/84Diagnose-/
14Collectorpins. Alte passive Alternativadapter bleiben deaktiviert, Corebytes
unverändert. Die echte Methodenquittung und ihre Fingerprints werden verlangt.
Der Fall ist noch nicht gestartet; unabhängiges Deltareview und nächste
vollständige Sicherung sind vor dessen einmaligem Start erforderlich.

Skulls024 wurde separat für600s Hard/8DEMON+Original20FPS/diag0 eingefroren,
Manifest `8e25263c70991733829ec0e1099564a848dd0ce8560b257f550cf0e8be80fcee`.
Ein Gate/zwei Namespaces/Repins; kein nativer Kartenlauf oder Promotion.
A bleibt offen, B nicht begonnen, der gemischte Livebestand bleibt erhalten.
