# Build023: deaktivierte Supplydiagnose180s/Diagnostics1

**PASS_OFFLINE_DISABLED_ONLY.** Genau ein180s-Fenster ist vorbereitet,
keine Runtime gestartet. Zweck: neue tatsächliche
`BotCecilSupplyDiagUnavailable`-Gründe und ihren Zielkontext beobachten.
Der frühere103s-Lebenslauf wird nicht als reproduziert vorausgesetzt.
Keine DLL-/Gameplayänderung, Promotion oder A4-Freigabe.

## Herkunft, feste Bedingungen und Deltas

Unveränderter deaktivierter Parent
`/srv/tse-nav20-023-red600-disabled-20261114`, Manifest
`51d72a2cf233ff87d2f0cac0d3ad2a532f6f287e6ef62bd154b43e6e4ba8e5e8`.
Derselbe tatsächlicheBuild023/Source4190baf, Manifest
`a7b057ba42cfe60eff057bddfde40436720074aa9247515990f9f92944b23080`,
DLL `4dec2aa434c50ad602f1f9f136bf7f8663e9d16c5896a17ea1d343db8faf4883`.
47Source-/28Overlaydateien, Manifest und DLL frisch geprüft; insgesamt77Buildpins.

Red Station, Hard2,8DEMON/tier3-Bots+Originalclient20FPS, dieselben Seeds,
Navdaten und Regeln. Nur180s/Diagnostics1 statt600s/Diagnostics0. Eine neue
kurze Diagnosepolicy erlaubt ausschließlich diese Kombination und023.
Die beiden bisherigen Vergleichs-/Hardmap-Optionspolicys bleiben bytegleich
und lehnen180s/Diagnostics1 weiterhin ab. Alle übrigen Funktionen, Renderer-
Zuweisungen, Reader, V3-Hüllen, Raten, Sleeps, Inputs, Ressourcen-/Aktivitäts-
Gates, Module-/Identitychecks sowie Close/Restore bleiben unverändert.

Die zwei exakt reversierbaren Quelldeltas betreffen ausschließlich:

- `run-a4.py`: neue enge Optionsprüfung, privateNamespaces, Diagnose-Scope/
  PASSbezeichnung und eindeutige CLIdefaults180s/diag1; Gate bleibtFalse.
- `adapter_policy.py`: Optionsimport zum neuen Diagnosetyp. Unverändertes
  `cohort(role,diag)` setzt die vorhandeneDiagnosticsvariable auf1.

69übrigeParentquellen sind bytegleich. NeueQuelldateien imRepository:
`build023_supply_diagnostic_policy.py`,
`prepare_build023_supply_diagnostic.py`,
`test_build023_supply_diagnostic.py` unter `tools/`. Der vorhandene
Finalizer selbst bleibt unverändert; nur sein zulässiges PASS-Präfix heißt
jetzt `PASS_LIMITED_SUPPLY_DIAGNOSTIC_OBSERVATION_ONLY`. Jeder vorhandene
Fehler oder unvollständigeCleanup bleibtFAIL.

## Messgrenzen und spätere Sourcebindung

Diagnostics1 aktiviert vorhandene Selection-/Candidate-/Unavailable-/Terminal-
Diagnostik, begrenzte Supply-/Approachfenster sowie weitere Aim-/Rotation-/
Input-/Weapon-/Snapshotlogs. Zusätzliche Metadatenreads, vorbereitetePfad-
Traversierung, Formatierung und Log-I/O ändern die Testbedingung und Last.
Es werden weder neue Memoryreader noch neue Gameplayeingaben eingeführt.
Die unveränderten Hostgrenzen gelten trotzdem strikt. Ein akzeptiertes
Diagnosefenster wäre keine Vergleichs-, Budget-, A4-, Strength-, Sync- oder
Dauerqualifikation. Aktivitätsgates werden für180s nicht gelockert; fehlende
Belege können den gesamten Lauf weiterhinFAIL beenden.

Die vorhandene Unavailablezeile enthält lokalenSlot, Sourcegeneration,
**Itementity** (nicht Botentity), typisierten ReadReason sowie Flags/Render,
Metadatengültigkeit, Playerindex, Pickedmask/-Status, PickupOnce/Dropped/
Respawn, rohenWaffentyp, WeaponsStay, Current/Owned/Usable/Mapped und
Goalstart/Deadline. Dies sind spätere Sourcebeobachtungen, keine schon
geprüften nativen Ursachen. Einzelne typed_need-Unterbedingungen werden durch
diesen Sammelgrund nicht vollständig getrennt.

Nach einem Rootlauf ist jeder Grund streng zu binden: Rolle/Local→tatsächlicher
Ownslot und Registry-PID/Start/World/Epoch; Sourcegeneration→CecilState-/Spawn-/
WPOkette und genau dasselbe lebendeNativeleben; Itementity/Goal/GoalEnd sowie
`since/deadline` getrennt vom BotEntitykontext erhalten. Vorhandene gedruckte
Rundungsintervalle/exakteNativefloat-Lebensgrenzen bleiben unverändert; keine
policytick/20-Interpolation oder neueEPS. Die bestehende V3-Auswertung und
sämtliche Rohhüllen bleiben bytegleich. Diese Vorbereitung implementiert
keinen neuen automatischen Kausalitätsauditor und behauptet keine erfolgte
Nativebindung.

Der Unavailablehelper ist auf höchstens eineZeile jeSekunde/Local gedrosselt.
Rasche Zielwechsel können daher Details verlieren. Fehlende, ambige oder
nicht ausreichend gebundene Gründe bleiben **UNKNOWN**; ein niedriger
Fehlerzähler oder fehlendeZeile löst die früheren103s-/76s-Leben nicht.

## Offlinebelege und Übergabe

Zunächst7erwarteteREDs bei fehlendem Builder/Diagnosetyp, Exit1. Danach7neue,
7Build023-,6Observer20- und9Vergleichstests: **29/29PASS**, alleExit0.
Generator und separater Paket-/Byte-/Pincheck ebenfallsExit0. Kein
Runtimecontroller wurde importiert; keine Compiler-/Spiel-/Displayoperation.

```sh
python3 -B -m unittest discover -s tools -p test_build023_supply_diagnostic.py -v
python3 -B -m unittest discover -s tools -p test_navigation_build023.py -v
python3 -B tools/test_navigation_observer20.py -v
python3 -B tools/test_navigation_comparison.py -v
python3 -B tools/prepare_build023_supply_diagnostic.py --destination /NEUER/PRIVATER/PFAD
```

Frischer deaktivierter Fork
`/srv/tse-build023-supply-diag1-disabled-20261114`:

- Manifest `01de2abab7fd5313c96529f8a63a4da8a960eb708005c82edf4fdb5f68ee3e95`.
- Controller `ddbb048f512c207320794f3aa26d4331503cf76c6b7984cf85dda39562b0f6a6`.
- 140Runtime-/76Source-/46Pythonpins frisch richtig; alle Runtime-/Reviewgates
  und QualificationflagsFalse. Kein Retry oder automatischer Folgearm.

Plan/Claim `df743fb`; adversarialerREDvertrag `9297ab3`; Produktionsvorbereitung
`3fdd9a3bcfbc0bafeeaa3d2c21dac368e28ea50f`. PrivateQuittung im eigenenWorktree
`/srv/tse-build023-supply-diag1-20261114/.codex/evidence/supply-diag1/final-receipt.json`,
SHA256 `f63915e864e287ee5a85d8e6bec440d9fb661e4f3366968b396a3fddf9868ea8`.
VollständigeCommands/Outputs und REDs daneben, Dateien0600/Verzeichnis0700.
Keine privaten Rohlogs oder Retaildateien im öffentlichenRepository.

NächsterSchritt: unabhängigerRootreview, gegebenenfalls separaterFreeze und
frischerPreflight. Root allein startet exakt einDiagnosefenster. Alle eigenen
Offlinejobs beendet, kein unbeaufsichtigter Auftrag läuft weiter.
