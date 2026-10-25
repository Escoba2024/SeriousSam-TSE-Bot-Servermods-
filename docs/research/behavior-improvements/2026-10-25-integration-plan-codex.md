# Integrationsplan für Codex (produktive Human-KI) – Combat 2.0 Candidate

Nur Vorschlag aus dem Research-Bereich. Keine Änderung an `poc/botcore/**`,
BotDriver oder GameMP in diesem PR. Reihenfolge nach Wirkung/Risiko; jeder
Schritt einzeln hinter eigenem Opt-in-Schalter, Default = qualifiziertes
Verhalten, jeder Schritt mit eigener Offline-Regression + nativer Abnahme,
bevor der nächste beginnt.

## Schritt 0 – Profil-Overlay als Config (F-2/F-9), Risiko minimal
`AdjustedSkill()`-Tabelle als alternative Skill-Tabelle übernehmen
(`SkillFor`-Seam in `bot_profile.h`), Persona-Tabelle unverändert.
Gate: botcore-Tests (Monotonie/Validierung existieren), danach
Behavior-QA-Vergleich aus PR #62 erneut fahren (t1-Mirror-Draws müssen fallen).

## Schritt 1 – Waffen-Scoring 2 (F-1), Risiko niedrig
Seam: `bot_loadout.h::ScoreWeapon/BestWeapon` bzw. `WeaponSelector::Update`.
`ScoreWeapon2` + `WeaponSelector2` sind drop-in (gleiche Inputs:
usable_mask, distance, persona/range_preference aus `BotProfile`, dwell/margin
aus `SkillParams`). Neu nötig: `tier` und `persona` an den Selector reichen
(beide stehen bereits in `BotProfile`). Opt-in `bot_bWeaponScore2`.
Gate: `--weapon-curve`-Tabelle als Regressionstest; Telemetrie
Waffen-Histogramm im Retail-Lauf muss ≥4 Waffenfamilien zeigen.

## Schritt 2 – Strafe aktivieren + Controller (F-5), Risiko niedrig–mittel
Seam: `HumanBotPolicy::MoveIntent` ersetzt sin/fixed-flip durch
`StrafeController`; Integrations-Default `bot_fStrafeScale` von 0 → 1 nur in
Kombination. `NotifyDamage` (existiert) zusätzlich an `StrafeController::
NotifyDamage` hängen. `StrafeFireTolMult` optional in `AimController`-Fire-Gate.
Achtung Sync: Eingabe bleibt normaler `CPlayerAction`-Pfad; trotzdem erst
1-Bot-, dann 4-Bot-Lifecycle, keine Abkürzung.

## Schritt 3 – Hitscan-Lead + iterativer Projektil-Lead (F-3), Risiko mittel
Seam: Aim-Point-Block in `bot_human.h::Step` (dort wird heute nur
`proj_speed>0` geführt). Ergänzen: für Hitscan `lead_time = latency_s +
tick`, Zielpunkt += v·lead·`prediction_gain`; Latenzschätzer muss die
Integration liefern (Session-Ping/Roundtrip – Schnittstelle zum
Hauptagenten klären; im Research-Sim wurde an der Sense-Schicht genähert).
`ProjectileLeadTime` ersetzt die Einmal-Formel. Gate: Mover-Probe-Szenario als
Offline-Test portieren; Retail: Trefferquote gegen strafende Spieler beobachten.

## Schritt 4 – Alert-Kegel + Zweiwege-Suche (F-8/F-6), Risiko niedrig
Seams: `Perception::NeedsLineOfSight` Alert-Zweig (Halbwinkel ≤125° statt
Bypass), `ReactionTicks` Boden 2, Such-Yaw in `Step` durch
`SearchYawDeltaDeg`. Reine Gate-Änderungen, gut unit-testbar.

## Schritt 5 – Zielpriorität 2 (F-7), Risiko mittel
Seam: Score in `ChooseTarget`. Zusätzlich nötig im Track: „hat mich kürzlich
beschädigt" (aus eigener Health-Differenz + zuletzt sichtbarem Angreifer –
nur clientbeobachtbare Daten, wie bisher) und optional Gegnerblickrichtung,
falls repliziert verfügbar (sonst 0). PR #57 (Cecil-P1) arbeitet am selben
Seam: **zuerst mit #57 abgleichen**, nicht doppelt implementieren; die hier
gelieferten 5 Szenario-Tests als gemeinsame Regression nutzen.

## Schritt 6 – Deckungs-Rückzug (F-4), Risiko mittel, abhängig von A3
Seam: `MoveIntent`-Retreat-Zweig. Interface-Vertrag mit Navigation (LMArena A3):
Nav-Schicht liefert bis zu N `CoverPoint{x,z,blocks_los}` aus Bot-Sicht
(Waypoint-Flags der Nav-2.0, PR #54) – Combat entscheidet nur. Ohne Nav-Daten
greift Zickzack-Fallback. Keine Nav-Implementierung in diesem Paket.

## Schritt 7 – Respawn-Plan (Aufgabe 9), mit PR #57 mergen
`PlanRespawn` als Erweiterung der Tier-Delays aus #57 (Scan + Weapon-Ready).
Ein gemeinsamer Schalter, keine zwei Delay-Systeme.

## Querschnitt-Gates (jeder Schritt)
1. `poc/botcore` offline komplett PASS (unverändert grün halten).
2. Diese Combat-QA erneut: `make test` (107 Checks + 11 Invarianten) –
   Werte dürfen sich kalibrieren, Invarianten nicht still kippen.
3. PR-#62-Behavior-QA `--compare` gegen deren Baseline.
4. Native Retail-Abnahme durch Codex-Hauptagent (Join/Sync/Lifecycle/CPU),
   qualifizierte DLL bytegenau unangetastet; neuer Kandidat = neuer Hash =
   neue Abnahme. Bis dahin bleibt alles: **NOT_TESTED_RETAIL**.
5. Kein Schritt verändert `ser_iKickOnSyncBad` oder Serverprozesse.
