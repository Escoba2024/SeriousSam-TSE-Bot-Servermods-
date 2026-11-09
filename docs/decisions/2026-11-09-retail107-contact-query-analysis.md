# Retail1.07-Kontaktanalyse: verfügbare Werkzeuge und statische Grenzen

09.11.2026,20:51UTC. Anlass ist der im vollständigen normalen041-Skulls-Lauf beobachtete NULL-Support-Stillstand. Weder ein fehlender Punktstrahltreffer noch ein SDK-Methodenname beweist native tragende Geometrie oder die Eignung eines Ersatzes.

Die aktuelle Toolinventur stellt keinen Ghidra-/Frida-Analyseaufruf bereit; lokal sind weder `ghidraRun` im PATH noch ein bestätigtes Ghidra-Verzeichnis unter `/opt` vorhanden. Das ersetzt keine Aussage über historische Shadow-Installationen. Der bekannte falsche `ghidra`-Endpoint auf8080 wurde nicht aufgerufen; kein Dienst gestoppt, keine neue Installation oder Sicherheitsumgehung vorgenommen.

Als bereits vorhandener lesender Fallback ist `/usr/bin/objdump` nachgewiesen. Ein echter PE-Export-/Disassembly-Smoke auf der eigenen unveränderten Originaldatei gelingt. Dies ist statische Binäranalyse, kein MCP-Smoke, Laufzeithook, native KI-Gate oder Netz-/CRC-Test. Python/Objdump lesen die Datei ausschließlich; Rohbinärdatei und vollständige private Disassembly werden nicht veröffentlicht.

## Direkt verifizierter Befund

Originale `Engine.dll`, SHA256 `b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f`, bevorzugte ImageBase `0x600c0000`. Der Export `CMovableEntity::IsSomeNearPolygonBelowPoint` liegt bei RVA `0x15a270`, bevorzugter VA `0x6021a270`. Tatsächliche Bytes `33 c0 c2 08 00` dekodieren zu `xor eax,eax; ret 8`. Main und unabhängige Analyse bestätigen: Diese Methode liefert in genau dieser Retail-Datei stets FALSE und führt keine Suche aus. Ein vorhandener Engine107-SDK-Vertrag begründet daher keine funktionale Ersatzabfrage.

Reproduzierbare lesende Kommandos mit einer privaten Originalkopie:

```sh
sha256sum ORIGINAL_ENGINE_DLL
objdump -p ORIGINAL_ENGINE_DLL
objdump -d -Mintel --start-address=0x6021a270 --stop-address=0x6021a280 ORIGINAL_ENGINE_DLL
```

Die Adressen sind bevorzugte Dateibild-Adressen, keine behaupteten live geladenen ASLR-Adressen. Serious Engine1.10 bleibt eine getrennte Referenz, keine belegte Retail1.07-ABI-/Implementierungsgleichheit.

## Weitere statische Gegenprüfung

`IsPolygonBelowPoint` bei `0x60219fa0` bis `0x6021a254` schreibt in der vollständig gelesenen Routine nur Stack-/Argument-Scratch. Sie liest die Punkt-/Polygon-/Gravitationsgeometrie und testet begrenzte Projektion und Polygoncontainment, keine Collision-Sphere-Aufstandsfläche. Der virtuelle Aufruf über VTable+`0x11c` ist für den originalen CPlayer separat aufgelöst: originale `EntitiesMP.dll` SHA256 `7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350`, VTable bei `0x6048bb90`, Thunk `0x6046f444`, IAT `0x6048b144`, Engine-Ziel `AllowForGroundPolygon` bei `0x6021a260`. Dieses Ziel liefert mit Bytes `b8 01 00 00 00 c2 04 00` konstant TRUE ohne Welt-/Entity-Schreiben. Andere Unterklassen und live veränderte VTables sind damit nicht geprüft.

`IsSomeSectorPolygonBelowPoint` bei `0x6021a280` bis `0x6021a314` iteriert tatsächlich die übergebene Polygonliste und ruft die vorige Routine. Main hat den vollständigen kurzen Körper separat gelesen; sichtbar sind Stack-/SEH-Schreibvorgänge, keine Szenen-/Cacheänderung. Eine Runtime-Abfrage, sichere Objektlebenszeit, Arbeitsmenge, physische Unterstützung oder Eignung im Bot-Timer sind damit noch nicht belegt.

`IsStandingOnPolygon` bei `0x60219d40` arbeitet laut unabhängiger vollständiger statischer Analyse mit dem aktuellen Collision-Handle und einer einseitigen signierten Ebenenprüfung gegen0,01, nicht einer absoluten Distanz oder einem zukünftigen Punkt. Außerdem dereferenziert der Körper den aktuellen Standpolygon-Owner ohne vorgeschalteten NULL-Check. Die Methode ist daher kein ungeprüfter NULL-Support-Ersatz; Main hat diesen langen Körper noch nicht vollständig unabhängig abgenommen.

`WouldFallInNextPosition` bei `0x6021a320` verwendet zwar vorhandene Stand-/Near-Polygone, ruft bei der Sektortraversierung aber `CListHead::AddTail` bei `0x600cdc10` und `RemAll` bei `0x600cdc70` mit eingebetteten Szenen-Sektorknoten auf. Die Analyse findet dadurch tatsächliche temporäre Weltlistenänderungen. Diese Routine darf nicht als rein passiver Sensor bezeichnet werden. Das beweist keine Ursache historischer Sync-Divergenzen. Vollständige private Disassembly, Exportzuordnung und Prüfsummen sind im Analyseartefakt SHA256 `05aa4bedda8eeb54329ee75f54cc384a26fcfdbef1b11993fcad4c8907a9b783` gebunden.

## Native Abgrenzung

Es wurde keine dieser untersuchten Methoden neu im laufenden Spiel aufgerufen. Die getrennte041diag-DLL liest bestehende Kontaktfelder und bereits vorhandene Strahlergebnisse ohne zusätzliche Enginequeries. Ihr erster vollständiger600,296s-Lauf reproduziert den NULL-Stillstand nicht. Erst der getrennte Wiederholungsversuch zeigt tatsächliche NULL-Stand-/Referenzzustände und lang anhaltende Stillstände. Nach546,003s ist dieser optionale Versuch administrativ normal beendet, ausdrücklich vor1800s mit `observation_completed=false`, erhaltenem Interruptstatus und vollständigem normalem Cleanup. Keine Diagnosezeit erhält Qualifikationskredit.

Eine zusätzlich begrenzte diagnostische Bodenabfrage bis zur tatsächlich nativen StepDn-Grenze wird separat vorbereitet, um die gemessene Lücke zwischen Fußstrahl und Schrägenfläche zu prüfen. Keine Steuerung darf ein unbekanntes Messergebnis als tragenden Boden verwenden; ein Messbuild wäre wiederum ein eigener unqualifizierter Kandidat mit eigenen Query-/Timingkosten. Die normalen041-Skulls-FAIL- und Supply-/Retail-Teilnachweise bleiben unverändert erhalten.
