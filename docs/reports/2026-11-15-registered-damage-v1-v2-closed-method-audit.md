# RegisteredDamageV1-v2: geschlossene Kontroll-/Methodenprobe

Die neue natürliche AI030/Originalopfer-Bedingung besteht ihre deklarierte inputfreie
Kontrolle und den begrenzten Callback-Methodenlauf. Sie enthält **keinen** Init-, Colt-
oder Schadensfall und qualifiziert weder A1 noch Erstzustand, normalen oder tödlichen
Schaden. Der frühere FULL18-Queuefehler bleibt unverändert; unterschiedliche Verläufe
erlauben keinen kausalen Vergleich seines Bursts mit dieser Probe.

## Eingaben, Custody und Grenzen

Nur die beiden neuen Fälle `a1-registered-damage-v1-v2-root-control-20261115-150725`
und `a1-registered-damage-v1-v2-root-trace-20261115-150838` wurden ausgewertet.
Result-SHA256:

| Arm | SHA256 |
|---|---|
| Control | `f215d5169aa9d211c94b47492eb6d5d5711d62eef25eddf8b75f5fd09ff3aaae` |
| Trace | `05c17acbd4854cd00631d54d4d47c1cf9d5f9cd7762ff22632862fc81a53cc1d` |

Der tatsächliche Controller entspricht F-v2 Manifest
`1e9a4c115669ca87c24761fb2ce71f46d0d3953447c0576c2f097887428c92d8`.
Die sieben ganzen neuen Scope-Inversen wurden gegen ihren FULL18-Quellparent
erneut bytegenau geprüft; Schema, Validator und Body stimmen mit D-v3 überein.
Der gepinnte Root-Anwendungsreview bleibt auf Rootdelta beschränkt. Die eigene
Template-/Policyautorschaft wird nicht als unabhängiger Review ausgegeben.

Vorab Statinventur; danach jede Raw-/Wiredatei genau einmal über aufgelösten Pfad
mit NOATIME/NOFOLLOW, stabiler Statprüfung und SHA256. Keine alten Rawreplays,
Assets oder Runtimezugriffe. Ergänzungen entstanden aus demselben RAMcache.
Gesamte physische Readbytes einschließlich Quellen: 9.226.437; Hardlimit32MiB,
Einzeldatei8MiB, privater Output unter5MiB, vorab8GiB+64MiB+Outputreserve geprüft.

Der reine Reader prüft alle58 vollständigen Wireantworten,208 Rawcaptures1..F,
Original-Offsets/Hashes vor Parse, sämtliche Packet-/Tracevalidatoren und
S=207/F=208. Kein Reply-, Guard-, Drop-, TLS- oder Scopefehler. Alle IPCs enden
innerhalb ihrer eigenen archivierten Deadline; längster Batch35,134ms,
längster Drain39,044ms, größter Drainstartabstand59,268ms. Connect817,663ms,
Arm61,343ms, Stopbarrier55,867ms. Diese Hostintervalle werden nicht mit JS-Wall-
oder nativen Gameclocks gleichgesetzt.

## Vollständige beobachtete Nenner

| Größe | Positiver Schnitt S | Final F |
|---|---:|---:|
| Native Edges | 2.897 | 2.898 |
| Vollständige Rawzeilen | 2.069 | 2.070 |
| Retained Enter / Leave | 1.035 / 1.034 | 1.035 / 1.035 |
| Echt abgeschlossene ausgeschlossene Weltcasts | 414 | 414 |
| Pending / incomplete_closed | 0 / 0 | 0 / 0 |

Die letzte GameTick-Leave-Zeile ist ein realer nach S zugelassener Cleanupabschluss.
Sie zählt nicht rückwirkend zum positiven Messschnitt:206 vollständige GameTickpaare
bis S,207 bis F. Native Sequenzen behalten die echten Ausschlusslücken; die eigene
Rowsequenz bleibt lückenlos. 2.898=2.070+2×414; 1.449native Calls=1.035retained+414excluded.

Alle18 Kindnenner sind erhalten. Tatsächlich:

| Kind | Enter/Leave F | Volle Zeilen | Excluded |
|---|---:|---:|---:|
| ProcessGameTick | 207/207 | 414 | 0 |
| ApplyAction | 414/414 | 828 | 0 |
| PostMoving | 414/414 | 828 | 0 |
| CastRay | 414/414 | 0 | 414 |
| Alle übrigen14 Kinds einschließlich ContinueCast, Init, Verbindungs-/Tod-, Colt-/Bullet- und Damagepfaden | 0/0 | 0 | 0 |

Die ausgeschlossenen Weltcasts tragen abgeschlossene Guard-/Ancestryzähler,
aber keine archivierten vollständigen Ziel-/Ownerpayloads. Daraus folgt kein
Bullet- oder Schadensbeweis. Alle retained Actorcallbacks verteilen sich exakt
auf207 ApplyAction- und207 PostMoving-Paare je Original und Bot. Beide haben in
diesen Zeilen ausschließlich Buttons0, HP100, Generation0, keinen Initanker.
Native GameTickbereich9,050016403198242–19,349990844726562; keine Clockfusion.
Beide Leben sind bezüglich Init vor Arm linkszensiert. Keine normalen/fatalen
Damageintervalle, keine Erstvalidtick- oder MayRespawnqualifikation.

Die natürliche Botrolle wurde aus tatsächlicher frischer Source-Logepoch,
PID-/Modul-/Stagingbindung, local0/GMS und exklusiver0→1→2-Admission reproduziert;
keine Registry-Selbstetikettierung und keine BotGameMP-RVAübertragung. Control
hat keinen eigenständigen archivierten Bot-Modulmapbeweis; diese Grenze bleibt sichtbar.

Finalzähler: drop/fault/errors_lost/rejected_entries/aborted_leaves/nonmain=0,
Gettercalls1, max_in_flight3. Queue64/native16384/order8192/damage1024/TTL15s/
TLS2s256Calls sind unverändert. Tatsächlicher kalter Runtime-Reply belegt QJS,
servergebundene PID, ia32 und pointer_size4, nicht nur requested_runtime.

38 Originalregionen stimmen in tatsächlichen Before-/Afterbytes überein;
Unload/Detach und normale Rollenschlüsse bestätigt. Worker nach Rollenende
absichtlich mit-15 gereaped, sticky_failureFalse, kein Ausnahme-Exitbeweis.
Root bestätigt je664Dateien/9Absenzen/3Logs/beideNamespaces/Units/Displays/4Locks.

Control enthält einen erhaltenen `state changed during read`-Discard bei zwei
Readattempts; Trace einen erfolgreichen Attempt ohne Readfehler. Kein Initial-
Null-Pending in diesen Proben und kein Nachweis dieses Zweigs.

CPUcompanion50/52Samples: PID/start-/Cgroupbindungen ohne Bindingfehler;
gültige und UNKNOWN-Intervalle bleiben pro Domäne getrennt. Nicht gestartete
botB-Domäne bleibt UNKNOWN, kein Nullverbrauchsbeweis. Keine Summe aus Prozess-
und Cgroupzeiten. Outer52/54Samples, CPUmax57,3604/62,6943%, maxgap1,00178/1,00231s;
innere Startupgaps26,3256/25,8196s. Beide behalten budget_pass_claimFalse;
keine allgemeine Ressourcen- oder Performancemessabnahme.

## Genau eine nächste Messbedingung, noch keine Umsetzung

Ein **neuer normaler Original-Respawn mit nach Arm beobachtetem Init** ist der
kleinste neue Trigger. Das gebundene Originalopfer muss vor Arm wirklich tot
und MayRespawn2 sein; dies erfordert tatsächliche Retailbelege, nicht aus HP
erfundene Bereitschaft. Nach Arm erst bei belegter Freigabe normale, fokussierte
Fire-Down/Up-Folge und Neutralitätsbeleg. Keine HP-/Positions-/Winkelwrites,
keine Input→Treffer-/Respawnannahme, keine Aimkalibrierung als Voraussetzung
dieses Respawninputs. EEnd/DeathHandler/Init/erster gültiger Tick und danach
normale/fatale registrierte Ownerketten müssen tatsächlich vorliegen oder bleiben
INCOMPLETE. Native10s/TTL15/Queue64/native16384 und alle Identitäts-/Release-/
Zeitgrenzen bleiben; keine Wiederholschleife oder Verlängerung bei fehlendem Beispiel.

Konkrete Quellen: SDK `Sources/EntitiesMP/Player.es:4391` verlangt
MayRespawn2+ReleasedFire+nichtPredictor;4437–4438 setzt nach neutralem Fire von1
auf2. Das ist Quellenrouting, kein neuer Retail-ABIbeweis. Build030
`overlay/BotDriver.cpp:1178–1183` trennt festen Testtarget vom automatischen
HumanAI-Modus;1621 fordert im festen Targetmodus Colt mit2L<<14 an.
1534–1542 zeigt den vorhandenen normalen Respawnpuls im automatischen Botpfad.
Der gepinnte030Driverhash ist
`7af47d87aaaf4c51ebaca6f65d628cfec3c2544419be07e39b65e52b370eb386`.

Eine echte Colt-Einschränkung ist damit als bestehender **anderer** Bot-Testmodus
vorhanden; sie gehört nicht still in die aktuelle automatische HumanAI-Konfiguration.
Ein neuer Respawn-/Normalinput-Harness muss Fokus, tatsächliches MayRespawn,
Down/Up und Lifewechsel aufnehmen. Der jetzige inputfreie MethodWindowvertrag
stellt dafür keine Eingabe bereit. `colt_preparation.py:119–140` verlangt für
seine separate Vorbereitung lebende unterstützte, stationäre Coltrollen; diesen
Pfad nicht zu einem toten Opfer umdeuten. Erst ein expliziter neuer Conditionsplan
darf nötige Harnessänderungen bestimmen. Ob in10s echte normale und tödliche
Coltkette eintritt, ist offen. Botopfer bleibt danach ein eigener Originalschützen-
Fall mit echten ACKs; kein Transfer aus dem jetzigen Originalopferlauf.

## Reproduktion und ehrliche Readerfehler

`python3 -B tools/audit_registered_damage_v1_v2_closed.py --output <NEUER_PRIVATER_PFAD>`
liest nur diese geschlossenen Fälle. PureTestdatei enthält vier gezielte Fälle;
erste drei RED6Fehler, danach GREEN. Beim ersten Audit trat nach abgeschlossenem
Raw-/Validatorpass ein tatsächlicher `NameError: json` im isolierten Namespace
des wiederverwendeten CPUreaders auf. Ein gezielter Dependency-RED belegte ihn,
der Namespacefix wurde mit insgesamt4Tests GREEN bestätigt. Kein Nativefehler.
Raw wurde nicht wieder gelesen; weiter im selben RAMcache abgeleitet. Eine
interaktive Diagnoseausgabe hatte zusätzlich einen SyntaxError ohne Dateieffekt.
Frühe Receipts/Readercheckpoint bleiben erhalten, finale Receipt pinnt den
aktuellen Reader frisch und enthält die sieben erneut ausgeführten Sourceinversen.

Private Belege: `/srv/tse-registered-damage-v1-v2-closed-audit-evidence-20261115`.
Final `final-verified-receipt.json` SHA256
`1495576237217e763de6d594c111837cc05f35173e617dedcb3f08767ba3c7b0`;
RAMsupplement `4e6f78fe0063ce8e2bcebc887bd14197e9c091eeeee0b7c5fda7ddb2dcf33fe2`.
Rohidentitäten und vollständige Rawdaten bleiben privat.
