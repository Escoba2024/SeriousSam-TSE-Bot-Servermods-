# Item-Utility-AI – Entscheidungskriterien, Formeln und Schwellen

**Datum:** 25.10.2026 · **Agent 5** · Basis `107d28a`
**Code:** `poc/research/item-utility/include/` (`item_scoring.h`, `item_planner.h`, `item_profile.h`)
**Tests:** `poc/research/item-utility/tests/` (378 + 91 711 + 401 Prüfungen, alle grün)

Dieses Dokument ist die **verbindliche Beschreibung** der Entscheidungslogik: jede Formel, jede
Schwelle und jeder Abbruchgrund, den der Prototyp tatsächlich benutzt. Wer eine Zahl ändert,
ändert sie hier mit.

---

## 1. Grundmodell

Ein **multiplikatives Utility-Modell** mit Bedarfs-Gating:

```
base    = need · scarcity · capability
utility = base · threat · priority · time · distance · freshness · skill
```

Alle Faktoren liegen in dokumentierten Bändern; das Produkt bleibt in `[0, 2.0]`
(Property-Sweep über 4 000 Zufallswelten: Maximum 1,045). Dadurch sind **verschiedene
Item-Typen direkt vergleichbar** — die zentrale Lücke der Cecil-Vorlage.

Ein Item ist ein **Kandidat**, wenn `need` nicht verschwindet, `base > ε = 0.02`, `utility ≥
min_utility` (0,10–0,20 je Vorsicht), die Reisezeit im Budget liegt und keine harte Sperre greift.

---

## 2. Die zwölf geforderten Kriterien

### 2.1 Gesundheitszustand — `HealthNeed()`
```
hf = health / max_health
hf ≥ 0.98            → 0                       (voller Zustand: kein Bedarf)
hf ≥ 0.35            → (1 − hf) · 0.75
hf <  0.35           → max( (1 − hf) · 0.75 , 0.55 + 0.45·(1 − hf/0.35) )
```
**Konvex**: die letzten 10 % HP sind mehr wert als ein beliebiges früheres 10 %.
Beispiel: 20 % HP → Bedarf 0,743; 60 % HP → 0,300; 95 % HP → 0,038 (→ unter der Schwelle).
Zusätzlich **wertbewusst** über `capability` (2.3): ein +1-Trank bei 40 HP hat Nutzen ≈ 0,01 und
wird nicht angesteuert, ein +50-Trank bei 20 HP hat Nutzen ≈ 0,63.

### 2.2 Rüstungswert — `ArmorNeed()`
```
ArmorNeed = (1 − armor/max_armor) · 0.82      (0 bei ≥ 98 %)
```
Rüstung ist bewusst **etwas schwächer** gewichtet als Gesundheit (Faktor 0,82) und linear statt
konvex: Rüstung schützt, Gesundheit entscheidet.

### 2.3 Munitionsbestand — `AmmoNeed()`
```
nur wenn die Waffe im Besitz ist und Munition braucht (Klinge: kein Bedarf)
fill        = ammo / ammo_cap
deficit     = 1 − fill
pressure    = 0.35 + 0.65 · ammo_pressure        (0..1)
relevance   = 0.30 + 0.70 · rel                  (rel = Waffen-Score / bester Score)
need        = deficit · pressure · relevance
Notfall     : current ≤ 0 und rel > 0.75  →  need = max(need, 0.75)
```
`ammo_pressure` (aus `AssessSelf`): `1.0` bei **Munitionshunger** (keine geladene Fernkampfwaffe),
sonst 0,60 / 0,35 / 0,20 nach Füllstand der besten Waffe. Munition für eine **nicht besessene**
Waffe hat Bedarf 0 (unbrauchbar), Munition für eine Nebewaffe wird über `relevance` abgewertet.

### 2.4 Vorhandene Waffen — `WeaponNeed()`
```
nicht im Besitz:
   kein brauchbares Gewehr überhaupt      → 1.00   (nur Klinge/Bodenkampf)
   sonst  gain = (score(Kandidat) − score(best)) / score(best)
          gain > 0                        → min(1, gain)
          gain ≤ 0 (Downgrade)            → 0.10 · (1 − ammo_pressure)
im Besitz (Duplikat = Munition)           → 0.45 · AmmoNeed(diese Waffe)
```
Beispiel: nur Klinge + Schrotflinte in 12 m → Bedarf 1,0, Utility ≈ 0,45 → Ziel.
Laser im Besitz, Schrotflinte angeboten → Bedarf ≈ 0,08 → unter der Schwelle, kein Trip.

### 2.5 Entfernung zum Item — `DistanceFactor()` und Reisebudget
```
DistanceFactor = 0.65 + 0.35 · clamp(1 − d/40, 0, 1)          ∈ [0.65, 1.0]
travel_s       = d / move_speed + 0.35                        (Aufnahme-Overhead)
```
Harte Grenze: `travel_s > tuning.max_search_time_s` → **kein Kandidat** (`kOutOfRange`).
Die Geschwindigkeit kommt vom Aufrufer (`move_speed_mps`), nicht aus einer Konstante.

### 2.6 Sichtbare Bedrohungen — `ThreatFactor()`, `Exposure()`
```
proximity = clamp(1 − nearest_enemy_m / 25, 0, 1)      (0 wenn kein Feind sichtbar)
exposure  = proximity · (under_fire ? 1.0 : 0.55)
ThreatFactor = clamp(1 − threat_weight · risk_awareness · exposure, 0.30, 1.00)
```
`threat_weight` (0,50–0,90) steigt mit Vorsicht, `risk_awareness` mit dem Skill-Level (0,35 →
0,95). Ein Anfänger unterschätzt Gefahr, ein Experte nicht — identische Welt, unterschiedliches
Ergebnis.

### 2.7 Aktuelle Kampfpriorität — `PriorityFactor()`, `CombatLock`
```
PriorityFactor = clamp(1 − combat_lock_priority · combat_priority, 0.05, 1.0)   (nur wenn engaged)
Sonderfall: Gesundheit/Rüstung und hf < 0.35 → combat_priority wird mit 0.25 multipliziert
Harte Sperre: engaged und priority > combat_lock_priority und hf ≥ 0.35
              → kein neuer Item-Trip (kCombatLock)
```
`combat_lock_priority` = 0,92 − 0,25 · Aggressivität (0,60–0,92): aggressivere Bots brechen
seltener ab. Ein sterbender Bot darf immer für Gesundheit/Rüstung disengagieren.

### 2.8 Skill-Level — `ItemSkillBlock`
| Feld | Tier 1 → 5 | Wirkung |
|---|---|---|
| `planning_horizon_s` | 2,5 → 13,0 | Zeitfaktor und Reisebudget (`max_search_time_s`) |
| `risk_awareness` | 0,35 → 0,95 | Gewichtung von Bedrohung und weiter Reise |
| `discipline` | 0,30 → 0,90 | Dwell-Zeit, Abbruch-Kooldown, Abweichungskosten |
| `tie_noise` | 0,020 → 0,002 | Streuung bei exakten Gleichständen |

Monotonie ist getestet (`TestSkillTablesAreMonotone`). Beispiel: ein Medkit in 60 m Entfernung
(≈ 6,4 s Reise) wird von Tier 1 **abgelehnt** (`max_search_time_s` ≈ 1,4 s) und von Tier 5
**angenommen** (≈ 7,4 s).

### 2.9 Persönlichkeit — `ItemPersonalityBlock`
Sechs Profile mit Appetiten `health/armor/ammo/weapon/powerup/strategic` (0…2) und
`caution`/`aggression` (0…1):

| # | Profil | Health | Armor | Ammo | Weapon | Powerup | Strategic | Caution | Aggr. |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | Aggressor | 0,75 | 0,80 | 1,10 | 1,25 | 1,10 | 0,70 | 0,25 | 0,90 |
| 1 | Survivor | 1,45 | 1,30 | 1,00 | 0,90 | 0,80 | 0,90 | 0,85 | 0,35 |
| 2 | Duelist | 1,00 | 1,00 | 1,05 | 1,05 | 1,00 | 0,80 | 0,50 | 0,65 |
| 3 | Controller | 1,00 | 1,00 | 0,95 | 0,95 | 1,00 | 1,30 | 0,60 | 0,45 |
| 4 | Marksman | 0,95 | 1,05 | 1,20 | 1,15 | 0,90 | 0,85 | 0,60 | 0,50 |
| 5 | Flaky | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 0,50 | 0,60 |

Indizes und Namen sind **identisch** zu `botcore::PersonalityName` (Test
`TestPersonalityIdentity`). „Flaky" moduliert den Bedarf mit einer deterministischen Sinuswelle
±18 % (seed-gebunden, `ItemMood`); alle anderen Profile sind statisch.

**Orthogonalität:** Skill-Felder hängen nie von der Persönlichkeit ab und umgekehrt — blockweise
getestet, analog zu `botcore::SkillUnaffectedByPersonality`.

### 2.10 Such-Kooldowns und Blacklists
| Auslöser | Wirkung | Bereich |
|---|---|---|
| Trouble-Abbruch (Damage, Threat, Stall, Timeout, Unreachable, Combat-Lock) | Per-Item-Kooldown `abort_cooldown_s` (0,8–2,2 s) **und** globaler Such-Kooldown `search_cooldown_s` (1,0–3,0 s) | blockiert Neustart |
| Erfolgreiche Aufnahme | Item-Blacklist `consumable_blacklist_s` = 30 s | verhindert Wiederanlaufen desselben (noch nicht respawnten) Items |
| `NavStatus::kUnreachable`/`kRejected` | Blacklist 30 s + 30 s | kein Retry-Sturm |
| Bedarf erfüllt / Item verschwunden | keine Sperre | nächster Bedarf darf sofort starten |

Wichtig: Der globale Kooldown wird **nicht** nach einem erfolgreichen Pickup gesetzt — sonst
könnte ein Bot nach dem Medkit nicht sofort Munition holen.

### 2.11 Zielwechsel-Hysterese
Drei Mechanismen, alle getestet:
1. **Start- vs. Fortsetzungsschwelle:** ein laufendes Ziel braucht nur `base > ε`, ein neues
   zusätzlich `utility ≥ min_utility`.
2. **Commit-Margin:** ein Konkurrent muss `utility_alt > utility_cur · (1 + commit_margin)`
   erfüllen (0,10–0,45).
3. **Dwell:** kein freiwilliger Wechsel innerhalb `min_commit_s` (0,40–2,60 s); in dieser Zeit
   lautet die Antwort `kKeep` mit `kHysteresisHold`.

### 2.12 Zeitbegrenzungen
| Grenze | Wert | Wirkung |
|---|---|---|
| `max_search_time_s` | 2,5–20 s (aus Horizont × Vorsicht) | Ziel-Timeout (`kTimeout`) und hartes Reisebudget für neue Ziele |
| `damage_window_s` | 2 s | Bezugsfenster für `DamageAbort` |
| `abort_damage_frac` | 0,20–0,45 der max. HP | Abbruch bei Beschuss |
| Nav-Ablauf | `issued_tick + max_search_time + 1 s` | Navigation muss das Ziel aufgeben |
| `kStallAbortReports = 2` | 2 Meldungen | Abbruch bei Stillstand |

---

## 3. Abbruch- und Auswahlregeln (vollständig)

Ein laufendes Ziel wird **in dieser Reihenfolge** geprüft:

| # | Bedingung | Ergebnis |
|---|---|---|
| 1 | Navigation meldet `kArrived` | `kReached`, Item geblacklistet |
| 2 | Navigation meldet `kUnreachable`/`kRejected` | `kAbort`/`kUnreachable` + Langzeit-Blacklist |
| 3 | Navigation meldet `kExpired` | `kAbort`/`kTimeout` |
| 4 | Navigation meldet 2× `kStalled` | `kAbort`/`kStalled` |
| 5 | Item nicht mehr im Snapshot | `kAbort`/`kItemGone` |
| 6 | Distanz ≤ 1,5 m | `kReached` |
| 7 | Item `respawn_s > 0` | `kAbort`/`kItemGone` |
| 8 | Reiseweg überschreitet Budget | `kAbort`/`kOutOfRange` |
| 9 | `base ≤ ε` (Bedarf weg) | `kAbort`/`kNeedSatisfied` |
| 10 | sichtbarer Feind ≤ `enemy_abort_radius_m` **und** `hf < health_abort_frac` **und** Ziel > 2,5 m | `kAbort`/`kThreatOverride` |
| 11 | HP-Verlust > `abort_damage_frac` im Fenster | `kAbort`/`kDamageAbort` |
| 12 | Ziel älter als `max_search_time_s` | `kAbort`/`kTimeout` |
| 13 | `engaged` und `priority > combat_lock_priority` und `hf ≥ 0.35` | `kAbort`/`kCombatLock` |
| 14 | sonst | `kKeep` (oder `kSwitch` über Commit-Margin) |

Ohne laufendes Ziel: globaler Kooldown → `kCooldown`; Combat-Lock → `kCombatLock`;
sonst bester Kandidat → `kSelect`, oder `kNoCandidate`/`kOutOfRange`/`kUnreachable` mit dem
**informativsten** Ablehnungsgrund der Evaluierungen.

**Fail-closed:** Ein Snapshot, der die Validierung nicht besteht (NaN, negativer Wert,
doppelte ID, ungültiger Waffenindex, `health > max_health`, `combat_priority ∉ [0,1]`), führt zu
`kInvalidWorld` und **keinem** Ziel.

---

## 4. Tuning-Ableitung (Skill × Persönlichkeit)

Die Tuning-Werte werden **berechnet**, nicht pro Bot gepflegt (`TuningFor`):

```
commit_margin        = clamp(0.12 + 0.18·caution + 0.10·(1−discipline), 0.10, 0.45)
min_commit_s         = clamp(1.60 − 0.90·discipline + 0.40·caution,   0.40, 2.60)
search_cooldown_s    = clamp(2.50 − 1.00·discipline,                  1.00, 3.00)
abort_cooldown_s     = clamp(0.90 + 1.10·caution,                     0.80, 2.20)
abort_damage_frac    = clamp(0.42 − 0.18·caution,                     0.20, 0.45)
enemy_abort_radius_m = clamp(12.0 + 12.0·caution,                     10.0, 26.0)
health_abort_frac    = clamp(0.70 − 0.30·caution,                     0.35, 0.75)
max_search_time_s    = clamp(0.65·horizon·(1 − 0.25·caution),         2.50, 20.0)
min_utility          = clamp(0.12 + 0.04·caution,                     0.10, 0.20)
threat_weight        = clamp(0.55 + 0.30·caution,                     0.50, 0.90)
deviation_weight     = clamp(0.35 + 0.40·discipline,                  0.35, 0.80)
combat_lock_priority = clamp(0.92 − 0.25·aggression,                  0.60, 0.92)
```

Alle Ableitungen sind begrenzt und validiert (`ValidateProfile`); ein Profil mit unsinnigem Tuning
wird abgelehnt, nicht stillschweigend geklemmt.

---

## 5. Was der Prototyp **nicht** entscheidet

- **keine Navigation**: kein Pfad, kein Wegpunkt, keine Richtung, kein Ray (siehe
  `2026-10-25-navigations-schnittstelle.md`);
- **kein Zielen, kein Feuern, keine Waffenwahl**: Waffenwahl bleibt bei `botcore::WeaponSelector`;
  die Item-Schicht liefert nur Wünsche;
- **keine Engine-Zugriffe**: alles läuft über synthetische, validierte Snapshots;
- **keine Item-Erkennung**: welche Items in Sicht/Reichweite sind, meldet der Aufrufer.
