# A1: lokaler Pitch-Faktor und kompensierter Original-Eingabevergleich

## Geschlossener Befund

Der Colt-Lauf 171044 bleibt FAIL mit opposite pitch gain does not reproduce. Result-SHA: e395aaf98377489c39442531969cc754bdec3190fe46a2050610d8f5e563f90e. Sechs tatsächliche Eingaben, 28 Policybeobachtungen, 64 erfolgreiche Doppelpaare und 68 Rohleseversuche wurden vollständig zugeordnet. Kein Fire.

Bei +12 relativen Y-Pixeln änderten sich beide Original-Viewpoints von 0 auf −3°. Vor dem Gegenrequest −12 standen die lokale und beide empfangenen Rotationen stabil bei −3°. Die erste erfolgreiche Nachprobe hatte lokal bereits +3°, während die empfangenen Werte noch −3° blieben; danach bestätigten beide Original-Viewpoints +3°. Damit entstehen die +6° vor der Serverübernahme lokal. Der tatsächliche XTest-Request war relativ, nicht absolut. Die letzte Policyprüfung lag jeweils nur wenige Mikrosekunden vor Requestbeginn.

Der genaue Mechanismus innerhalb Cursor/Recenter, Betriebssystem-/Wine-Eingabe und Prescan/Timer ist mangels entsprechendem Ereignistrace unbewiesen. Es gibt keinen belegten festen asymmetrischen Transfervertrag. Alte Fehlproben werden nicht umgewertet und Gain-, EPS-, Zeit- oder Wiederholungsgrenzen nicht erweitert.

## Separater, ausdrücklich autorisierter Vergleich

Original Retail Engine GetInput multipliziert bei AllowMouseAcceleration≠0 die MouseSensitivity mit exakt Float32 0,25. Bei Flag=0 entfällt dieser Faktor. Der kontrollierte normale Vergleich lautet deshalb AllowMouseAcceleration 1→0 und MouseSensitivity 1→0,25. In beiden Fällen beträgt der Engine-Grundfaktor 0,25. Keine weiteren Filter-, Precision-, Prescan- oder Smooth-Änderungen.

Nur das transaktional versiegelte Vanilla-PersistentSymbols-Profil erhält einen angehängten normalen Shellblock. Das vorhandene Präfix muss exakt dem gesicherten Original entsprechen. Im neuen Start bestätigt die Original-Shell bedingt tatsächliche Baselinewerte 1/1 und Zielwerte 0/0,25. Fehlende, falsche, doppelte oder umgeordnete Marker verhindern jede Eingabe. Die alten effektiven Globals wurden nicht mitgelesen und werden nicht rückwirkend behauptet.

Ein neuer optionaler Reader-Modus liest die beiden Engineglobals in beiden Konsistenzdurchgängen. Jedes erfolgreiche Vanilla-Paar muss genau 0/0,25 belegen. Abweichende oder während des Reads wechselnde Werte sind fatal; vollständige Fehlrohwerte bleiben im Attemptbeleg erhalten. Der Readerstandard bleibt unverändert. Drei zusätzliche Retailguards binden Flag/Sensitivität, den Original-SPI_SETMOUSE-Setter und die Kompensationskonstante an die geladenen Bilder.

Der Original-Setter prüft seinen API-Rückgabewert nicht. Tatsächliche Wine-/X11-Wirkung und reproduzierbarer Gain sind Gegenstand des späteren einen Vergleichs, kein vorweggenommener Erfolg.

## Offlinebelege und unveränderte Grenzen

Gezielte echte RED→GREEN gegen Profilinstallation, Restore, Reader und Controllerverdrahtung; danach 240 private Tests ohne Skip sowie 32 bestehende Readertests gegen den neuen Reader bestanden. Drei zusätzliche statische Retail-/Relokationsfälle sind enthalten. Ein expliziter Adapter verwendet bei der alten Original-Datei-Pinprobe verifizierte statische Originalbilder, ohne aktuelle Labdateien zu qualifizieren. Frischer Root-Preflight bleibt zwingend.

54 Schutz-/Lifecyclefunktionen sind AST-identisch. Zwölf Kern-/Policy-/Transportdateien einschließlich CP, RD und X11Endpoint bleiben bytegleich. 85/90 s, 48 Actions, 2 s ACK, 0,2 s Freshness, finaler Requestcheck, Safe-Release, PID/Start/Module/World/Life/Weapon, Host sowie normale Close-/Restoregrenzen gelten weiter. Der echte −3°/+6°-Gegenfall bleibt nach sechs Inputs vor Fire FAIL.

Altes Autorenpaket (233 Dateien), Root-Freeze (233) und Nativefenster (686) sind vollständig unverändert. Beide neuen Autorengates sind false. Kein Native, Attach, Build oder Root-Worktreewrite durch den Autor.

## Übergabe und Grenze

Paket: /srv/tse-a1-colt-noaccel-completion-20261112.
Analyse: /srv/tse-a1-colt-pitch-analysis-20261112.
Finale Pins, Quittung und Dokumentationscommit: HANDOFF.json und FINAL-VERIFY.json im neuen Paket.
Runtime-Diff SHA f606e84725011523367e754d951db585c4f61693c48376ff63aa851b5f4c0a9a.
Normalized-Delta SHA 38acff4761d3d44815823430196a1fab6e262637d3a36ac35d04c83afc51cbf5.

Root darf erst nach unabhängiger Prüfung separat einfrieren und höchstens ein neues 90-s-Fenster ausführen. Ein Abbruch wird normal geschlossen/restored und nicht automatisch wiederholt. Die Arbeit ist ein kontrollierter Vergleich, kein behaupteter Ursachenfix.

Bei erfolgreicher unveränderter Vorbereitung bleibt es bei höchstens einem normalen Colt-Firehold. Historisch etwa 129 Einheiten Distanz und Originalreichweite ≤500 beweisen keine freie Sichtlinie. Fehlende beidseitige Clip-/HP-Abnahme nach dem einen Hold bleibt FAIL/LOS-offen; keine zusätzliche Bewegung oder weitere Schüsse.

Preparation allein bleibt kein A1-Pass. Offen sind die tatsächliche Lebens-/Gültigkeits-/autoritative First-State-Ordnung, kausale Original-Fire-/Bullet-/Fremdschadenbindung, gemeinsamer Endvalidator mit vollständigen Nennern sowie begrenzter Zwei-Spieler-Controller mit uninstrumentierter Kontrolle und externem Originalrestore. Maßgeblich: /srv/tse-a1-first-state-contract-20261112/REPORT.md. Damage-/Lifecycle-Drafts sind Kandidaten, keine native Freigabe.
