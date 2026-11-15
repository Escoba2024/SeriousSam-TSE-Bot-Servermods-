# Umsetzung: registrierte Erstzustands-/Schadensdomäne

Spec: `../specs/2026-11-15-registered-first-state-damage-method-contract.md`.
Rootauftrag nach geschlossenem Hole031. Keine Runtime/Builds/Input/Originaldateiänderung.
Ausführung mit executing-plans und TDD, kein Subagent. Alte FULL18-FAILs bleiben unverändert.

## Claim und Quellen

Nur neue `tools/first_state_registered_damage*.py`, `tools/test_first_state_registered_damage*.py`,
`tools/prepare_first_state_registered_damage.py` und dieser Plan/eigener Report.
Parent ist ausschließlich NaturalAI030 StatusV2-disabled, Manifest
`2c43de1f91809d591a8631a7aeac2c03f02ee365c0b33d00993803c88a4d26b9`.
Keine Änderungen an alten FULL18-Helfern, Paketen oder Root-Handoff.
Private Belege: `/srv/tse-registered-first-state-damage-evidence-20261115`,0600/exklusiv,
höchstens5MiB; vor Paketquelle mindestens8GiB+64MiB plus Ausgabegröße frei.

## Task1: vollständiger Sourcevertrag vor Package

1. Gepinnte Observer-/Schema-/Validator-/Sessioninterfaces NOATIME lesen.
2. Echte Callbacktests führen die transformierten Produktionsfunktionen aus.
   RED: Weltcast erzeugt im Parent weiterhin volle Rows; neue Scopekennung fehlt.
3. Kleinster exakt inverser Transform: nur neue Scopekennung, separate Zähler,
   Pendingmark im vorhandenen Stack, reine Vorfahrenklassifikation und Ausgabeauswahl.
   Kein neues Native-/Clock-/Getterlesen. Der vollständige alte emit-Pfad einschließlich
   Guard wird auch auf ausgelassenen Kanten durchlaufen; Queue64 bleibt voller Payloadpuffer.
4. GREEN/Differenzialbelege: erhaltene Ketten/Argumente/IDs/Parents/Lifestates exakt gleich;
   relevante Nachkommen unter Pending sofort sticky, nie nachgereichte Eintrittsrows.
5. Gegenfälle: beliebig tiefer Colt-/Launchvorfahr, nested worldcasts/Reentry, unbekannter
   Owner, Nonmain/Threadwechsel, Life/Weltfehler, echter fehlender Leave, Getter/TTL/Event/
   Queue-/Stackgrenzen. Alle18 Attachstellen/G/Read-/Guardfunktionen unverändert belegen.

## Task2: eigener strikter Scope-/Streamvalidator

Erst RED für neue Schema-/Row-/Nativecounterabgrenzung, CallID-Lücken/Parents/Pending und
FULL18-Mischreplay; dann engster Transform einer separaten Parentkopie. Der alte Validator
bleibt unverändert. Dessen Zustands-/Life-/Originalbyteprüfungen bleiben im neuen Validator
vollständig vorhanden; nur die explizit neuen Nenner-/CallIDregeln ändern sich.
Raw-before-parse, all1..F, S/F und38Regionen sind keine Erfolgsausnahmen.
Relevanznachweis ist Source-begrenzte Gleichheit, keine Retail-ABI-/Damageabnahme.

## Task3: frischer deaktivierter Fork und Handoff

Nur nach belegter Task1/2-Vollständigkeit: neuer Builder auf exakt gepinntem Parent,
ganze Sourceinversen, neue Runtime-/Sourcepins/Schema, alle aktiven Gates False,
Core-/Restore-/Input-/TTL-/Queue-/IPC-/Cutoff-/Originalguards unverändert.
Portable Tests gegen tatsächliche Produktionsquellen/transformierte Funktionen; keine
breite Suite und keine Runtime. Neue Methode bleibt inputfrei und unqualifiziert.
Bei konkretem Vollständigkeitswiderspruch STOP ohne Paket/Scopeaufweichung und Root melden.

## Fortschritt / Entscheidungen

- Docvertrag a2033e2 abgeschlossen; Root präzisiert ausschließlich Queue64 (kein32erLimit).
- Vorprüfung: alter TraceValidator setzt `CallID=vorher+1` und `events_attempted=Rows` voraus.
  Neue Native-/Rowzähler dürfen deshalb nicht als FULL18-Paket maskiert werden.
- Task1: vier echte Callback-REDs, danach GREEN. Zusätzlicher Differenzial-RED zeigte,
  dass Original-`sequence` wegen Init-Ankern unverändert bleiben muss; separate `row_sequence`
  implementiert, ursprüngliche Kettenpayloads einschließlich Anker bytegleich.
- Task2: alte Policy verwirft die tatsächlichen neuen Pakete (`unexpected fields`, erwarteter
  Scope-RED); neuer strikter Validator GREEN. Unbekannter echter Waffenbesitzer zunächst
  fälschlich akzeptiert (RED), danach erhaltene Row + INCOMPLETE/FAIL. Schema gegenseitig strikt.
- Task3: fehlender Builder zwei REDs; danach sieben ganze Quellinversen und Manifestvertrag GREEN.
- Ruling: S friert den positiven Row-/Nativezählerstand ein, F den endgültigen Rawnenner.
  Bereits zugelassene normale Cleanup-Leaves nach S bleiben bis F roh archiviert, zählen aber
  nicht nachträglich zum positiven S-Fenster. Bestehende Session/Worker/Rawprotokolle unverändert.
- Ruling aus echtem RED: ein fehlgeschlagener echter Return ist nicht weiter offen Pending.
  Neuer reiner `incomplete_closed`-Fehlerzähler; jeder Wert>0 bleibt INCOMPLETE/FAIL. Keine
  künstliche Excluded-Finalisierung zur Reparatur eines Guardfehlers.
- Ruling aus echtem RED: Pending darf keine volle Row über `frame.partial` zurückhalten.
  Nach erfolgreichem unverändertem Emitguard wird ausschließlich auf der Auslassungsseite
  diese alte Rowreferenz gelöscht. Guardfehler behalten ihren echten Terminal-/Frame-Rawbeleg.
- Erster deaktivierter Autorencheckpoint (Pfad ohne `-v2-`) ist superseded und unverändert;
  kein Runtime/Native. Finaler separater v2-Fork erst nach abschließendem Source-/Pinaudit.
- Gezielte20 Tests GREEN1,683s; kein Gesamt-/Native-/Damage-/Firststate-PASS.
  Zwei gesonderte Fixturefehler (falscher nonmain-call-Parameter und fehlender Test-ops-Marker)
  wurden in eigenen Logs erhalten; keine Produktiv-REDs daraus behauptet. Ebenso erster
  GREEN-Versuch mit vertipptem Parenthash und exakter Fragmentabweichung offen geloggt.
- Root-Folgeruling nach abschließendem echtem Receive-RED: jede explizit vorhandene
  `payload.chain_bound=false` und `respawn_source.chain_bound=false` ist INCOMPLETE,
  Receive zusätzlich nur mit echtem Inflictor und `chain_bound=true` auf beiden Kanten.
  Fehlende/nicht zutreffende optionale Felder und `respawn_source=null` sind kein Fehler.
  Tatsächliche gebundene Colt- und vollständige originale Respawn-Kette bleiben positiv.
  Neun False-Chain-Gegenfälle plus echte Receive-Ownerlücke RED→GREEN; keine JS-/Queue-/
  TTL-/Originalguardänderung. D-v2 und erster Root-Fork vor Native superseded/erhalten.
  Frischer D-v3 nach engem Forwardfix; keine gleichartige alte Nativewiederholung.
- Abschluss:23gezielte Tests PASS1,982s. Frischer D-v3,274/77/14Pins,
  sieben ganze Sourceinversen,121Parentdateien und vier Coredateien bytegleich.
  Private `final-source-proof-v3.json` SHA256
  `ff660d92c3e662d5838b409ad082c3ac35a3cc3a8232e50d73c27aa3edfe1e10`.
  Keine Nativeausführung/Qualifikation; alte D/D-v2 und Root-F-v1 bleiben superseded/NEVER_NATIVE.
