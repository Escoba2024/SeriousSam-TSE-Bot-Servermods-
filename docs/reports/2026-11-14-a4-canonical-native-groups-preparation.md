# Feste native Beobachtungsgruppen: deaktivierter prospektiver Entwurf

Status: **OFFLINE_VORBEREITET**, unabhängiger Implementierungsreview und neues natives Fenster offen. Der geschlossene Hardlauf `a4-020-hard-redstation-20261114-112608` bleibt **FAIL**. Der neue Vertrag entstand nach diesem Lauf; die Archivprüfung ist keine nachträgliche Freigabe.

Der [Diagnosebericht](2026-11-14-hard-map-duplicate-observation-diagnosis.md) und die [acht bereinigten Konflikte](a4-canonical-groups-20261114/eight-conflicts.json) belegen unterschiedliche Gesamtrows zwischen zwei separaten Gruppenreads. Der bestehende Reader garantiert zwei gleiche Lesepässe pro Aufruf, keine Atomizität zwischen Aufrufen. Die Engine-Schreibphase ist nicht gemessen.

## Umsetzung des unabhängig geprüften Plans

`a4_canonical_native_groups.py` deklariert anhand der tatsächlichen physischen Slotzuordnung die drei bereits vorhandenen Readgruppen. `botA_actual` bleibt alleinige V2-Belegquelle für botA, `botB_actual` für botB. Der Controller archiviert den Vertrag vor dem ersten Inventoryread und vor Freigabe der Gameplaybarriere. Jedes pausierte und aktive Sample erhält tatsächlichen Gruppennamen, angeforderte Slotreihenfolge und Vertragsdigest.

Vor Auswahl prüft der Wrapper sämtliche aktiven Rohsamplehüllen: exakte Gruppen-/Slotfolge, Originalmodule, PID/Start, Phase/Epoch sowie gegen die vollständige physische Registry gebundene Entity-/Worldidentitäten. Die unveränderte V2-stamp-Regel prüft außerdem endliche Session-/positive Spawnclocks auch für ausgeschlossene Hüllen. Auch ausgeschlossene Overlapdaten können diese Prüfung scheitern lassen. Fehlende Gruppen scheitern; die feste Zuordnung lässt sich nicht nachträglich umstellen.

Eine einzige vorbestimmte Teilmenge geht für FIRE **und** tatsächliche Inventargewinne an den unveränderten V2-Kern. Innerhalb der zuständigen Gruppe bleiben widersprüchliche Gesamtrows bei gleichem Tick harte Fehler. Sourcewachstum, exakte Leben-/Epochbindung und bisherige Zeitrundung bleiben unverändert. Es gibt keinen EPS, Feldvergleich als Ersatz für Gesamtrows, Crossgroup-Fallback oder Auswahl anhand günstiger Waffen-/Feuerwerte.

Die vollständigen aktiven Rohsamples gehen weiterhin an die bisherigen Aktivitätsgates und Rohjournale. Reader-, Session-, Query-, Host-, Sleep- und Controlaufrufe sind im Adapter AST-identisch zum geprüften Startupfinal-Elterncontroller. Start, normale Rollenschließung, Teilstartschutz, Transaktion und abschließende Gates bleiben identisch. Nur zwei Assertions des kopierten alten Adaptertests benennen jetzt den neuen zuständigen Wrapper. Beide alten V2-Dateien sind bytegleich.

## Gezielte Offlineprüfung

RED: Die zehn neuen Gruppenfälle scheiterten zunächst am fehlenden Wrappermodul. Danach PASS für diese Fälle, darunter ungültige ausgeschlossene Hüllen vor Coreaufruf, fehlende/falsch etikettierte Gruppen, falsche Slots, unveränderter Within-group-Konflikt und ausdrücklich kein günstiger Crossgroup-FIRE-/Pickupersatz. Der elfte Fall für NaN-Session-/Spawnclocks im ausgeschlossenen Overlap war anschließend ebenfalls erst RED, dann GREEN. Ein neuer Adaptertest nannte anfangs die nicht existierende Elternfunktion `start_role`; dieser Fixturefehler wurde auf den tatsächlich vorhandenen Namen `launch` korrigiert.

Abschließender gezielter Befehl, im unten genannten deaktivierten Paket:

```sh
TSE_A4_CANONICAL_PACKAGE=/srv/tse-a4-build020-hard-canonical-envelope-final-20261114 \
TSE_HARD_MAP_PACKAGE=/srv/tse-a4-build020-hard-canonical-envelope-final-20261114 \
python3 -m unittest test_a4_canonical_native_groups test_prepare_a4_canonical_native_groups \
  test_a4_fire_observer_v2 test_audit_a4_native_fire_observer_v2 \
  test_a4_hard_maps test_stability_hard_rules test_preflight_startup -q
```

Ergebnis: **63 Fälle PASS, keine Skips, 0,236 s**. Das umfasst aktuelle Paket-/Quellpins, beide unveränderten V2-Suiten, Hard-/Startup-/Normalcloseprüfungen und die reinen Adaptervergleiche. Kein Compiler, Frida, Attach oder nativer Prozess wurde gestartet. Die Tests und Archivprüfung endeten vollständig; keine unbeaufsichtigte Aufgabe läuft.

## Geschlossene Archivdaten als Entwurfsprüfung

`check_a4_canonical_archive_design.py` liest ausschließlich abgeschlossene Dateien und liefert ausdrücklich `OFFLINE_DESIGN_CHECK_NOT_NATIVE_QUALIFICATION`, `qualified=false` und `functional_pass=false`. Alte Gruppennamen werden dabei retrospektiv an geparste Kopien gebunden. Der historische Lauf hatte diesen prospektiven Vertrag nicht.

Die [bereinigte Ausgabe](a4-canonical-groups-20261114/offline-design-check.json) enthält 13.683 geprüfte aktive Rohhüllen: 4.551 botA, 4.572 botB und 4.560 Overlap. Die feste kanonische Menge umfasst 9.123 Samples. Der unveränderte V2-Kern findet darin je eigenem Slot 268–503 gebundene native FIRE-Beobachtungen und 11–24 tatsächliche brauchbare Inventargewinne, ohne Within-group-Gesamtrowkonflikt. Drei pausierte Smokes sind keine aktiven Gameplaybelege. Andere alte Aktivitätsgates wurden durch dieses reine Werkzeug nicht neu abgenommen.

Alle sieben Archivdateihashes waren vorher/nachher gleich; insbesondere das alte Resultat bleibt `493ddee10ad4b6202be522447bf97b8a74020bb7deffc8b2a3dd7f6b500a85ad`. Der neue Entwurf benötigt unabhängig davon einen neuen kontrollierten nativen 600-s-Lauf.

## Paket und nächster Schritt

Deaktiviertes Autorenpaket: `/srv/tse-a4-build020-hard-canonical-envelope-final-20261114`.

- Manifest: `293c7d49e590e28164caf2db52660f144f14ebd32eca0c60fece40a5adc26de9`.
- 62 frische Runtimepins; `RUNTIME_REVIEWED=False`, Manifest-/Rootgates ebenfalls `false`.
- Elternpaket `/srv/tse-a4-build020-hard-map-startup-final-20261114`, Manifest `593e29ac10f68654e01e17f566a4aaa409a4843087d52560624aed2acca18f8f`.
- Alter V2-Kern `201ca2d0f3098637ffb129162d84e126062df24790cfa865693781683732e5fc`; Auditor `3ac187c8775b2bd1ed7021dc7b4037b0eeda6aec2a0292f9d87e47c9d8f4b466`.

Reproduktion: `python3 tools/prepare_a4_canonical_native_groups.py --destination NEW_EMPTY_PATH`. Bestehende Pakete werden nicht überschrieben. Frühere lokale Autorenentwürfe bleiben unbenutzt und sind keine Runtimekandidaten.

Private Diagnosebelege liegen unter `/srv/tse-a4-canonical-group-scan-20261114`: reproduzierbarer Scanner `scan.py`, Hashreceipt `receipt.json`, erster `canonical-design-check.json` und endgültiger `canonical-envelope-design-check.json`. Die private Quelle des geschlossenen Fensters bleibt unverändert. Keine Rohspieleridentitäten oder Retailbytes wurden veröffentlicht.

Nächster Schritt: unabhängiger Source-/Paketreview, dann ausschließlich durch Root neuer Freeze mit konsistenten Pins, Sicherung/Publikation, frischer exklusiver Preflight und gegebenenfalls genau ein neues 600-s-Fenster. Kein automatischer Retry, keine Livepromotion und keine A-Abschlussbehauptung aus Offlinebelegen.
