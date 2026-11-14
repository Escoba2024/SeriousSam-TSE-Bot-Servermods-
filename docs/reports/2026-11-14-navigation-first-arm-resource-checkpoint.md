# Erster048-Vergleichsarm: Ressourcen-FAIL, kein Navigationsrang

Am14.11.2026 ab18:11:17UTC lief genau ein048-Arm mit dem geprüften
Original-Dedicated, acht Cecil048-Bots und dem unveränderten Originalclient
auf isoliertem Hard2/Red Station. Tatsächliche Profilreceipts beider Gruppen:
BOT-Expert-Rifle/tier5/marksman, alle lokalen Slots vorhanden. Die
unveränderte Original-Pausebarriere und anschließende Neunerbesetzung
gelangen. Der Vergleich wurde nicht auf Live ausgeführt.

Nach rund253,46s Gameplay statt der vorgesehenen600s verletzte eine
1,041807s-Hostprobe die75%-Grenze: **75,245098%**. Der Lauf bleibt **FAIL**,
auch wenn die Überschreitung klein ist.246 Hostproben insgesamt;
RAM mindestens2708918272Byte, Datenträger mindestens9964077056Byte;
Gameplay-Messlücke höchstens1,159695s. Gesamtmesslücke einschließlich
Startbarriere47,274264s. Keine vollständige600s-/Ressourcenabnahme und kein
mit anderen Fenstern kombinierbarer Navigationsrang.

Alle vier Rollen wurden regulär geschlossen; sämtliche geschlossenen Logs
enthalten0 Sync-/Disconnect-/CRC-/Crash-/InvalidAction-/Joinfehler. Root
prüfte unabhängig640 Dateien mit Inhalt/Metadaten, vier Schlusslogs sowie
Prozess-/Hilfsprozess-/Displayenden: **PASS_RESTORE**.

| Beleg | SHA256 |
|---|---|
| Root-Manifest048 | `85921b07860d7ec6f8270b04bcb3dc48990c2ae654ea9bdf9ca2b94c98b7e7fb` |
| Resultat FAIL | `543b31cefe6183b7435ceb114e7d6dc570eaa76049944913c2d0539a34beab2c` |

Privat:
`/srv/tse-milestone-a-evidence-20261111/nav-048-root-redstation-20261114-181117`.
RootEV/navigation-comparison-048-root-restore.json und
navigation-comparison-048-unit-accounting.json sind die getrennten
Restore-/systemd-Quittungen. Vorherige Delta043-Sicherung wurde vollständig
aus Drive zurückgelesen:12263687Byte,
SHA`d15936f5c20597296239bffd3875da2635c17f9d176901d7f50a913677ca32be`,
1272 Dateien/Metadaten nach Rekonstruktion erneut geprüft.

## Konkreter Ansatz für weniger Testlast

systemd verbuchte für den Original-Beobachter **174,166CPU-s**, für die beiden
endgültigen Botgruppen14,645 und14,498CPU-s, für den Server16,398CPU-s.
Die getrennte frühe Bootstrap-Botgruppe hatte zusätzlich4,216CPU-s.
Dies sind ganze Unitlaufzeiten einschließlich Startup und Winehelfern,
keine Attribution des letzten1,042s-Spikes und keine reine Renderzeit.
Die Hostbudgetformel wurde geprüft: Gastzeiten werden nicht doppelt gezählt,
idle+iowait werden abgezogen. Ein Messfehler ist damit nicht belegt.

Eine gesonderte dreisekündige Baseline ohne Lab zeigte38,75% Hostauslastung
und0 Steal; sie beweist weder die Ursache noch die Last am Fehlerzeitpunkt.
Unabhängige Offlinewriter durften zu diesem späteren Zeitpunkt wieder laufen.

Für eine neue gemeinsame Reihe wird ausschließlich der eigene zusätzliche
Original-Beobachter auf das normale Renderlimit20/20 statt30/30 gestellt.
Dies gilt gleichermaßen für alle drei Kandidaten; bereits gesammelte
30FPS-Rohdaten werden nicht hineingemischt. Der
[neue Plan](../superpowers/plans/2026-11-14-navigation-observer-render-budget.md)
erhält600s, alle Inputs/Reader/Serverregeln und die75%-Grenze.
Ein neuer Fehler beendet erneut die Reihe; kein blindes Wiederholen.

Sechs neue Offlineverträge wurden zuerst RED und dann GREEN geprüft;
zusammen mit neun Kandidaten- und24 V3-Fällen39/39PASS in0,218s. Ein
zusätzliches Zwischen-RED betraf eine fehlende Abschlussnewline im
Duplikat-Ankerfixture; nach Herstellung des tatsächlich doppelten Ankers
wurde die unveränderte Ablehnung geprüft. Kein Gameplaygate wurde geändert.
Die drei deaktivierten20FPS-Pakete haben jeweils139 Runtime-/61 Source-/
39 Pythonpins. Actual-FPS-Messung, neuer nativer Vergleich und
Gesamtabnahme bleiben offen. Unsere Vergleichsvorbereitung änderte die Liveflotte nicht. Der spätere unabhängige Publicrollout ist im folgenden Nachtrag abgegrenzt.

## Nachtrag18:46UTC: zusätzliche gleichzeitige Hostarbeit

Der spätere18:37-Audit fand einen zweiten unabhängigen Publicrollout mit
Namenrefresh auf demselben Host. Dessen tatsächliche Botstarts und Belege
liegen unter anderem18:10–18:18UTC und überlappen diesen18:11–18:16-Lauf.
Die Zusatzlast ist damit real; ihre genaue Beteiligung am letzten CPU-Sample
ist ohne passende Prozesszeitreihe unbekannt. Der Original-Beobachter darf
nicht als alleiniger Fehlerverursacher bezeichnet werden. Der Lauf bleibt
FAIL. Vor einer neuen Reihe müssen auch fremde Deploy-/Refreshjobs als
Störbedingung ausgeschlossen werden. Der Nutzer hat den jetzt gemischten
Livebestand ausdrücklich bestätigt; siehe [Flottenabgleich](2026-11-14-shared-host-fleet-reconciliation.md).
