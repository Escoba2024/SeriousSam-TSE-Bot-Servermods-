# FirstState: deaktivierter inputfreier Original-Methodenvergleich

**DISABLED_INPUTFREE_METHOD_PAIR_PREPARATION_ONLY**. Keine Runtime, Frida-, Display-, Input- oder Spielausführung. Kein A1-/Schadens-/18-ABI-Nachweis. Root prüft, friert ein und startet gegebenenfalls selbst.

Der neue private Fork übernimmt den vorhandenen PitchRoot mit Originalserver und zwei eigenen unveränderten Originalclients. Genau zwei separat deklarierte Arme `control|trace`, jeweils zehn Sekunden inputfreie Beobachtung nach normalem Join. Kein automatischer Paarstart und kein Retry. Die Rootentscheidung ersetzt die frühere Einzelfensterannahme; alte fehlgeschlagene Versuche werden nicht als gültige Kontrolle verwendet.

Der enge Runnerpatch entfernt die unbenutzten Worker-/Recorderimporte und die Pitch-/Eingabevorbereitung aus dem Mainpfad. Er erzeugt keine X11Transport-/Endpointobjekte, keinen Fokus, XTest, Maus- oder Fireaufruf. Die bisherigen eigenen PID-Fenster werden passiv mit denselben xwininfo/xprop-Prüfungen gebunden. Original-/Map-/Profil-/MIP-/NIP-/Module-/Namespace-/Query-/Host-/Transactionguards und normaler Close bleiben erhalten. Alle übrigen Top-Level-Funktionskörper sind AST-gleich. Die vollständige inverse Source ergibt den alten Runner SHA256 `5b348963edd8333aa500bde864675fc167cc0d4fdae07445dae3de5c2fc0051a`.

`parent_started` beginnt am Maineintritt. Setup verbraucht das 85s-Innen-/90s-Admissionbudget; kein Reset nach Join. Kontext- oder Workerkosten dürfen eine abgelaufene Admission nicht durch Armung reparieren. Das ist kein harter Kill-Watchdog: ein bereits gebundener langsamer Startupaufruf oder normaler Cleanup/Restore kann überlaufen und muss ehrlich als FAIL abgeschlossen werden. Kein Rollenparent wird blind beendet und es gibt keine unbelegte PASS≤90s-Gesamtlaufbehauptung.

Control importiert keine Worker/Frida/MethodenAPI und verwendet nur die bestehenden passiven Guards. Trace lädt den unveränderten Methodenadapter verzögert: NativeContext/LegacyWorkerPorts/ObserverSession, 72 Pins, 38 Originalregionen, 11 Importbindungen, 18 Calllistener und exakt zwei Registryakteure. Die feste Tracekonfiguration bleibt 64 Records/8192 Calls/16384 Events/1024 Damagecalls/256 Gettercalls/2000ms Binding/15000ms TTL. Absolute Observerdeadline ist `min(parent_started+85, arm_now+15)`; IPCgrenzen 3s Arm/.1s Drain/2s Cleanup bleiben. Keine Input-/Gain-/ACK-/Toleranzänderung.

Der Methodenhandle wird vor `run()` im Parent gehalten. Auch bei Armfehlern bleiben Observer/Worker erreichbar. Im `finally` erfolgen Stop, finaler Drain, Unload, Detach und externe Originalregionen vor dem unveränderten normalen Rollenclose. Erst nach frischem Quiescencebeleg und Normalcloses/leerem Unitnachweis aller drei Rollen wird ausschließlich der eigene Worker gereapt. Rawantworten, Pakete, Counter und Cutoff bleiben privat vollständig; die API behält ihre 2-MiB-Payload-/16-KiB-Hüllengrenze.

Eigene Statusprädikate lassen keinen GenericTrial-PASS als Ersatz zu. Control kann höchstens `PASS_LIMITED_UNINSTRUMENTED_TWO_ORIGINALS_ONLY` erreichen. Trace verlangt echten TLSbeleg, mindestens ein vollständiges autoritatives ProcessGameTick-Enter/Leavepaar, vollständigen alten TraceValidator, 38 externe Restoreregionen und normalen Gesamtcleanup für `PASS_LIMITED_FIRST_STATE_METHOD_OBSERVED_CALLBACKS_ONLY`. Ein Non-main-Tickpaar zählt nicht. `observed_callback_kinds` nennt nur tatsächlich aufgerufene Callbacks; unaufgerufene Init-/Bullet-/andere ABIs und Erstzustandsschaden bleiben unqualifiziert.

Author-Runner und Manifest sind false; auch die MethodenAPIgates sind false. Die sechs geerbten Input-/Collector-Gates, der ungenutzte BaseWorkerCLI und der alte unveränderte FirstStateRunner bleiben false. Andere geerbte eigenständige Methodenquellen werden weder importiert noch ausgeführt.

Der Rootreview fand eine echte Lücke im ersten Paketverifier: nur Keysets und selbst gepinnte Werte wurden geprüft. Fünf tatsächliche RED-Gegenfälle (repinnter API-Body, Policy, verschachtelter Hash, Pfad, Helper) belegen dies. Der finale Verifier vergleicht vollständige erwartete Hashwerte gegen unveränderte gepinnte Eltern; nur exakter Runnerdelta, vollständig retargetetes Untermanifest und fest gepinnter Helper sind eigene Sollwerte. Das aktuelle erste Paket war bytekorrekt; seine unzureichende Verifiergarantie bleibt dokumentiert. Checkpoint `f2cae1f7…` ist erhalten.

Finaler Fork: `/srv/tse-a1-first-state-inputfree-method-final-disabled-20261115`, Manifest SHA256 `51e1bc45eb312f3d9b03dd07640fa436a588f3363ed1d00d93454a01f1ceb365`; 151 Gesamtpins einschließlich aller 72 Methodenpins. Runner `2c79c51dcdd3c757c9fd190c56d33a21c0a1635aa16e0d55890f54783c6f7eef`, Helper `6ec98fa31f2280285a0fb41d0afc5bf0b51e9efe2ba005efb3642aba32e131e2`, Untermanifest `075de9a579a22bc2807586eb454e30273f51ad6c01d2e8d53af89e6bb610d278`.

21 fokussierte Offlineprüfungen bestanden in 5,113 Sekunden: zwölf Helper-/Clock-/Cleanupfälle und neun Source-/Closurefälle, einschließlich tatsächlicher vorheriger REDs für abgelaufenes Kontextbudget vor Arm, nichtautoritative Tickpaare und alle fünf Rootreview-Gegenfälle. Reproduktion:

```sh
python3 -m unittest tools/test_first_state_inputfree_method.py tools/test_prepare_first_state_inputfree_method.py
python3 tools/prepare_first_state_inputfree_method.py --output /NEUER/PRIVATER/PFAD
```

Private Logs/Sourcepins/Vollquittung: `.codex/evidence/first-state-method/`. Die frühere MethodenAPI selbst ist bytegleich und deren 35 Prüfungen werden nicht als neue Nativeabnahme wiederholt. Noch offen: unabhängiger finaler Rootreview, tatsächlicher Control-/Trace-Methodenvergleich, beobachtete Callback-ABIs und Messkosten. Kein Livewechsel.

## Rootstand vor dem Nativevergleich

Root hat den vollständigen Source-/Testreview abgeschlossen und21Checks erneut
bestanden(5,106s). EigenesEnabledFreeze b86615c1/Runner6a33221a/Nested0c4ab262
aktiviert ausschließlich Main, den tatsächlich verwendeten Methodentransport,
dessen Manifest und das kompilierte Observergate; zwei private Namespaces ändern
sich. Alle weiteren90Dateien bleiben bytegleich, einschließlich Body, Policy,
Bindungen und ungenutzten Input-/BaseCLI-/FirstStategates. Unabhängiger enger
Rootdelta-/151+72Pinreview:3f787786PASS_SCOPE. Das frühere Rootfreeze26d62d26
blieb als ungestarteter Checkpoint mit deaktiviertem Trace erhalten. Keine
qualifizierte18ABI-/Schadensbehauptung und keine Lockerung der Konfiguration.

Root startet genau einen getrennten Controlarm und, nur nach dessen Erfolg und
Restore, einen Tracearm. Der jeweilige Wrapper hält zusätzliche gemeinsame
Sperren; der Runner hält die Fixture exklusiv. Privatarchive werden vor Start
voll extern rückgelesen und rekonstruiert. Beide tatsächlichen Ergebnisse stehen
noch aus; ein Build oder Start ist kein Methoden- oder A1-Erfolg.
