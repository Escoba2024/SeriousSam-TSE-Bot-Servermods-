# Build018: belegte Verbesserung und verbleibende Abnahme

Stand: 12.11.2026 23:01:07 MEZ.

## Ergebnis des Vergleichs

Build018 ist in den sechs abgeschlossenen kurzen Vergleichen gegen die bisherige öffentliche Bot-DLL im direkten Kampf überlegen. Jede Stufe wurde zweimal jeweils 120 Sekunden mit vertauschten Startverteilungen geprüft. Der vollständige Rollout bleibt offen.

| Stufe | Direkte Abschüsse neu gegen alt | Direkte Abschüsse alt gegen neu |
| --- | ---: | ---: |
| MITTEL | 31 | 12 |
| STARK | 31 | 13 |
| DEMON | 47 | 8 |
| Gesamt | 109 | 33 |

Diese Zahlen stammen aus vollständig verknüpften tödlichen Fremdschadensereignissen. Die getrennten Query-Fragwerte 148:87 enthalten auch Kämpfe innerhalb derselben Kohorte und werden deshalb nicht als direkter Versionsvergleich ausgegeben. Alle 1490 Schadensereignisse bleiben kategorisiert. Eine nach der bestehenden Waffenmaske nützliche Zusatzwaffe wurde in 71 von 100 neuen und 16 von 186 alten beobachteten Leben nachgewiesen. Die Maske schließt Messer, Colt, Doppelcolt und Kettensäge aus; fehlender Zusatzwaffenbesitz bedeutet nicht völlig unbewaffnet.

Der Vergleich belegt weder STARK zuverlässig stärker als MITTEL noch eine bestimmte menschliche Spielstärke. Für die vier STARK-/DEMON-Fenster wurden ausschließlich die beiden Dev-Botclients zeitweise normal angehalten, um den unveränderten RAM-Guard einzuhalten. Beide Vergleichskohorten hatten innerhalb desselben Fensters dieselben Bedingungen. Die unterschiedlichen Hostbedingungen zwischen den Stufen bleiben eine Einschränkung. Beide vorherigen STARK-RAM-Fehlläufe bleiben erhalten.

Vollständige Paarwerte und Methodik: [Sechs Vergleichsfenster](2026-11-12-build018-six-window-comparison.md).

## A1: Prescan als alleinige Ursache nicht bestätigt

Der zusätzliche begrenzte Versuch wurde mit Original-Eingaben und geprüftem Prescan-aus-Profil tatsächlich ausgeführt. In allen 72 erfolgreichen passiven Doppelbeobachtungen waren Mausbeschleunigung0, Empfindlichkeit0,25 und Prescan0 wirksam. Der Original-Shell-Start wurde akzeptiert.

Die Vorbereitung scheiterte vor dem ersten Schuss erneut an einer widersprüchlichen Drehantwort. Aus der Kalibrierung waren bei zwölf horizontalen Eingabepixeln minus3Grad zu erwarten; Server und Client zeigten beide minus6Grad. Sieben Eingabeaktionen wurden versucht, die Vorbereitung dauerte5,8656Sekunden. Prescan abzuschalten behebt diesen Fehler folglich nicht. Eine Ursache in der Original-Eingabeglättung oder dem Zeitpunkt der Bestätigungsbeobachtung ist eine noch ungeprüfte Hypothese.

Der Versuch bleibt FAIL. Es gibt daraus keinen Schuss-, Fremdtreffer-, Schadens- oder First-State-Nachweis. Bestehende vorbereitete Receipt-Flags wurden nicht nachträglich umgeschrieben. Das effektive Profil ist durch tatsächliche erfolgreiche Doppelbeobachtungen und die Startmarkierungen belegt.

Alle drei gestarteten Spielrollen wurden normal geschlossen, ihre drei Schlusslogs akzeptiert und unabhängig nachgehasht. Root prüfte664 reguläre Dateien und neun ursprüngliche Abwesenheiten; alle vier Labwurzeln sind ruhig und beide Testdisplays entfernt. Die Wiederherstellung ist bestätigt. Es gibt keinen automatischen Folgeversuch und keine Lockerung von Gain-, Zeit-, Identitäts- oder Restoregrenzen.

[Sanitisierte native Quittung](milestone-a-20261112/a1-prescan-v2-native-summary.json).

## A1: neuer deaktivierter Observer und Controller

ObserverV2 bindet die tatsächliche Original-Todesereignis-/Dispatch-/Respawnkette an die konkrete Lebensgeneration. Ein gültiger InitializePlayer-Return kann bereits der erste gültige Zustand sein; es wird keine zusätzliche Tick- oder Actionbedingung erfunden.89 tatsächlich ausgeführte Offline-Prüfgruppen bestehen. Die Originalbindungen und synthetischen Gegenfälle ersetzen keine native ABI- oder Trefferprüfung.

Der getrennte Controller besteht in V1 aus76 fokussierten Offline-Tests. Das unabhängige Review fand anschließend einen konkreten Fehler: Wenn die Journalablage nach einem erfolgreichen Drain scheiterte, fehlte das bereits empfangene Paket im kanonischen Nenner. Der Endstatus blieb zwar FAIL, die Vollständigkeitszählung war dennoch falsch.

V2 verschiebt ausschließlich die vorhandene einmalige Paketaufnahme vor diesen Journalaufruf. Der eigene reproduzierte Gegenfall zählte vorher nur ein Paket mit null Ereignissen statt tatsächlich zwei Paketen mit20Ereignissen. Danach stimmen tatsächlicher und kanonischer Nenner überein.13 unmittelbar betroffene Prüfungen bestehen. Das unabhängige Folgereview bestätigt im Kontroll- und Fehlerfall zwei Pakete mit20Ereignissen, die Ereignisse1–20 genau einmal, weiterhin sticky FAIL und sämtliche fünf Cleanupversuche. Ergebnis: READY,0Critical/0Important innerhalb dieses engen Reviewumfangs. Die historische76er-Suite wurde nicht als neue V2-Gesamtsuite ausgegeben; alle173 V1-Dateien bleiben unverändert.

Alle Lauf- und ABI-Gates bleiben deaktiviert. Die vorhandenen Adapter decken nur Vanilla/warm ab. Echte KI, Kartenwechsel und Neustart sowie der praktische Erstzustandstreffer und ausreichender tödlicher Schaden bleiben offen. Die festgelegte Abnahmematrix mit zwölf Kontrollpaaren/24Fenstern ist der daraus abgeleitete Testplan, keine wörtliche Mengenangabe des ursprünglichen Nutzerauftrags. Die normale Colt-Vorbereitung muss vor einem solchen Versuch tatsächlich erfolgreich sein.

[Controllerumfang und Grenzen](2026-11-12-a1-first-state-controller-disabled.md).

## A4: Beobachtungslücke erklärt, Versorgungstest weiterhin FAIL

Der ursprüngliche Build018-Test bleibt bei23 von24 Slotphasen gescheitert. In Phase1 erreichte botB:1 in acht beobachteten Leben keinen nach der bestehenden Maske nützlichen Zusatzwaffenbesitz, keine entsprechende Aufnahme und kein entsprechendes natives Feuer. Diese tatsächliche Versorgungslücke ist weiterhin offen.

Die separat untersuchte Abweichung bei einem anderen Slot ist erklärt:133 serverseitig inventarbeobachteten Leben stehen134 im Clientlog begonnene Leben gegenüber; entsprechend110 gegenüber111 Todesfällen. Das frühe zusätzliche Leben von botA:2 beginnt mit nativem Spawnzeitwert0,400000036 und endet vor dem ersten Inventarsample bei8,40001392364502. Positive native Waffenbeobachtungen dieses frühen Lebens reichen von0,45 bis3,399998. Die erste inventarbeobachtete Lebensgeneration wurde erst bei7,350009918212891 geboren.

Dieses frühe Leben bleibt ausschließlich logbeobachtet und außerhalb der Inventarabdeckung linkszensiert. Es wird kein Inventarleben erfunden. Die ursprüngliche fehlgeschlagene vollständige Korrelation bleibt unverändert erhalten; die Erklärung wird nicht zu einem vollständigen Korrelations-PASS umgedeutet. Insbesondere beseitigt sie nicht den Waffenversorgungsfehler des anderen Slots. Karten-, Navigations-, Gefahren- und Resetabnahme bleiben offen.

[Ursprünglicher nativer A4-Fehllauf](2026-11-12-a4-build018-native-failure.md).

## Betrieb, Quelle und Sicherung

Die letzte tatsächliche Bestandsprüfung vom12.11.2026 um22:43:05MEZ bestätigt sechs Instanzen mit jeweils acht eigenen Bots, keine zusätzlichen UNKNOWN-Teilnehmer, effektiven Spawnwert0 und die bisherigen geladenen DLLs. Die öffentlichen aktuellen Logzähler stehen jeweils bei0BAD/0Disconnect; die bekannte Devhistorie bei37/3. Die zeitweise Dev-Clientpause ist beendet. Build018 wurde weder auf Dev noch auf Public installiert.

Build018 stammt aus Quellcommit1802fb3f0720b53feb032abfe2c2a83407bfea6e. Seine DLL hat SHA2566db89204e33dc7d76ecdfed68055d2b75bde4950475793a57101fd0cefcb8e4a. Der vorherige Fortschrittsbaum wurde als GitHub-Commitc275e93eee36fd7cae50f73a4189be98209d74eb tatsächlich gefetcht und exakt mit dem lokalen Baum verglichen. Dieser Bericht wird als eigener Quellencheckpoint veröffentlicht.

Delta022 ist auf dem Server erstellt und getrennt restauriert:101451161Archivbytes,16033 reguläre Dateien und826890437 wiederhergestellte Bytes; Dateihashes und Metadaten geprüft. Zwei Symlinks sind indexiert und nicht materialisiert. Archiv-SHA256e88caecf53ed94ddbac6ade1b3c638a637b50459d4dc4ff699dec50513861196. Der historische Scope-Text BUILD017 in einer Quittung bleibt unverändert; das tatsächliche Build018-Payload wurde separat geprüft und die Abweichung im Restoremanifest erklärt.

Der Drive-Upload scheitert tatsächlich an „no primary turn environment is available“. Delta021 bleibt der letzte hochgeladene und durch Rückdownload geprüfte Stand. Für Delta022 wird keine externe Kopie behauptet. Die späteren Observer-/Controllerstände, Prescanbelege und dieser Quellencheckpoint werden als eigener Delta023-Nachtrag vorbereitet. Ein nativer Start aus der gesamten wiederhergestellten Kette wurde nicht ausgeführt.

## Offene Abnahme und genaue Fortsetzung

A2 ist abgeschlossen:208 bestehende plus250 neue Namen,458 insgesamt,48 eindeutige eigene Bots und erhaltene GUIDs. A1, vollständige A3-/A4-Abnahme, die fortgeführten3600/3600/7200-Sekunden-Stabilitätsprüfungen, vollständige externe Sicherung und qualifizierter Dev-zuerst-Rollout bleiben offen. B wurde nicht begonnen.

1. Quellencheckpoint tatsächlich veröffentlichen und seinen Baum durch Fetch prüfen; anschließend den expliziten ruhigen Delta023-Umfang archivieren und separat restaurieren.
2. Sobald die bestehende Dateitransportumgebung wieder verfügbar ist, Delta022 und Delta023 samt Manifesten in den vorhandenen privaten Drive-Ordner übertragen und tatsächlichen Rückdownload samt Hash prüfen.
3. Für A1 den tatsächlichen Eingabeverarbeitungspfad und den Zeitpunkt der ACK-Beobachtung kausal eingrenzen. Keine weitere Prescan-Wiederholung ohne geänderte, belegte Voraussetzung; keine Toleranz-/Timeoutlockerung.
4. Die A4-Versorgungslücke gezielt aus den vorhandenen Belegen untersuchen und eine begründete Korrektur separat prüfen. Anschließend unveränderte verbleibende Abnahmen erfüllen.
5. Erst nach nachgewiesenem Abschluss der Abnahmekriterien den neuen Stand zunächst auf Dev und danach kontrolliert weiter ausrollen.

Alle Root-Native-/Buildfenster dieses Stands sind geschlossen. Beide Worker sind nach den dokumentierten Ergebnissen ruhig. Root besitzt ausschließlich die verbleibende Quellenveröffentlichung und Sicherung; es läuft kein verdeckter Spieltest.
