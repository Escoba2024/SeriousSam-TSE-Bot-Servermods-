# LittleTrouble031600: ein deaktivierter Diagnosefall

Der neue private Fork `/srv/tse-nav20-031-trouble600-diag1-disabled-20261115` ist genau eine Little-Trouble/600s/DIAG1-Bedingung. Fester Parent ist das unveränderte Hole031-D mit Manifest `f1557ca679ed5511a98fb6ece6863ea729be706d5846337f05f61d0d2e9224ca`. Kein Controllerimport, Build, Native, Frida, Input oder Livezugriff; alle Author-/Manifestgates false. A bleibt offen, B nicht begonnen.

Build031 bleibt vollständig identisch: Quellcommit `226276880c847ed145ee36f1415eb53fd3c01588`, Manifest `9c8cabf8d2a3a56803ac25ce8af55a38884a14de47ebeb5b1399095a2d4b40c5`, DLL `5c5c21d651f5513bcba4c1c3cc8ddc6495fbfbe7cdbbee506c70853bd15bbb0b`/461824 Bytes. Alle81 tatsächlichen Buildpinwerte (49 Sources/30 Overlay/Manifest/DLL) wurden frisch validiert und sind zwischen Parent und neuem Paket unverändert. Es gibt keinen Kandidatenaustausch aufgrund einer höheren Nummer.

Nur zwei geerbte Dateien sind geändert: Runner (zwei private Namespaces, CLI allein trouble, Diagnosebeschreibung) und Adapter (Import der neuen festen Kartenpolicy). Vollständige Inversen ergeben:

|Datei|exakter Parent-SHA256 nach Rücktransformation|
|---|---|
|run-a4.py|12a583e85cdadd1256579ea4c4372b661e9ac8bc3e180e93337d6793438e8cdb|
|adapter_policy.py|1f083067fe497df34063420f226d67493f9f330d43d47ea156245c79aaeb90aa|

121 andere geerbte Dateien sind vollständig bytegleich, einschließlich Comparisonkatalog, kanonischer Botconfigs,20FPS-Observervorlage, V2/V3-Reader/Source-/Lifejoins, Backend-/Start-/Closepfade und Transaktion. Hard2/achtDEMON3-duelist/Original20FPS/600s/DIAG1, Ressourcen-/Fehlergrenzen und beide Snapshotfelder atime_ns/mtime_ns bleiben unverändert. Keine automatische Sequenz oder Wiederholung. Der frühere Holezustand und dessen Ergebnisse werden nur als Herkunft übernommen, keine Funktionsabnahme transferiert.

Katalog `11fc9080480dfa23cf0fc1f117a486b8f785daefbdeeb53dce26797c644018c3` ist unverändert. Tatsächlich selektiv verifiziert wurden World `Levels/LevelsMP/Deathmatch/DM_LittleTrouble.wld` (SHA `e74e48e99bcc6e945500e1f28921c443515898791bfbca4d7ebf1ae61a26593c`, CRC4060d0dd) und Nav `DM_LittleTrouble_6C64BF87.nav` (SHA `252d7e4c003804fe9ae2afef359843feb39b5dda29c1d6eadb0835fbe64a30ac`, CRC980013d4/110 Knoten/BNMV6). Bestehende NOATIME-/NOFOLLOW-Reads wurden wiederverwendet. Der historische Vollarchivhash ist ausdrücklich geerbt; keine gesamten Assets oder früheren Rawfälle wurden erneut abgespielt. LoadedWorld bleibt false, Navfunktion ungeprüft.

Echtes Behavioral-RED gegen die tatsächliche Holeparentpolicy: trouble wird fälschlich abgelehnt und hole noch akzeptiert (ein ValueError/eine fehlende erwartete Ablehnung; neue Builderklasse vor Implementation übersprungen). Nach dem engen Retarget acht fokussierte Tests PASS1,991s. Sie prüfen feste Map/Dauer/Diag/Candidate inklusive bool/NaN/Inf/höherer Buildnummer, eindeutige Transformanker und vollständige Inversen, jede relevante Katalogfeldmutation, tatsächlich falsche World-/Navbytes, alle81 aktiven Buildpinmutationen, Parentmanifestbindung sowie bereits belegte Zielpfade. Keine C++-/SDK-/Runtime-Vollsuite wiederholt.

Aufruf: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools -p test_navigation_build031_trouble.py -v`. Reproduzierbare frische Ableitung: `PYTHONDONTWRITEBYTECODE=1 python3 tools/prepare_navigation_build031_trouble.py --destination /srv/FRESH-PRIVATE-DISABLED-TARGET`. Wiederverwendete Hole-/030-Helfer dienen ausschließlich reinen File-/Pin-/Closureprüfungen; kein Runtimecontroller wird importiert. Alle neuen privaten Dateien exklusiv0600, jede Paketdatei mit8GiB+64MiB Writefloor.

Finale Manifest-SHA `122e1dee0e1b620b2f764a9226c219a750b2986b53f5b9bc809c4f6c903a7989`, Runner `b5a22664a4fb0c30425fc305359dd836dc49a1aff6747ba760cca217d9d8a55e`. Nach Erzeugung sämtliche152 Runtime-/126 Source-/71 Pythonpinwerte,81 unveränderte Buildtargets,121 bytegleiche Parentdateien sowie beide vollständigen Inversen geprüft. Kleiner privater Vollreceipt `.codex/evidence/build031-trouble600/final-receipt.json`: SHA `c8852eed1c3e26db5778ddcd50abbd2b7bfec402e7cd04e7dd7484c7389d3f10`,68311 Bytes; reproduzierbarer Prüfer/RED-/GREEN-Logs daneben. Kein unabhängiger Review der eigenen Policy wird behauptet.

Root übernimmt Source-/Policyreview, Integration, getrennten Freeze, Sicherung und allein einen eventuellen begrenzten Nativefall. Diese Vorbereitung liefert weder tatsächliche Kartenaktivität noch Movement-/Pickup-/Treffer-ACK, A4-PASS oder Produktionspromotion. Keine neue Hypothese oder Verhaltensänderung.
