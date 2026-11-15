# Build024 Skulls600: stabile Beobachtung, konkrete Versorgungslücke

Build024 schloss den isolierten Skulls-Fall mit 600,110787308 Sekunden
Beobachtung, acht DEMON-Bots, Hard2 und einem eigenen Originalclient bei20FPS.
Das technische Resultat bleibt
`PASS_LIMITED_A4_OBSERVATION_FUNCTIONAL_REVIEW_REQUIRED`. Es gibt **keine
funktionale Kartenfreigabe**: Slot0 blieb im letzten beobachteten Leben
242,490814 Sekunden ohne brauchbare Zusatzwaffe bis zum Fensterende.

## Exakte Bindung

- DLL: `192169fe8396bfe1fb9c49419657b9146120c64eb3ac15095ac50a6f8659753c`.
- Quellcommit: `100bda43eb46c7d671d71b7a50fae673a9e4406e` im Buildmanifest.
- Rootmanifest: `8e25263c70991733829ec0e1099564a848dd0ce8560b257f550cf0e8be80fcee`.
- Resultat: `b22aba0aa29eb8e16ec6ddc9121813ccaafc3ac8adace9731074802595ac7376`.
- Private Evidenz: `/srv/tse-milestone-a-evidence-20261111/nav20-024-skulls-root-skulls-20261115-010531`.

World/Navbindung, aktive Konfiguration und Rollen sind im tatsächlichen Fall
geprüft. Der Dedicated und der eigene Vanilla waren Originaldateien; die
Bot-DLL blieb auf die beiden eigenen Vierergruppen begrenzt. Kein Livewechsel.

## Vollständige Nenner und Gegenbefund

Die unveränderte geordnete V3-Lifeauswertung akzeptierte alle Rohgruppen und
14040 Leseversuche einschließlich 541 gespeicherter Fehlversuche. Sie zählt
192 beobachtete Leben,95 mit Usefulbesitz und113 tatsächliche beobachtete
Inventargewinne.96Leben sind linkszensiert,6rechtszensiert und4haben mehrdeutige
HP-Reihenfolgen. Alle acht Slots haben im Gesamtfenster Bewegungsaktionen,
Waffengewinne und native Fernfeuerflagproben. Die170 Serverabschusszeilen
sind kein Ersatz für die Einzelbetrachtung und kein direkter Buildvergleich.
Die Flagproben beweisen keine einzelnen ursprünglichen Waffenfunktionsaufrufe.

Slot0, Spawnclock358,1360778808594, wurde lebend von358,1860656738281 bis
600,6768798828125 ohne Usefulbit beobachtet. Der maximale Abstand dieser
Leseproben beträgt0,39990234375s. Das Leben ist links- und rechtszensiert;
eine lückenlose kontinuierliche Beobachtung wird nicht behauptet.
Der Bot bewegte sich zeitweise. Die242s dürfen deshalb nicht als absoluter
Stillstand bezeichnet werden. Die vollständige gebundene Source-/Routen- und
Recoveryanalyse bleibt separat offen. Beide geschlossenen Botlogs enthalten
keinen `CecilGroundReplan`-Marker. Die neue Stale-Anchor-Verzweigung ist hier
nicht nativ bewiesen.

## Schließen und Ressourcen

Alle vier Rollen schlossen regulär. Vier geschlossene Logs enthalten keine
neuen Ereignisse der sechs geprüften Sync-/Crash-/Action-/Joinfehlerklassen.
Root prüfte01:17:18UTC unabhängig640Dateien, vier Loghashes, Prozessgenerationen,
Units, Displayabwesenheit und freigegebene Sperren: `PASS_RESTORE`.
Geprüft sind Inhalt/UID/GID/Modus und Dateimengen, keine exakte Fixture-Mtime.

Der äußere Hostbeobachter schloss `PASS_HOST_OBSERVATION_ONLY`:683Proben,
maximale Lücke1,002483288s, CPUmaximum63,427110%, minimal verfügbarer RAM
2520137728Bytes, freier Datenträger9047359488Bytes, keine Budgetverletzung,
kein Signal/Retry, KindExit0 und Quellenhash nachher gleich vorher.
Das ersetzt weder formale Dauergates noch eine B-Kapazitätsqualifikation.

Nächste Schritte: Versorgungslücke kausal untersuchen, übrige Kartenfälle
getrennt beobachten, geschlossene Rohdaten extern alsDelta060 sichern.
A bleibt offen, B nicht begonnen. Live bleibt der bestätigte gemischte Stand.
