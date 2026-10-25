# Session-Hybrid-Lab – Ressourcenmodell 4/8/16 Bots (Architekturen A/B/C1)

**Datum:** 2026-10-25 · **Status:** Modell + Offline-Reproduktion · **Evidenz:** `[T]` = zitierte Hetzner-/PR-Messung, `[D]` = DERIVED (Rechenoperation auf Ankern), `[P]` = PROJECTED (Extrapolation), `[A]` = Architekturvorschlag

> **Keine Kapazitätsfreigabe.** Projektionen sind lineare Extrapolationen, keine Messwerte. In der LMArena-Sandbox wurde kein Live-Wine-Benchmark ausgeführt. Ressourcenmodelle sind eindeutig von echten Wine-Messungen unterschieden (Evidenzklasse pro Zelle).

## 1. Modellgrundlage

Das Modell wird exklusiv parametrisiert durch gemessene Hetzner-Anker in
`poc/research/session-hybrid-lab/measurements.json` (jede Zelle zitiert ihre
Quelle, überwiegend PR #45/#47/#51):

* Host: 3819 MiB RAM, 2 vCPU, 0 Swap [T].
* Architektur A (status quo): 1 DedicatedServer + 2 Viererclients, 8 Bots,
  Server-RSS 50,2 MiB, je Client ~184,2 MiB RSS, Test-cgroup-CPU 69,031 %
  [T].
* Architektur B (PR #47): 1 Client pro Bot, Einzelclient cgroup-Peak 555,8 MiB
  / 51,5 % CPU, 4 Clients 1158,0 MiB / 72,5 % CPU; 8-Client-Läufe am
  1068-MiB-Reserve-Gate blockiert [T]; Redstation 7 joined + 1 joining peaked
  bei 1725,9 MiB [T].
* Abgeleitet: marginaler B-Client ~200,7 MiB; Basisoverhead ~355,1 MiB [D].

Basiswerte für das C1-RAM-Modell [D]: Server 50,2 MiB, Client 184,2 MiB (RSS,
geteilte Seiten mehrfach gezählt – PSS noch offen [N]).

## 2. Ressourcenmodell 1/4/8/16

Erzeugt mit `python3 resource_model_hybrid.py` (reproduzierbar).

| Arch | Bots | Clients | RAM MiB | RAM-Evidenz | CPU %Kern | CPU-Evidenz | Host-Fit (3119 MiB) | Pro-Bot Join/Leave |
|---|---:|---:|---:|---|---:|---|---|---|
| A | 1 | 1 | 234,4 | [D] | 36,6 | [D] | fits | nein (ganzer Client) |
| B | 1 | 1 | 555,8 | **[T]** | 51,5 | **[T]** | fits | ja |
| C1 | 1 | 1 | 234,4 | [D] | 36,6 | [D] | fits | pro-Bot (Latenz) |
| A | 4 | 1 | 234,4 | [D] | 39,0 | [D] | fits | nein (ganzer Client) |
| B | 4 | 4 | 1158,0 | **[T]** | 72,5 | **[T]** | fits | ja |
| C1 | 4 | 1 | 234,4 | [D] | 39,0 | [D] | fits | pro-Bot (Latenz) |
| A | 8 | 2 | 418,6 | **[T]** | 69,0 | **[T]** | fits | nein (ganzer Client) |
| B | 8 | 8 | 1960,9 | [P] | n/a | [P] | fits | ja |
| C1 | 8 | 2 | 602,8 | [D] | 69,0 | **[T]** | fits | pro-Bot (Latenz) |
| A | 16 | 4 | 787,0 | [P] | 131,2 | [P] | fits | nein (ganzer Client) |
| B | 16 | 16 | 3566,7 | [P] | n/a | [P] | **exceeds** | ja |
| C1 | 16 | 4 | 971,2 | [D] | 131,2 | [P] | fits | pro-Bot (Latenz) |

C1-RAM = A-Basis (50,2 + Clients × 184,2) + transienter +1-Client pro
gleichzeitigem Roster-Restart-Fenster (konservativ stop-vor-start). Bei 1 Bot
fällt kein Restart an (kein Co-Resident), daher kein transienter Aufschlag.

## 3. Koexistenz mit öffentlicher Flotte (`--coexist-public`)

Wird die gemessene öffentliche Acht-Bot-Flotte (cgroup-Snapshot 530,9 MiB)
vom Budget abgezogen, schrumpft das Budget auf 2588 MiB. B16 überschreitet
dann das Budget; C1/A passen weiterhin. Reproduzierbar:

    python3 resource_model_hybrid.py --coexist-public --bots 8,16

## 4. Bewertung

| Kriterium (8 Bots) | A | B | C1 |
|---|---|---|---|
| Echte Einzel-Session | ✗ | ✓✓ | ✓ (Latenz/Restart) |
| RAM | ✓✓ 419 MiB [T] | ✗ ~1,9 GiB [P] | ✓✓ ~603 MiB [D] (mit Restart-Transient) |
| CPU | ✓✓ 69 % [T] | ✗ ~100 % [P] | ✓✓ 69 % [T] (gleiche Prozesszahl wie A) |
| Isolation / Blast-Radius | ✓ (4 Bots/Prozess) | ✓✓ (1 Bot) | ✓ (wie A je Prozess) |
| Join/Leave-Granularität | nur ganzer Client | echt pro Bot | pro-Bot (Batch-Fenster) |
| Qualifizierungsaufwand | 0 (produktiv) | hoch (blockiert) | mittel (nur Orchestrierung) |
| Vanilla-Kompatibilität | ✓ [T] | ✓ [T] | ✓ (nur Start/Stop außen) |

**Empfehlung:** C1 liefert unabhängig wirkende Sessions zum gemessenen A-Preis
(8 Bots ≈ 419 MiB + Restart-Transient) ohne neue Engine-Fähigkeit. C2
(Dynamic-Slot, E1/E2) bleibt unverifiziert [N] und ist keine Voraussetzung.

## 5. Offene Messwerte

* PSS statt RSS (geteilte Wine-Seiten ehrlich atribuieren) – Messauftrag M2
  aus PR #56, noch nicht ausgeführt [N].
* Transiente RAM während Roster-Restart-Fenstern (messbar über cgroup-Peak
  pro Phase) [N].
* KSM/zram-Potenzial für die gemeinsame Lower-Layer [A, K1–K3 aus PR #56].
