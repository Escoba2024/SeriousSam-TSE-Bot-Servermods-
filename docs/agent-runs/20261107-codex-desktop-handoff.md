# ssam.ai – Übergabe für Codex / Desktop, 7. November 2026

## Zuerst lesen

Der Nutzer möchte am Desktop weiterarbeiten. Diese Übergabe startet keinen Agenten und erteilt keine zusätzliche Produktivfreigabe. Nicht von vorne anfangen: vorhandene Quellen, Tests und den gespeicherten Plan übernehmen. Vor weiteren Änderungen den tatsächlichen Projektstand und mögliche andere Writer prüfen.

**Wichtig: Die Cecil-Wegpunkte sind vorbereitet und offline getestet, aber NICHT live ausgerollt.** Der laufende Dev-Stand und der neue Cecil-Kandidat sind zwei unterschiedliche Dinge.

## Speicherorte und verbindlicher Stand

- Repository: `Escoba2024/SeriousSam-TSE-Bot-Servermods-`.
- GitHub-Übergabezweig: `handoff/20261107-cecil-navigation`. Dieser Zweig basiert auf GitHub `main` bei `ab0c7400353a108f8461bb82280c539fdfe81499` und enthält die Übergabedokumentation. Er ist nicht mit dem vollständigen lokalen Entwicklungszweig gleichzusetzen.
- Autorisierter Hetzner-Host: `ubuntu-4gb-nbg1-2`.
- Vollständiger lokaler Entwicklungs-Worktree: `/srv/tse-redstation-supply-20261107`.
- Lokaler Entwicklungszweig: `agent/ai/20261107-redstation-supply`.
- **Lokaler Sicherungscommit der Cecil-Arbeiten: `5eb8d19ef0784822636f114e57b2f809f476820a`.** Nachricht: `handoff: preserve Cecil waypoint research, safe exporter and offline test evidence`.
- Vorheriger Stand: `73c680d6f4ecc39aee95472a30e017a24a743b39`; Source-Fix des laufenden Supply-Builds: `38e42ae84a8b147411f236e3e015187a27bc1e2a`.
- Der vollständige lokale Zweig ist **nicht als nach GitHub gepusht bestätigt**. Ein direkter Git-Push scheiterte an fehlenden HTTPS-Anmeldedaten. Diese Dokumentation wurde über die autorisierte GitHub-Verbindung gespeichert. Keine Tokens in Dateien oder Prompts eintragen.
- Die vorbestehenden unversionierten Dateien `docs/agent-runs/20261107-regression-after-review.log` und `supply-test` wurden erhalten, nicht gelöscht oder pauschal mit veröffentlicht.

Für reine Recherche reichen diese Übergabe und die nachfolgenden Befunde. Für Weiterentwicklung mit dem vollständigen Code zuerst den genannten Ubuntu-Worktree verwenden oder die ausgewählten Quellen auf sicherem, autorisiertem Weg synchronisieren. Ein frischer Checkout nur von `main` enthält nicht automatisch diesen Arbeitsstand.

## Schutz der laufenden Server

Nur der sechste, öffentliche Entwicklungsserver auf **Port 25650** (GameSpy 25651, Red Station) ist für geprüfte neue Kandidaten vorgesehen. Die fünf Produktivinstanzen auf **25600, 25610, 25620, 25630 und 25640** dürfen nicht geändert oder neu gestartet werden. Dedicated Server und menschliche Retail-1.07-Clients bleiben unverändert.

Vor Arbeiten lesen:

- `AGENTS.md` im tatsächlichen Entwicklungs-Worktree;
- `docs/decisions/2026-11-07-public-development-first.md`;
- `/srv/tse-development-policy.json`.

## Bereits live: Gen2 mit optionaler Waffenversorgung

Auf beiden Dev-Bot-Clients wurde zuletzt folgende GameMP.dll geprüft:

`ce559971ce4a1677c1b299a7d0c27f148fa4ecace2a55d45e006bdb1598ac6a4`

Die aktivierte Waffenversorgung verwendet weiterhin den **gemessenen 236-Knoten-Graphen**, nicht Cecils Originalgraphen. Installierte Graph-SHA256:

`a9ed23e0212cc3fbd280d50058a66e678260138167bd1ce570680bacd237ac3f`

Runtime: `/srv/tse-development-live-20261107`; Clients `botA` und `botB`, jeweils vier lokale Spieler. Supply-Konfiguration: `bot_bSupplyNavigation=1`; klassische Kampfsteuerung, nicht vollständige Cecil-KI.

### Historische Live-Evidenz dieses Gesprächs

Beide früheren kurzen Canary-Tests bestanden. Eine zusätzliche Beobachtung am 07.11.2026 von **16:24:55 bis 16:26:25 Europe/Berlin** (90,62 s) zeigte:

- alle acht Dev-Bots bewegten sich und erzeugten Schussaktionen;
- 16 aktive Supply-Stichproben, davon 10 mit Wegpunktbezug;
- sieben neue Waffenaufnahme-Ereignisse, darunter zweimal Raketenwerferbesitz;
- 50 Kampf-Waffenstichproben: 47 Colt, zwei Messer, eine Doppelflinte;
- insgesamt +31 Frags der Dev-Bots;
- keine der ausgewerteten neuen Sync-/CRC-/Join-/Absturz-Fehlermarken im beobachteten Bot-Logabschnitt;
- Dienst-, DLL- und Konfigurations-Snapshots während der Beobachtung unverändert.

Dies ist begrenzte historische Evidenz, keine aktuelle Dauerzustandsgarantie, kein kontrollierter A/B-Nachweis höherer Kampfstärke und keine vollständige Human-Client-Abnahme. Nicht jede Aufnahme lässt sich kausal der Routenlogik zuschreiben.

Private Rohbelege bleiben auf Ubuntu:

`/srv/tse-development-live-20261107/evidence/live-check-20261107T152454Z/`

Darin insbesondere `report.json` und `RESULT.md`. Frühere Canaries: `evidence/supply-rollout-001/`.

### Reproduzierte offene Waffenwahl-Lücke

Der Supply-Planer beendet die Suche nach dem Erwerb einer Zusatzwaffe. Die klassische `SelectWeapon`-Prioritätsliste schließt Raketenwerfer jedoch aus. Mit Raketenwerferbesitz wählt sie bei den getesteten Entfernungen 5/20/40 weiterhin den Colt. Dies wurde mit den zum laufenden Build passenden Quellen reproduziert; es ist **noch nicht behoben**. Cecil-Wegpunkte allein lösen diese Waffenwahl-Lücke nicht.

## CecilBotMod-Untersuchung und tatsächliche Übernahme

Originalreferenz: `DreamyCecil/CecilBotMod` bei Commit

`953b477e53fdc5a5d84c8ae8d759c84fdf6c973c`

Lokaler Referenzklon: `/srv/tse-cecilbot-reference-20261020`.

Originaldatei: `Cecil/Navmeshes/RedStation_5AF1A276.nav`.
SHA256:

`70e2839587b0f14c024ef978579133e84eed594a3cbbd0fa1f1db98d99aa37c6`

Die BNMV-v6-Datei wurde vollständig strukturell gelesen: **12.245 Bytes, 193 Punkte, 879 gerichtete Verbindungen**. Referenzformat wurde gegen `Navmesh.cpp`, `PathPoint.cpp`, `PathPoint.h` und die Bewegungslogik geprüft. Cecils Punkte enthalten unter anderem Sprung-, Override-, Teleport- und Sperr-/Entity-Semantik. Der Dateinamenssuffix ist ein Levelpfad-Hash, kein Beweis identischer Map-Inhalte.

Der bestehende strikte Parser aus der früheren Projektanalyse wurde wiederverwendet, nicht nochmals parallel neu geschrieben. Der konservative Export übernimmt **172 Punkte und 279 beidseitig vorhandene Geh-Verbindungen**. 21 spezielle beziehungsweise entityabhängige Punkte sowie 165 nur einseitige Verbindungen zwischen den verbliebenen Punkten wurden nicht als normale Gehwege übernommen. Keine erfundenen Rückrichtungen, keine willkürliche Koordinatenverschiebung.

Der Kandidat ist absichtlich **keine vollständige Cecil-Parität**: Originalradien werden als Herkunftsdaten erhalten, aber die bestehende Ankunftstoleranz bleibt aktiv. Sprünge, Türen/Sperren, Teleports und vollständige gerichtete Routen sind nicht integriert.

Graphvergleich (nur strukturell):

- Original Cecil: eine schwach zusammenhängende Komponente mit 193 Punkten; daraus folgt keine vollständige gerichtete oder native Begehbarkeit.
- Konservativer Kandidat: 18 Komponenten, größte 105 Punkte.
- Bisheriger gemessener Graph: 236 Punkte, 1.273 gespeicherte Kanten, 27 Komponenten.

Weniger Komponenten oder andere Knotenzahlen beweisen keine bessere Navigation. Collision/Floors und tatsächliche Routen müssen im Originalspiel geprüft werden.

## Gesicherte Dateien im lokalen Commit

- `tools/parse_cecil_navmesh.py` – strikter Parser und konservative Exportfilter;
- `tools/export_cecil_walk.py` – reproduzierbarer Export mit SHA256-Pin, Ausgabe nur in neues Staging-Verzeichnis;
- `tools/test_parse_cecil_navmesh.py`;
- `tools/test_cecil_walk_export.py`;
- `tools/test_cecil_walk_cli.py`;
- `poc/candidates/cecil-waypoints-20261107/RedStation.cecil-walk.nav`;
- `poc/candidates/cecil-waypoints-20261107/provenance.json`;
- `poc/candidates/cecil-waypoints-20261107/test_existing_graph.cpp`;
- `docs/superpowers/specs/2026-11-07-cecil-waypoint-adoption-design.md`;
- `docs/superpowers/plans/2026-11-07-cecil-waypoint-adoption.md`;
- `docs/agent-runs/20261107-cecil-waypoint-adoption.md`;
- `docs/agent-runs/20261107-cecil-verification.json`.

Candidate-Graph SHA256:

`ae9fcdb72277cc97dc746d2be986ad4c1adc95c09215abd78e3dbbd4e3c67ee1`

Aktuelle Supply-Quellen für den Vergleich stehen unter `poc/candidates/redstation-supply-20261107/`. Der vollständige native Source-Overlay bleibt zusätzlich unter `/srv/tse-redstation-supply-native-overlay-20261107`; Buildbeleg: `/srv/tse-redstation-supply-build-002-20261107/manifest.json`. Keinen neuen Build ohne Quellen-/DLL-Abgleich und separate Abnahme als qualifiziert ausgeben.

Vorhandene Copyright-/GPL-2.0-Hinweise erhalten. Keine Retail-Binaries, Zugangsdaten oder Spieler-Rohlogs veröffentlichen.

## Tests – vor der lokalen Sicherung erneut geprüft

Verifikation: **07.11.2026, 15:45:51 UTC**.

- 15 Python-Tests erfolgreich, einschließlich Parser, Exportfilter und CLI.
- Bestehender C++-Graphloader und SupplyPlanner: 172 Knoten, **12.040 erreichbare geordnete Knotenpaare**, 17.372 korrekt unerreichbare Paare, **0 Fehler**.
- Derselbe Kompatibilitätstest mit AddressSanitizer/UndefinedBehaviorSanitizer erfolgreich.
- Botcore-Regressionssuite erfolgreich, einschließlich **555 Human-AI-Prüfungen ohne Fehler**.
- Erneuter Export ergab identische Graph-Bytes und identischen SHA256.

Einschränkung: Ein zusätzlich verschärfter Build mit `-Werror` scheiterte an drei `maybe-uninitialized`-Warnungen im unveränderten SupplyPlanner. Mit den bestehenden Projektflags wurde gebaut und getestet. Diese Warnungen wurden nicht behoben oder als unbedenklich qualifiziert.

Reproduzierbare Offline-Prüfung im vollständigen Worktree:

```bash
python3 -m unittest -v tools.test_parse_cecil_navmesh tools.test_cecil_walk_export tools.test_cecil_walk_cli

g++ -std=c++17 -O2 -Wall -Wextra \
  -Ipoc/candidates/redstation-supply-20261107 \
  poc/candidates/cecil-waypoints-20261107/test_existing_graph.cpp \
  -o /tmp/ssam-cecil-compat

/tmp/ssam-cecil-compat \
  poc/candidates/cecil-waypoints-20261107/RedStation.cecil-walk.nav 172

make -C poc/botcore test
```

## Belegter Rollout-Blocker – nicht umgehen

`operate_tse_service` lehnte `ssam-development-bota.service` mit **`Service not explicitly permitted`** ab. Lesender Statuszugriff ist keine Neustartberechtigung. Ein Wechsel von Chat zu Work oder Codex ändert diese Freigabeliste nicht.

**Keine Umgehung über systemctl, SSH, RDC-Shell, alternative Prozesskills oder stillschweigende Erweiterung von Rechten.** Zuerst den vorgesehenen, vom Eigentümer geprüften Verwaltungsweg für genau die Dev-Dienste herstellen. Die fünf Produktivinstanzen bleiben geschützt.

## Gezielte Fortsetzung am Desktop

1. Vollständigen lokalen Sicherungscommit und aktuelle Änderungen/Claims prüfen; andere Writer und vorbestehende Dateien erhalten. Nicht pauschal `reset --hard`, `clean` oder neue parallele Implementierungen starten.
2. Gesicherten Export/Tests prüfen. Die konservative Teilübernahme kritisch gegen den Wunsch nach Cecil-Verhalten abgleichen; ausgeschlossene gerichtete/spezielle Routen nicht stillschweigend als erledigt betrachten.
3. Den autorisierten Dev-Rolloutweg klären. Bis dahin keine Liveänderung. Bei zulässigem Test zuerst aktuelle Backups/Hashes und Rollback sichern, externe Spieler berücksichtigen und native Kollisions-/Etagen-, Wegpunkt-, Pickup-, Bewegungs-/Schuss- sowie Sync-/CRC-Belege sammeln.
4. Waffenwahl-Lücke als getrennten, reproduzierten Befund erhalten. Keine Aussage, dass der Cecil-Graph sie bereits löst.
5. Fortschritt, tatsächlich durchgeführte Tests und Grenzen persistent aktualisieren. Erst nach nachgewiesenem Abschluss oder belegtem Blocker beenden; keine unbelegte Produktiv- oder Langzeitfreigabe.

**Status bei Übergabe:** Recherche und konservativer Export lokal gesichert; Offline-Tests bestanden; Cecil-Liveintegration nicht durchgeführt. Keine weitere Entwicklung läuft aus diesem Chat unbeaufsichtigt weiter.
