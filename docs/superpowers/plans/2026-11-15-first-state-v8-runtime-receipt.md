# FirstState: expliziter V8-Request und kalte Runtimequittung

Owner/Claim: a4_diagnosis, eigener WT `tse-build026-skulls-closed-audit-20261115`.
Nur neue Transform-/Test-/Plan-/Berichtdateien. Keine alten JS-/Runtimepakete ändern;
keine Paketgenerierung, Frida, Native, Builds oder Liveänderungen.

Root-Ruling: Option 2 ist autorisiert. Ein zusätzlicher kalter RPC im selben
Observer ändert den gesamten JS-Hash. G, Originalbodies, alle bestehenden Guards,
18 Hooks, alte RPC-Bodies und Hotpath bleiben über ganze Inversen bytegleich.
Die bisherige Retail-Runtime bei `runtime=None` und die CPU-Ursache sind UNKNOWN.

Parent: `/srv/tse-a1-first-state-getter-receipt-disabled-20261115/method-api`.
Native Python SHA d2801018afb64702826d9329f082ee314e718ab149f6211983170e4b04a12cd7;
Body abeab90d6a656c53e4acb349313686ead6a81f1b95a463e1dcd2de1262deb4d8;
compiled f5cc6498598fbd9de77dfc229ad04a4c7b0275be2b0c6541c9a5857b9c144c78.

1. Echte Behavior-RED am extrahierten unveränderten `NativePorts.load`:
   fehlendes literal V8, fehlender kalter RPC/Receipt. Tatsächliche compiled VM
   darf fehlenden RPC zeigen; kein Importfehler als RED.
2. Exakter SHA-gebundener Transform: einmal `runtime='v8'`, nach load einmal
   Runtimeidentity-RPC, bestehendes privates `atomic_json` vor Validierung,
   exakte vier Schlüssel/Werte und Typen. Fehler propagieren vor arm; kein Retry.
   JS fügt ausschließlich den kalten Metadaten-RPC hinzu. Kein Guard/Gatewechsel.
3. GREEN: tatsächliches AST-extrahiertes load samt atomic_json, Fehler bei
   Create/Load/RPC/Rawwrite, falsche Identitäten/Typen; tatsächliches compiled
   JS in bestehender VM, alte strikte Guards/TTL/I1/I2 und falsche Gates.
4. Ganze Python-/Body-/compiled-Inversen, G-Prefix gleich, fremde Mutation
   abweisen; private Quittung und bereinigter Report. Root reviewed/integrated
   später. Frisches Control/Trace und PID-CPU-Messung sind keine Agentenaufgabe.

Grenzen unverändert: alle TTL/Queue/Deadline/Schema-/Observerlimits. Kalte
Quittung beweist nur die gemeldete Runtime dieses Scripts; kein ABI-/A1-/CPUfix.

Status: COMPLETE_SOURCE_ONLY/HANDOFF. Actual RED:15 Tests,20 Verhaltenfailures,
2 Transform-Inversen zunächst skipped; keine Importerrors. GREEN:15/15 in0.759s
inkl.Null-/Typ-/Raw-/Failurefälle und neun vorhandene Guard-VM-Fälle. Ganze
Inversen/G-Prefix geprüft. Keine Pakete/Native; neue Rootableitung/Review offen.
Alle eigenen Jobs nach Receipt/Commit beendet; Claim frei für Rootintegration.
