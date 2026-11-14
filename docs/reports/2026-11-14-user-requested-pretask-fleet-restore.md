# Auf Nutzerwunsch ursprüngliche Botstände wiederhergestellt

Am14.11.2026 verlangte der Nutzer die Botlogik von vor diesem Codex-Auftrag
auf Dev und allen öffentlichen Servern zurück. Weitere Entwicklung ist
weiterhin beauftragt; erneut ausrollen erst bei belegten Verbesserungen.
Die frühere Anweisung zum initialen Cecil-Rollout bleibt historisch erfüllt
und wird nach dieser neuen Steuerung nicht erneut angewendet.

Root prüfte vor jeder Änderung die sechs tatsächlichen Prozessgenerationen,
geladenen Module und die gesicherten ursprünglichen DLL-/Config-/Navdateien
einschließlich Modus/Eigentümer. Dev, Red Station und Yodeller entsprachen
bereits exakt dem Sicherungsstand, daher kein Neustart. Skulls, Trouble und
Hole wurden unter bestehenden exklusiven Deploysperren nacheinander mit
normalen eigenen Botcloses zurückgestellt. Ihr bisheriger018-Payload wurde
vorher separat gesichert und anhand rekonstruierter Dateihashes/Metadaten
geprüft. Alle Dedicated-Prozesse, Maps, aktuellen Regeln und Teilnehmerdaten
blieben unverändert; Namen und GUIDdateien separat identisch geprüft.

Um17:12:46UTC luden alle zwölf Botprozesse nachweislich die vor diesem
Auftrag gesicherten DLLs und zugehörigen ursprünglichen Konfigurationen/
Navdateien. Ein zusätzlicher Dev-Teilnehmer blieb verbunden; keine Aussage
über seine Identität allein aus früheren Nutzerangaben.

| Server | Port | Map | Botstand / SHA256-Präfix | Eigene Bots | Zusätzliche Teilnehmer |
|---|---:|---|---|---:|---:|
| Dev |25650|Red Station|Cecil048 / ec820d04|8|1|
| Red Station |25600|Red Station|Gen2 / 7fc94a39|8|0|
| Yodeller |25610|Yodeller|Gen2 / 7fc94a39|8|0|
| Skulls’n’Bones |25620|We Got Skulls'n'Bones Too|Gen2 / 7fc94a39|8|0|
| Little Trouble |25630|Little Trouble|Gen2 / 7fc94a39|8|0|
| Hole |25640|Hole|Gen2 / 7fc94a39|8|0|

Anschließende rein lesende gemeinsame Beobachtung:92,8206s, je37 gültige
Queries. Jeder der48 eigenen Slots bewegte sich nachweislich innerhalb
desselben Lebens mehr als1m. Auf allen sechs Maps wurden weitere eigene
Fragzuwächse, Gesundheitsverluste, tote Zustände und Respawnwechsel beobachtet.
Alle18 Server-/Botlogpräfixe wurden separat hashgebunden; im neuen Fenster
null BAD/Syncdisconnect/Crash/InvalidAction/Join-/CRC-Ereignisse. CPUspitze
48,9011%, verfügbarer RAM mindestens3491651584B, freier Datenträger mindestens
9985638400B. Begrenzter Betriebsbeleg, keine Ursachenbehebung, Langzeit- oder
A-/B-Abnahme. Individuelle Sessions und Botchat noch nicht implementiert.

Die Nutzerbeobachtung möglicher schlechterer Bewegung/Navigation beziehungsweise
Festhängens im neueren Stand ist ausdrücklich subjektiv und noch keine
bestätigte Regression. Der folgende kontrollierte Vergleich soll Stillstand,
Recovery, Weg zur brauchbaren Waffe und Kampf getrennt prüfen. Der historische
[018-Killvergleich](2026-11-12-build018-six-window-comparison.md) gegen Gen2
ersetzt keinen Navigationsvergleich gegen die bisherige Dev-Cecil048-Logik.
Keine erneute018-/020-Promotion allein aufgrund einer Buildnummer oder der
kurzen109:33-Killbilanz.

Private Quittungen liegen unter RootEV/user-pretask-restore-ended.json und
dem darin gebundenen Run mit sechs result-private.json sowie gemeinsamen
postrestore-result.json/postrestore-samples-private.json. Laufende Prozesse,
DLL-/Startkonfigurationspins und Identitätserhalt sind dort nachvollziehbar.
