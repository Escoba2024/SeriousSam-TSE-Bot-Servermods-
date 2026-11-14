# Eigene Win32-Instruktionsprobe: getrennte Methodenergebnisse

Diese Prüfung betrifft ausschließlich einen eigenen IA32-Prüfling unter Wine. Sie gibt weder Retail-Kausalität noch A1/A3 oder den Gesamtauftrag frei.

Der ursprüngliche Prüfling scheiterte vor dem R-Kommando. Eine getrennte native Diagnose belegte `PeekNamedPipe` → `ERROR_NOT_SUPPORTED` (50). Der neue Prüfling ersetzt ausschließlich den eigenen Kommandoleser durch einen ReadFile-Thread mit unverändertem 15-s-Wait; bei Timeout/Waitfehler endet der eigene Prozess mit Code12. Seine beiden Midpoint-Codebereiche bleiben exakt 17/14Bytes bei RVA1000/1070. Zwei frühere Linkfehler und der erste Baseline-FAIL bleiben erhalten.

Neuer eigener PE: 3584Bytes, SHA256 `4305c136f460f6fec4ff8b6ccb9419394514e2cee808b5ab5865b12b59f5acf4`. CPP `551f1672d96996d23d3a05f7149f1b1216cdb9fb10cf64368170e878d96b0f09`. Deaktiviertes Autorenmanifest708d7714, separat geprüfter Rootfreeze `4c4fb264ddce7ed51cfaf3cea0b4a0185da26837c49cb0b00cb4c4f9a4c57edb`; je20Pins, nur Root-Runtimegate verändert. 18 gezielte Python- und7JS-Prüfungen bestanden; der geerbte Proxy hatte separat10 bestandene Fälle.

| Einzelmodus | Native EDI / Argumentergebnis | Cleanup | Urteil |
|---|---|---|---|
| Baseline125220 | 12345678 / 10203040 | Originalbytes, normales Exit0, Prozessende bestätigt; kein Hook | PASS_METHOD_ONLY |
| Funktionsprobe125238 | 12345678 / 10203040 | Beide exakten Hookkontexte, vollständige Originalbytes, Scriptunload und Sessiondetach; normales Exit0 und Workerreap nach Prozessende | PASS_METHOD_ONLY |
| Historische Objektform125305 | 7f51460f / 7e534b0b | Close-RPC überschreitet2s; Byte-/Unload-/Detachquittung unbekannt. Normales Q/Exit0 und anschließender eigener Workerreap belegt | **FAIL_METHOD_EVIDENCE** |

Ergebnishashes:

- Baseline: `c76101bc3ec95fa3bf7eea7483d51783181652cfadec3551d75ffb101f384b4e`.
- Funktionsprobe: `42b2f249ac55b968bf7ae36c87c3723454d1755ab7600d4ee869fb6f40d299b0`.
- Objektform: `050b8472223ef93ddaa83f61ba268f573bee7dbeb0a9b0379f1246c15aa54148`.

Die Objektform verfälscht die tatsächlichen nativen Werte. Ihr Cleanupfehler verhindert ausdrücklich einen vollständigen negativen Kontroll-PASS. Er wird weder gelöscht noch durch eine längere Frist kaschiert. Der Parent schloss den eigenen Prüfling trotz hängendem Worker regulär; erst danach wurde ausschließlich der eigene Worker beendet. Bei den Instrumentierungsfällen bedeutet Workerreap kein behauptetes reguläres Workerexit.

**Ruling:** Baseline und korrigierte Funktionsform bestehen ihre vollständigen eigenen Kriterien. Zusammen mit dem statisch belegten Listenervertrag rechtfertigt das genau einen neuen passiven Retail-Diagnoselauf mit korrigierter Form; die fehlgeschlagene Objektkontrolle muss dafür nicht unsicher wiederholt werden. Die Retail-Kausalität bleibt bis zu diesem neuen Lauf offen. Kosten eines falschen Schlusses: auch die korrigierte Form könnte den Retailprozess beeinflussen; deshalb gelten unverändert Originalbytevergleich, bounded Worker, normale Rollenschließung, unabhängiger Restore und keine Live-Instrumentierung.

Alle drei eigenen Prüflinge sind beendet und Worker aufgeräumt. Nach unabhängiger PID-/Start-/Prefix-/Mappingprüfung wurde ausschließlich der reproduzierbare eigene Wineprefix entfernt; Code, Builds, Quellen, Registrykopien und Ergebnisquittungen bleiben erhalten. Das gewann rund1,3GiB zurück; danach9.961.406.464Bytes frei. Keine TSE-Installation wurde bei diesen Methodenläufen verändert.

A4-V3 wurde separat integriert. Root bestand den dokumentierten85-Fälle-Paketbefehl ohne Skips. Ein vorheriger zusätzlicher Vorfahren-Pakettest war mit der neuen statt der alten Paketvariablen aufgerufen worden und scheiterte erwartbar am Parentmanifest; dieser Aufruffehler ist kein bestandener Test und wird nicht dem Paket zugerechnet. Neuer Runtime-Nachweis bleibt offen.
