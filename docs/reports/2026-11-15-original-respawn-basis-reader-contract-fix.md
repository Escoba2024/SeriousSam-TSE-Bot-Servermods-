# Korrektur des expliziten DEAD_READY-Readervertrags

Der geschlossene Root-Control vom 15.11.2026, 17:03:21 UTC, scheiterte vor dem
MethodWindow, Readinessreads oder Input am unveränderten Readerguard:
`mouse input profile requires explicit Colt mode`. Result SHA256
`1b60c4088456518e6a0b2ca19cab8e46cd810d3141cd12ecb54d397a21dac88c`;
Status FAIL und null Inputs wurden aus dem vorhandenen Resultat bestätigt.
Root meldete vollständigen unabhängigen Restore; dieser Bericht ersetzt dessen
Nachweis nicht. Alte D-v1/v2/v3 und der tatsächlich gelaufene F-v1 bleiben erhalten.

Die Ursache ist meine neue Runnerkonfiguration, keine belegte Null-/Startup-
Transientursache: sie kombinierte `colt_preparation=False` mit
`mouse_input_profile=True`. Der tatsächliche Konstruktor in
`retail_inventory_readonly.py:325–341` und `snapshot:37–45` verlangen ausdrücklich
Coltmodus für den optionalen Mausprofilzusatz. Die bisherige Builderprüfung
prüfte diese echte Interfaceabhängigkeit nicht.

Die engste von Root bestätigte neue Bedingung setzt am Vanilla-Basisreader beide
Flags ausdrücklich auf False. Nur dieses Builderliteral und neue beschreibende
Metadaten ändern sich. Die alte Readerquelle, Pointer-/Klassen-/Readinessguards,
Fehlerklasse, Fristen, Source-/Role-/DLL-/ABIbindungen und Firepfade bleiben
unverändert. Es gibt keinen Fallback und keinen akzeptierten Nullsnapshot.
Der reine normale Fire-/Respawnfall fordert weder lebende Muzzlegeometrie noch
perFrame Maus-Gain-/Prescan-Globals an. Daraus folgt keine Maus-/Aim-/Gainabnahme.

Die transaktionale MIP-Startupintervention samt tatsächlichen Originalmarkern
bleibt unverändert. Ebenso bleibt `NIP.run_after_verified_controls` aktiv:
`a1_controls_diagnostic.sample:103–114` nutzt unabhängig `pins/_guard/_read`,
prüft Originalbytes und liest tatsächliche lokale Controls zweimal, ohne die
beiden optionalen Inventoryflags zu benötigen. Das ist nicht derselbe Read wie
der nun nicht angeforderte perFrame Mausprofilzusatz. Der unveränderte
`NativeContext.input_frame` liest weiterhin Health/Spawn/MayRespawn/buttons
doppelt und vergleicht die tatsächlich vorhandenen Basisreaderfelder.

Sechs gezielte Builder-/Verbrauchertests bestehen (.081s). Der echte RED führte
die unveränderten Konstruktor-Flagguards mit den tatsächlichen transformierten
Runnerargumenten aus und erhielt genau die native Fehlermeldung. Getestet sind
außerdem derselbe Snapshotguard vor jeglichem Read, gültige Basisframes mit
Nullanimator ohne Animatorread, deren tatsächlicher Fieldcontract für die
unveränderte NativeContext-Methode und die tatsächliche Controls-Guard-/
Doppelreadkette einschließlich eines fatalen geglätteten Controls-Gegenfalls.
Die Konstruktorprüfung endet ausdrücklich vor Filesystem-/proc-Zugriff; sie ist
kein vorgetäuschter vollständiger Runtime-Readerstart. Die vorhandenen 20
Policy-/Methodtests wurden mangels dortiger Änderung nicht erneut ausgeführt.

Frischer deaktivierter D-v4:

- `/srv/tse-a1-original-respawn-fixedtarget030-v4-disabled-20261115`
- Manifest `360afce14b4a1193c28ff8cd33d9fbe34b2da167c30affff52640a8040af99f6`
- Nested `2b5f4accdf0b25659a3be50ccefaa5640516192a644b32e35274331404b9dc7e`
- Controller `adc3695def54dbaf9c5b0420979ffc97427e93f29c2f2d7e756df887ca524d90`
- 1644803 Bytes; alle 280/77/14 Pinwerte und vier ganze Parentinversen geprüft.

Private0600-Quittung:
`/srv/tse-original-respawn-colt-evidence-20261115/disabled-v4-final-receipt.json`,
SHA256 `fda261c7047a6881ed078f769a30833ce24bca42a1410f177c14a4ebecdf4fc4`.
Die echten Logs heißen `v4-real-reader-contract-red.log`,
`v4-real-reader-contract-green.log`, `v4-final-builder-contract-green.log`.
Alle Pin-/Quellenreads erfolgten nach explizitem Resolve mit NOATIME/NOFOLLOW.

Claim nur neuer Builder/Test sowie eigener Plan/Bericht; Writer bleibt
`/srv/tse-build030-skulls-closed-audit-20261115`. Keine Runtime, keine Pointer-
oder Readinesslockerung, keine Änderung alter Frozenartefakte. Root allein prüft,
integriert und entscheidet einen begründeten neuen Kontrollfall.
