# Weitere Sync-Gegenbelege im unveränderten Dev-Stand

Eine reine Logleseprüfung vom15.11.2026,02:49:28UTC erfasst den seit dem
archivierten Serverprefix vom14.11.,23:54:00UTC hinzugekommenen Abschnitt.
Das unveränderte Dev lädt weiterhin Cecil048 `ec820d04…` als Botclient und
separat die Dedicated-Powerupvariante `fe4a77bd…`. Kein neuer Rootkandidat wurde
dort ausgerollt. Die frische02:48-Abfrage und geladenen Module aller18Rollen
stimmen mit dem auf ausdrücklichen Nutzerwunsch beibehaltenen Mischstand überein.
Jede der sechs Instanzen hat acht eigene Bots; auf Yodeller war zusätzlich eine
ungeklärte Verbindung vorhanden, auf den anderen Instanzen keine.

| Gelesener Abschnitt | Neue BAD | Neue Sync-Disconnects | Neue SYNCOK |
|---|---:|---:|---:|
| Dev Dedicated,1440855Bytes |70|3|29055|
| eigener Dev-Botclient A,59850157Bytes |0|0|0|
| eigener Dev-Botclient B,58224238Bytes |0|0|0|

Die Server-BADs betreffen eine im Log benannte externe Verbindung; die drei
Disconnects und maximaler Zähler10 bleiben echte Gegenbefunde. Sie werden
keinem Nutzer zugeordnet. Die ursprünglichen Prefixhashes und Prozessgenerationen
wurden vor dem Lesen geprüft; feste Dateigrenzen, Inode und Prozessgenerationen
binden die neuen Abschnitte. Vollständige Deltaabschnitte sind privat verlustfrei
gzip-gesichert, sofort zurückdekomprimiert und gegen ihre SHA256 geprüft.
Keine Rohidentitäten stehen in diesem Bericht. Die Bots haben in diesem
Abschnitt keine eigenen Syncmeldungen; das erklärt die externen Abweichungen
nicht und bedeutet keinen allgemeinen Stabilitätspass.

Die Ursache bleibt unbekannt. Insbesondere sind weder Cecil048 noch der
Powerupfilter allein als Ursache bewiesen. Die [frühere Diagnose](2026-11-11-spawn-zero-sync-diagnosis.md)
trennt die Dedicatedvarianten und normalen Sessionwerte. Die bereits
[geschlossenen drei Originalserverfenster](2026-11-14-navigation-three-window-checkpoint.md)
enthalten für048/018/020 jeweils600s mit achtBots und Originalbeobachter ohne
neue Syncfehler; sie sind weder ein aktiver WAN-Originalinputtest noch eine
exakte Reproduktion der Dev-Powerupumgebung.

Kein Kickzähler, keine CRC-Prüfung, keine Liveidentität und kein laufender
Prozess wurde geändert. RootEV/dev-sync-after-025-private.json und drei
komprimierte Deltas enthalten die privaten Prüfpins. Ein kontrollierter
Vergleich muss die Serverbinary-/Input-/Joinbedingungen ausdrücklich binden;
ein erneutes unverändertes Originalserverfenster allein würde den neuen Befund
nicht erklären. A und die Syncursache bleiben offen.
