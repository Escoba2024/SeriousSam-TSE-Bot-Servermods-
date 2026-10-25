# Session-Hybrid-Lab – Session-Lifecycle, Ghost-Zustände und Recovery

**Datum:** 2026-10-25 · **Status:** Entwurf / Offline-Prototyp · **Evidenz:** [T] zitierte PR-#47-Konzeption, [O] offline getestet, [A] Entwurf, [N] nicht geprüft

## 1. Session-Zustände

Der portablen Session-Politik (übernommen aus PR #47 `tools/bot_sessions.py`) folgen die Zustände:

```
OFFLINE -> WAITING -> JOINING -> PLAYING -> LEAVING -> COOLDOWN -> OFFLINE/WAITING
```

| Zustand | Bedeutung |
|---|---|
| OFFLINE | Identität existiert, ist nicht geplant (Admin-Off oder noch nicht gestartet) |
| WAITING | Startverzögerung läuft, wartet auf Join-Freigabe |
| JOINING | Join-Absicht reserviert, Client-Platzierung läuft |
| PLAYING | Bot ist aktiv verbunden (Session läuft) |
| LEAVING | Geplanter Abgang reserviert, Slot wird freigegeben |
| COOLDOWN | Pause nach Beendigung, bevor Rejoin möglich |

**Wichtige Unterscheidungen [T aus PR #47]:**
* geplanter Abgang (`left`, Grund gespeichert) vs. Crash (`crashed`) vs. unerwarteter Abgang (`disconnected`) werden getrennt gespeichert;
* Crash kürzt eine geplante Pause nicht ab und hebt Admin-Off nicht auf;
* ein Neustart übernimmt persistierte Zustände; JOINING/LEAVING erzeugt keinen zweiten Auftrag (at-most-once pro Epoch).

## 2. Stabile Botidentität

Jede Identität besitzt [O-Prototyp]:
* UUIDv5-GUID, deterministisch aus `pool_id/seed/ident` – identisch über Crash, Cooldown und Rejoin;
* festes Human-KI-Rosterprofil (0–7) und deterministischen Spiel-Seed;
* bereinigten, case-insensitiv eindeutigen sichtbaren Nickname (Farbe bleibt inaktive Metadaten bis zur nativen Qualifikation).

Die Identität wird **nicht** bei jedem Prozessstart neu erzeugt (keine zufällige GUID pro Login).

## 3. Session-Zeiten und Pausen (realistische Planung)

Konfigurierbare, gewichtete Zeitbänder [Vorschlag, nicht gemessen]:

| Band | Gewicht | Dauer | Anteil |
|---|---|---|---|
| kurz | 10 % | 5–19:59 min | Test-Szenarien |
| mittel | 80 % | 20–90 min | Normalbetrieb |
| lang | 10 % | 90:01–180 min | Ausdauer-Sitzungen |

Pause nach jeder Sitzung: 15–120 min (Default 900–7200 s). Join-Abstand 1–3 × Join-Intervall (Dreiecksverteilung). Höchst ein laufender Join und ein laufender Leave global; Mindestpause 15 min [Vorschlag aus PR #47, nicht nativ gemessen].

Diese Zeitwerte sind **virtuelle Simulationswerte** [O], keine reale Stundenabnahme.

## 4. Mindestpopulation und Human-Slot-Reserve

* `min_bots`: Die Session-Politik plant keinen Leave, der die Anzahl PLAYING-Bots unter `min_bots` fallen ließe [O-Implementiert].
* `reserved_human_slots`: Menschliche Spieler sind echte Reserve. Die effektive Kapazität pro Server ist
  `capacity = max(0, min(max_bots, maxplayers − reserved_human_slots − anzahl_menschen))`.
  Menschenreserve wird nicht durch fremde Belegung verbraucht.
* Unbekannte oder veraltete Server-Queries blockieren neue Joins (nie Humans verdrängen).

## 5. Ghost-Zustände

Ein **Ghost** liegt vor, wenn die Server-Query einen Slot belegt meldet, aber kein zugeordneter laufender Client-Prozess mehr existiert (z. B. nach Crash ohne sauberen Quit, oder nach Server-Neustart).

Modelliertes Verhalten [O-Prototyp]:

| Beobachtung | Zustand | Reaktion |
|---|---|---|
| Query hat Spieler, Prozess tot | GHOST | Slot blockiert, Identität nicht wiederverwendet |
| Query hat Spieler, Prozess lebt | healthy | normale Sitzung |
| Query keine Spieler, Ghost lange genug ungekannt | verified_absent | Slot darf wiederverwendet werden |
| Prozess kommt zurück | cleared/acknowledged | Ghost geklärt |

Eine Identität darf erst nach **verifizierter Abwesenheit** (Query bestätigt Slot-frei über ein Mindestalter) wiederverwendet werden. Epochen schützen vor Doppelstart: ein JOINING-Epoch darf nur einmal gestartet werden.

## 6. Server-Neustart und Recovery

* Alle PLAYING-Sitzungen werden bei einem Server-Neustart getrennt (`disconnected`, nicht als geplanter Leave gewertet) und in COOLDOWN überführt.
* Die stabile Identität (GUID, Profil, Seed) bleibt erhalten.
* Nach dem Neustart rejoinen die Bots mit identischer Identität; der Scheduler packt sie erneut auf die Viererclients (ROSTER_RESTART).
* Verwaiste Sessions (Prozess tot, Query unklar) werden durch die Ghost-Logik quarantänisiert, bis verifizierte Abwesenheit vorliegt.

## 7. Doppelstartverhinderung

Jede Absicht ist transaktional an `(identity_id, epoch)` gebunden. Ein Launch-Claim wird **vor** dem Prozessstart verbraucht. Zwischen Claim und externer Seiteneffekt crashing = Quarantäne; kein impliziter Retry. Native Wiederherstellung muss eigenständig nachweisen, welcher Prozess existiert [A, gemockt].

## 8. Abnahmekriterien (Prototyp, offline)

Alle Kriterien sind im Offline-Prototyp [O] getestet; keine davon ist eine Live-Retail-Abnahme:

1. GUID/Seed-Stabilität über Crash, Cooldown, Rejoin.
2. Zustandsgrafik wird eingehalten; JOINING/LEAVING nicht dupliziert.
3. min_bots wird nicht unterschritten.
4. Human-Slot-Reserve reduziert Kapazität korrekt.
5. Ghost wird nicht vor verifizierter Abwesenheit wiederverwendet.
6. Epoch-Schutz verhindert Doppelstart.
7. Server-Neustart: alle PLAYING → COOLDOWN, stabiler Rejoin mit gleicher Identität.
8. SQLite-Transaktionen (BEGIN IMMEDIATE) schützen vor doppelten Controllern.

## 9. Risiken

* Ghost-Detektion beruht in diesem Lab auf einer vereinfachten Query/Prozess-Korrelation; native Abnahme erfordert frischen Besitzer-/PID-/Start-/CWD-/cgroup-Abgleich [N].
* Join-Latenz von C1 (Batch-Fenster + Clientstart) ist für sekundengenaue Einzel-Leaves unkritisch, für „natürlich wirkende Sessions“ (Minuten-bis-Stunden) unkritisch [A].
* Keine echte Retail-Session-Wiederkehr ohne qualifizierten Runtime-Adapter [N].
