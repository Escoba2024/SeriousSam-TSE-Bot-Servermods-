# Parallele Arbeitsteilung: GPT-Agent (Shadow/Hetzner) × Arena-Sitzung `ad36e19b`

**Stand: 21.10.2026**, Base `fdfc46e` (= `origin/main`, PR #45 integriert).
**Zweck:** Dieses Briefing erlaubt zwei Agenten gleichzeitige, konfliktfreie Arbeit
ohne Warteschleife. Es ist ein Informationsstand nach
[README.md](README.md) und [HANDOFF.md](HANDOFF.md), **keine** Freigabeinstanz
und kein Lock. Kanal für `STARTED`/`HANDOFF` bleibt
[Issue #18](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/issues/18).

## 1. Rollenteilung (gilt für diese Runde)

| Wer | Umgebung | Schreib-Scope (diese Runde) | Nicht sein Scope |
|---|---|---|---|
| **GPT-Agent** (Codex/ChatGPT, Nutzerleitung) | **Shadow/Windows + Hetzner**: MSVC/v143, Wine, native Retail-Läufe | Eigene offene PRs: `codex/*`- und `agent/*`-Zweige, eigene Worktrees; native Gates & Runtime in **isolierten** Kopien | `docs/coordination/**` dieser Runde; Arena-Zweige `arena/e39db2a9` (#42), `arena/fc36ae4f` (#44); fremde Worktrees |
| **Arena-Sitzung `arena/ad36e19b`** (diese) | Linux-Sandbox: kein Wine, kein MSVC, kein Hetzner-Zugang | `docs/coordination/**`, Offline-Doku, gelesen-basierte PR-Reviews, portable Tests auf `main` | Jede native/Wine-/Hetzner-Laufzeit; `poc/release/**`-Produktivdateien; 61DC-DLL |

**Dritte offene Lanes (nicht anfassen):** `arena/fc36ae4f` → PR #44 (Bot-AI,
**merge-konfliktgefähig**), `arena/e39db2a9` → PR #42 (Independent Review),
Branch `arena/89ecfb03` (P0-Diagnose-Candidate, siehe
[P0-Report](../reports/2026-10-22-p0-bot-tick-diagnosis.md)).

## 2. PR-Iststand 21.10.2026 (Ist, kein Anspruch auf Vollständigkeit)

Alle offenen PRs waren mergebar, **keine** automatischen Checks konfiguriert –
Testbelege gehören wie gewohnt in PR/Bericht. ‚Nächster Schritt‘ ist eine
Empfehlung, keine Anordnung.

### GPT-Lane – frisch (20.–21.10.), zuerst dranbleiben

| PR | Branch | Status | Nächster Schritt |
|---|---|---|---|
| **#41** | `agent/cpu-opt/20261021-hetzner-qualified-harness` | Draft, MERGEABLE | Kleiner Harness-Fix (Rechte, Bot-Verifikation vor A/B): gegen neue Tests abrunden, Review-Kommentare beantworten, ggf. undraften |
| **#40** | `agent/cpu-opt/20261021-null-render` | Draft, MERGEABLE, im Repo als *BLOCKED* markiert | Blockade ist A/B-/P0-Diagnose (kein `bot_bEnabled`-Nachweis, Cap-Konfundierung). Reihenfolge steht in [TECHNICAL_HANDOFF §9](TECHNICAL_HANDOFF-2026-10-21-cpu-opt.md): **erst** 0008-Marker-Lauf → **dann** gültiges A/B → **dann** ikonisch. Draft bleibt, bis 1–3 belegt |
| **#46** | `agent/ops/20261021-next-phase` | Draft, MERGEABLE | Neuester Ops-Zweig (Disk-Recovery/Monitoring/isolierte Restart-Qualifizierung): portable Nachtests dokumentieren, Scope gegen #41/#40 abgrenzen |
| **#47** | `agent/identities/20261021-sessions` | Draft, MERGEABLE | Neuester Identitäten-/Sitzungsplaner-Zweig: portablen Kern fertigstellen, Retail-Teil offen als `NOT_TESTED` stehen lassen |
| **#39** | `agent/bot-ai-cecil-20261020` | Draft, **CONFLICTING** | Vor Rebase Modul-Overlap mit PR #44 (Arena, A07-Bot-AI) prüfen; nur eigener Branch, dann seriel statt blind rebasen |

### GPT-Lane – Review-fähig von 17.10. (stille seit 4 Tagen)

| PR | Branch | Status | Nächster Schritt |
|---|---|---|---|
| **#17** | `codex/chatgpt-vanilla-preflight-framing-…` | **offen**, MERGEABLE | Einziger nicht-Draft der alten Reihe: PR-Kommentare seit 17.10. beantworten, 8 Portable-Preflight-Tests grün dokumentieren, entscheiden: mergeen oder in Draft zurück |
| **#7** | `codex/supervisor-readiness-recovery-20261016` | **offen**, MERGEABLE | Readiness-Recovery: Familie #3→#7→#10… beachten – nicht isoliert blind mergen, integrierten Kandidaten (#12) laut [Koordination](README.md) bevorzugen |
| **#14** | `codex/cloud-query-evidence-validation-…` | Draft, MERGEABLE | Fleet-UDP-Evidenz: eigene QA-Familie, eigenständig ab schließbar |
| **#16** | `codex/chatgpt-sync-log-regressions-…` | Draft, MERGEABLE | Sync-Parser-Regressionen: eigenständig ab schließbar |
| **#21** | `codex/chatgpt-syncdump-compare-…` | Draft, MERGEABLE | Sync-Dump-Vergleich (braucht nur Reproduktion mit dem privat belegten Snapshot-Pfad, keine neue Runtime) |
| **#15** | `codex/rdc-retail-harness-restore-…` | Draft, MERGEABLE | **Seriell** mit #12: beide ändern `tools/Test-Publication.ps1` – erst nach #12-Integration fortsetzen (Regel aus Koordination README) |

### GPT-Lane – Supervisor-/QA-Familie (schwerer, Windows-Gates)

- **#3 → #7 → #10** und **#8 → #11**, zusammengeführt in **#12**, danach **#13**
  (Lock-Marker-Schutz). Integrationsreihenfolge siehe Koordination README;
  **ein** gemeinsamer Kandidat, keine sechs Einzelmerges.
- **#12/#13** nur nach dokumentiertem W1 (Windows/PS5.1) und W2 (begrenzter
  Retail-Test) bewerten – dafür hat allein die Shadow-Lane die Umgebung.
- #26/#27/#28 (A03/A01-Scope-Hardening, Offline-Scope-Gate), #22 (Docs-Audit),
  #24 (A08 ABI/CRC, read-only) sind in sich abgeschlossene Pakete: jeweils
  portable Tests + Handoff, dann reviewbar.

### Nicht GPT-Lane

- **#42**, **#44** (andere Arena-Sitzungen; #44 hat Merge-Konflikte gegen
  neuen `main` – Owner löst das), **#3** bleibt WIP-Eltern-PR der Familie.

## 3. Priorisierte Queue für den GPT-Agenten

1. **P1 – laufende Woche:** #41 zuerst (klein, unmittelbar brauchbar für alle
   CPU-Läufe), dann #46 und #47 portabel absichern. Parallel: #39-Konfliktlage
   gegen #44 klären, ohne fremden Zweig anzufassen.
2. **P2 – P0-Kette (Runtime, braucht Hetzner/MSVC):** TECHNICAL_HANDOFF §9
   abarbeiten: Patch `0008` bauen + Marker-Lauf (30 min) → gültiges A/B (2 h)
   → ikonisch-Experiment → `DedicatedServer +connect`-Test. Ergebnis als neuer
   Candidate mit eigener SHA256, **nie** über die qualifizierte `61DC…`-DLL.
   Details: [P0-Report](../reports/2026-10-22-p0-bot-tick-diagnosis.md),
   [Messprotokoll](../reports/2026-10-22-cpu-measurement-protocol.md).
3. **P3 – alte codex-Reihe:** #17 → #14 → #16 → #21 → #7 (Review-Antworten,
   Testbelege, undraften/entscheiden); #15 erst nach #12.
4. **P4 – Familie:** #12+#13 als Integrationskandidaten vorbereiten (W1/W2-Gates
   auf Shadow), dann #26/#27/#28, #22, #24 in Ruhe nachziehen.
5. **Nie vergessen:** Offene Sync-Frage `Too many bad syncs` und externe
   Sichtbarkeit haben laut AGENTS.md Vorrang vor Skalierung/Kosmetik.

## 4. Kollisions- und Sicherheitsregeln (Kurzfassung – gilt unverändert)

1. **Zwei Writer, ein Worktree – nie.** Vor Beginn:
   `git worktree list --porcelain`, `git status --short`; eigene Worktrees
   außerhalb des geteilten Checkouts; `codex/*`- und `agent/*`-Zweige der
   anderen Sitzungen nicht überschreiben, kein Force-Push fremder Arbeit.
2. **Runtime nur mit technischem Exklusivnachweis** (Prozesse, Ports, PIDs
   prüfen): qualifizierte `61DC…`-DLL, produktive Ports, Hetzner-Spieler,
   fremde Ghidra-Projekte unantastet; isolierte Kopien mit eigenen Ports.
3. **Nichts als bestanden melden, was nicht getestet wurde.** Portable /
   Windows-PS5.1 / native Retail / WAN / Soak bleiben getrennte Evidenzstufen
   (`NOT_TESTED` ehrlich kennzeichnen). Kein `ser_iKickOnSyncBad=0`-Scheinfix.
4. **Konflikt ohne Warteschleife:** betroffene Ressource meiden, an unabhängiger
   Teilaufgabe weiterarbeiten, `CONFLICT` optional in #18 notieren.
5. **`STARTED`/`HANDOFF` sind Nachweise, keine Anfragen** – Vorlagen in
   [HANDOFF.md](HANDOFF.md).

## 5. Minimal-STARTED für diese Runde (Kopiervorlage in Issue #18)

```text
STARTED
slot: (optional)
ticket_or_pr: #18
goal: <Backlog-PR xyz zuerst | P0-Marker-Lauf | Koordination/Docs>
branch: <eigener>
worktree: <eigener>
write_scope: <eigene Pfade/PRs>
runtime_scope: NONE | ISOLATED_COPY | SHARED_RESOURCE (nur mit Exklusivnachweis)
check: existing_worktrees_and_writers_checked
```

Arena-Sitzung `ad36e19b` übernimmt in dieser Runde ausschließlich
`docs/coordination/**` auf ihrem eigenen Zweig – der GPT-Agent bearbeitet die
oben genannten PRs, ohne diese Dateien gleichzeitig zu schreiben.
