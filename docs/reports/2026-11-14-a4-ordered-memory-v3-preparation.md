# A4 V3: geordnete Speicherbeobachtungen, deaktivierte Vorbereitung

Status: **OFFLINE_VORBEREITET**; unabhängiger Review, Root-Freeze und neue prospektive Nativeprüfung offen. Kein DLL-Rebuild, kein Native-/Frida-/Compilerstart durch den Autor. Alte600s-FAILs bleiben FAIL. Der [Rootplan](../superpowers/plans/2026-11-14-a4-ordered-memory-observations.md) korrigiert den durch echte Within-group-Konflikte widerlegten Datentyp; er macht den Reader nicht atomar.

## Verhalten und erhaltene Grenzen

`a4_ordered_memory_v3.py` bindet jede aktive Speicherbeobachtung an Server-PID/Start, Epoch, feste Gruppe, globale positive Readserial und monotone Start-/Endzeit. Sämtliche Rohhüllen einschließlich des ausgeschlossenen Overlaps werden vor jedem Evidenzaufruf geprüft. Typverwechslungen wie `True` statt Seriennummer1 oder `False` statt Phase0 scheitern ebenfalls.

Alle kanonischen Rows bleiben in ihrer tatsächlichen Readreihenfolge erhalten. Der separate `audit_a4_ordered_memory_v3.py` führt keine Tickmap, Ticksortierung, Feldwhitelist, First-/Best-row-Auswahl oder Same-tick-Verwerfung aus. Innerhalb eines gebundenen Lebens werden mehrere Reads desselben Sessionticks als verschiedene Beobachtungen gewertet. Gleiche oder rückläufige Beobachtungs-IDs, Seriennummern, Zeitintervalle und widersprüchliche Herkunft scheitern vor Evidenz. Die beiden alten V2-Dateien und der bisherige Canonical-Wrapper bleiben bytegleich.

Source-Zeitzeugen, vollständige Decimal-Rundungsintervalle, Generation-/Lifebindung, Counterwachstum und Resetregeln bleiben unverändert. Eine Inventarzunahme zählt weiterhin nur zwischen aufeinanderfolgenden Beobachtungen desselben gesunden Lebens mit strikt `oldTick < newTick`. Same-tick-Übergänge liefern keinen Pickupbeleg und werden nicht zur Wahl eines günstigeren Vorgängers verwendet. Overlap liefert weder FIRE- noch Pickupbelege.

Neue Belegfelder heißen ausdrücklich `memory_flag_observations` und `native_fire_flag_observations_with_same_life_source_growth`; Referenzen nennen `read_serial`. Sie zählen Flagbeobachtungen, keine Schüsse oder Waffenfunktionsaufrufe. `atomic_snapshot=false` und `weapon_function_call_proven=false` stehen im Vertrag und Ergebnis. A1-Erstzustandsschaden und A3-Schadens-/Killvergleiche bleiben eigenständig offen.

## Producer und begrenztes Versuchsjournal

Der neue Controller leitet sich ausschließlich vom deaktivierten Canonical-Elternpaket mit Manifest `293c7d49e590e28164caf2db52660f144f14ebd32eca0c60fece40a5adc26de9` ab. Er archiviert festen Gruppenvertrag und Lesetypvertrag vor dem ersten Read und vor Freigabe der Gameplaybarriere.

Jeder ohnehin vorhandene Inventorycall erhält vorher eine globale Seriennummer und eine Begin-Metadatenzeile. Nach Erfolg oder Fehler folgt eine Endzeile mit Endzeit und Status; fehlgeschlagene Reads bleiben ohne Gameplaybeleg. Die Beginzeile wird vor dem Aufruf geschrieben; einmaliges Flush nach der Endzeile begrenzt zusätzliche Flusharbeit. Es werden keine Inventarrows doppelt protokolliert. Das neue Journal ist auf **100.000 Versuche, 200.000 Metadatenzeilen und64MiB** begrenzt. Fehlende/mehrfache Enden, Serienlücken und erfolgreiche aktive Versuche ohne genau eine zugehörige Samplehülle scheitern. Pausierte Smokes tragen denselben Herkunftsvertrag, sind aber keine aktiven Gameplaybelege.

Serien-, Journal- und CPU-Uhrarbeit sind neue Instrumentierung mit Kosten. Kein behaupteter Null-Overhead: Die bestehenden Host-, Gap- und Ressourcengates müssen die neue prospektive Messung prüfen. Die AST-Prüfung bestätigt identische Inventory-/Session-/Query-/Control-/Sleepaufrufe und identische Funktionen für Start, Count, normale Schließung und Quieszenz. Hard2,600s, Gruppen, Rollen, Rohaktivität, vorhandene Logs, Bounds und Restorepfad bleiben erhalten. Nur der neue Metadatenstream kommt zur bestehenden begrenzten Ressourcen-Schließschleife hinzu. Der kopierte Hard-Adaptertest benennt die erweiterte Bindesignatur; alte Quelldateien werden nicht geändert.

## Gezielte RED/GREEN-Prüfung

Die neue V3-Suite war zunächst RED wegen fehlender Module. Der neue Produceradapter war ebenfalls zunächst RED wegen fehlendem Builder. Anschließend wurden zusätzliche Bool-Identitätsverwechslungen erst durch eigene RED-Fälle reproduziert und dann abgewiesen. Ein Same-tick-Pickupfixture änderte zunächst nur einen Gruppentick und erzeugte dadurch selbst eine rückläufige globale Tickfolge; das Fixture wurde auf eine konsistente gleiche Zeit für alle Gruppen korrigiert, der harte Zeitguard blieb erhalten.

Abschließend **85 gezielte Fälle PASS, keine Skips,0,277s**:

```sh
TSE_A4_ORDERED_PACKAGE=/srv/tse-a4-build020-hard-ordered-memory-clean-final-20261114 \
TSE_HARD_MAP_PACKAGE=/srv/tse-a4-build020-hard-ordered-memory-clean-final-20261114 \
python3 -m unittest test_a4_ordered_memory_v3 test_prepare_a4_ordered_memory_v3 \
 test_a4_fire_observer_v2 test_audit_a4_native_fire_observer_v2 \
 test_a4_canonical_native_groups test_a4_hard_maps test_stability_hard_rules test_preflight_startup -q
```

Ausführen im deaktivierten Paketverzeichnis. Darunter sind13 unveränderte Source-/Life-/Decimal-/Counter-/Pickupregressionen gegen den neuen Auditor, die übrigen alten V2-/Canonicalfälle, neue ID-/Zeit-/Fehlerjournalfälle, sämtliche frischen Paketpins sowie Hard-/Startup-/Normalclose- und AST-Vergleiche. Frühere reine Autorenläufe vor Paketerzeugung hatten den ausdrücklich bedingten Paketcheck noch übersprungen; der angegebene Abschlusslauf hat keine Skips.

## Geschlossenes Archiv ausschließlich als Entwurfsmodell

`check_a4_ordered_archive_design.py` verarbeitet die geschlossenen120936-Daten ohne Änderung. Weil das alte Archiv keine echten Readserials oder individuellen Start-/Endzeiten enthält, versieht das Werkzeug geparste Kopien ausdrücklich mit **retrospektiven Ordnungsnummern und synthetischen Intervallen**. Diese fehlende historische Provenienz wird niemals als bestanden ausgegeben. Das Werkzeug heißt `OFFLINE_DESIGN_MODEL_NOT_NATIVE_QUALIFICATION`; andere alte Aktivitätsgates werden nicht neu abgenommen.

Die [bereinigte Modellprüfung](a4-ordered-memory-v3-20261114/closed-archive-design-model.json) erhält alle13.627 aktiven Rohsamples, davon9.079 kanonische und4.548 Overlap, dazu drei pausierte Smokes außerhalb aktiver Belege. Je eigenem Slot ergeben sich342–588 Flagbeobachtungen mit gebundenem Sourcewachstum und11–20 Inventargewinne. Sämtliche drei früher widersprüchlichen Same-tick-Rows bleiben erhalten. Das ist ein bestandener Datenmodellversuch, keine neue native Abnahme.

Fünf gelesene Archivdateihashes waren vorher/nachher identisch, insbesondere das alte Ergebnis `935f6d88c1741bd2a37d6b5c076a7b409db2abf604c394b38fb5ed8c1763cc29`. Private Modellquelle und Ausgabe: `/srv/tse-a4-canonical-conflict-scan-20261114/ordered-memory-design-check.json`; der zugrunde liegende private Konfliktscanner/Receipt bleiben dort erhalten. Keine Rohspieleridentitäten oder Retailbytes wurden veröffentlicht.

Die Modellartefakte nennen die tatsächlich ausgeführten Quellhashes aus Commit `58391473f99ccc11d98b3ef2137b258bc231ff74`. Danach wurde genau eine zusätzliche EOF-Leerzeile im neuen Auditor entfernt, nachdem der staged Diffcheck darauf hingewiesen hatte. Die AST ist identisch. Das alte Modellpaket bleibt zur genauen Hashreproduktion erhalten; das endgültige saubere Paket hat neue Pins und erneut85 bestandene Fälle. Der Modellversuch wird nicht als Prüfung einer historisch vorhandenen Serien-/Zeitprovenienz ausgegeben.

## Paket und Handoff

- Isolierter Worktree `/srv/tse-a4-ordered-memory-observations-20261114`, Basis `63f6bf74519748bd25fa26c78cdc6d1d0beecfb4`.
- Deaktiviertes Paket `/srv/tse-a4-build020-hard-ordered-memory-clean-final-20261114`.
- Manifest `a4568cbe60716887e195f7996ffeed774c1035cadcb11660b644c1fe64b4b2d9`;64 frische Runtimepins, Code-/Manifest-/Rootgates false.
- V2-Kern unverändert `201ca2d0f3098637ffb129162d84e126062df24790cfa865693781683732e5fc`, V2-Auditor unverändert `3ac187c8775b2bd1ed7021dc7b4037b0eeda6aec2a0292f9d87e47c9d8f4b466`.
- Reproduktion `python3 tools/prepare_a4_ordered_memory_v3.py --destination NEW_EMPTY_PATH`; bestehende Pakete werden nicht überschrieben.

Tests, Generator und Archivmodell sind beendet; keine eigene Aufgabe läuft weiter. Nächster Schritt: unabhängiger Source-/Paketreview, Root-Freeze mit konsistenten Pins, Veröffentlichung/Sicherung, exklusiver frischer Preflight und genau ein neues600s-Red-Fenster. Keine automatische Wiederholung und keine A-/B-Abschlussbehauptung.
