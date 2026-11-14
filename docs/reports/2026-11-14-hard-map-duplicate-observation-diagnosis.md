# Geschlossener Hard-Kartenlauf: acht widersprüchliche Gesamtrows

Der Lauf `a4-020-hard-redstation-20261114-112608` bleibt **FAIL**. Nach 600,132663 Sekunden scheiterte der unveränderte V2-Auswerter an `conflicting duplicate inventory sample`. Diese Analyse ändert weder Ergebnis noch Kriterien und ist keine neue native Abnahme.

Der [bereinigte vollständige Konfliktbeleg](a4-canonical-groups-20261114/eight-conflicts.json) enthält alle acht Konfliktpaare, geänderte Felder, Inventarzeilen, physische Rolle/Local/Slot, beobachtetes Leben, Sessiontick und verfügbare Zeitangaben. Teilnehmernamen, GUIDs, IPs, Entity-/Pointeridentitäten und Retailbytes sind nicht enthalten. Ein geänderter interner State-Stackwert wird ausschließlich als Differenz ausgewiesen.

## Vollständige Auswertung

13.683 Gameplay-Samples enthalten 54.716 vorhandene Spielerrows mit gültigem Spawnclock. Es gibt 43.374 verschiedene Slot-/Entity-/World-/Life-/Sessiontick-Tupel und damit 11.342 wiederholte Beobachtungen. Bei sämtlichen ungeordneten Paarvergleichen ergeben sich 11.433 exakt gleiche und acht widersprüchliche Paare; einzelne Tupel haben bis zu vier Beobachtungen. Alle Samples tragen dieselbe Observer-Epochbindung.

Alle Konflikte liegen zwischen `botA_actual` und der später gelesenen Gruppe `vanilla_plus_overlap` desselben Schleifendurchgangs:

| Inventarzeilen | BotA-Local/Slot | beobachtetes Leben | Sessiontick | Änderungen |
|---|---|---:|---:|---|
| 898/900 | 0/0 | 2 | 35,899738 | Translation X/Z, Position X/Z, Heading |
| 898/900 | 1/2 | 3 | 35,899738 | Translation X, Position X/Z, Heading |
| 898/900 | 2/3 | 3 | 35,899738 | Translation X/Z, Position X/Z, Heading |
| 2520/2522 | 0/0 | 7 | 107,901985 | Translation XYZ, Position X/Z, Heading |
| 2520/2522 | 1/2 | 5 | 107,901985 | Position Y, Physicsflags, Waffen-State-Stack |
| 2520/2522 | 2/3 | 6 | 107,901985 | Translation XYZ, Position XYZ, Heading |
| 5798/5800 | 0/0 | 14 | 253,510864 | Translation XYZ, Position XYZ, Heading |
| 5798/5800 | 2/3 | 12 | 253,510864 | Translation X/Z, Position X/Z, Heading |

Entity-/Pointer-/World-/Lifeidentität, HP, Armor, Waffenbesitz, aktuelle Waffe, Ammo und Feuerfelder bleiben innerhalb aller acht Paare gleich. Sieben Positionsdifferenzen entsprechen rechnerisch neuer absoluter Geschwindigkeit mal 0,05 Sekunden; größter absoluter Restwert 0,000003576279. Das ist eine arithmetische Beschreibung, kein neuer EPS-Test oder Toleranzvorschlag.

Der achte Fall liegt im ersten Respawntick (`spawn_clock == session_tick`): Position Y 0,295→0,220, Physicsflags `0x40000287→0x40000284` und interner Waffen-State-Stackwert um −3 verändert. Es gibt keinen Beleg für eine Epochverwechslung oder einen Syncfehler aus diesen Paaren.

## Belegte Ursache und Grenzen

`retail_inventory_readonly.snapshot` liest das Sessionwort bei `session+0x4c`, führt zwei gleiche Lesepässe pro Aufruf durch und kontrolliert den Tick nochmals. Der Reader kennzeichnet dies ausdrücklich als `two_equal_reads_not_atomic`: Er garantiert keine atomare Momentaufnahme zwischen mehreren Aufrufen. Der V2-Auswerter verlangt dagegen vollständige Gleichheit sämtlicher Spielerfelder über solche getrennten Aufrufe, sobald Slot/Life/Tick gleich sind. Genau diese zusätzliche Annahme ist durch die acht realen Paare widerlegt.

Die drei Gruppen werden nacheinander gelesen. Ihr äußeres `elapsed` wird einmal zu Schleifenbeginn ermittelt und für alle Gruppen wiederverwendet. `snapshot.elapsed_seconds` ist jeweils nur die Lesedauer. Es gibt keine individuellen absoluten Aufnahme-/Callbackzeitstempel oder Callbacksequenzmarker. Der genaue Engine-Schreibzeitpunkt beziehungsweise die Mutex-/Callbackphase bleibt deshalb unbekannt. SDK107 beschreibt einen 20-Hz-Tick; eine neue Engine-Schreibfunktion wurde hier weder dekompiliert noch instrumentiert.

## Reproduktion und unveränderte Quellen

Privater ausschließlich lesender Scanner: `/srv/tse-a4-canonical-group-scan-20261114/scan.py`; Quittung im selben Verzeichnis `receipt.json`. Der Scanner verändert keine Quelldateien und startet keinen Prozess des Spiels. Reproduktion: `python3 /srv/tse-a4-canonical-group-scan-20261114/scan.py`.

- Scanner-SHA256: `7fa39a8d186292c64f48e67f9e89f9afe19e697e7f1c4bde27b2e721e35ab9ed`.
- Inventar-SHA256: `a6873074a34136f847dbb9a863b34bdfce542ff13349b9cee38477ee1b2c86d0`.
- Registry-SHA256: `58b2130a9c0a7c64e9f2241554339597dc3ab5fb8da63c99f28064093e443db3`.
- Resultat-SHA256: `493ddee10ad4b6202be522447bf97b8a74020bb7deffc8b2a3dd7f6b500a85ad`.
- Bereinigtes JSON: `f0875c250cc75efe5bece50c387b729f8dd0aaf69b9fbc3e90f50ea9f56cd861`.

Root meldet alle vier Rollen normal geschlossen, vier geschlossene Logs ohne Sync-/Crash-/CRCfehler und unabhängigen Restore. Diese Beobachtungen ersetzen den fehlgeschlagenen Auswerterabschluss nicht. Der getrennte prospektive Plan3714337 wurde vor Implementierung unabhängig geprüft; das alte Archiv darf dafür ausschließlich als Offline-Entwurfsprüfung dienen. Keine Umwertung des alten FAIL, kein automatischer Retry und keine Livepromotion.
