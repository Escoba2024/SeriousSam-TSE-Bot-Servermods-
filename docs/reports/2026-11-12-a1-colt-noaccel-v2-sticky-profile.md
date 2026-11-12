# I1-Korrektur: Profilfehler bleibt vor Tickfehlern fatal

READY für unabhängigen Offline-Re-Review. Beide Gates bleiben false; kein Native, Attach, Build oder aktueller Labread durch den Autor. Root besitzt Integration, Freeze und höchstens das eine separat autorisierte Vergleichsfenster.

## Nachgewiesener Fehler

Der unveränderte V1-Reader las AllowMouseAcceleration=1 und MouseSensitivity=0,25. Ein danach erkannter Tickwechsel löste jedoch vor der Profilprüfung einen allgemeinen state changed during read aus. main.sample verwarf den Versuch und akzeptierte später richtige Werte; die falschen Rohbytes fehlten im Attempt. Der exakte unabhängige Test wurde in eigener Kopie tatsächlich RED reproduziert: drei Fälle, zwei PASS und eine Assertion FAIL.

## Enger Fix

1. Der optionale Reader prüft die gelesenen Globals sofort auf exakt 0/0,25. Zuerst werden Adresse, Phase, Raw-Hex und dekodierte Werte gespeichert. Auch ein nicht endlicher Float bleibt über seine Originalbytes und einen JSON-kompatiblen Textwert erhalten.
2. Im vorhandenen zweiten Durchgang bleiben Read-Reihenfolge und vorgesehene Adressen gleich. Im optionalen Modus wird ein gewöhnlicher Mismatch erst nach dem restlichen vorgesehenen Durchgang gemeldet. Dadurch hat ein tatsächlich gelesener falscher zweiter Profilwert Vorrang. Es gibt keinen zusätzlichen Read-Durchgang, keine neue Adresse und keinen weiteren Retry.
3. read_rotation_pair übernimmt die Profil-Rohlesungen vom Fehler in die bestehende Failure-Receipt. main.sample schreibt und flusht sie über seinen vorhandenen finally-Pfad. Korrekte Globals bei einem reinen Tickwechsel bleiben weiterhin transient.
4. Ein Profilfehler wird zusätzlich im bestehenden Report als fatal_mouse_input_profile mit dem ersten Attemptindex gespeichert. Jeder weitere sample-Aufruf scheitert vor Throttle, Zeitlesung und neuem Readerzugriff. Auch ein anschließend korrektes Profil kann diesen Fehler nicht aufheben. Das verhindert akzeptierte Folgepaare und damit Folgeeingaben; Safe-Release und Cleanup benutzen diesen Guard nicht.

Die zweite Fehlerkennung wurde ebenfalls zuerst RED gegen die tatsächliche main.sample-Funktion reproduziert. Danach sind sämtliche sieben gezielten Fälle GREEN. Es wurden keine nativen Zwischenzustände erfunden; alle Gegenfälle sind reine Speicherfixtures.

## Bewusst erhalten

Das gekoppelte normale Profil 1/1→0/0,25, der exakte Grundfaktor 0,25, Setter, Seal, Startquittung und vollständiger Restore sind unverändert. mouse_input_profile.py sowie zwölf weitere Kern-/Policy-/Transportdateien sind bytegleich. 53 der bisher 54 geschützten Funktionen sind AST-identisch; die einzige Änderung darunter ist die eben beschriebene terminale Fehlerbehandlung in main.sample.

Defaultreader, Coltgeometrie, 14 ursprüngliche Colt-Guards und drei Mouse-Guards bleiben erhalten. Die bestehende Erwerbsgrenze von acht Reads/0,2 s, 2-s-ACK, 85/90 s, 48 Aktionen, Gain/EPS, finaler Transportcheck, Safe-Release und alle Identitäts-/Host-/Close-/Restoregrenzen wurden nicht geöffnet. Keine Inputentscheidung oder Anzahl wurde geändert. Ein eindeutiges V2-Unitpräfix verhindert Labelverwechslung.

## Tatsächliche Tests und Belege

64/64 gezielte und betroffene Reader-/Erwerbstests in 0,416 s, ohne Fehler oder Skip. Enthalten sind 32 bestehende Repository-Readertests, sechs Colt-Readertests, vier optionale Mouse-Readertests, zwei tatsächliche Paar-/Receiptprüfungen, 13 bestehende Erwerbsregressionen und sieben konkrete Sticky-/Raw-Fälle. Keine zusätzliche Vollsuite wurde gestartet.

Die V1-Quittungen 240+32 bleiben historisch erhalten. Sie werden für bytegleiche Setter-/Start-/Restoreteile wiederverwendet und nicht als neuer V2-Gesamtlauf ausgegeben. Neue Quittung: evidence/final-v2-targeted-regression.json. RED-Stufen: evidence/red-reviewer-sticky-profile-tests.log, evidence/red-v2-sticky-profile-tests.log und evidence/red-terminal-v2-sticky-profile-tests.log.

V1 (252 Dateien), ursprünglicher Colt-Autor (233), Root-Freeze (233) und Native-FAIL 171044 (686) bleiben vollständig unverändert. Beleg: evidence/v2-protected-final.json. Der genaue alte Cursor-/Recenter-/Prescanursprung bleibt offen.

## Übergabegrenzen

Quellenvergleich: evidence/v2-runtime.diff und evidence/v2-normalized-delta.json. Finale Pins: source-manifest.json, HANDOFF.json und FINAL-VERIFY.json. Der Reader-/Controllerpfad wurde ausschließlich offline qualifiziert; Root braucht weiterhin einen frischen vollständigen Runtime-/Fixturepreflight.

Original EnableInput prüft seinen Plattform-API-Rückgabewert nicht. Ein tatsächlicher Beschleunigungseffekt und reproduzierbare Achsengewinne bleiben Gegenstand des späteren einen Vergleichs. Kein automatischer Retry und keine weitere Parameteränderung. Vorbereitung bleibt ohne First-State- oder Exactly-once-Nachweis. Auch ein später erfolgreicher Colt-Hold ersetzt weder freie LOS noch kausale Fire/Bullet/Damage- und Lebens-/First-State-Belege.

Paket: /srv/tse-a1-colt-noaccel-v2-completion-20261112
Delta-SHA: 3042a37d640d616880d61691274c76141b2c20c13ae87b2d4ed7e5021317503b
