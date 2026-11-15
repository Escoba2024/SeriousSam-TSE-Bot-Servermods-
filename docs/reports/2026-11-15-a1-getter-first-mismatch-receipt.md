# A1: Fehlerbeleg aus genau dem ersten Gettervergleich

Der neue reine Transform `tools/first_state_getter_mismatch_patch.py` erweitert
ausschließlich Fehlerdaten. Er akzeptiert den unveränderten deaktivierten
Observerkörper `206a232e…` und die kompilierte JS-Datei `7108529a…`.
Alle bisherigen Dateien und Pakete bleiben unangetastet.

Drei bestehende Getterguards – in `lifetime()`, am Eingang von `emit()` und
im gestoppten `drain()` – rufen dieselbe neue Routine auf. Diese liest denselben
22-Byte-Bereich einmal, ruft die unveränderte HIGHLOW-Rebasierung auf und
vergleicht mit derselben Längen-/Bytebedingung. Bei PASS folgt kein zusätzlicher
Read. Bei FAIL wird **dieses bereits gelesene Array** über den bestehenden
`need`-/`fail`-Pfad als `errors[].raw.detail` erhalten:

- `actual_hex`, `expected_rebased_hex`, `rva`, `length`;
- `getter_registered`, `getter_callbacks`, `tls_bound`, `tls_binding`.

Es gibt keinen späteren Ersatzread, Flush, nativen Funktionsaufruf, Timer,
Gettereingriff, Memorywrite oder neue Hookstelle. Fehlertext, Faultzähler,
äußeres Packetschema, Grenzen, Gates und bestehende Guardentscheidungen bleiben
erhalten. Das Detail verwendet ausschließlich bereits vorhandenen JS-Zustand.

Echtes RED gegen den alten kompilierten Observer: fünf VM-Verhaltensfälle
scheiterten am fehlenden Raw-Detail, ein Inversentest war vor Existenz des
Transforms explizit übersprungen. Kein Import-/Setupfehler als RED gewertet.
Danach sieben fokussierte Tests PASS (0,571 s); abschließend mit den geerbten
gezielten Fällen auf **dem neuen kompilierten Quelltext**:

```sh
nice -n 15 python3 -m unittest tools.test_first_state_getter_mismatch_patch
```

**8 Tests PASS, 1,074 s.** Die Tests decken alle 22 Byte-Mutationen an zwei
Modulbasen ab, einschließlich HIGHLOW, je genau einen Getterread auf PASS/FAIL,
echten `fail()`-Detaileintrag, Non-Main-Emit und gestoppten Drain sowie aktive
Gettercallbacks mit noch registrierter Probe. Beim Same-Read-Gegenfall ändert
das Modell den Speicher nach dem Read wieder auf Original; der Fehlerbeleg
enthält dennoch die zuvor gelesene abweichende Sequenz. Die geerbten I1/I2-
Ketten, TTL-/Epoch-/Header-/Body-/IAT- und Disabled-Guards bleiben bestanden.

Ganzkörper-/Compiled-Inversen, bytegleicher `G`-Präfix und Abweisung fremder
Quell-, Gate- und Guardänderungen sind geprüft. Private Logs und Quittung mit
vollen Quellhashes liegen unter `.codex/evidence/a1-getter-mismatch-receipt/`.

Dies liefert **keine Getterursache oder A1-Abnahme**. Auch Roots eigener
ELF32-Instruktionsprobe-`+15`-Methodenfall reproduzierte den nativen äußeren
Callbackfehler nicht (Quittung SHA256
`e652e3d00b557ad7b9453eb87e1eb52f2498117acd2109fd7ce7d9d35dea5120`).
Darum wird der Getterguard nicht abgeschaltet oder verändert. Erst ein
gesonderter prospektiver Root-Diagnoselauf könnte die tatsächlich ersten
abweichenden Nativebytes erfassen. Kein Paket, Freeze oder Native wurde hier
erzeugt oder gestartet.
