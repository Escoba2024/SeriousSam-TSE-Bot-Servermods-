# A1 V4: Approach → Flight bei verspäteter Beobachtung

Datum: 2026-11-12
Owner: /root/review_names_transaction
Status: **READY_FOR_INDEPENDENT_ROOT_REVIEW** — Paket eingefroren, Gates false.
Basis: c5e36ed55f4ad3ecf7b2130161ab251eaa8b25b7
Worktree: /srv/tse-milestone-a-a1-flight-transition-v4-20261112
Branch: codex/20261112-a1-flight-transition-v4
Privates Paket: /srv/tse-a1-flight-transition-v4-20261112
Claim: /srv/tse-milestone-a-continuation-evidence-20261112/a1-flight-transition-v4-claim.json

## Auftrag und belastbare Ausgangslage

Originalauftrag /srv/tse-milestone-a-evidence-20261111/request.md, AGENTS.md, Toolpolicy und FINAL-HANDOFF.md wurden gelesen. A1 verlangt einen gültigen normalen Treffer ab dem ersten verarbeiteten Respawnzustand. Diese V4-Arbeit bereitet weiterhin nur normale Waffenbeschaffung/Kontrollfeuer vor; kein Treffer-/Erstzustands-/Exactly-once-Nachweis.

V3-Parent /srv/tse-a1-route-after-rotation-completion-v3-20261112 bleibt unverändert, Manifest 8aa93b6db274fe78af30c23caa2b2e7fb946345468fa96788745c5911a53bb87. 126 Parent-Dateien wurden vor Änderungen inventarisiert. Der native Lauf 111716 bleibt FAIL; Analyse /srv/tse-a1-route-v3-native-111716-analysis-20261112 bleibt unverändert.

Belegt: Raw 211 zeigt eine gültige gestützte Approach-Pose im Original-Node 12-Radius. Raw 212 folgt 0.386162 s später; die drei Flug-Geschwindigkeitsbedingungen sind erfüllt, x liegt bereits jenseits der bisherigen x<−35-Erkennung. Der folgende z-Korridorguard lehnt ab. Der 17. Request wurde nicht ausgeführt. Keine Zwischenpose oder Bouncer-Eventidentität ist bekannt.

## Geplanter enger Entwurf

1. shooter_policy.Route behält Approachkorridor, Originalplan und direkte Flugsignatur. Für eine bereits weiterbewegte Probe darf ausschließlich die unmittelbar vorherige gültige Approach-Probe als Anker dienen: gleicher Lebens-/Weltbezug, tatsächlicher Support, innerhalb des bestehenden Original-Node 12-Radius. Der aktuelle Zustand benötigt Null-Support, die bestehenden drei Geschwindigkeitsbedingungen, unverändertes Heading sowie räumlichen Fortschritt auf die Originalkante 12→34.
2. Neuer konservativer Nachweisdeckel: sowohl Host- als auch Native-Tick-Abstand strikt kleiner als 0.5 s. Das ist keine Erweiterung eines bestehenden Budgets. Die volle tatsächliche 211/212-Lücke liegt darin; ältere Anker bleiben unzulässig. Kein Rückgriff auf eine günstigere ältere Probe.
3. Das Flight8-Budget beginnt bei einer solchen verspäteten Beobachtung bereits am Lesebeginn der letzten Bodenprobe, nicht erst bei der späteren Erkennung. Rohzustände und das beobachtete Zeitintervall bleiben im Beleg. Eine Bouncer-ID oder ein exakter Startzeitpunkt werden nicht behauptet.
4. preparation_policy überprüft dieselbe pending Forward-Aktion mit dem neuesten tatsächlich beobachteten Routenzustand. Ein beobachteter Wechsel nach flight ist ausschließlich eine autorisierte Rücknahme dieser Eingabe. Andere Abweichungen bleiben fatal; kein Neuplanen/Retry.
5. Erkennt erst der letzte Callback nach allen Endpoint-/Transportguards den Übergang, behandelt action_step ausschließlich diese typisierte Rücknahme vor Requestbeginn. Kein XTest-Down, keine Holdphase; vorhandenes sicheres Key-up/Cleanup bleibt unverändert. PP akzeptiert die Rücknahme nur mit einer eindeutigen Quittung ohne Request. Positive Inputreceipts zählen weiterhin nur tatsächlich bestätigte Eingaben.
6. Nach dem Übergang folgen ausschließlich bestehende passive Flug-/Pickupprüfungen. Route45/Flight8, globale85/90, Aktionen 48, Reader-Freshness0.2, Retries, RD/ACK/EPS und alle Lifecycle-/Host-/Closure-Regeln bleiben bestehen.

## Aufgaben und Abnahme

- [x] Originalauftrag/Handoff/Regeln lesen, Ausgangsbefund und Gitbasis prüfen.
- [x] Neuen Worktree/Branch/Claim und deaktivierte separate Parentkopie anlegen.
- [x] Reale 111716-Paare und Quittungen unverändert als privaten Testbeleg pinnen.
- [x] RED: echte Route und tatsächlichen PP-/Controller-/Endpoint-Pfad mit diesen Daten reproduzieren; bis zum bekannten Beobachtungsende, ohne erfundene Folgepose.
- [x] Gegenfälle: unzulässiger/zu alter/vorteilhaft ausgewählter Anker, falsches Leben/Prozess, unpassende Geometrie/Support/Geschwindigkeit, alle Fristgrenzen und nicht bestätigbare Rücknahme.
- [x] Minimale Implementierung: bedingter beobachteter Übergang plus vor Request quittierte Rücknahme; unveränderte direkte Route-/RD-Pfade erhalten.
- [x] GREEN: echte 211/212-Folge führt zu flight und keinem 17. Down; alle Gegenfälle fail-closed, kein Folgeinput nach Fehler.
- [x] Gesamte relevante private Regression und tatsächliche Verdrahtungsprüfung; keine Builds/native Starts.
- [x] Unveränderte Parent-/Originalbelege, normalisierte Diffs, Import-/Runtimeclosure, Gates false und genaue Pins sichern.
- [x] Bereinigten Bericht/Plan committen, kompakten Handoff für unabhängiges Root-Review.
- [ ] Root: unabhängig prüfen, separat einfrieren; ausschließlich Root entscheidet über einen tatsächlichen Folgelauf.

## Restrisiken

Die tatsächliche Flug-/Pickup-Folge nach Raw 212 fehlt. Ein bestandener Replay beweist nur die Behandlung des beobachteten Übergangs und die sichere Eingaberücknahme. Neue native Bewegungsdaten können weiterhin konservativ abgewiesen werden. Alle Schuss-/Treffer-/Erstzustands-/Qualifikationsbehauptungen bleiben false; B bleibt unbegonnen.

## Abschlussnachweis

174/174 private Tests PASS in 1,251 s;19 gezielte Tests PASS in 0,456 s. Vollständiger tatsächlicher Replay bisRaw 212:27 RD-Paare/66Rollenframes/16vorhandene Eingabequittungen, kein 17. Down. Ein neuer Same-Tick-Ankergegenfall wurde separat RED→GREEN nachgewiesen.

Bericht: docs/reports/2026-11-12-a1-flight-transition-v4.md
Manifest-SHA256:330c5c3b972bb6e83d3f573f1105b4ee3077559a8edc3b20865967d811339e71
Normalisierter Delta-SHA256:ec58c4d82fa06f9eda9f11575982cc8e490df1e4ec6549914e8d6d09a6763f61
Testquittung-SHA256:c0fc478c5690fbd451933c29e8f5865d678dd06b64714cfe79b224a998da759d

48 Runtime-/44 eigene-/96 Evidenz-Pins;126 Parentdateien unverändert,18 eigene Runtime-Dateien bytegleich. Keine nativen Starts/Builds/Root-/Produktionsänderungen. Der originale111716-FAIL bleibt unverändert und alle Abnahmeflags bleiben false; die nachRaw 212 fehlenden Zustände werden nicht ergänzt.
