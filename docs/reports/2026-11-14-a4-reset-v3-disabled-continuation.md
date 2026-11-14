# A4-Reset-V3: deaktivierte Offlinevorbereitung

Stand: Nur portable Quellen-/Modellprüfungen und Paketbau. Kein TSE-, Wine-, Frida-, Display-, Build-, Netzwerk- oder Liveaufruf. Unabhängiger Review und jeder native Resetnachweis stehen aus. `qualified=false`, `functional_pass=false`; der positive native Terminal-Watchdogfall bleibt `NOT_EXERCISED`.

Der pausierte Worktree `/srv/tse-a4-epoch-reset-v3-20261114` auf8002109 blieb unverändert. Vier unversionierte Dateien wurden vorab mit Hash/Größe/mtime/Mode inventarisiert und abschließend erneut exakt verglichen. Nur seine drei erforderlichen Tooldateien wurden in den neuen Worktree `/srv/tse-a4-epoch-reset-continuation-20261114` aufeb4a8c1 übernommen; der alte Bericht blieb dort. Keine Änderungen an Root-Handoff, Navadapter oder A1.

## Tatsächliche Ableitung

- 018-Resetparent: `/srv/tse-milestone-a-continuation-evidence-20261112/a4-build018-extended-root-frozen`, Manifest `9064439561caac5deed96b1be4e546d8fa0c69ac6fbdf24a5c836b3538d0817c`.
- V3-Autorenparent: `/srv/tse-a4-build020-hard-ordered-memory-clean-final-20261114`, Manifest `a4568cbe60716887e195f7996ffeed774c1035cadcb11660b644c1fe64b4b2d9`. Der WIP-Verweis auf eine Root-Laufkopie wurde durch diesen beauftragten Autorenparent ersetzt.
- 020: Quellcommit `e5f7a65502fbea683014ef8fcc95ecdd2a927b6a`, DLL `094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0`, Buildmanifest `3099a0be953be1ff8047289de056b6cddf931cac9a4791f2520d3898357950c6`. 47 Quell- und 28 Overlaydateien frisch verifiziert. Die kanonische Kampfkonfiguration bleibt bytegleich, Profile7/DEMON gemäß vorhandener Migration; Diagnostics0 ist die ausdrücklich verlangte Laufbedingung.

`PhaseReads` umhüllt exakt die drei vorhandenen Inventory-Aufrufstellen. Jeder wirkliche Read erhält vorab seine konkrete physische Gruppe, eine fortlaufende Seriennummer innerhalb der aktuellen echten Resetepoche und sein vorhandenes begrenztes V3-Attemptjournal. Fehlgeschlagene Reads werden mit Fehlerende archiviert; nur erfolgreiche Gameplayreads dürfen Aktivitätsbelege werden. Die bisherigen frühen Acht-Bot-Rawreads bleiben erhalten, kein zusätzlicher Inventoryread oder Input und kein zusätzlicher Sleep wird eingeführt.

Der vorhandene Gruppenwrapper wurde ausschließlich auf die bereits vom unveränderten V2-Kern unterstützten Phasen0/1/2 verallgemeinert; der V3-Body ändert nur seinen Gruppenimport. V2-/V3-Auditoren einschließlich Same-Life-, Sourcegeneration-, voller Decimal-Rundungsbereich-, FIRE-/Ammo-/Owned- und strikt fortschreitender Pickup-Tick-Prüfung bleiben bytegleich. Alle Rawgruppen werden weiterhin vor der festen Auswahl geprüft; keine Overlap-Ausweichquelle und keine Outcomeauswahl.

Phase0 bindet die tatsächlich aus dem Dedicatedlog geprüfte Beginfolge1. Phase1/2 binden zusätzlich die tatsächliche bestätigte `PhaseInventory`-Quittung: Begin1/2 bzw1/2/3, Uhrreset nach≥120Spielsekunden, frische Latin1-Sourceoffsets, identische persistente Server-/BotA-/BotB-PID+Startzeit und alle acht frühen Entity-/Pointer-/Worldbindungen gegen die spätere Neunerregistry. Pointerreuse bleibt zulässig, bildet allein aber keinen Resetbeweis. Die Schlussprüfung verlangt drei solche Epochen mit fortschreitenden Sourcecuts und insgesamt24Botslotphasen.

Die ursprüngliche Rotation, beobachtete normale Enden, zwei tatsächliche Originalobserverneustarts,19s-Closedeadline,50s-Übergang,480s-Gesamtkappe und dritte Phase≥120Wall- **und** Spielsekunden bleiben erhalten. `observer_policy.py`, `phase_inventory.py`, `round_script_io.py`, Backend, Ressourcen- und Restorecode bleiben bytegleich. Die neue vollständige Hard2-Sessionprüfung verwendet dieselben bereits gelesenen156Bytes, mit ausschließlich phasenabhängigem Zeitlimit2/2/0; die vorhandene native Bytes/Hash-Prüfung bleibt dazu bestehen. Querytransportleere bleibt nur im vorhandenen Startup-/Wartezustand nicht bereit; gültige Queries müssen Hard sein. Kein externes Ein-Bot-Preflight wurde verändert.

## Prüfungen und ehrliche Grenzen

Fokussiertes RED beobachtet: fehlende Controller-/Readerbrücke; außerdem fehlende Zurückweisung falscher Registryphase, vertauschter physischer Gruppe und falscher tatsächlicher Beginfolge. Anschließend GREEN. Ein früher Aufruf aus dem Repositoryhauptverzeichnis erzeugte zwei reine `ModuleNotFoundError`-Testladefehler; der dokumentierte Befehl läuft im Paketverzeichnis.

Die drei historischen synthetischen Fixtures mit leeren Sessionfeldern bzw Diagnostics1 scheiterten zunächst erwartbar an der neuen vollständigen Hard2-/Diagnostics0-Bedingung. Der Builder ergänzt in **abgeleiteten Testkopien** die tatsächlichen Hardfelder, retargetet Diagnostics0 und normalisiert nur die erlaubten Quellunterschiede. Keine alten Dateien oder Grenzassertions wurden verändert. Der bestehende isolierte Terminal-Cap-Test stubbt ausdrücklich nur die separat getestete neue Sequenzprüfung; das ist ein portabler Clocktest, kein Resetbeleg.

117 gezielte Fälle, keine Skips, PASS in1,168s:13neue Epoch-/Builderfälle,47übernommene Reset-/Timing-/Early-Inventory-/Budget-/Restore-/Scriptfälle sowie57ausgewählte V2-/V3-/Gruppenfälle. Darin werden13Life-Regressionsmethoden sowohl direkt als auch durch die vorhandene V3-Testklasse wiederverwendet; dies sind keine zusätzlichen unabhängigen nativen Beobachtungen. Die24Slotphasen im Modell sind synthetisch und beweisen keine tatsächlich gefahrenen Resets.

Paket: `/srv/tse-a4-build020-hard-reset-v3-disabled-review-20261114`; Manifest `2a93b4f03c560e6f7364ca8cac06002d28b1157dbc7d0f6226d2dc6af381e9fb`.144Runtimepins und71Paketdateipins frisch rückgeprüft. Gate und Manifestfreigabe sind False. Frühere unveränderte Entwürfe `disabled-draft` und `disabled-fixturecheck` wurden nie nativ verwendet. Prüfbefehl und Pinquittung: [epoch-reset-v3-offline-preparation.json](milestone-a-20261114/epoch-reset-v3-offline-preparation.json).

## Nächster ausführbarer Schritt für Root

Unabhängiger Quellen-/Diffreview, insbesondere `reset-v3-runtime.diff`, `reset-v3-policy.diff`, generierte Epochwrapper, frühe8→späte9-Bindung und Schlusssequenz. Danach bei Bedarf frische Rootcopy erstellen: nur das eine `RUNTIME_REVIEWED`-Gate, eigene Service-/Evidenceprefixe und die entsprechenden Manifestpfade/-Hashes ändern; alle144Runtime- und71Dateipins frisch prüfen. Kein vorhandenes Autoren- oder Laufpaket ändern.

Erst Root darf nach exklusiver Lab-/Prozess-/Namespace-/Lockprüfung, unverändertem externem Preflight, Ende paralleler CPUarbeit und frischem75%/1,5GiB/8GiB-Preflight genau einen geplanten480s-Lauf starten (`python3 /NEUE_ROOTCOPY/run-mapreset.py`). Kein automatischer Retry.24Slotphasen, tatsächliche Begin-/End-/Clock-/Source-/Registryepochen, ursprüngliche Aktivitätsnenner, drei normal archivierte Originalobserver und unabhängiger Dateimetadaten-/Log-/Prozessrestore sind anschließend real zu prüfen. Ein solches Ergebnis ist hier noch nicht vorhanden; vollständige A4-/A1-/Stärke-/Dauerstabilitätsabnahme bleibt offen.
