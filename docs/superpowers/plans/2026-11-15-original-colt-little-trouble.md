# Original-Colt Little Trouble – prospektiver Prüfplan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans erst nach Rootreview; keine Delegation. Aktuell nur Designauftrag, keine Implementierung/Runtime.

**Goal:** Einen konkreten normalen Zweiakteur-Colt-/Originalrespawnfall mit
nachgewiesener eigener Aufstellung vorbereiten, ohne alten F3-FAIL umzuwerten.

**Architecture:** Vorhandenen Root-F3-Respawncontroller und exakte Mapretarget-
Muster wiederverwenden. Neue deklarierte Map-/Move0-/Metadatenbedingung; keine
Änderung von ABI/Reader/Observer/Core oder künstlichen Spielzustandswrites.

**Tech Stack:** vorhandene Python-Sourceinversen, Vanilla TSE1.07/Build030,
Retail-WLD und vorhandene Cecil-NAV; Root allein Runtime.

**Spec:** `docs/superpowers/specs/2026-11-15-original-colt-little-trouble-design.md`.

## Verbindliche Grenzen und Reviewfokus

- F3 bleibt FAIL;84 echte Ownershipbelege/83 vollständige Frames/kein DEAD_READY.
- 10s/15TTL/64Queue/16384/85inner90outer/.2s8/ACK2/Hold.35/48/96/38Restore bleiben.
- Kein Map-/Spawn-LOS aus Navknoten, keine statische Retail-ABIübertragung.
- Move0 verhindert Testsprünge nicht; tatsächliche Aufstellung kann scheitern.
- Änderung der operativen Metadatenreserve ist explizit; kein Treffer-/Damageguard.
- Keine Sourceimplementierung oder Nativefolge durch diesen Plan autorisiert;
  Root prüft die neue Bedingung im bestehenden Projektauftrag.

### 1. Entscheidend offene Spawn-/Sichtvorbedingung schließen

- [ ] Rootreview der exakten LittleTrouble-Assets und normalen Startflags.
- [ ] Konkreten eigenen Admissionbeleg für normale Spawnpositionen und freie
  Schussachse festlegen. Aktuelle Manifeste enthalten keine solche Paarung.
  Ist sie nicht belegbar: kein Methodenstart; konkrete normale Originalbewegungs-
  vorbereitung separat spezifizieren statt zufälliger Rejoins/Spawncheats.
- [ ] Keine erneute reine10s-AI-Probe als Ersatz für diesen Beleg.

### 2. Erst danach exakte deaktivierte Sourcebedingung

Vorgeschlagene neue Dateien: `tools/prepare_a1_original_colt_trouble.py` und
zugehörige portable Tests; kleine neue feste Map-/Configpolicy nur bei Bedarf.
Keine Änderung bestehender qualifizierter Dateien oder Rootpakete.

- [ ] REDs am echten F3-Parent: alte World-/Nav-/Config-/CecilLoad-Bindung wird
  zurecht abgelehnt; falscher CRC/Map/Role/Originalhash bleibt fatal.
- [ ] Minimaler exakter retarget: ded_strLevel, Mapmanifest, NAI-Loadtuple110 und
  World/Navpins, Move1→0; alle übrigen Bytes über ganze Inversen beweisen.
- [ ] Staging ausschließlich nach bestehendem seal; vollständige Rücksicherung
  eigener Scripts/Profile/INI inkl. Metadaten. Keine tatsächliche Stagingausführung
  durch Test; portable Transaktionsfixtures und Sourcecallsitebelege.
- [ ] Pure maximaler Escapefall/GMS/PID-Feldlängen beweisen ≤416KiB pro gültiger
  Receiptform;1024Records/512MiB Vor-/Nachgrenzen und Primärfehlererhalt prüfen.
  Falls konkreter Formvertrag diese Grenze nicht trägt: keine Zahl als bewiesen
  ausgeben, Rootbefund und neue Reserveberechnung statt stiller Lockerung.
- [ ] Neues Disabledpaket nur nach belegtem Diskminimum9730785280B plus allen
  gebundenen Nebenoutputs; volle Pins/Inversen. Kein automatischer NativeRetry.

### 3. Root entscheidet einen eigenständigen realen Fall

- [ ] Frühestes falsches Mapping/Actor/Life/Fokus/Read/Deadline oder unklarer
  Spawn-/Sichtbeleg: FAIL vor Arm; keine Controllerbewegung improvisieren.
- [ ] Echter normaler Tod→DEAD_READY→Arm/TLS→ein FireDownUp→reale ACK/Init/erste
  Ticks/normal+fatalColtketten; fehlende Beispiele INCOMPLETE. Alle Raws/S-F/38-
  Restore-/Cleanup-/Hostkosten bewahren. Kein Aim-/FirstState-/Botopfer-PASS aus
  begrenzten späteren Beispielen, kein unbekannter Weaponowner zugelassen.
