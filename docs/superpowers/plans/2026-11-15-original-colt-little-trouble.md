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

## Rootruling / tatsächlicher Umsetzungsauftrag

Neu beauftragt: LittleTrouble/Festziel030/Move0, normaleSpawns/Testsprünge,
OriginalStartDifficulty3/sonstige beobachteteStartflags unverändert. KeineRuntime.
Der512MiB-Entwurf oben ist NICHT der umzusetzende Wert: separate neue Condition
hat64MiB operative Ownershippayloadreserve, weiter1024Reads und vorhandenen
1,5MiB-Vorbehalt. Alte RP-3MiB-Quelle/Condition/F3 bleiben unverändert.
Keine Garantie für alle1024Reads, Payloadcap bleibt FAIL.

Claim NEU tools/a1_colt_trouble_condition.py, prepare_a1_colt_trouble.py und je
Tests. Generierte neue Method-/Policykopien werden aus ganzen gepinnten alten
RP-Dateien abgeleitet; exakte Inversen statt gemeinsamer Refaktor/Monkeypatch.
Die neue Condition übernimmt vorhandeneplacements/ActorLife aus Roleframes,
archiviert beide getrennten Server-/Originalread-Geometrien ohne Clockfusion,
fordert tatsächlich positiveHP→HP-Abfall→DEAD_READY und behauptet keineLOS.

1. Kurze pure REDs: tatsächliche Geometryfelder/Actor-Life/HPabfall ohne neueReads.
   GREEN kleinsterConditionhelper; RootNativepause jederzeit beachten.
2. ActualSource REDs: alter3MiB-Guard/realeMap-/Configbedingungen scheitern;
   erzeugte neue64MiB-Method-/Policykopie und exakteNAI/Runner-Transforms.
   GanzeInversen; alteRP/Reader/ABI/Observer/Core unverändert.
3. Neue transaktionaleStartupscript-Mapauswahl nachseal; echteTempdatei-
   Snapshot/Restore- und Falsepositiveprüfungen. Kein Stage in echtemLab.
4. Fresh disabledFork nur nach Speicherprüfung:8GiB+64MiBSicherheitsreserve+
   64MiBMetadata+bestehende512MiBRawjournalreserve+Copybytes+expliziteNebenreserve.
   NeueMetadatenwahrheit/pins, Rootreview/Handoff. KeinNativeReady ausSource/TDD.
# Vorwärtsstand: explizites RAM-Evidenzvolume

Root hat nach dem unverändert erhaltenen D-v1 ausschließlich eine optionale Evidenzvolume-Wahl beauftragt. `--evidence-ram-base` bzw. der entsprechende explizite `main`-Parameter wählt ein bereits vorhandenes eigenes0700-Verzeichnis unter `/dev/shm`. BASE, Programme, DLLs, Fixture, Locks und Toolpfade bleiben auf Disk. Aliase/Symlinks, fremderOwner, falscherModus/Typ oder abweichendesDevice werden abgewiesen. Ohne Option bleibt die9328132096B-Diskreserve bestehen.

Mit RAM-Option gelten vorCaseanlage und bei jedem vorhandenen Hostsample: FixtureDisk mindestens8GiB+64MiB Safety+64MiB Runtime; MemAvailable mindestens1,5GiB+64MiB Ownership+512MiB Journal+64MiB Case+512MiB Nativeheadroom; freies gewähltes RAM-Volume mindestens640MiB. Die bestehenden CPU/RAM/Disk-Messwerte werden genau einmal erfasst und wiederverwendet; nur der freie Platz des separaten Evidenzvolumes wird zusätzlich einmal gelesen. Fehlende/untypisierte Werte oder unterschrittene Reserven bleiben FAIL. Hostsample und RAM-Freiplatz werden vor neuerReservevalidierung archiviert, bestehendes `finally`/Cleanup bleibt erhalten.

Vor jedem Nativefall prüft Root zusätzlich das tatsächliche tmpfs-Mount und die exklusive frische Verzeichnisverantwortung. Nach vollständigem Close bleiben die RAMdaten erhalten, bis Root bei genügend freiem Diskplatz die vollständige exakte persistente Kopie samt Hash-/Metadatenbeleg erstellt hat. Kein automatisches Löschen, keine Symlinks/Mountänderung, kein Runtime-/Input-/Fallbackpfad. Source-/Unit-PASS ist keine Nativebereitschaft.

Beobachteter neuer RED: zwei fehlende Volume-/Pfad-Funktionen; danach16 gezielte Tests GREEN. Ganze sechs Quelleninversen bleiben verbindlich; alter RP und D-v1 bleiben unverändert. Ein frischer D-v2 enthält diesen Vorwärtsstand.
# Metadaten-Forwardfix nach Rootbefund

D-v2/F-v1 sind vor Native superseded/NEVER_NATIVE. Echter RED gegen tatsächliche Builderstatements reproduzierte RedStation-Nav-/Snapshotmetadaten trotz tatsächlicher LittleTrouble-NAI-Quelle. Nur aktive `natural_ai_condition`-Nav-/Snapshotfelder werden nun in beiden Manifesten aus statischen tatsächlichen NAI-Literalen abgeleitet. Historische Parent-Status-/Inputs0-/Sourcepinprovenienz bleibt erhalten und explizit vom aktuellen Conditioninputtotal2 abgegrenzt.17gezielte GREEN; frischer D-v3, keine Runtimequellen-/Guardänderung. Details und vollständige Quittung im Vorbereitungsbericht.
