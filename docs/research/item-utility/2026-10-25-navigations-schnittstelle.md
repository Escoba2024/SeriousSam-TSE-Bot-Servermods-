# Item-Utility → Navigation: Schnittstellenvertrag

**Datum:** 25.10.2026 · **Agent 5**
**Code:** `poc/research/item-utility/include/navigation_interface.h`
**Tests:** `TestNavigationSeamCommitsAndCancels`, `TestNavigationArrivalAndUnreachable`,
`TestNavigationStallAborts`, `TestNavigationGoalTranslation`,
`TestPlannerDoesNotImplementNavigation`

Der Navigation-Agent (WaypointGraph, A*, Pathfinding, Bodenprüfung) entwickelt **separat**. Diese
Schnittstelle ist die einzige Kopplung: die Item-Schicht sagt **was und warum**, die Navigation
sagt **wie und ob überhaupt**.

---

## 1. Arbeitsteilung (verbindlich)

| Verantwortung | Item-Schicht | Navigation |
|---|---|---|
| Auswahl des Items, Begründung | **ja** | nein |
| Priorität, Zeitfenster, Abbruch | **ja** | nein |
| Wegpunkte, A*, Pfadverfolgung | **nie** | ja |
| Boden-/Abgrundprüfung, Sprung/Crouch | **nie** | ja |
| Rays, Entity-Zugriff, Weltabfragen | **nie** | ja |
| Fortschritts-/Blockierungsmeldung | liest nur | **ja** |

Die Item-Schicht enthält deshalb **keine** Pfad-, Wegpunkt- oder Richtungsdaten. Selbst der
Reiseaufwand für das Utility ist eine reine `Distanz / Geschwindigkeit`-Schätzung und wird
**ausschließlich** zur Bewertung benutzt, nie zur Steuerung.

---

## 2. Typen

### 2.1 Ziel (`NavGoal`)

```cpp
struct NavGoal {
  int goal_id;                 // Item-ID aus dem Snapshot, stabil
  Vec3 pos;                    // Item-Position (Aufnahmepunkt)
  double arrive_radius_m;      // 1.5 m – Aufnahme-, nicht Pfadtoleranz
  NavPriority priority;        // Soft | Normal | Urgent | Critical
  double max_speed_frac;       // 0.6..1.0, aus der Vorsicht des Profils
  bool allow_jump;             // Hinweis, Entscheidung liegt bei der Navigation
  bool yield_to_combat;        // false nur bei Überlebenszielen
  int issued_tick, expires_tick;
};
```

`priority` und `yield_to_combat` werden **aus dem Bedarf** abgeleitet, nicht aus dem Item-Typ:
ein Rüstungs-Trip bei 20 % HP ist `kCritical` ohne Combat-Yield, derselbe Rüstungs-Trip bei 90 %
HP ist `kSoft` mit Yield.

### 2.2 Status (`NavStatus`) und Rückmeldung (`NavFeedback`)

| Status | Bedeutung | Reaktion der Item-Schicht |
|---|---|---|
| `kAccepted` | angenommen, noch nicht geplant | weiter warten |
| `kInProgress` | Pfad existiert, Bot folgt | weiter warten |
| `kArrived` | innerhalb `arrive_radius_m` | `kReached`, Item geblacklistet |
| `kUnreachable` | kein Pfad | `kAbort`/`kUnreachable` + Langzeit-Blacklist (30 min) |
| `kStalled` | Pfad existiert, kein Fortschritt | 2 Meldungen → `kAbort`/`kStalled` |
| `kExpired` | Zeitfenster abgelaufen | `kAbort`/`kTimeout` |
| `kAborted` | von einer Seite verworfen | `kAbort`/`kItemGone` |
| `kRejected` | Navigation lehnt grundsätzlich ab | `kAbort`/`kUnreachable` |
| `kIdle` | unbekanntes Ziel | wird ignoriert |

`NavFeedback.path_remaining_m` und `line_of_sight` sind **optional**; die Item-Schicht liest sie
derzeit nicht (bewusst: keine zweite Wahrnehmungsschicht).

---

## 3. Ablauf pro Tick

```
ItemPlanner::Step(world, nav)
  ├─ world validieren                     (fail closed → kInvalidWorld)
  ├─ alle Items bewerten                  (≤ 64)
  ├─ wenn Ziel aktiv:
  │    ├─ nav->Poll(goal_id)              → Arrived/Unreachable/Stalled/Expired?
  │    ├─ harte Abbruchregeln             → ggf. nav->Cancel(goal_id), kAbort
  │    └─ sonst Keep oder Switch
  ├─ sonst: Kooldown / Combat-Lock / bester Kandidat
  └─ bei Commit:  nav->Submit(NavGoal)    → kAccepted?
                  vorherigen Goal canceln (erst nach erfolgreichem Submit)
```

Reihenfolge-Detail: Ein **Wechsel** submittet zuerst das neue Ziel und bricht erst danach das alte
ab. Lehnt die Navigation ab, bleibt der laufende Trip erhalten (Test
`TestPlannerDoesNotImplementNavigation`).

---

## 4. Anforderungen an den Navigation-Agenten

1. **`Submit` idempotent** für dieselbe `goal_id`; gleiche ID mit anderer Position = neues Ziel.
2. **Kein Callback-Zwang**: `Poll` wird mit 20 Hz aufgerufen, die Navigation darf intern langsamer
   planen und beliebig budgetieren. Die Item-Schicht hat kein Zeitverhalten, das davon abhängt.
3. **Ehrliche Meldungen**: `kUnreachable` statt Scheinfortschritt. Ein falsches „unerreichbar"
   kostet ein echtes Pickup; ein verschwiegenes „hängt fest" kostet den Such-Slot.
4. **`expires_tick` respektieren** und danach `kExpired` melden.
5. **Nur melden, nicht entscheiden**: die Navigation darf kein anderes Item vorschlagen.
6. **Kein Schreibzugriff** auf Planner-Zustand; die einzigen Rückkanäle sind `Poll` und
   `NotifyItemPicked`.
7. **Kein Engine-Zugriff in der Item-Schicht**: die Navigation liefert Positionen und Status,
   keine Entities.

---

## 5. Anbindung an den bestehenden Code (Skizze)

Die bestehende Navigationsbasis in `poc/botcore/` (`ObstacleRecovery` in `bot_navigation.h`,
`WaypointGraph` in `botcore_ai.h`) bleibt unverändert. Der Adapter ist ein dünner Sink:

```cpp
// Integration (neue Datei, nicht Teil dieses PR):
class BotcoreNavigationSink : public itemai::NavigationSink {
  botcore::WaypointGraph* graph_;      // vom Navigation-Agenten gefüllt
  botcore::ObstacleRecovery* recovery_; // reaktive Erholung, unverändert
  int active_goal_ = -1;
 public:
  NavStatus Submit(const NavGoal& g) override;   // graph_->NearestNode(g.pos) + NextHop
  void Cancel(int id) override;                  // active_goal_ = -1
  NavStatus Poll(int id, NavFeedback*) override; // Fortschritt/Stall aus der Bewegung
  const char* Name() const override { return "botcore"; }
};
```

Der Item-Planner erhält diesen Sink in `Step(world, sink)`; ohne Sink (Offline-Tests) verhält er
sich identisch, nur ohne Submit/Poll.

---

## 6. Testdouble

`RecordingNavigationSink` ist ein **skriptbarer** Sink ohne Pfadfindung: Annahme/Ablehnung,
„kommt nach N Polls an", „meldet nach N Polls Stillstand", „Item X ist unerreichbar". Damit sind
alle Abbruchpfade ohne Retail, ohne Map und ohne Navigation-Agent reproduzierbar.

---

## 7. Was diese Schnittstelle **nicht** leistet (bewusst)

- keine Mehrzielplanung (ein aktives Ziel; Alternativen werden nur bewertet),
- keine Pfadkostenrückmeldung in das Utility (die Reisezeit ist eine Schätzung),
- keine Koordination zwischen mehreren Bots (kein Item-Reservierungsprotokoll),
- keine Kampf-Ausführung: `suppress_combat` ist eine **Bitte** an die Kampfschicht, kein Befehl.

Diese Punkte sind Kandidaten für Folgeaufträge und in
`2026-10-25-integrationsplan.md` als offen markiert.
