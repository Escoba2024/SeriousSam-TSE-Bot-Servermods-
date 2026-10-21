# MASTER GOAL – ALPHA-GAMING / SERIOUS SAM TSE CLASSIC 1.07
# Datum: 21.10.2026
# Priorität: P0 – Integration, CPU-Optimierung, Bot-KI und Runtime-Abnahme
# Arbeitsmodus: Autonome End-to-End-Ausführung
# Infrastruktur: Ausschließlich Hetzner
# Rolle: Technischer Hauptagent und Integrationsverantwortlicher

====================================================================
1. HAUPTAUFTRAG UND ERFOLGSKRITERIEN
====================================================================

Du übernimmst die technische Verantwortung für die weitere
Fertigstellung des Projekts:

Alpha-Gaming – Serious Sam The Second Encounter Classic 1.07

GitHub-Repository:
https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-

Hetzner-Server:
91.99.75.33

Das System besitzt bereits eine grundsätzlich funktionierende
Multiplayer-Architektur mit echten Bot-Clients.

Das bisher erreichte Fundament darf nicht gefährdet werden.

DEIN HAUPTZIEL:

Führe die vorhandenen CPU-Optimierungen, die neue Bot-KI,
die Telemetrie und die bestehende Multiplayer-Architektur
zu einer nachweislich funktionierenden Gesamtlösung zusammen.

Die fertige Lösung muss:

1. Unter Serious Sam TSE Classic Retail 1.07 funktionieren.
2. Mit unveränderten Original-Clients kompatibel bleiben.
3. Ausschließlich auf dem Hetzner-Server entwickelt und
   betrieben werden.
4. Ohne Shadow-PC auskommen.
5. Acht oder mehr gleichzeitig aktive Bots unterstützen.
6. Die optimierte CPU-Nutzung nachweislich verwenden.
7. Fünf KI-Fähigkeitsstufen unterstützen.
8. Sechs unterschiedliche Bot-Persönlichkeiten unterstützen.
9. Natürliches, menschlich wirkendes Bot-Verhalten erzeugen.
10. Einen stabilen öffentlichen Multiplayer-Server ermöglichen.
11. Mindestens 60 Minuten unter realistischen Bedingungen
    ohne kritische Synchronisationsfehler laufen.
12. Reproduzierbare Messwerte, Logs und Testnachweise liefern.

Erst wenn diese Eigenschaften nachgewiesen sind, darf die
vollständige technische Abnahme als bestanden gelten.

Ein erfolgreicher Offline-Test, ein funktionierender Compiler
oder ein abgeschlossener GitHub-Pull-Request allein reichen
ausdrücklich NICHT aus.

====================================================================
2. ARBEITSGRUNDSÄTZE
====================================================================

Arbeite eigenständig und zielorientiert.

Erstelle keine zusätzlichen Agenten, solange die bestehende
Hauptagenten-Struktur ausreicht.

Keine unnötigen Zwischenfreigaben.

Keine künstlichen A00-CLAIM/GRANTED-Warteschleifen.

Kein Shadow-PC.

Keine nicht erforderlichen Installationen oder externen Dienste.

Nutze die bestehende Hetzner-Infrastruktur und bereits
installierte Entwicklungswerkzeuge.

Nutze nach tatsächlicher Verfügbarkeit:

- Superpowers: using-superpowers
- Superpowers: writing-plans
- Superpowers: executing-plans
- Superpowers: systematic-debugging
- Superpowers: test-driven-development
- Superpowers: verification-before-completion
- GitHub
- Remote Desktop Commander
- Git
- Microsoft Build Tools unter Wine
- Windows SDK
- Python
- CMake/Make, soweit im Projekt vorhanden
- vorhandene Benchmark- und Telemetrieprogramme

Beachte:

Bestehende produktive Dateien und Dienste schützen.

Bestehende laufende CPU-Messungen nicht unkoordiniert
unterbrechen oder durch zusätzliche Last verfälschen.

Bei Konflikten zwischen CPU-Benchmark, Build und
Multiplayer-Test die Arbeiten sinnvoll nacheinander
ausführen.

Keine unkontrollierten parallelen Laufzeittests.

Keine Überschreibungen fremder Änderungen.

Keine destruktiven Aktionen außerhalb eindeutig
zugeordneter Testumgebungen.

Keine neue Lizenzannahme, kostenpflichtige Bestellung oder
sonstige rechtlich erforderliche Freigabe ohne Zustimmung.

Bei Fehlern zuerst Ursache diagnostizieren, anschließend
gezielt beheben und reproduzierbar erneut testen.

====================================================================
3. AUSGANGSSTAND VERIFIZIEREN
====================================================================

Vor Änderungen ist der tatsächliche Stand direkt auf
GitHub und Hetzner erneut zu prüfen.

Bekannter Ausgangsstand:

PR #41:
CPU-Benchmark, Hetzner-Testumgebung und Messprotokoll.
Mehrere Messfenster laufen beziehungsweise waren zuletzt
noch nicht abschließend ausgewertet.

PR #42:
CPU-Analyse, BotDriver-Diagnostik und optionale
KI-Throttling-Optimierungen.
Neun statische Tests bestanden.
Noch keine vollständig qualifizierte Runtime-Integration.

PR #43:
Telemetrie, Null-Render-Kandidat und Messwerkzeuge.
65 portable Tests bestanden.
Der PR wurde nach letzter GitHub-Prüfung bereits in
main gemergt.
Bekannter CSV-Fehler: 22 Formatangaben für 21 Werte.

PR #44:
Neue Human-Bot-KI.
Fünf Fähigkeitsstufen.
Sechs Persönlichkeiten.
555 KI-Checks bestanden.
Integrations-Smoke bestanden.
Noch kein vollständig qualifizierter MSVC-Build.
Noch keine erfolgreiche Runtime-Abnahme.
KI noch nicht produktiv aktiv.

Wichtige Ausgangsinformationen:

- Microsoft-Toolchain wurde laut aktuellem Hetzner-Bericht
  unter Wine installiert und erfolgreich getestet.
- Der genaue Build-Status muss erneut geprüft werden.
- PR #42 und PR #44 enthalten kollidierende Änderungen
  beziehungsweise Patch-Bezeichnungen.
- Der bestehende qualifizierte GameMP-DLL-Kandidat muss
  als unveränderte Rollback-Version erhalten bleiben.
- Der öffentliche Server mit acht Bots wurde für
  CPU-Messungen kontrolliert beendet.

VERIFIZIERE:

- Status und Commits sämtlicher Pull Requests
- main-HEAD
- offene lokale Änderungen
- vorhandene Worktrees
- tatsächlich installierte Toolchain
- Wine-Konfiguration
- Build-Skripte
- DLL-Versionen und SHA256-Hashes
- aktive Prozesse und laufende Messungen
- CPU- und RAM-Auslastung
- vorhandene Logs
- GitHub-Issues
- bestehende Pläne und technische Handoffs

Erstelle anhand der Ergebnisse einen persistenten
Ausführungsplan mit Abnahmekriterien.

Verwende die bestehenden Planungsdateien, wenn möglich.

Keine bereits erledigten Arbeiten unnötig wiederholen.

====================================================================
4. PHASE A – BESTEHENDE CPU-MESSUNG ABSCHLIESSEN
====================================================================

PRIORITÄT: SEHR HOCH

Prüfe zunächst, ob der CPU-Benchmark aus PR #41
noch läuft.

Falls ja:

- Prozesszustand prüfen.
- Fortschritt anhand der Logs prüfen.
- Keine konkurrierenden Lasttests starten.
- Messung regulär abschließen lassen.
- Bereits abgeschlossene Messfenster sichern.

Falls der Benchmark beendet oder abgebrochen wurde:

- Vorhandene Ergebnisse auswerten.
- Ursache eines möglichen Abbruchs feststellen.
- Nur fehlende oder ungültige Messungen wiederholen.

Verwende soweit vorgesehen das bestehende Protokoll:

3 Wiederholungen je Variante
180 Sekunden Warm-up
600 Sekunden Messdauer

Vergleiche:

A: Bestehender Renderer beziehungsweise Baseline
B: Optimierter Null-Render-Modus

Achte insbesondere auf:

- tatsächliche Bot-Ticks
- Bot-Aktionen
- aktive Bot-Slots
- CPU-Zeit je Prozess
- CPU-Gesamtverbrauch
- RAM-Verbrauch
- Linux-cgroup-Throttling
- Host-Sättigung
- Timer-Stabilität
- Frame- beziehungsweise Tickfrequenz
- Synchronisationsfehler
- überlappende Messfenster
- Render-Modus und tatsächliche DLL-Identität

Prüfe zwingend, ob die Bots während der Messungen
tatsächlich aktiv waren.

Eine geringe CPU-Auslastung zählt nicht als Optimierung,
wenn die Bot-Logik nicht ausgeführt wurde.

Nutze die vorhandenen Aktivitätskriterien aus PR #43,
insbesondere ungefähr 20 Hz sowie die dokumentierten
Mindestwerte für Ticks und Aktionen.

Erstelle eine nachvollziehbare CPU-Baseline.

ERGEBNIS:

Belastbare CPU-Verbrauchswerte für die bisherige
Bot-Architektur sowie eine Bewertung des Null-Render-Modus.

Falls eine Messung durch Ressourcenbegrenzung oder
fehlende Aktivität ungültig ist, kennzeichne sie als
nicht qualifiziert und verwende sie nicht als
Optimierungsnachweis.

====================================================================
5. PHASE B – TELEMETRIEFEHLER AUS PR #43 BEHEBEN
====================================================================

PRIORITÄT: P0

Prüfe zuerst, welche Änderungen aus PR #43 bereits
in main enthalten sind.

Verhindere eine doppelte Anwendung des Pull Requests.

Behebe den bekannten Fehler:

22 CSV-Formatangaben bei 21 übergebenen Werten.

Prüfe nicht nur die Anzahl der Formatangaben, sondern
auch die vollständige Zuordnung:

- Feldnamen
- Feldtypen
- Werte
- Reihenfolge
- Header
- Datensätze
- CSV-Escaping
- Zeilenabschluss
- Datenvalidierung

Prüfe, ob die vorhandenen Python-Telemetrieparser
die tatsächlich erzeugten Daten korrekt lesen können.

Führe Regressionstests aus.

Erweitere die Tests bei Bedarf um einen reproduzierbaren
Test speziell für diesen Formatfehler.

ABSCHLUSSKRITERIUM:

Die Telemetrie erzeugt vollständig korrekte CSV-Dateien.

Alle erforderlichen Felder sind vorhanden.

Der Parser liest die Werte fehlerfrei ein.

Es entstehen keine stillen Datenverschiebungen oder
falschen Messergebnisse.

====================================================================
6. PHASE C – KONFLIKTE ZWISCHEN PR #42 UND #44 AUFLÖSEN
====================================================================

PRIORITÄT: P0

Die Änderungen aus PR #42 und PR #44 können nicht
ungeprüft hintereinander angewendet werden.

Analysiere sämtliche betroffenen Dateien.

Besonders:

- BotDriver.cpp
- Game.cpp
- BotTelemetry.h
- vorhandene KI-Helferklassen
- Build-Konfiguration
- Patch-Skripte
- Konfigurationsprofile

Untersuche die unterschiedlichen Patch-Versionen
einschließlich der mehrfach verwendeten Patchnummer 0008.

Verwende einen isolierten Integrationsbranch.

Erstelle eine konfliktfreie Gesamtimplementierung.

WICHTIG:

Keine der folgenden Funktionen darf durch die
Zusammenführung verloren gehen:

1. Bestehender Vanilla-kompatibler Multiplayer-Betrieb.
2. Bisherige Botsteuerung.
3. BotDriver-Tick-Verarbeitung.
4. Telemetrie und Diagnostik.
5. CPU-Optimierungen.
6. Null-Render-Funktion.
7. Neue Bot-KI.
8. Konfigurierbare Feature-Flags.
9. Bestehende Synchronisationslogik.
10. Sichere Rückfallmöglichkeit auf bisheriges Verhalten.

Prüfe insbesondere:

- doppelte Funktionen
- doppelte Symbole
- widersprüchliche Includes
- unterschiedliche Funktionssignaturen
- konkurrierende Timer
- konkurrierende KI-Updates
- veränderte Lock-Reihenfolgen
- Thread-Safety
- Speicherzugriffe
- Versionsabhängigkeiten

Stelle sicher, dass CPU-Optimierungen die neue
Bot-KI nicht unbeabsichtigt deaktivieren.

Die zusammengeführten Änderungen müssen
gemeinsam kompiliert und getestet werden können.

====================================================================
7. PHASE D – CPU-OPTIMIERUNG IMPLEMENTIEREN
====================================================================

PRIORITÄT: P0

Integriere die nach den Messungen technisch
gerechtfertigten Optimierungen aus PR #42 und #43.

Ziel ist eine möglichst niedrige CPU-Auslastung
bei vollständig aktiven Bots.

Untersuche und optimiere insbesondere:

RENDERING:

- Null-Render-Modus
- unnötige GameRedrawView-Aufrufe
- SwapBuffers
- Direct3D/OpenGL-bezogene Renderarbeit
- verdeckte Fenster
- minimierte Fenster
- Render- versus Simulationsthreads

KI-BERECHNUNGEN:

- Zielfindung
- Scanning
- Distanzberechnung
- Sichtlinienprüfungen
- Raycasts
- Hinderniserkennung
- Waffenwahl
- Navigationsentscheidungen
- Wiederholungsberechnungen

ZEITSTEUERUNG:

- Bot-Tickrate
- KI-Entscheidungsintervalle
- getrennte Bewegungs- und Entscheidungsupdates
- Timerauslastung
- unnötige Polling-Schleifen

ARCHITEKTUR:

Prüfe, welche Komponenten tatsächlich einen
vollständigen grafischen Client benötigen.

Bevorzuge technisch sichere Optimierungen der
bestehenden Clientarchitektur.

Bewerte alternative Headless- oder BotHost-Architekturen,
ohne einen vollständigen Architekturumbau zur
Voraussetzung dieses Auftrags zu machen.

WICHTIG:

Headless darf nicht bedeuten, dass Bots keine
Spielsimulation mehr ausführen.

Bewegung, Aktionen, Multiplayer-Synchronisierung
und KI müssen weiter funktionieren.

Vermeide Optimierungen, die lediglich Last auf andere
Prozesse verlagern oder die Bot-Aktivität reduzieren.

Implementiere Optimierungen schrittweise.

Führe für jede relevante Änderung gezielte Tests durch.

Miss die tatsächliche Einsparung gegenüber einer
vergleichbaren Baseline.

Dokumentiere Verbesserungen und mögliche Nachteile.

====================================================================
8. PHASE E – NEUE BOT-KI VOLLSTÄNDIG INTEGRIEREN
====================================================================

PRIORITÄT: P0

Übernimm die neue KI-Architektur aus PR #44.

Diese orientiert sich an CecilBot und vergleichbaren
klassischen Shooter-Bots.

Ziel sind Bots, die sich hinsichtlich Fähigkeiten,
Entscheidungen und Fehlern wie unterschiedlich gute
menschliche Spieler verhalten.

VORHANDENE KOMPONENTEN:

- bot_profile.h
- bot_perception.h
- bot_aim.h
- bot_loadout.h
- bot_human.h
- Human-AI-Integrationspatch

Prüfe zunächst die tatsächlichen Funktionen
und Schnittstellen dieser Module.

Erhalte die vorhandene getestete Logik.

Erweitere sie nur dort, wo für die Runtime-Integration
tatsächlich erforderlich.

--------------------------------------------------
8.1 FÜNF FÄHIGKEITSSTUFEN
--------------------------------------------------

Unterstütze mindestens fünf unterscheidbare
Spielstärken.

Beispielhafte Zielcharakteristik:

Stufe 1 – Anfänger:
Langsame Reaktion, ungenaues Zielen, häufige Fehler.

Stufe 2 – Gelegenheitsspieler:
Mäßige Genauigkeit, einfache Entscheidungen.

Stufe 3 – Durchschnittsspieler:
Ausgewogenes Verhalten und glaubwürdige Trefferquote.

Stufe 4 – Fortgeschrittener Spieler:
Gute Reaktion, bessere Bewegung und Waffenwahl.

Stufe 5 – Experte:
Schnelle Reaktionen, gutes Aim und taktisch
überlegene Entscheidungen.

Die Unterschiede müssen messbar und im Spiel
erkennbar sein.

Verhindere unrealistische Eigenschaften:

- sofortige Zielerfassung
- perfekte Dauerverfolgung
- unbegrenztes Sichtfeld
- Wallhack-Verhalten
- unmenschliche Reaktionszeiten
- vollkommen fehlerfreies Zielen

--------------------------------------------------
8.2 SECHS PERSÖNLICHKEITEN
--------------------------------------------------

Nutze die sechs tatsächlich implementierten Profile
aus PR #44.

Prüfe ihre Definitionen und Charakteristika.

Die Persönlichkeiten sollen sich beispielsweise
in folgenden Eigenschaften unterscheiden:

- Aggressivität
- Risikobereitschaft
- Distanzverhalten
- Waffenpräferenz
- Zielwechsel
- Rückzugsverhalten
- Verfolgungsverhalten
- Positionswahl

Keine sechs Namen für identisches Verhalten.

Die Unterschiede müssen das Bot-Verhalten
tatsächlich beeinflussen.

--------------------------------------------------
8.3 MENSCHLICHE WAHRNEHMUNG
--------------------------------------------------

Verwende:

- begrenztes Sichtfeld
- Sichtlinienprüfung
- verzögerte Gegnererfassung
- zeitlich begrenztes Gegnergedächtnis
- realistische Zielwechsel
- kontrolliertes Suchverhalten

Ein Bot darf einen verdeckten Gegner nicht dauerhaft
durch Wände exakt verfolgen.

--------------------------------------------------
8.4 MENSCHLICHES ZIELVERHALTEN
--------------------------------------------------

Integriere:

- begrenzte Drehgeschwindigkeit
- begrenzte Drehbeschleunigung
- Zielkorrekturen
- zufällige, aber kontrollierte Ungenauigkeit
- mögliches Überschwingen
- Reaktionsverzögerung
- situationsabhängige Schussfreigabe

Das Verhalten muss reproduzierbar testbar bleiben.

Nutze deterministische Seeds für automatisierte Tests.

--------------------------------------------------
8.5 WAFFENWAHL
--------------------------------------------------

Berücksichtige:

- Entfernung
- Munitionsvorrat
- aktuelle Bedrohung
- Persönlichkeit
- Skilllevel
- Waffenwechselzeiten

Verhindere dauerhaftes hektisches Waffenwechseln.

--------------------------------------------------
8.6 AKTIVIERUNG
--------------------------------------------------

Die neue KI muss tatsächlich über den
BotDriver ausgeführt werden.

Prüfe das vorhandene Feature-Flag:

bot_bHumanAI

Ermittle seine tatsächliche Laufzeitsemantik.

Die bisherige KI muss während der Integrationsphase
als Rückfalloption verfügbar bleiben.

Nach erfolgreicher Validierung muss die neue
KI für die vorgesehenen Produktivbots ausdrücklich
aktiviert werden.

Eine bloß vorhandene KI-Datei gilt NICHT
als erfolgreiche Integration.

====================================================================
9. PHASE F – VOLLSTÄNDIGEN WINDOWS-DLL-BUILD DURCHFÜHREN
====================================================================

PRIORITÄT: P0

Nutze die bereits installierte Microsoft-Toolchain
auf Hetzner unter Wine.

Prüfe:

- MSVC-Compiler
- Windows SDK
- MSBuild
- erforderliche SDK-Versionen
- Include-Pfade
- Linker
- x86-Zielarchitektur
- Retail-1.07-Kompatibilität

Baue die vollständige integrierte GameMP.dll.

Verwende die projektseitig vorgesehene
Release_TSE107/Win32-Konfiguration, sofern
dies der aktuelle gültige Buildpfad ist.

Behebe alle relevanten Compiler- und Linkerfehler.

Keine ungeprüften Workarounds.

Keine Veränderung kritischer ABI- oder
Retail-Kompatibilitätseigenschaften ohne
nachfolgende Runtime-Prüfung.

Erstelle SHA256-Hashes der Build-Artefakte.

Dokumentiere:

- Commit-SHA
- Compiler-Version
- Build-Konfiguration
- Build-Befehl
- Ergebnis
- Artefakt-Hash

Erhalte die bisherige qualifizierte DLL
als unveränderte Rollback-Version.

ABSCHLUSSKRITERIUM:

Ein reproduzierbarer vollständiger Build
der integrierten GameMP.dll ist erfolgreich.

====================================================================
10. PHASE G – GESTUFTE RUNTIME-TESTS
====================================================================

PRIORITÄT: P0

Starte zunächst eine isolierte Testumgebung
auf Hetzner.

Den öffentlichen Produktivserver noch nicht ersetzen.

--------------------------------------------------
TEST 1 – EIN BOT
--------------------------------------------------

Ein Bot verbindet sich erfolgreich.

Prüfe:

- Join
- CRC
- aktiven BotDriver
- Tickrate
- Bewegung
- Schüsse
- Gegnererkennung
- Waffenwechsel
- KI-Aktivierung
- keine sofortigen Sync-Fehler

--------------------------------------------------
TEST 2 – VIER BOTS
--------------------------------------------------

Vier Bots gleichzeitig.

Prüfe:

- gleichzeitige KI-Ausführung
- gegenseitige Erkennung
- Bewegung
- Kampfhandlungen
- unterschiedliche Skillprofile
- unterschiedliche Persönlichkeiten
- Telemetrie
- CPU und RAM

--------------------------------------------------
TEST 3 – ACHT BOTS
--------------------------------------------------

Acht Bots auf einem isolierten Testserver.

Prüfe:

- stabile Clientverbindungen
- keine eingefrorenen Bots
- aktive Bot-Ticks
- funktionsfähige neue KI
- nachvollziehbare Profile
- keine kritischen Synchronisationsfehler
- CPU-Verbrauch
- RAM-Verbrauch
- Ressourcen-Throttling

--------------------------------------------------
TEST 4 – ORIGINALCLIENT
--------------------------------------------------

Prüfe einen echten Multiplayer-Beitritt
mit unverändertem Serious Sam TSE Classic 1.07.

Keine modifizierten Spielerclients voraussetzen.

Prüfe:

- erfolgreicher Join
- sichtbare Bots
- korrekte Spielerzahl
- Bewegungssynchronisation
- Treffer und Schaden
- Kills und Deaths
- Scoreboard
- normale Spielbarkeit

Verwende einen tatsächlichen Retail-Client.

Ein reiner Netzwerkport- oder Protokolltest
ersetzt diesen Test ausdrücklich nicht.

Falls ein notwendiger echter Spieler-Client nicht
verfügbar ist, dokumentiere diesen konkreten Blocker.
Behaupte keine bestandene Abnahme.

--------------------------------------------------
TEST 5 – 60-MINUTEN-STABILITÄT
--------------------------------------------------

Mindestens 60 Minuten Laufzeit.

Mindestens acht aktive Bots.

Sammle:

- CPU-Zeit
- RAM
- Tickrate
- Bot-Aktivitätsmarker
- Netzwerkfehler
- Synchronisationsfehler
- Prozessabstürze
- Client-Disconnects
- Server-Logs
- Telemetrie

Ein bloß laufender Prozess reicht nicht.

Die Bots müssen während der Messung tatsächlich
aktiv spielen.

====================================================================
11. PHASE H – CPU-BENCHMARK DER FERTIGEN VERSION
====================================================================

Nach erfolgreicher Runtime-Integration sind
erneut vergleichbare CPU-Messungen durchzuführen.

Vergleiche mindestens:

A: Bisherige qualifizierte Bot-Version.

B: Optimierte Bot-Version mit alter KI.

C: Optimierte Bot-Version mit neuer Human-KI.

D: Soweit sinnvoll, neue Human-KI ohne einzelne
   optionale CPU-Optimierungen zur Ursachenanalyse.

Verwende:

- dieselbe Map
- dieselbe Botanzahl
- dieselben Laufzeitbedingungen
- vergleichbare Bot-Aktivität
- gleiche beziehungsweise kontrollierte Seeds
- dieselbe Serverhardware
- dieselbe Messmethodik

Achte auf mögliche CPU-Unterschiede durch
unterschiedliche Bot-Entscheidungen und Spielverläufe.

Werte aus:

1. CPU je Bot.
2. CPU-Gesamtauslastung.
3. RAM je Bot.
4. CPU-Einsparung gegenüber der Baseline.
5. CPU-Mehrkosten der verbesserten KI.
6. CPU-Kosten relevanter KI-Funktionen.
7. Verhalten bei vier und acht Bots.
8. Stabilität der Tickrate.
9. Ressourcendrosselung durch den Host.

Berechne prozentuale Einsparungen nur aus
qualifizierten Messungen.

Keine Hochrechnung auf Basis inaktiver Bots.

Erstelle eine übersichtliche Ergebnistabelle.

====================================================================
12. PHASE I – SKALIERBARKEIT UNTERSUCHEN
====================================================================

Untersuche auf Basis der gemessenen Ergebnisse,
wie viele Bots die bestehende Hetzner-Maschine
zuverlässig tragen kann.

Unterscheide:

- mathematische CPU-Hochrechnung
- konservative Kapazitätsschätzung
- tatsächlich gemessene Botanzahl

Ermittle:

- CPU pro aktivem Bot
- RAM pro Bot
- CPU-Grundlast je Server
- zusätzliche Belastung durch mehrere Server
- Reserven für echte Spieler
- Reserven für Betriebssystem und Hintergrunddienste

Bewerte die Machbarkeit von:

8 Bots
16 Bots
32 Bots
64 Bots

Starte höhere Botzahlen nur, wenn die bisherigen
Tests ausreichende Reserven belegen.

Keine Überlastung des produktiven Servers.

Mehrere Server dürfen nur dann parallel betrieben
werden, wenn die verfügbare Ressourcenreserve
dies nachweislich erlaubt.

Beschreibe, ob für die langfristige Skalierung
ein größerer VPS, VDS oder Dedicated Server
wirtschaftlich sinnvoll wäre.

Keine kostenpflichtigen Server-Upgrades durchführen.

====================================================================
13. PHASE J – PRODUKTIVDEPLOYMENT
====================================================================

ERST NACH ERFOLGREICHER ABNAHME.

Vor dem Deployment:

- vollständige Sicherung der bisherigen DLL
- bestehende Konfiguration sichern
- bekannte funktionierende Version dokumentieren
- Rollback prüfen
- Logs sichern
- Ports und Servicekonfiguration prüfen

Setze anschließend die integrierte Version
kontrolliert auf dem öffentlichen
Alpha-Gaming-Server ein.

Zielkonfiguration:

Serious Sam TSE Classic 1.07
Deathmatch
Acht aktive Bots
Neue Human-KI aktiviert
CPU-Optimierung aktiviert
Telemetrie eingeschaltet, soweit für
Produktivbetrieb angemessen

Prüfe anschließend:

- Server startet
- Bots verbinden sich
- Server ist extern erreichbar
- Serverlisteneintrag sichtbar
- Originalclient kann beitreten
- Bots spielen aktiv
- keine neuen Sync-Fehler
- CPU- und RAM-Verbrauch im erwarteten Bereich

Führe einen abschließenden kontrollierten
Produktions-Smoke-Test durch.

Bei schwerwiegenden Fehlern sofort auf die
gesicherte funktionierende Version zurückrollen.

Keine Erfolgsmeldung ohne entsprechende Nachweise.

====================================================================
14. PHASE K – GITHUB-INTEGRATION
====================================================================

Arbeite mit einem isolierten Integrationsbranch.

PR #43 nicht erneut mergen, wenn seine Änderungen
bereits in main enthalten sind.

Änderungen aus #42 und #44 konfliktfrei integrieren.

Prüfe die Verwendbarkeit der Benchmark-Arbeiten
aus PR #41 unabhängig von dessen Branch-Basis.

Vermeide doppelte Commits und versehentliches
Überschreiben bereits integrierter Änderungen.

Sichere:

- Quellcode
- Build-Skripte
- Konfigurationen
- Tests
- Telemetrie-Korrekturen
- CPU-Messungen
- Runtime-Ergebnisse
- technische Entscheidungen
- Rollback-Informationen

Führe notwendige Commits und Pushes aus.

Erstelle einen konsolidierten Integrations-PR
oder nutze eine vorhandene geeignete
Integrationsstruktur.

Merge nur, wenn:

- erforderliche Tests bestanden sind
- keine ungeklärten Codekonflikte bestehen
- Build erfolgreich ist
- Runtime-Kompatibilität bestätigt wurde
- keine kritischen Regressionen vorliegen

Dokumentiere den tatsächlichen Merge-Status.

====================================================================
15. PHASE L – DOKUMENTATION UND ROADMAP
====================================================================

Aktualisiere die vorhandene Projektdokumentation.

Dokumentiere insbesondere:

- aktuelle Architektur
- verwendete GameMP.dll
- KI-Profile
- Feature-Flags
- Build-Prozess
- Hetzner-Betrieb
- CPU-Messverfahren
- Kapazitätsplanung
- bekannte Einschränkungen
- Rollback-Verfahren
- offene Verbesserungen

Aktualisiere die vorhandene Roadmap.

Markiere jede Aufgabe anhand nachgewiesener Ergebnisse:

ERLEDIGT:
Vollständig implementiert und erfolgreich getestet.

IN ARBEIT:
Teilweise implementiert oder aktuell in Bearbeitung.

BLOCKIERT:
Konkreter externer oder technischer Blocker.

OFFEN:
Noch nicht begonnen oder nicht qualifiziert.

Keine geschätzten Fertigstellungsprozente als
nachgewiesene Fortschritte ausgeben.

====================================================================
16. ABSCHLIESSENDE QUALITÄTSKONTROLLE
====================================================================

Führe nach der Integration eine abschließende
Prüfung aller Abnahmekriterien durch.

PFLICHTKRITERIEN:

[ ] PR-Konflikte beseitigt
[ ] CSV-Telemetriefehler behoben
[ ] CPU-Messungen qualifiziert
[ ] CPU-Optimierungen integriert
[ ] Fünf KI-Fähigkeitsstufen implementiert
[ ] Sechs Persönlichkeiten implementiert
[ ] KI im BotDriver tatsächlich aktiv
[ ] GameMP.dll erfolgreich mit MSVC gebaut
[ ] GameMP.dll unter Wine funktionsfähig
[ ] Acht Bots erfolgreich verbunden
[ ] Acht Bots bewegen sich und kämpfen
[ ] CPU- und RAM-Verbrauch dokumentiert
[ ] Originalclient erfolgreich beigetreten
[ ] Multiplayer-Synchronisation geprüft
[ ] 60-Minuten-Stabilitätstest bestanden
[ ] Öffentlicher Server erreichbar
[ ] Öffentlicher Server in Serverliste sichtbar
[ ] Rollback sichergestellt
[ ] GitHub aktualisiert
[ ] Dokumentation aktualisiert

Kennzeichne jedes Kriterium nur dann als erfüllt,
wenn ein tatsächlicher Nachweis vorhanden ist.

====================================================================
17. ERGEBNISBERICHT
====================================================================

Erstelle nach Abschluss einen kompakten,
technisch nachvollziehbaren Bericht.

Struktur:

1. Gesamtstatus
2. Integrierte Änderungen
3. Verwendete DLL und SHA256
4. GitHub-Commits und Pull Requests
5. Funktionierende KI-Eigenschaften
6. CPU-Verbrauch vorher/nachher
7. RAM-Verbrauch je Bot
8. Gemessene maximale Botanzahl
9. Multiplayer-Testresultate
10. Stabilitätstest
11. Produktivstatus
12. Verbleibende Einschränkungen

Trenne ausdrücklich zwischen:

- technisch implementiert
- offline getestet
- unter Wine getestet
- im Retail-Multiplayer getestet
- produktiv aktiviert

Gib keine unbelegten Erfolgsmeldungen aus.

====================================================================
18. AUTONOME FORTSETZUNG
====================================================================

Beginne unmittelbar mit der Bestandsprüfung.

Erstelle anschließend den Ausführungsplan und
arbeite die Phasen selbstständig ab.

Verwende bestehende Werkzeuge, Prozesse,
Repositories und Dokumentation.

Vermeide unnötige Rückfragen und Zwischenberichte.

Nach jedem abgeschlossenen Arbeitsschritt
automatisch mit dem nächsten fortfahren.

Halte wichtige Ergebnisse persistent in GitHub fest.

Wenn die Umgebung oder Sitzung unterbrochen wird,
muss der aktuelle Stand anhand der Dokumentation
und Commits eindeutig wiederaufgenommen werden können.

Stoppe nur bei:

1. Vollständigem, nachgewiesenem Abschluss.
2. Einem technisch belegten externen Blocker.
3. Einer zwingend notwendigen rechtlichen,
   finanziellen oder sicherheitsrelevanten Freigabe.

Ein laufender Benchmark, ein offener Pull Request
oder ein erfolgreicher Teiltest sind keine
ausreichenden Gründe, die Bearbeitung als
abgeschlossen zu erklären.

DEIN ENDZIEL:

Ein öffentlich erreichbarer Alpha-Gaming-Server
für Serious Sam TSE Classic 1.07 mit acht
voll funktionsfähigen, CPU-optimierten Bots,
aktivierter menschlich wirkender KI,
fünf Spielstärken, sechs Persönlichkeiten
und nachgewiesener Multiplayer-Stabilität.

Arbeite auf dieses konkrete Ergebnis hin.

BEGINNE JETZT MIT DER VERIFIKATION DES TATSÄCHLICHEN
GITHUB- UND HETZNER-STATUS UND SETZE DIE ARBEIT
ANSCHLIESSEND EIGENSTÄNDIG FORT.
