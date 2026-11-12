# Build017: begrenzte A4-Diagnose und offene A1-Prüfung

Stand: 12.11.2026 15:59:33 MEZ

## Nachgewiesener Stand

Build017 wurde um 15:53:38 MEZ tatsächlich mit Exit0 beendet; alle15 Übersetzungseinheiten und der Linkschritt waren erfolgreich. Die neue DLL ist428032Bytes groß. Sie ist ein unqualifizierter Diagnosekandidat und wurde nicht in die öffentliche oder Dev-Laufzeit übernommen. A bleibt insgesamt offen, B unbegonnen.

| Gegenstand | SHA/Stand |
|---|---|
| Lokaler Buildquellstand | b35397f024b8a8722a01178a08c06d3d40802f65 |
| Exakter Quellbaum | ce74a529a1c55dd3317476d44137f1bd2327d9c0 |
| DLL | a5a379aadfd0cc376ad15a8368dd6814518e3f2da1fde22fdde9bd86f02abc5d |
| Buildmanifest | b4905cf1c279c6461ea892f159c16d3e92196901c6aa8d255bf62311a8e0e32f |
| Beobachterheader | ad54eef28d087654dd7ad5107f547091f1cda5b7ed2f03e06e9ec40593064bd1 |
| Unabhängige Sourcequittung | 96c097c06ef5938fa2f6d4d884874197cd986d32f2bb41f1800608b853494064 |
| GitHub-Commit, tatsächlich gefetcht | 6687e2abb5b46d7a1be0f95ab24f26a4222f4644 |

Die [GitHub-Veröffentlichung](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/commit/6687e2abb5b46d7a1be0f95ab24f26a4222f4644) wurde um15:50:04MEZ vom Ubuntu-Repository erneut abgerufen. Ihr Baum entspricht exakt dem lokalen Buildquellstand. Kein Force-Push und kein Merge in main. Spätere Dokumentationscommits sind von diesem Nachweis getrennt.

## Änderung und Prüfgrenze

Nur BotSupplyNative.h erhält100 additive Produktionszeilen; BotDriver und sämtliche Spielentscheidungen bleiben unverändert. Der standardmäßig ausgeschaltete Beobachter erfasst zwei konkrete Waffenversorgungsannäherungen,68→6 und den ungebundenen Quellpunkt87. Er verwendet vorhandene Capture-/Final-Aufrufe, keine neue Navigation, Casts oder Zufallsauswahl.

Die Grenze beträgt je Klasse, Slot und Mapepoche höchstens200 tatsächliche Actionproben innerhalb von strikt weniger als10Sekunden. Tod, Zielwechsel, Reset und Diagnose-Aus/Ein erneuern das Kontingent nicht. Die unabhängige Prüfung bestätigt0Critical/0Important sowie89 korrekt zugeordnete Logargumente und eine maximale Zeile von1869Bytes aufWin32 beziehungsweise1988 aufLP64; mindestens59Bytes inklusive NUL bleiben im bestehenden2048Byte-Puffer frei.

Die tatsächlichen abschließenden Sourceprüfungen sind68 neue Beobachterchecks und2687 bestehende Bridgechecks unterASan/UBSan sowie die vorhandenen Driver-Action-Guards, jeweils Exit0. Root hat alle12 Autorenpins, die integrierten10Repositorydateien und die Originalreceipts erneut geprüft. Diese Tests belegen weder native Logkosten noch ein Auftreten der beiden beobachteten Klassen und keine funktionale Waffen-/Navigationsabnahme.

## Nächster begrenzter nativer Schritt

Ein neues deaktiviertes Controllerpaket wird aus dem unveränderten frühen Build016-Inventarprotokoll abgeleitet. Es erhält nur Build017-Pins, neue Beleg-/Unitnamen und eigene Closurepfade. Der tatsächliche Ablauf bleibt RedStation→RedStation→RedStation; alte abweichende Manifestmetadaten werden nur im neuen Paket berichtigt.300Sekunden,50SekundenTransition,19SekundenClose, Ressourcen-, Inventar-, Registry-, Pickup-/Fire- und Restorebedingungen bleiben unverändert. Root muss den konkreten neuen Controller separat prüfen und freigeben.

Der Build016-Lauf104821 bleibt FAIL. Der neue Build repariert die Bewegungsverzögerungen noch nicht. Erst die tatsächlichen Requests, Reached-/Safety-Daten und folgenden Bewegungszustände können die Ursache weiter eingrenzen. Ohne entsprechende Beobachtung gibt es keinen neuen Gameplay-PASS.

## A1 und Sicherung

V4 bleibt wegen des unabhängig reproduzierten ignorierten After-Input-Ankers BLOCKED. Der separate [V5-Entwurf](2026-11-12-a1-flight-transition-v5.md) hat187 bestandene Tests und einen strikten Replay aus allen203 vollständigen Originalpaaren/213Rohversuchen. Seine unabhängige Gegenprüfung läuft; beide Gates sindfalse. Der alte native111716-FAIL bleibt erhalten. Wiederholter Schaden im ersten verarbeiteten Respawnzustand ist weiterhin nicht belegt.

Delta020 ist vollständig auf Drive zurückgeprüft, enthält aber diesen späteren Build017 und die neue V5-/Reviewarbeit noch nicht. Dafür ist der nächste private Sicherungsnachtrag erforderlich. Aktive öffentliche/Dev-DLLs und der abgeschlossene Namensrollout bleiben der zuvor belegte Stand. Die formalen3600/3600/7200-Sekunden-Gates, vollständige A3/A4-Abnahmen und der Release-Rollout sind offen.
