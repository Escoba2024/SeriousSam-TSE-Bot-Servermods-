# Begrenzte neue Original-Respawn/Festziel030-Bedingung

Ein neuer **deaktivierter** Fork bereitet genau eine normale Original-Fire-
Down/Up-Sequenz nach tatsächlich beobachtetem lebend→dead/MayRespawn2 vor.
Die bisherige inputfreie Methode, alle Maus-/Keyboard-FAILs sowie alte Rawdaten
bleiben unverändert. Es wurde keine TSE-/X-/Frida-Runtime gestartet.

Writer ist `/srv/tse-build030-skulls-closed-audit-20261115`, Branch
`codex/20261115-build030-closed-audit`. Claim: drei neue Quellen und deren drei
Tests, eigene Spec/Plan/dieser Bericht. Root allein integriert/friert/führt aus.
Die Commits vor dem abschließenden Dokumentationscommit sind `854e96c`,
`5b13c3d`, `f6f4a3c`, `c71e76b`, `ab7c95e`, `3634cdf`, `6adfe0f`.

## Tatsächliche Vorbereitung

Parent ist `tse-a1-registered-first-state-damage-v1-v3-disabled-20261115`,
Manifest `1b58376cc824a597fd16be43fb8f7a956467dc05dfa1300c364a5fa37d92809b`.
Build030, Original-Dedicated, Originalopfer global0 und ein tatsächlich
nachgewiesener lokaler AI-Schütze global1 bleiben exakt gepinnt. Einzige aktive
Botconfigänderung ist `bot_iTestTarget=-1`→`0`; die bestehende tatsächliche
Move-/Yaw-/Fire-/Nav-/Settingsclosure bleibt erhalten. Die normale Festziel-
Coltentscheidung ist kein Treffer- oder Todversprechen.

Neue Staging-/Ownershipschemas und exakter neuer Confighash verhindern eine
stillschweigende Übernahme der alten AI-only-Bedingung. Beide Reader werden nur
in der neuen Runnerkopie mit `colt_preparation=False` konstruiert: die optionale
lebende Muzzlegeometrie ist für DEAD_READY nicht erforderlich. Die tatsächliche
Readerquelle/Fehlerklasse/Pointerguards bleiben bytegleich. Es gibt keinen
Fallback oder Readiness-Guard für ungültige Pointer.

Die Vorbereitung verlangt zuerst positive Originalgesundheit **und** Aliveflag,
dann einen tatsächlichen Tod, MayRespawn2 und neutralen Firezustand. Bestehende
passive Context-ASTs lesen MayRespawn/Input doppelt und binden Actor/World/Slot/
PID/Start/Spawn. Die Original-Replik wird zusätzlich mit Serverdaten gebunden;
prozesslokale Pointer werden nicht gleichgesetzt. last_buttons und buttons_now
sind verschiedene Enginefelder: die geforderte tatsächlich beobachtete Gleichheit
ist keine Behauptung garantierter zeitlicher ABIäquivalenz. Abweichungen sind
fatal, ohne Interpolation oder neue Toleranz.

Nach Arm und vorhandener TLS-Bindung wird einmal normal Button1 gedrückt und
freigegeben. Angefragt sind .1s; tatsächliche Down-/Hold-/Up-/Flush-/Neutral-
Zeiten und Server-/Clientzustände entscheiden. .35s Hold, 2s ACK, .2s/8 Reads,
2.35s Mindestreserve, 48 Aktionen/96 Attempts und 85/90s bleiben unverändert.
NativeUp, XSync und Neutralprüfung bleiben auch nach Journalfehler getrennte
Cleanupversuche. Ein fehlender ACK oder Metadatenfehler bleibt FAIL. Es gibt
keine zweite Pressphase und keinen Retry.

Das unveränderte alte 10s-/15s-/64-/16384-/S-F-/Worker-/38-Regionen-Protokoll
wird per eigener Klasse verwendet, ohne dessen Globals zu überschreiben.
Control importiert keine Trace-/Frida-Module; der bestehende passive Context
wird über exakt gepinnte ausgewählte AST-Knoten bereitgestellt. Trace verwendet
weiter den unveränderten tatsächlichen Context/Worker. Die bestehende
Registered-Scope-Validierung bleibt vor der neuen Beispielpolicy zwingend.

Ein Trace-Erfolg erfordert echte vollständige normale Respawn-/Init-/Anchor-/
GameTick- sowie normale und fatale bekannte Colt→Bullet→Cast→Direct→Receive-
Ketten innerhalb S für dasselbe gebundene Opferleben. Init/Anchor/erster Tick/
erste Damage-Sequenzen und native Tickdeltas werden getrennt ausgewiesen.
`first_valid_state_damage_proven=False` bleibt immer ausdrücklich gesetzt:
spätere gebundene Beispiele sind kein Schaden ab erstem gültigem Zustand.
Botopfer, Aim/Gain, ExactlyOnce und A1-Abnahme bleiben offen.

## Portable Nachweise und Artefakte

20 Policy-/Methodtests und 3 Buildertests bestehen; letzter Lauf .408s/.041s.
Die Tests verwenden Fake-C-Ports/Fakeclock und tatsächliche vorhandene reine
Callback-/Validatorquellen. Sie qualifizieren keine Retail-Runtime. Echte REDs
für fehlende Policy/Window/Replica/Namespace/Builder sowie Aliveflag und ehrliche
Inputmetadaten sind gespeichert. Frühe Syntax-/Fixturefehler und ein zu großer
synthetischer Callbackburst bleiben ausdrücklich als solche erhalten; Queue64
wurde durch echte Drains zwischen synthetischen Schüssen eingehalten.

Frischer finaler Checkpoint:

- Pfad `/srv/tse-a1-original-respawn-fixedtarget030-v3-disabled-20261115`
- Manifest `57c65e12ac413ca3231bc9141dc428e44563fe70bc1d86c1811f122ff2bf7177`
- Nested `76b7b2eec759c9e9e414ef8e97c032882655cda180bb7cc3457715d8a69f8907`
- Controller `379dd4cd6a34173c6b203a5d2760cf33c87dd0a2fdc6fa480368df1e756e1c01`
- 280/77/14 tatsächliche vollständige Pinwerte geprüft; 1.64MB kopiert.

Vier ganze Sourceinversen (Runner, beide Ownershipkopien, aktive Config) sind
gegen feste vollständige Parenthashes geprüft. Zusätzlich ändern sich nur
ungenutzter Collector-PRIVATE-Pfad und die beiden Manifeste; 130 Parentdateien
bleiben bytegleich. Alte Inputfreequelle, Body/kompilierter Observer, Schema,
Validator und vier passive Coredateien bleiben unverändert. Aktive Main-/
Instrumentierungsgates und Collector-Metadaten sind False; historische
qualifizierte Core-Gatefingerprints bleiben unverändert.

Private Quittung:
`/srv/tse-original-respawn-colt-evidence-20261115/disabled-v3-final-receipt.json`,
SHA256 `17302d53a6276889f32166072ffe888346a43fcab2915d487a58b80f943e75ec`.
RED/GREEN-Logs liegen dort ebenfalls mit Mode0600, insbesondere
`final-v3-policy-method-green.log` und `final-v3-builder-green.log`.
Der erste Checkpoint mit Manifest `209c359e…` ist unverändert erhalten,
superseded/NEVER_NATIVE; V2 korrigiert auch die obere Inputmetadatenmeldung nach
tatsächlich ausgeführtem Down trotz späterem FAIL.

Ein abschließender konkreter Sourcebefund wurde mit echtem LateRead-RED
reproduziert: ein für sich .02s frischer Read konnte nach 1.99s vorangegangener
Guardarbeit knapp nach der unveränderten 2s-ACK-Frist zurückkehren. V3 prüft
die vorhandene Frist nach `_sample` und vor Akzeptanz zusätzlich. Der Guard
verändert weder Deadline noch Reader. D-v2 `882234d3…` bleibt deshalb ebenfalls
unverändert superseded/NEVER_NATIVE; Root hatte keinen der Checkpoints gefroren
oder ausgeführt. Private `method-late-ack-red.log` enthält den tatsächlichen
fehlenden Reject, nicht einen Aufruf-/Fixturefehler.

Reproduktion: `python3 -B tools/prepare_a1_original_respawn.py --output <frischer
Pfad>`. Private `verify-disabled-v3.py` enthält zusätzlich den tatsächlich
ausgeführten Vollpin-/7-Delta-/ganze-Inversen-Check. Dessen Receiptoutput ist
O_EXCL und muss bei einer erneuten unabhängigen Prüfung einen neuen Pfad haben.

Alle externen Builder-/Pin-/Assetreads verwenden nach explizitem Resolve
NOATIME/NOFOLLOW. Eine frühere gezielte Hilfsquellenlektüre ohne NOATIME ist im
Planledger erhalten; mangels Vorherpin wird dafür keine unveränderte atime
behauptet. Es wurden keine Fixturezeiten korrigiert und keine Originaldaten
geschrieben. Diskfloor8GiB+64MiB+Kopiergröße wurde vor dem Fork geprüft.

Dies ist ein Autoren-Source-/Pinbeleg. Rootreview und jede tatsächliche neue
Kontroll-/Tracebedingung bleiben getrennte Nachweise; keine NativeReady- oder
FirstState-/Damagequalifikation folgt aus dem deaktivierten Paket.
