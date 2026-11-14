# XRes-V2 begrenzt bestanden, Build024 erstellt, Dev-Sync offen

Die neue eigene XRes-Methode ist um23:45:31UTC abgeschlossen:
**PASS_METHOD_XRES_LOCAL_PID_METADATA_ONLY**, ResultSHA256
`18d16f195c64d2d5f6564b0166422d63aa72011c4dcd71284f05d1d9a1afc953`.
Zwei tatsächliche Snapshots, je sechs passende Resource-/Base-PIDantworten für
zwei Driver- und eine Peerverbindung. Zwei Clientlisten und zwölf IDarrays
allokiert und exakt einmal freigegeben. Vier reguläre Closes/reapedExit0, keine
Force, drei Fenster zerstört, vier Verbindungen geschlossen, Fehlerhandler
restauriert. Root prüfte die komplette Purepolicy erneut sowie exakte alte
Prozessgenerationen/167Absenz/fünf freie Zugriffssperren. Methode0,212714s.
Kein TSE/Wine/RECORD/Input. Keine kontinuierliche Clientbase-Lebensdauer, alte
U-Zuordnung, Gain-/A1-/Retailabnahme aus zwei Snapshots.

Eine vorausgehende Wrappervorprüfung blieb FAIL: Root hatte den exakten
Scopebezeichner der alten Peerquittung übernommen, während die gepinnte neue
Quittung ausdrücklich V2/Policy benennt. Der Fehler trat vor Owner/Locks/Native
auf. Der fehlerhafte Wrapper und sein FAIL bleiben erhalten. Ein neuer Wrapper
korrigiert ausschließlich den exakten Vergleich auf den tatsächlichen Scope;
alle übrigen Assert-/Quellpins und Grenzen gleich. Seine vollständigen reinen
Vorprüfungen bestanden vor dem ersten V2-Nativestart. Parent3f0c4180,
äußerer Wrapperdd2fae12. Kein automatischer Methodenretry.

Äußere Hostbeobachtung PASS_HOST_OBSERVATION_ONLY: ChildExit0/reaped,
Quellhash nachher gleich, zwei Proben/maximal0,316071s Abstand,
CPU51,2397%, verfügbarer RAM3496824832B/Datenträger9813692416B.
Das ist eine kurze Metadatenprobe und keine Gameplayressourcenabnahme.
Vorher Delta056 vollständig Drive-rückgelesen und74Dateimetadaten zweimalPASS:
372691B/SHAe7b08bb850db0c1528fa46bc5b43b79de11d5c5306d7aad54ea75776a7e61322,
Drive1igT1TbeOyHDP7NM81Yxs1lGA7H14Lgff. Neue Wrapper-/Laufdaten folgen im057.

## Build024 – neuer unqualifizierter Kandidat

Bestehender MSVC/Wine-Builder kompiliert15Units und linkt erfolgreich.
Quellcommit `100bda43eb46c7d671d71b7a50fae673a9e4406e`, Tree
`a1c049f440ed1600a718c07ef3fcd5477668250f`; dieser Tree ist durch tatsächlichen
Fetch des Remotea62d198d73008d8a01c8322b748b27ebe01a282d bestätigt.
DLL438272B/SHA256
`192169fe8396bfe1fb9c49419657b9146120c64eb3ac15095ac50a6f8659753c`,
Manifest8903d7db0437f8c9ff0f71e056523be35d9c6ef75c165e2f0491cb67818691c9.
Root prüfte alle47Quell- und28Overlaypins. Gegen023 ändert sich genau
BotSupplyNative.h; keine zusätzliche Quelle oder Parameteränderung.
qualified=false, noch keine Runtime-/Native-/Rolloutabnahme.

## Neuer Dev-Gegenbefund – unveränderter048-Stand

Präfixverifizierte Serverlogs23:27→23:47 zeigen zwölf weitere SYNCBAD und
**einen Sync-Disconnect**, derselbe externe Peer wie bei den früheren sechs
BADs. Die zusammenhängende letzte Folge zählt1→10; Sequenzen1102784 bis
1102964, Ticks55695,88 bis55705,02. Zuvor hatte derselbe Peer796 erfolgreiche
Checks nach der alten Fehlergruppe. Diese Erholung war folglich kein Dauerfix.
Eigene beide Dev-Botlogdeltas in allen sieben Fehlerklassen0; acht eigene Bots
bleiben verbunden, zusätzlicher Peer jetzt0. Keine Spieleridentität veröffentlicht.
Nutzer hatte seinen Client bereits als getrennt gemeldet; ihm wird diese
Verbindung nicht zugeordnet und sie wurde nicht instrumentiert.

Der Befund besteht mit dem unveränderten Cecil048 und separatem bestehenden
Dedicated-Powerupmodfe4a77bd. Kein neuer Rootrollout/Build024 war beteiligt.
Das widerlegt jede dauerhafte Syncheilung durch den früheren Botrückroll;
es beweist weder Powerupmod, Botlogik, Originalclient noch Netz als Ursache.
[Bestehende Ursachentrennung](2026-11-11-spawn-zero-sync-diagnosis.md) und
[früherer Rückroll-Gegenbefund](2026-11-14-development-sync-rollback.md)
bleiben relevant. Keine Syncschwelle geändert, keine unbelegte Livekorrektur.

Nächste Arbeit: ausschließlich isolierte024Red600-Vorbereitung und getrennte
A1-Prozess-/Basezuordnungsplanung; native Gegenproben müssen ursprüngliche
Dedicatedrollen/aktive Bedingungen sauber unterscheiden. A bleibt offen,
B nicht begonnen; die vereinbarte gemischte Liveflotte bleibt erhalten.
