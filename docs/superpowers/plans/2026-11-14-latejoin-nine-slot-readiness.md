# OwnNS: zwei vollständige Neun-Slot-Runden vor Admission

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans undtest-driven-development. Root integriert und führt Runtime allein aus. Dieser Auftrag erlaubt ausschließlich die enge Offlinekorrektur, neue Tests und eine neue deaktivierte Ableitung.

**Goal:** Nach echter Query9-/Endpointbindung innerhalb der unveränderten30s
Admission zunächst zwei vollständige fortschreitende native Neun-Slot-Runden
beobachten und sämtliche bereits erfolgreichen Originalreads privat erhalten.

**Architecture:** Der vorhandene native_frame-Reader und seine Rawquittungen
bleiben. Nur während Admission darf der Originalpeer noch ausschließlich0..7
zeigen; die alten Botslots bleiben unveränderlich gepinnt. Nach zwei vollständigen
Runden prüft das unveränderte validate_frames weiterhin exakt range(9).
Keine neue Join-/Launchwiederholung, keine neue Frist oder Lockerung.

**Tech Stack:** vorhandener Pythonadapter, passive Originalreader,
exklusives0600-JSONjournal, deterministische Offlinefixtures.

**Spec:** Rootauftrag nach geschlossenem173005-Lauf; Result
`b44bab627e5cebbfa325a6fb9d6808a36f041c70d6534f7a9e0235d30b9e0a14`.

## Beleg und Scope

Originalframe16 enthält in beiden echten Reads nur0..7 bei Tick22,649940;
Frame20 enthält in beiden0..8 bei23,199932. Die drei alten Rollen sind in
Frames13–15 bereits vollständig0..8. validate_frames lehnt die alte erste
Originalrunde zu Recht ab. Query9 undvier tatsächliche Endpointbindungen
beweisen keine bereits vollständige Original-Simulationstabelle.

Die bisherigen Original-localSource-/Slot8-Inventarreads werden erst spät in
eine Erfolgsquittung aufgenommen. Scheitert die nachfolgende Frameprüfung,
fehlen diese erfolgreichen Rawbelege; aus bloßem Ausnahmeort folgt keine
native ABIqualifikation. Alter FAIL und Archiv bleiben unverändert.

## Verbindliche Grenzen und Reviewfokus

- Ausschließlich ownns_latejoin_runtime.py verändern; neue Tests/Builder/
  Bericht. preflight.validate_frames, OriginalABIreader, Decoder, Capture,
  Readiness20s, Inputs, Samplingrate, Host-/Close-/Restoregates unverändert.
- Gleicher0,2s-Rundenabstand und eigene native_frame-Readpaare; Capture-
  admission_remaining vor/nach jeder Runde. Absolutes Capturestart+30s bleibt.
- Alle alten0..7-Pointer pro Rolle an die vorhandene Prestartbeobachtung binden;
  Original0..7 bei erster echter Beobachtung festhalten. PID/Module/Session/
  Endpoint-/alteBotbindung und unerwartete Slots/Pointers sofort FAIL.
- Nur anfängliches Fehlen vonOriginalslot8 ist NotReady. Auftauchen von8
  verändert keinen alten Slot; nach seiner ersten Beobachtung ist Verlust/
  Pointerwechsel FAIL. Rückläufiger Tick ist FAIL, gleicher Tick kein
  Fortschrittsbeleg. Kein First-fit-PASS aus einer einzelnen kompletten Runde.
- Alle Rawframes einschließlich NotReady behalten. Neuer localSource- und
  jeder erfolgreiche Inventarread sofort vor dessen Folgeassertions O_EXCL/
 0600 persistieren. Jeder spätere Admissionfehler enthält vorhandene Frames,
  Readinessmetadaten, localSource, Teilinventare und Originalfehler; alle
  Qualifikationsflags False, kein Gameplaystart.

## Aufgaben

- [ ] Engen RED beobachten:8→9 allein reicht nicht; erst8→9→9progressiv
  erfolgreich. Dauerhaft8, fehlender Bot, unerwarteter Slot, falsche PID/Hash/
  Pointer/Ports, Regression und Fristablauf bleiben FAIL. Lokale Tests führen
  keine echten Proc-/Reader-/Display-/Netzaktionen aus.
- [ ] Kleinsten Admissionbeobachtungsloop mit denselben Rohreaderpaaren
  implementieren. Vorherige Rawframes nicht verwerfen; unveränderte finale
  validate_frames-Funktion verwenden. Keine Änderung an normalem Launch.
- [ ] Persistenz-RED für späten Fehler und vorliegende erfolgreiche lokale/
  Inventarreads; einheitliche private Fehlquittung implementieren. Fehler
  werden nicht als erfolgreiche ABIbeobachtung qualifiziert.
- [ ] Relevante alte Latejointests fokussiert prüfen, neue deaktivierte Kopie
  aus dem bisherigen Autorenpaket ableiten und alle geerbten Pins frisch
  prüfen. Nur Runtimeadapter, neue Test-/Builderdateien, Namespace/Pinpfade.
- [ ] Report mit genauen Belegpins/RED/GREEN/Grenzen committen; Root reviewed
  und entscheidet über einen einzelnen Retest. Kein autonomer Native-Retry.
