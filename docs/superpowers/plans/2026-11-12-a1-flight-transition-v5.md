# A1 V5: Alle tatsächlichen Route-Proben in der Ankerhistorie

## Auftrag und Stand

V4 bleibt wegen des unabhängigen Important/P1 blockiert. PP speichert die neuere `route-after-input`-Probe, übergibt sie jedoch nicht an Route. Ein älterer günstiger Anker kann so überleben. V5 entsteht ausschließlich im neuen privaten Paket; der vorhandene isolierte V4-Worktree erhält nur neue V5-Dokumentation. Root besitzt Integration und alle nativen Aktionen.

## Abnahmekriterien

- Die drei vollständigen unabhängigen Gegenfälle werden vor Änderung mit echtem PP/RD/Route RED reproduziert: neuere Same-Tick-Probe ohne Support, außerhalb Node 12-Radius, außerhalb Korridor.
- Jede relevante tatsächliche Route-Probe aktualisiert oder verwirft die Historie. Auf dem gleichen Beobachtungspfad wird nach weiteren ausgelassenen Proben gesucht; kein älterer günstiger Zustand darf ausgewählt werden.
- Nach der Eingabe wird ausschließlich beobachteter Zustand verarbeitet. Keine zusätzliche Eingabe, kein Inputretry, keine nachträgliche Änderung einer ausgeführten Aktion. Vor dem Request bleibt jede andere Änderung der pending Aktion fatal.
- Gültiger Übergang bereits nach einer Eingabe wird mit seinem echten vorherigen Anker und dessen Lesebeginn verarbeitet. Die 8-s-Flugfrist beginnt nicht später.
- Exakter unveränderter 111716-Replay bleibt bis Raw 212 bestehen: 27 RD-Paare, 66 Rollenframes, 16 echte gespeicherte Quittungen; 17. Input vor Request zurückgenommen, keine erfundene Folgepose.
- Originalgeometrie, Support-/Geschwindigkeits-/Identitätsprüfungen, Zeitgrenzen 85/90, Route 45, Flight 8, .5-s-Verlaufslücke, .2-s-Frische, 48 Aktionen, RD, Release, Normal Close und Restore bleiben unverändert.
- Beide Ausführungsgates false, alle aktuellen relevanten Offline-Regressionsprüfungen grün, vollständige Source-/Runtime-/Evidenzclosure und Erhaltung alter Dateien belegt.

## Ablauf

1. [x] Unabhängigen Review, exakte Gegenfälle und tatsächliche Verdrahtung lesen.
2. [x] Isolierten V5-Claim und Kopie mit Parent-/Review-Pins sichern.
3. [x] Drei vollständige Gegenfälle und sinnvolle Grenzfälle RED gegen unveränderte Implementierung.
4. [x] Minimalen Beobachtungspfad korrigieren; keine neue Laufzeitaktion.
5. [x] Gegenfälle GREEN, exakten Replay und vollständige relevante private Suite prüfen.
6. [x] Diff, Closure, Gates, Parent-/Review-/Raw-Erhaltung, Pins, Bericht und Folgecommit sichern.
7. [x] READY für unabhängigen Re-Review an Root; anschließend idle.

Alle synthetischen Änderungen und Replays sind ausschließlich Tests und keine nativen Zwischenzustände oder Bouncer-IDs. Es gibt weiterhin keinen neuen Pickup-/Schuss-/Treffer-/Erstzustandsnachweis.

## Abschlussstand

AUTHOR_READY_FOR_INDEPENDENT_REVIEW. Die drei Reviewer-Gegenfälle sind RED→GREEN. Der zusätzliche tatsächliche periodic/sample-Pfad ist separat reproduziert und mit Erfolgssequenz/konservativer Ankerinvalidierung geschlossen. Die konkrete Float-Grenze wird gegen die feste absolute 8-s-Deadline geprüft; keine Toleranzänderung. 187 relevante Tests bestanden in 1.958 s. Strikter Replay mit allen 203 Originalpaaren erhält 66 Rollenframes, 27 RD-Paare, 16 Quittungen und die Rücknahme des 17. Inputs. Closure 48/46/125 vollständig; Parent 141 / Review 15 / Native 9 unverändert. Native/Build/Root-Änderungen: keine. Beide Gates false.

Unabhängiger Re-Review und späterer Root-Freeze/Native sind ausdrücklich noch offen und liegen nicht bei diesem Worker. Der Bericht enthält den konkreten nächsten Normal-Ausrichten-/Damage-/Lifecycle-Schritt zur späteren eigentlichen A1-Abnahme.
