# Deaktivierte registrierte Erstzustands-/Schadensmethode

Der neue Messvertrag `REGISTERED_FIRST_STATE_DAMAGE_V1` lässt ausschließlich konservativ
abgeschlossene Weltcast-Aufrufe ohne beobachteten Colt-/Launchvorfahren aus vollen Eventrows aus.
Der bisherige NaturalAI030-FULL18-Lauf bleibt FAIL (Queue64/drop1); es findet keine Umwertung
seiner Rawdaten statt. Dies ist portable Quell-/Methodenvorbereitung, keine Retailqualifikation,
kein nachgewiesener Erstzustand, normaler/tödlicher Schaden oder A1-PASS.

Ausgangspunkt ist die exakt gepinnte NaturalAI030-StatusV2-Kopie, Manifest
`2c43de1f91809d591a8631a7aeac2c03f02ee365c0b33d00993803c88a4d26b9`.
Neue Quellen sind `first_state_registered_damage_patch.py`,
`first_state_registered_damage_policy.py`, `prepare_first_state_registered_damage.py` und
drei zugehörige Tests. Alte öffentliche FULL18-Helfer und alle alten Pakete bleiben unverändert.
Der Builder erzeugt sieben genau inverse Quellenänderungen ausschließlich in einer frischen Kopie;
hinzu kommen eigene Namespace-/Manifestpins und der ungenutzte Collector-PRIVATE-Pfad.

Der tatsächliche Callback behält echte globale CallIDs, Parents, Native-`sequence` und alle
alten Daten-/Lebensupdates. Eine zusätzliche `row_sequence` benennt nur volle Rows. Jeder
Weltcast-Kandidat bleibt im vorhandenen Stack Pending; erst sein echter Leave mit vollständigen
Guards finalisiert beide Excluded-Zähler. Relevante Kinder darunter machen die Probe sticky
INCOMPLETE, ohne nachgereichte Eintrittsrow oder gekürzte Parentkette. Beliebig tiefe bekannte
Waffen-/Launchvorfahren verhindern die Auslassung. Nicht registrierte Besitzer/Ketten bleiben als
volle Rows erhalten und werden ausdrücklich INCOMPLETE verworfen.

Alle18 Attachstellen, G/PE/HIGHLOW-Fingerprints, Original-/TLS-/Lifetime-/State-/ABIlesungen,
`enterData`/`leaveData`,38Regionen und Inputfreiheit bleiben erhalten. Der alte Emitguard einschließlich
Getter, beiden Clockprüfungen, TTL, native16384 und Queue64 wird auch vor jeder ausgelassenen Kante
ausgeführt. Es gibt keine zusätzliche Engineabfrage oder Zeitabfrage. Keine Rowpayloads werden
als versteckter Pending-Nebenpuffer behalten; nur der vorhandene Frame und Skalare bleiben.
Ein tatsächlich zurückgekehrter, aber nicht erfolgreich abgeschlossener Kandidat ist
`incomplete_closed`, niemals weiter offen Pending oder künstlich Excluded.

Der neue Validator bewahrt die ursprünglichen Zustands-/Generations-/Parent-/Originalbyteprüfungen
und prüft getrennte Native-/Row-/Kind-/Pendingnenner. Beide Scopes verwerfen Pakete des jeweils
anderen Vertrags. S bleibt der positive eingefrorene Row-/Nativezählerstand; F bleibt der finale
Rawnenner einschließlich bereits zugelassener normaler Cleanup-Leaves. Worker, Session,
Raw-before-parse, alle1..F-Versuche, Hash-/Zeit-/S/F-Grenzen und Cleanup sind unverändert.
Die alte FULL18-Schadens-Endauswertung darf nicht ungeprüft auf die neue Rowdomäne übertragen
werden; dieser Fork bleibt eine inputfreie Methodenprobe mit neuem beschränktem Statuslabel.

Echte REDs wurden vor den jeweiligen Ergänzungen beobachtet: Weltcast-Rows/Pending/Ancestorfehler,
native Sequence/Init-Anker-Differenz, neue Scopepakete am alten Validator, unbekannter Besitzer,
fehlender Builder, zurückgekehrter Fehlerkandidat und versteckter Pending-Rowpayload. Gezielte
Offlinefälle prüfen außerdem den vollständigen tatsächlichen Colt→Prepare→Launch→Cast→Direct→
ReceiveDamage-Pfad gegen den Parent, einen Immediate-Parent-Mutanten, Queue/Event/TTL/Getter/
Welt/Stack, fehlende Leaves, Thread-/Life-/Rawfehler, echte BatchSession mit neuen Paketen sowie
Raw/Hash/S/F/Drop-Gegenfälle. Kein Test führt Frida, Wine, X11 oder Spielprozesse aus.

Reproduktion im Autorenworktree:

```sh
python3 -B -m unittest tools.test_first_state_registered_damage_patch tools.test_first_state_registered_damage_policy tools.test_prepare_first_state_registered_damage -v
```

Private Logs/Sourceproof liegen unter
`/srv/tse-registered-first-state-damage-evidence-20261115` (0600). Bewahrte technische
Fixture-/Import-/Pinfehler werden nicht als Verhaltens-RED ausgegeben. Root prüft und entscheidet
eine neue deklarierte Methodenbedingung; keine automatische Ausführung oder Wiederholung.

Die abschließende Autorenprüfung reproduzierte noch eine engere Policylücke: ein tatsächlicher
ReceiveDamage mit `scope=registered`, unbekanntem Inflictor und `chain_bound=false` war transportseitig
akzeptiert worden. Dieser echte RED und neun False-Chain-Gegenfälle führten gemäß Rootentscheidung
zu einem separaten Forwardfix: jede tatsächlich vorhandene explizit falsche Kettenbindung
(einschließlich vorhandener Respawnquelle) ist INCOMPLETE; Receive verlangt zusätzlich echten
Inflictor und wahre Bindung auf beiden Kanten. Optionale nicht zutreffende/null-Felder werden nicht
erfunden oder pauschal verworfen. Vollständig tatsächliche Colt- und Respawn-Ketten validieren weiter.
JavaScript/Originalguards/Queue/Fristen sind unverändert. Alle früheren Autoren- und Rootpakete
dieser Vorbereitung bleiben unverändert, superseded und NEVER_NATIVE; nur ein frischer D-v3 ist
für die anschließende Rootquellenprüfung bestimmt. Das ist keine Umwertung alter Nativebelege.

Finaler Autorenstand:23gezielte Tests PASS1,982s. Der frische deaktivierte Fork liegt unter
`/srv/tse-a1-registered-first-state-damage-v1-v3-disabled-20261115`, Manifest
`1b58376cc824a597fd16be43fb8f7a956467dc05dfa1300c364a5fa37d92809b`, nested
`6f96c79c7838133b05b8d697ab6efaf3a538119732fa858e177f0157d0b6cf03`.
Alle274Runtime-/77Nested-/14historischen ungenutzten Collectorpins frisch geprüft;
sieben ganze Quelleninversen,121unveränderte Parentdateien und vier unveränderte Coredateien.
Der JavaScript-Hash ist gegenüber D-v2 unverändert. Private Autorenquittung
`final-source-proof-v3.json` hat SHA256
`ff660d92c3e662d5838b409ad082c3ac35a3cc3a8232e50d73c27aa3edfe1e10`.
Dies ist Autorenprüfung, keine unabhängige Prüfung der eigenen Policy. Frühere Rawarchive
wurden durch diese Aufgabe weder verändert noch erneut vollständig gehasht/replayed.

Noch offen: tatsächliche neue Retail-Methode, beobachteter Init nach Arm/erster gültiger Tick,
Original-/Botopfer, normale/tödliche vollständige Schadensketten und die prospektiven normalen
Respawn-/Firebedingungen. Ein callback-only Methodenresultat ersetzt keinen dieser Nachweise.
