# Serious Sam TSE 1.07 – Vanilla Bot Clients

Bots joinen als reguläre Netzwerkspieler über separate modifizierte BotClient-Prozesse. Dedicated Server, Engine, Entities und menschliche TSE-1.07-Clients bleiben unverändert. Eingaben entstehen ausschließlich über normale `CPlayerAction`-/`CPlayerSource::SetAction`-Pfade. Pro Prozess sind maximal vier lokale Spieler vorgesehen; acht Bots verwenden zwei getrennte Installationen.

## Aktuelle Integration – 21.10.2026

[Abnahmebericht mit 12 Punkten](docs/reports/2026-10-21-human-cpu-final.md),
[bereinigte Messwerte](docs/reports/2026-10-21-integrated-runtime-results.json),
[CPU-A/B mit drei Paaren](docs/reports/2026-10-21-qualified-cpu-ab.json),
[Buildbeleg](docs/reports/2026-10-21-integrated-gamemp-build.json).

Neue integrierte DLL `7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835`: MSVC unter Wine gebaut, neue Retail-Multiplayer-Abnahme mit einem/vier/acht Bots bestanden. Die Acht-Bot-Stunde mit Originalclient dauerte 3600 s; alle acht Bots in jedem Fünfminutenabschnitt aktiv, null SYNCBAD/Disconnects und null Throttling. Human-KI mit fünf Spielstärken und sechs Personas sowie NullRender tatsächlich aktiv. Vier Bots: unveränderte alte DLL 103,593%, integrierte Legacy-Policy 22,658%, Human-Policy 21,305% eines CPU-Kerns; je ein Fenster, keine isolierte Human-Kausalität. Acht Bots sind die höchste neu gemessene Anzahl.

Öffentlich aktiv: **91.99.75.33:25600, acht Human-Bots**. Öffentlicher 600 s-Smoke bestanden, Original-Ingamebrowser zeigt Alpha-Gaming8/16, Beitritt aus dieser Liste und normales Originalspiel bestätigt. Vier unabhängige externe UDP-Queries erhielten vollständige Statusantworten. Der eigene Observer ist wieder geschlossen, acht Bots bleiben aktiv. Öffentliche Test-cgroup 69,031% eines Kerns, gesamter Zwei-vCPU-Host 35,333% ausgelastet. Eine Wine-Originalgegenstelle ersetzt keinen unabhängigen Windows-Spieler-PC. Kein 24/7- oder 16+-Bot-PASS. Geschütztes 61DC-Release und frühere Installation bleiben bytegenau erhalten. [Betrieb und Rückfall](docs/reports/2026-10-21-hetzner-operations.md).

Die folgenden datierten Abschnitte beschreiben historische Kandidaten und ihren damaligen Nachweisumfang.

## Nachweisbarer Stand – 13.10.2026

Die [Fortsetzung vom 13.10.2026](docs/reports/2026-10-13-serverbrowser-preflight.md) bestätigt zusätzlich das exakte sparsame Acht-Bot-Profil über 601,984 s Steady-Betrieb und 595,771 s unabhängige vollständige Spielerabfragen. Öffentliche 333networks-Listung, externe UDP-Erreichbarkeit und Vanilla-Browser bleiben offen; Shadow Neo Lite ist ein Cloud-Testsystem. Die bisherigen Abnahmen behalten ihren unten angegebenen Geltungsbereich.

| Bereich | Stand |
|---|---|
| Phase 1: Retail-PoC | BESTANDEN: Build/CRC/Join, Vanilla-Observer, native Actions, Schaden/Frag, Tod/Respawn, kontrollierte Mapwechsel/Reconnects, regulärer Shutdown, eigene 10-/30-/60-Minuten-Läufe plus unabhängige Stundenwiederholung. |
| Phase 2: vier Bots | BESTANDEN: zwei bis vier getrennte lokale Spieler; eigene Vier-Bot-Stunde auf Shadow am 08.10. mit 240 vollständigen aktiven Minutenfenstern. |
| Phase 3: acht Bots / 2 × 4 | LOKAL BESTANDEN: eigene Recovery-Stunde, 480 aktive Bot-Minuten, vollständige native Namen/Slots, Human-Lifecycle und BotClient-Ersatz. Kurze Mehrkarten-/Failed-Join-/Hard-Exit-Szenarien separat geprüft. |
| AutoCombat + Hinderniserholung | LOKAL BESTANDEN mit aktuellem 61DC-Kandidaten: eigene Acht-Bot-KI-Stunde, 3697.291299 s vollständige Serverabfragen, 480 vollständige 20-Hz-Minutenfenster und 69 reguläre Brush-Advances ≥ 2 m; jeder Bot mit belegtem Fortschritt. |
| Sparsames `LocalBotRelease.ini` | Separater Lifecycle-Smoke BESTANDEN: 176.503899 s Serverabfragen. Dieser Smoke ersetzt keine weitere KI-Stunde. |
| Population Manager | TEILWEISE: geprüfte reine Populationsregeln und Fleet-Werkzeuge; dauerhafter automatischer Supervisor und robuste Human/Bot-Erkennung offen. |
| Navigation und Betrieb | Globale Wege, Items, Boden-/Abgrundsicherheit, weitere Waffenfamilien, Coop, öffentliche Serverbrowser-/333networks-Prüfung, 12/16 Bots, mehrere Server und 24/7 offen. |

Der aktuell nativ qualifizierte KI-Kandidat hat DLL-SHA256 **`61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9`**. Es wird keine DLL mit diesem Repository ausgeliefert. Eine neu gebaute DLL benötigt ihre eigene Runtime-Abnahme. Die 1124 im Observer bezeugten Kampfkills gehören zum gesamten gespeicherten Lauf einschließlich Lifecycle/Vorlauf/Teardown; sie sind keine ausschließlich dem Stundenfenster zugeordnete Killzahl.

Der Ground-Lookahead-Versuch vom 11.–12.10. hat nach BotClient-Ersatz native Sync-Fehler und **keine bestandene Abnahme**. Seine Quellen und Rohbelege sind lokal privat gesichert und außerhalb dieses qualifizierten Quellreleases. Der aktuelle Bericht dokumentiert den offenen Versuch.

## Historischer eigenständiger P0-Kandidat (ursprünglich 22.10.2026 bezeichnet)

Der P0-Kandidat `poc/candidates/p0-nullrender-20261022/` ergänzt die
GameMP-Quelle um eine timerunabhängige Evidenzspur (`BotTelemetry.csv`) und
einen opt-in Null-Renderer (Rücksprung vor `tm_csHooks`). Der Quellstand wird
per `apply.sh` aus dem qualifizierten Release-Baum erzeugt (Hash-geprüft), nie
in ihn hineingeschrieben. **Die damalige eigenständige Kandidatenbeschreibung enthielt keine Build-/Runtime-Abnahme**; aktuelle Integration und Messungen stehen oben.
die qualifizierte DLL `61DC...` und der öffentliche Server bleiben unverändert.
Analyse und Verfahren:
[P0-Diagnose](docs/reports/2026-10-22-p0-bot-tick-diagnosis.md),
[Messprotokoll](docs/reports/2026-10-22-cpu-measurement-protocol.md),
[Null-Render/Headless-Pfade](docs/research/2026-10-22-nullrender-and-headless-paths.md).
PR #40 bleibt Draft.

## Einstieg / Übergabe an eine andere KI

1. [Aktueller Entwicklungsstand und Belege](docs/reports/2026-10-12-shadow-development-status.md): Meilensteine, exakte Kandidaten, Messwerte, Fehlerhistorie, Einschränkungen und Prioritäten.
2. [Lokales Release und Reproduktion](poc/LOCAL-RELEASE.md): Vorbereitung, Start/Stop, Rücknahme, SDK-Pins und eigene native Abnahme.
3. [Phase-3-Abnahme](poc/PHASE-3-ABNAHME.md): Recovery-DLL und separate Acht-/Zweibot-Stunden.
4. [Publikationsprüfung](docs/reports/2026-10-12-publication-validation.md): Regressionen und Prüfung aus einem separaten Checkout.
5. [Source-Provenance](docs/reports/2026-10-12-source-verification.json) und [bereinigte Acceptance-Summary](docs/reports/2026-10-12-acceptance-summary.json): Original-/Veröffentlichungs-Hashes und genaue Prüfumfänge.
6. [Architektur](docs/superpowers/specs/2026-09-30-vanilla-server-bots-design.md), [Runbook](poc/RUNBOOK.md), [historischer Retail-Bericht](CODEX_WINDOWS_POC_REPORT.md).
7. [Bot-KI: Profile, Wahrnehmung und nächster Schritt](docs/reports/2026-10-20-bot-ai-profiles-and-perception.md): Lieferung A–H, Patch `0008`, 555 Offline-Checks; Windows-Build und Runtime-Abnahme ausdrücklich **offen**.

`poc/release/gamemp/` enthält die 13 erfassten GameMP-Anpassungen des aktuellen Kandidaten. Vor der Veröffentlichung stimmten sie mit dessen originalen Buildquellen überein; der vollständige Quellvergleich umfasst 32 Game-Eingaben. Die veröffentlichten Dateien tragen zusätzlich datierte GPL-Änderungshinweise. Die Provenance-Datei enthält beide Hashes und den exakten Hinweisblock; ausschließlich dessen Entfernung stellt die ursprünglichen Quellen wieder her. Der qualifizierte DLL-Hash bleibt unverändert.

`poc/botcore/` enthält enginefreie Regeln und sieben C++-Tests (`make test`, `make smoke`, `make bench`), `poc/scripts/` Fleet-/Release-/Build-/Audit-Werkzeuge, `tools/` die bisherigen lokalen Sicherungshüllen und älteren unabhängigen Auditoren. `poc/patch/gamemp/` und Patches `0001`–`0007` dokumentieren vorangegangene Entwicklungsstufen, `0008` die profilgesteuerte Bot-KI (standardmäßig inaktiv); für den aktuellen vollständigen Quellbuild die Release-Anleitung verwenden.

Build: SE1-ModSDK `aa7869c2c2c4db0562281814d0ac3784e6b9d6f0`, Includes `94ff8cd0e63941f8601294350b616472f772ed51`, VS2022/v143/x86 und Windows SDK 10.0.19041.0. SDK und rechtmäßig vorhandene Retail-Kopien werden separat benötigt. Lokale Daten liegen unter dem ignorierten `.codex/`; Git enthält keine privaten Profile, Runtime-Rohlogs, Zugangsdaten, Retail-Binaries oder Spieldaten. [Lizenzen und Herkunft](THIRD-PARTY-NOTICES.md).
