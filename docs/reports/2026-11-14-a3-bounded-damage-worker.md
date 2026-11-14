# A3: deaktivierter begrenzter Originaldamage-Worker

Arbeitsstand: neue Quelladaption, noch kein nativer Lauf und keine A3-Freigabe.
Das bisherige Hard2-Paket mit Manifest7730510e… darf wegen des bestätigten
unbegrenzten Parent-Fridapfads und Stop-ohne-Idle-Befunds nicht gestartet werden.
Der Hauptagent behält allein die Runtime-/Integrationszuständigkeit.

## Genaue Änderungen

`original_damage_worker.py` übernimmt den zuvor geprüften A1-Fresh-exec-/Socket-
Lebenszyklus für genau vier eigene Rollen. Einzig der Socket-FD wird vererbt,
keine Arena-Lock- oder Reader-FDs. Der Rollencontroller importiert Frida nicht
mehr und führt weder Attach/Load/RPC noch Unload/Sessiondetach aus. Arm ist auf
3s, Drain auf100ms, Close auf2s begrenzt. Ein Fehler bleibt sticky; normaler
Rollenclose und FileTransaction-Restore laufen unabhängig davon weiter.

Nur das eigene Popen-Child darf nach belegtem normalem Ende sämtlicher
gestarteter Rollen und eigener Quieszenz beendet werden. PID/Start wird vor
einem Signal erneut geprüft. Ein Startfehler vor erster möglicher Armnachricht
darf ausschließlich das nachweislich unarmed eigene Child beseitigen. Worker-
PID/Start und Config-/Quellhash werden sofort privat im Ergebnis festgehalten,
damit auch ein späterer Cleanupblocker einen ausführbaren Handoff besitzt.

`original_damage_collector.py` besitzt sämtliche möglicherweise blockierenden
Fridaoperationen und einen eigenen unveränderten Original-InventoryReader für
Byteprüfungen. Pinned Python-/Fridaquellen, Originalmodule, PID/Start, CWD,
Namespaces, vollständige Bodyfingerprints und elterlicher exklusiver Runtime-
Lock bleiben erforderlich. Vollständige Getter-/ReceiveDamage-Bytevergleiche
liefern explizite private Quittungen mit Phase, Modul/RVA, Länge, erwartetem und
tatsächlichem SHA256. Keine Fingerprintbytes werden öffentlich verteilt.

## Admission und Cleanup

Der JS-Stop schließt zuerst neue Damage-Aufnahmen. Bereits zugelassene
ReceiveDamage-OnLeave-Paare dürfen ausschließlich unter dem ursprünglichen
TTL und denselben Entity-/World-/Bodygrenzen fertig beobachtet werden.
Fehlerzustände oder abgelaufene Fristen geben keine weitere Speicherlesung frei.
Vor Hookdetach müssen Admission geschlossen und vier echte Zähler null sein:
native Damage-InFlight, aktive Records, laufende Listenercallbacks und
Gettercallbacks. Erst dann Hookdetach, vollständiger Originalbytevergleich,
Scriptunload und Sessiondetach. Ein fehlender Idle-/Bytebeleg verweigert Unload.
Die interne Idlewartefrist beträgt1s innerhalb der unabhängigen2s-Parentfrist;
ein dort blockierender RPC bleibt ausschließlich im Worker.

Die bereits getestete Getter-TLS-Bindung einschließlich ihrer historischen
Selbstabnahme bleibt im Body bytegleich. Nur eine Zählerhülle beobachtet die
Callbacks. Sie ersetzt keinen neuen nativen Frida-/Trampolin-Sicherheitsnachweis.
Ein späterer Retail-Lauf muss tatsächliche Idle-/Byte-/Detachquittungen liefern.
Message- oder Journalfehler bleiben FAIL, dürfen aber ein anschließend sicher
belegtes Cleanup nicht überspringen.

## Geerbter Partialstart-Befund

Der unabhängige Review fand zusätzlich: nach erfolgreichem Service-Start,
aber fehlgeschlagener nativer Identitywait, konnte `record.identity=None` einen
normalen Close verhindern. Der Hauptagent autorisierte den engen bereits bei
V2/Map verwendeten Pfad: vorhandene Identitäten unverändert prüfen; bei fehlender
Identität nur eigene strikte Ready-/CWD-/Unitbindung und frisch eigene Identity
übernehmen. Alternativ muss die eigene Unit belegbar PID0/empty sein und der
eigene Root zusätzlich quiescent; dann gibt es ausdrücklich eine
`started=False`-/Closed-Quittung. Kein Force, keine neue Wartefrist oder Retry.

## Prüfstatus und Grenzen

Nach bestätigtem Ende und Restore des exklusiven Root-Mapfensters bestanden
58 gezielte Fälle in 0,448s: zehn Proxy-/Childfälle, zehn Collector-/Bytequittungs-
und Closefälle, sechs tatsächliche JS-Logikfälle in Node-VM, neun Paket-/Partialstart-
fälle und die bisherigen 23 A3-Adapter-/Analyzer-/Hard2-Fälle. Ein echter frischer
Python-Testchild simulierte einen blockierenden Attach; er wurde anschließend
nachweislich beendet. Keine Frida- oder Spielruntime wurde gestartet.

Worker und Collector hatten vor Implementierung echtes fehlende-Implementierung-
ROT. Die JS-Fälle waren vor Implementierung geschrieben, wurden wegen exklusiver
Root-Nativeläufe erst danach ausgeführt. Ein früher Fake-Close besaß kein `idle`;
nur diese Fixture wurde dem unveränderten strikten Protokoll angepasst. Der erste
abschließende Testaufruf verwendete falschen CWD/Importpfad und drei falsche
Modulnamen (17 gemeldete Fälle, sieben Importfehler, ein Skip). Der korrekte
explizite Aufruf bestand 58 Fälle ohne Skip. Diese Ausführungsfehler werden
nicht als Produktfehler oder erfolgreiche Tests umetikettiert.

79 Runtimeabhängigkeiten, 109 finale Paketquellen, die 98 Parentquellen,
47 Build- und 28 Overlayquellen sowie DLL/Buildmanifest wurden frisch gehasht.
Neun Original-Damage-/Host-/Restoredateien blieben bytegleich; private Guard-
Header und historischer Getterbinderbody ebenfalls. Die Hook-Lebenszyklusänderung
ist ausdrücklich eine neue noch unqualifizierte Instrumentierung.

Finales privates Paket:
`/srv/tse-a3-direct020-hard-worker-final-20261114`

Manifest-SHA256:
`3e9a93ac6f06503f84f8f914b5a6b45aec03a35dfce7ed6552b9905676c39a5e`

Kandidat bleibt Build020, DLL-SHA256:
`094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0`.
Alle drei Codegates, `runtime_reviewed`, `qualified` und `runtime_allowed`
bleiben false. Root darf nur nach unabhängigem Review einen getrennten
konsistent gepinnten Namespace einfrieren. Vor jedem Einzelstart sind originale
Host-/Lab-/Lock-/ABI-/Hard2- und Ressourcenprüfungen frisch erforderlich.
`RUNPLAN-disabled.json` und `HANDOFF.json` enthalten die konkreten nächsten Schritte.

Gezielte Offline-Reproduktion aus `tools/` (kein Runtime-Start):

```sh
TSE_A3_BOUNDED_PACKAGE=/srv/tse-a3-direct020-hard-worker-final-20261114 \
TSE_A3_DIRECT_PACKAGE=/srv/tse-a3-direct020-hard-worker-final-20261114 \
TSE_ORIGINAL_DAMAGE_JS=/srv/tse-a3-direct020-hard-controller-20261114/frozen-v2/damage_readonly.js \
python3 -m unittest test_original_damage_worker test_original_damage_collector test_a3_damage_quiescence test_a3_bounded_damage_package test_a3_direct_tiers test_a3_direct_compare_closed test_a3_direct_closed_fixture test_a3_direct_adapter test_a3_direct_behavior -v
```

Der öffentliche Offlinebuilder erzeugt nur einen neuen deaktivierten Fork:

```sh
python3 tools/build_a3_bounded_damage_package.py \
  --parent /srv/tse-a3-direct020-hard-controller-20261114 \
  --destination /ABSOLUTER/NEUER/PFAD
```

Er erzeugt bewusst keine positiven Testquittungen. Der konkrete finale Fork
enthält zusätzlich die nach den tatsächlich ausgeführten Prüfungen erfasste
Offlinequittung und den entsprechend aktualisierten Handoff. Sourcecode und
ausführbare Konfiguration sind reproduzierbar; Zeitstempel und Prüfquittung
behaupten keinen deterministischen Neubau. Bereinigte minimale
[Controllerdiff](a3-bounded-damage-worker-20261114/worker-controller.diff),
[Hookdiff](a3-bounded-damage-worker-20261114/worker-hook.diff),
[Analyzerdiff](a3-bounded-damage-worker-20261114/worker-analyzer.diff) und
[Offlinequittung](a3-bounded-damage-worker-20261114/worker-offline-receipt.json)
sind versioniert. Die Diffs enthalten keine Retail-Fingerprintbytes.

Keine zusätzliche Samplerrate, kein Gameplayinput und keine Enginefunktion.
120s pro einzeln gewähltem Tierfenster, Hard2,125000ms Hook-TTL,2000ms Getter-
Bindung und Fensterreserve, Queue64,1024 Damagecalls,256 Gettercalls, unveränderte
Damagepartition, Anfangsreferenz, Hostbudget und physische Kriterien.
Die paarweisen Starts 1↔2 und 2↔3 werden jeweils vertauscht; identische Build020-
Konfigurationen unterscheiden sich ausschließlich im ArenaTier. Der Analyzer
bindet außerdem Worker-/Collector-/Hook-/Host-/Guard-SHA und Fridaversion an die
gemeinsamen Bedingungen. Unentschiedene/widersprüchliche Werte bleiben offen;
keine neue Killmarge und keine A3-Akzeptanz aus synthetischen Daten.

Finaler unabhängiger Review sowie tatsächliche Original-Idle-/Body-/Detach-,
Schadens-,Kill-,Hard2- und Tierunterschiedsbelege bleiben offen. Die alten
Legacy-Siege belegen diese direkten Tiervergleiche weiterhin nicht.
