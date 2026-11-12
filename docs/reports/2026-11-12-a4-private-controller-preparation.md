# A4-Kartencontroller: privater Prepared-only-Entwurf

Privater Draft `/srv/tse-nav-a4-prepared-draft-20261112`, keine Runtime, kein Zugriff auf laufende Prozesse und keine Änderung der aktiven Fixture. Der Root-exklusive012-Lauf bleibt davon getrennt. `PREPARED-ONLY.md` beschreibt den vollständigen vorgesehenen Ablauf; `prepare_a4.py` erzeugt ausschließlich einen JSON-Plan auf stdout. Es gibt keine native Startfunktion. Der Runtime-Adapter muss nach Rootreview separat implementiert und gegen einen simulierten Backend-Lebenszyklus geprüft werden.

Ziel: acht Bots mit demselben ausdrücklich durch Root gepinnten Kandidaten, Originalserver und Stock-Vanilla, kanonische Konfiguration mit physischen RosterOffsets0/4, normale frühe Pausebarriere, tatsächliche Attach-Zuordnung und vollständige nach normalem Ende archivierte Rollenlogs. Root muss das private Kandidatenmanifest ausfüllen; die Vorlage enthält absichtlich weder DLL-Auswahl noch Freigabe. Der Plan selbst liefert stets `runtime_authorized=false`, `qualified=false` und `functional_pass=false`.

Die fünf Bindungen wurden gegen die tatsächlichen privaten NAV-Dateien und WLD-Mitglieder in `SE1_00_Levels.gro` erneut mit CRC32 und SHA256 nachgerechnet. Alle Pfade beginnen mit `Levels\\LevelsMP\\Deathmatch\\`; die NAV-Dateien liegen unter `Scripts/Cecil/`.

| Karte | Weltdatei / Inhalts-CRC | NAV-Datei / Inhalts-CRC | Knoten |
|---|---|---|---:|
| Red Station | RedStation.wld / ff3776e0 | RedStation_5AF1A276.nav / e4571656 | 193 |
| Hole | Hole.wld / 582bd040 | Hole_1AD627D0.nav / d7cac057 | 139 |
| Skulls | WeGotSkullsNBonesToo.wld / 42d03dd2 | WeGotSkullsNBonesToo_9B573405.nav / 70b554dd | 296 |
| Yodeller | Yodeller.wld / b3c8ceeb | Yodeller_FC72665B.nav / a4a7950c | 111 |
| Little Trouble | DM_LittleTrouble.wld / 4060d0dd | DM_LittleTrouble_6C64BF87.nav / 980013d4 | 110 |

NAV-Dateinamenssuffixe sind Cecil-Pfadhashes und ausdrücklich keine Welt-/NAV-Inhalts-CRCs. Die genaue bereinigte Assetmatrix liegt bereits in `docs/reports/cecil-full-20261107/assets.json`; der private Draft bindet sie zusätzlich an tatsächlich neu gelesene Bytes. Private Rohkoordinaten und Retail-Dateien werden nicht veröffentlicht.

Der Entwurf verlangt den gemeinsamen Arena-Ressourcenlock und einen eigenen Fixture-Lock vor jeder späteren Mutation. Eigene Unit-/Evidence-Präfixe ersetzen keine Belegungsprüfung. Alle modifizierten Dateien einschließlich DLLs, Spieleranzahl/Profile, Server-INIs und Cecil-Dateien müssen vor Staging gesichert und nach normalem Schließen bytegenau restauriert werden. Die Starts erfordern eigene Prozess-/CWD-/Namespace-/Modulidentitäten, neun eigene ungespawnte Spieler, identische Peer-Sitzungen und echte Load-Marker mit korrektem Weltpfad, Ready, Knotenzahl, Welt-/NAV-CRC. Eine feste Red-Station-Positionsreferenz wird nicht verwendet.

120s-Smoke und600s-Funktionsfenster sind getrennte Modi. Inventar/HP/Armor/Velocity/Support und native Lebens-/Routen-/Flüssigkeits-/Todesbelege werden vollständig aufgezeichnet, einschließlich fehlgeschlagener und zensierter Leben; useful-ranged-Maske bleibt `0x3df8`. Frags/Queries sind zusätzliche Beobachtungen. Sprunginput, Teleportflags, Ortsänderung oder begrenzte Schleifen beweisen keinen erfolgreichen gerichteten Übergang. Fehlende Spezialaktionen bleiben NOT_EXERCISED. Festkartenfenster beweisen keinen In-process-Mapreset und keine Langzeit-/externe-/Erstzustandsabnahme.

Der vorhandene048-Harness wird nicht blind umgepinnt: sein `RuntimeBackend` bindet alte eingefrorene Quellen und048-DLL-/Display-Annahmen. Nur einzeln geprüfte Mechanismen dürfen in den späteren neuen Adapter übernommen werden. Mandatory-Postclose prüft erst nach allen normalen Closeversuchen frische `*-closed.log`-Archive; fehlende/falsche Rollen, Kopierfehler, spätes SYNCBAD, Crash oder InvalidAction verhindern einen vollständigen Beobachtungsbeleg. Keine Force-Fallbacks oder fremden Prozesssignale.

**Offlineprüfung:** 15 Tests bestanden (`python3 -m unittest test_a4_policy -v`). Abgedeckt sind zwingendes privates Kandidatenmanifest, fünf Karten, gleicher Kandidat für beide Kohorten, unveränderte kanonische Konfiguration mit dokumentiertem optionalem Diagnoseoverride, echte statische Assetbytes, strikte Load-Marker und unterschiedliche Hasharten, eingefrorene Peerbarriere/tatsächliche Zuordnung, Close→Archiv→Finalizer-Reihenfolge, fehlende Artefakte/Rollen, späte Fehler und ein importier-/aufrufbarer Plan-CLI ohne Prozess-/Socketzugriffe. Das sind Offline-Tests; kein nativer A4-PASS.

Reviewhashes: `a4_policy.py` SHA256 `5422f9ad6f1c1824b125c4b2479084853739a677e18fa3431e862195374ce817`; `prepare_a4.py` `1cd6bd8bf69c5b41333395aa889e76e908cef98ba9a58f8057d535726500feb0`; `map-catalog.json` `11fc9080480dfa23cf0fc1f117a486b8f785daefbdeeb53dce26797c644018c3`. Vollständige private Pins in `review-sha256.json`. Vor einer echten Runtime fehlen noch Rootreview, exakte Kandidaten-/Serverpolicy-Auswahl, implementierter/geprüfter Runtime-Adapter und frischer nativer Preflight.
