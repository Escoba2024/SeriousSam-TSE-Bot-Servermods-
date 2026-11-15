# Build024: vier getrennte Kartenfälle vorbereitet, kein Native gestartet

Vier deaktivierte Pakete für die tatsächlich betriebenen Karten Skulls,
Little Trouble, Hole und Yodeller sind aus dem unveränderten024Red600-Parent
abgeleitet. Sie bereiten fehlende Kartenfunktionsprüfungen vor. Sie sind keine
Kartenfreigabe, kein A4-Abschluss und keine Veröffentlichung für die Liveflotte.

## Herkunft und unveränderte Bedingungen

Parent `/srv/tse-nav20-024-red600-disabled-20261114`, Manifest
`ea00456a147418f54db3b3b83c96a61a122ae8c5d652a3608317c5919c379f5a`.
Build024-Quellcommit `100bda43eb46c7d671d71b7a50fae673a9e4406e`,
Buildmanifest `8903d7db0437f8c9ff0f71e056523be35d9c6ef75c165e2f0491cb67818691c9`,
DLL `192169fe8396bfe1fb9c49419657b9146120c64eb3ac15095ac50a6f8659753c`,
438272Bytes. Tatsächlich47Quell-/28Overlaydateien plus DLL/Manifest frisch geprüft.

Hard2, achtDEMON3/duelist und ein unveränderter Originalclient mit derselben
20FPS-Startvorlage,600s,Diagnostics0, Profile/Seeds, Original-Dedicated,
V3-Gruppen/Readversuche/Readraten, Lebens-/Source-/Inventarbeobachtungen,
Hostgrenzen, Ressourcen, normale Closes und Restore bleiben unverändert.
20FPS ist die vorhandene Vorlage; tatsächliche Framerate ist hier nicht gemessen.

Jedes Paket bindet genau seine Karte. Ein Aufruf mit RedStation, einer anderen
Karte, einer Dauer ungleich600 oder Diagnostics1 scheitert. Kein automatischer
Serienlauf oder Retry. Alle Code-/Manifestgates sind weiterhinfalse.
Root muss jeden einzelnen Fall separat prüfen/einfrieren/starten.

## Genaue Bindungen

Katalog unverändert SHA256
`11fc9080480dfa23cf0fc1f117a486b8f785daefbdeeb53dce26797c644018c3`.
Alle Welten liegen unter `Levels/LevelsMP/Deathmatch/`, Nav unter `Scripts/Cecil/`.

| Case | World | WorldCRC | Nav | NavCRC | Nodes |
|---|---|---|---|---|---:|
|skulls|WeGotSkullsNBonesToo.wld|42d03dd2|WeGotSkullsNBonesToo_9B573405.nav|70b554dd|296|
|trouble|DM_LittleTrouble.wld|4060d0dd|DM_LittleTrouble_6C64BF87.nav|980013d4|110|
|hole|Hole.wld|582bd040|Hole_1AD627D0.nav|d7cac057|139|
|yodeller|Yodeller.wld|b3c8ceeb|Yodeller_FC72665B.nav|a4a7950c|111|

Der Builder liest für genau die gewählte Karte den tatsächlichen Worldmember
und die vorhandene Navdatei; vollständige Member-/NavSHA, CRC, BNMV6 und
Nodezahl müssen dem Katalog entsprechen. Der Vollarchivhash ist geerbt und wurde
hier nicht erneut berechnet. Keine Behauptung eines geladenen Worlds. Die
bestehende native Prüfung auf sole matching Archive/keinen Loose-Shadow und
tatsächliche CecilLoad-/Serverlevelbelege bleibt unverändert.

## Exakter Quellumfang

Neue Dateien `tools/prepare_navigation_build024_maps.py`,
`tools/navigation_build024_maps_policy.py` und zugehöriger Test.
Die reine Policy bindet Karte/024/600/diag0. In jedem Paket ändern sich nur:

- `run-a4.py`: zwei Service-/Evidence-Namensraumliterale;
- `adapter_policy.py`: Import dieser reinen Optionspolicy und zusätzlicher
  fester Kartenliteral beim bestehenden Optionsaufruf.

Beide Dateien sind durch die Umkehrfunktion bytegenau zum Parent rekonstruierbar.
74weitere geerbte Quelldateien bleiben bytegleich, darunter alter Red-only-
Vergleichsvertrag/Tiercheck, Katalog, Assetsvalidator, alle Reader/V2/V3-Auditoren,
Hard-/Host-/Life-/Error-/Close-/Restorepolicies. Die neue Policy hat einen eigenen
Runtimepin. Neue Metadaten unterscheiden den einzelnen Kartenfall vom geerbten
Redvergleich; historische Vergleichsmetadaten bleiben separat erhalten.
Keine Gameplay-/DLL-/Speicherdecoderänderung.

## Offlineprüfungen

Erste Ausführung:9/9 erwartete REDs wegen fehlendem Builder. Erster GREEN-Versuch:
8/9, ein Test mockte versehentlich den lokalen SHA-Helper statt des tatsächlich
verwendeten geerbten Buildvalidators. Dieser Fixturefehler wurde korrigiert;
keine Produktionsprüfung wurde gelockert. Alte Logs sind privat erhalten.

Finaler fokussierter Lauf:

```bash
PYTHONPATH=tools nice -n 15 python3 -B -m unittest tools/test_navigation_build024_maps.py tools/test_navigation_build024.py -v
```

16Tests PASS in0.818s: vier feste Kartenfälle, falsch zugeordnete Karte,
Red/Ersatz/unknown/Build023, bool/NaN/599/601/diag1, doppelte Retargetanker,
veränderte World-/NavSHA/CRC/Nodezahl, vollständige Buildpins samt
Overlaymutation, Parentmutation vor Zielanlage, alle Gatesfalse,
Source-/Runtime-/Pythonpins,74bytegleiche Dateien und zwei exakte Inversen.
Keine Imports von Controllern/Runtime, keine Displays/Frida/Netz-/Spielprozesse.

## Deaktivierte Pakete

Alle Pakete liegen unter `/srv/`; Namensschema
`tse-nav20-024-<case>600-disabled-20261115`.

| Case | ManifestSHA256 |
|---|---|
|skulls|9254b47fddb163bfc476df1198cab090c0c814bf16f59154d390919189389f0e|
|trouble|c06291ee3b19e580ed0ca668de15b6b54c6c60a46eab856eb12717c15192a50c|
|hole|fea0f68119ec5b63f7d72866eab86af8caed625e6331b0bbba16f10acaae2ae5|
|yodeller|60186c5f4a572ddc5b59a22b210edafcee6a4b7b875ebfe49067cd4456c16778|

Je140Runtime-/81Source-/48Pythonpins frisch geprüft. Gemeinsamer RunnerSHA
`be04bd015fb8b8ea674f0c18426648b1a827607961a970592ead7d2f04bb2fb5`;
die feste Kartenbindung liegt im jeweils gepinnten Adapter.
Private Vollquittung im eigenen Worktree:
`.codex/evidence/navigation024-maps/final-receipt.json`, SHA256
`aa79f6498a5e702dd22a9bd4e2b0a953f30dfcf6ca47fe212bcea4d2c5c7d4db`.
Reproduzierbarer privater Nachprüfer `verify-final.py` prüft alle Pins,
Bytegleichheit/Inversen undfalse-Gates ohne Controllerimport oder Start.

Einzelne Offlineableitung, Beispiel:

```bash
PYTHONPATH=tools python3 -B tools/prepare_navigation_build024_maps.py --map hole --destination /srv/NEUER-PRIVATER-DISABLED-PFAD
```

Der Zielpfad muss neu sein; dieser Builder ist kein nativer Starter.

## Offene Abnahme

Skulls historische223/263s-Unbewaffnetheit bleibt FAIL. Hole benötigt explizite
Bewertung von Liquid/Lava, Höhenwechseln und Recovery. Yodeller020-Belege sind
keine024-Abnahme. Alle vier Karten benötigen tatsächlich geladene Module/Worlds,
Bewegung, Waffenbeschaffung, Kampf/Respawn und Prüfung von Fehlern/Ressourcen.
Auch ein vollständiger600s-Fall schließt Kartenreset, Spezialübergänge,
Dauerstabilität, komplette Cecil-Parität oder menschliches Niveau nicht ab.

Die ursprüngliche Neunkartenmatrix wird nicht reduziert: Compound wird nicht
stillschweigend durch KuntaKinte ersetzt, DesertTemple bleibt bei fehlenderWelt
gesperrt, LostTomb/Fortress bleiben separate offene Kartenpunkte. Kein Native,
keine neue Liveversion, A offen und B nicht begonnen.
