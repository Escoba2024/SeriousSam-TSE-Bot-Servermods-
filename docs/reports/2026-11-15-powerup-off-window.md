# Isolierter Filter-OFF-Kontrast: begrenzter Erfolg

Case `powerup-048-offon0-modulev2-root-redstation-20261115-064825`,
ResultSHA256 `6d1e17606f1abee35674df2e782a4520a7448021e6a79fbbf44821e7c16b06ff`.
600,1353s RedStation, bestehende Dedicatedfe4, acht048ExpertRifle/Tier5/Marksman,
Hard2, Original-Retailobserver20FPS, Diagnose0, Filterflag0. Keine Liveänderung.

Der Census vor Freigabe und am Ende bestätigt ein Unsichtbarkeits- und ein
Schadenspowerup, keines entfernt. Der neue erste ungebundene Rohread ist vor
Binding vollständig gesichert:1919B, SHA256
`8602146c5473557414e38c6a7eefe3e977d9f82a2a72c4cfdaeb672dae11aea1`,
korrekteServeridentität/fe4 und originaleEngine/Entities. Die zuvor fehlgeschlagene
Original-GameMP-Prüfung ist damit in einem echten Fall durchlaufen.

Alle vier Abschlusslogs:0SYNCBAD/0SyncDisconnect/0Crash/0InvalidAction/
0Joinfailure. Server1987SYNCOK. AchtBotaktivitätsprädikate erfüllt,63serverseitig
gemeldeteAbschüsse andererTeilnehmer. Der bestehende Reader berichtet80AILeben/
72beobachteteTode/69LebenmitbrauchbarerWaffe; keine vollständige Lebens-/A4-Abnahme.
13604gültige Rohstichproben,9079kanonischeGruppenstichproben,352fehlgeschlagene
Leseversuche bleiben unverändert gezählt; nichtatomare Zustände/zensierteLeben
werden nicht nachträglich geglättet. KeineWaffenfunktions-/Erstzustandsschadensbehauptung.

Vier reguläre Rollencloses und Rootrestore07:00:20UTC:640Dateien/4Logs,
Units/PIDs/Display/vierSperren geprüft. Rootwrapper1624637/Start135170285,
Exec86476 beendet/reaped0, keinAutoRetry. Outer685Samples:CPUmax64,05063%,
RAMmin2510659584B, Diskmin10363150336B, maximaleLücke1,00278s,
PASS_HOST_OBSERVATION_ONLY. InnerStartup-Lücke46,935s bleibt offen;
Gameplaylücke1,1633s. Daraus wird kein formales Ressourcen-/A5-Gate bestanden.

Ein begrenztes unbewegtesOriginalobserver-Szenario reproduziert den externen
Live-Syncfehler nicht. Flag0 ist damit nicht als allgemeine Lösung bewiesen.
Nächster fest geplanter Kontrast: dasselbe Paket/Profil mit Flag1 nach vollständiger
Sicherung/Restore, separat600s. Auch zwei passende kurze Fenster beweisen keine
CRC-Ursache, aktiveOriginalinputgleichheit, Dauerstabilität oder vollständigeA-Abnahme.
