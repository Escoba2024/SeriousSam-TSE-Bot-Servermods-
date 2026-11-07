# Qualifikationsprotokoll Cecil-Port, 07.11.2026

Fortgeschriebener Stand während der Build010-Qualifikation; keine vollständige Runtime-Abnahme. Vollständiger Auftrag und private Messreihen liegen in der privaten Evidence-Ablage. Keine Runtime-Abnahme aus Offline-Tests ableiten.

## Baseline und Vergleichsgrenzen
A: sauber wiederholte bisherige Entwicklungs-DLL ce559971ce4a1677c1b299a7d0c27f148fa4ecace2a55d45e006bdb1598ac6a4 auf RedStation:360,56s/72 Samples, keine neuen Fehler. Messwerte stehen in baseline-clean-summary.json; keine vollständige Langzeitqualifikation dieser Baseline.
B: gepinnte Cecil-Quell-/Tabellen-/NAV-Fixtures. Keine Originalmod-Runtimeparität: die ursprünglichen v60/v120-Toolsets fehlen, die vorhandene v143-Toolchain würde eine eigene Entities-/ABI-Qualifikation benötigen. Die Originalmod wird nicht in die Vanilla-Umgebung installiert.
C: integrierter Cecil/Human-Port, aktuell Build010. Native Skulls-Beobachtung ist nicht automatisch ein kontrollierter RedStation-Ressourcenvergleich. Gleiche Servereinstellungen/Profile/Seeds und drei120-s-Fenster bleiben für den begrenzten Vergleich maßgeblich; Spawn-/Kampfzustände sind nicht bitidentisch kontrollierbar.

## Vorab festgelegte Gates
- Unveränderte Dedicated/Engine/Entities-Hashes; PE32-x86-Bot-DLL eindeutig manifestiert. Null neue SYNCBAD, CRC-, Join-, Access-Violation- oder Fatalfehler.
- Je Bot nach Spawn/Respawn binnen5s Bewegung (>0,25m) oder sichtbarer Kampf. Keine unbegründete zusammenhängende Stillstandsphase >10s. Sichtbarer Kampf darf stationär sein; Positionsstillstand wird getrennt ausgewiesen.
- Für den Einzelbot-Supplytest auf RedStation werden die ersten zehn tatsächlich vom Planner gewählten, beim Zielbeginn aufnehmbaren Waffenitems als feste prospektive Szenariomenge erfasst. Mindestens neun erreicht; verschwundene Items und reale Bedrohungsabbrüche separat dokumentieren, nicht nachträglich als Erfolg zählen. Erster sinnvoller Pickup Median<=15s/P95<=30s über mindestens zehn Spawnbeobachtungen; unkontrollierbare Spawn-/Verfügbarkeitslagen explizit als Vergleichsgrenze.
- Doppel-Colt/Rocket/Grenade/Cannon/Flamer: nativer Pickup, Besitz, Auswahl und aktueller Waffenwechsel belegen; nahe Explosivdistanz verhindert Feuer. Nach geeigneter Auswahl Wechsel innerhalb eines CD-Zyklus zuzüglich nativer Wechselanimation; Animation und Botverzögerung getrennt erfassen.
- Alle acht Bots bewegen sich, feuern im Kampf und zeigen Treffer-/Scoreentwicklung. 100 beobachtete Todesfälle gruppenweit; kein dauerhaft toter Slot, Respawn spätestens Presetverzögerung+5s.
- 1 Bot >=3600s, 4 Bots >=3600s, 8 Bots >=7200s, dann kontrollierter Wiederanlauf. Finaler DLL-Hash identisch. Verhaltensänderung setzt betroffene Gates zurück. Temporäre Gatepopulation nur Entwicklung; finale Sollpopulation bleibt acht.
- Maps: alle fünf betriebenen Maps jeweils eigener Join/Navigation/Pickup/Kampf/Respawn-/Mapwechselnachweis. Originalrotationen bleiben erhalten. Sonderflags/Teleporter, Absturzränder, Locks und Crouch/Jump benötigen echte beobachtete Actions/Positionsfolgen.
- Original-Retailclient muss mit Originalkomponenten beitreten und reguläre Gameplay-Actions ausführen. Eine reine UDP-Abfrage genügt nicht.
- Acht-Bot-CPU-Median/P95 je Botprozess maximal20% über sauber wiederholter Baseline; Host-P95<85%, keine dauerhafte Swap-/RSS-Zunahme. RSS nach10min Warmup über letzte60min: Trend<=1MiB/min und Nettoanstieg<=32MiB je Prozess. Mindestens8GiB freie Platte.
- Flottenprüfung nach gestaffeltem Rollout: alle sechs Instanzen gleichzeitig mindestens15min, richtige Identitäten/Maps/Populationen/Hashes, aktive neue Policy, Bewegung/Kampf/Respawn, keine neuen Netzwerk-/Syncfehler, Host-P95<85%.

Ein fehlgeschlagenes Gate wird als fehlgeschlagen dokumentiert. Schwellen werden nicht nach Messbeginn gelockert. Begründete Szenariokorrektur erfordert neue Version und neuen Lauf.

## Aktueller Status — Build010
Build010, Quellstand df1ca40d3feb3788b7be1cb098d26a035a4a3b0e, DLL224ee607072982a521bdab36250554039f9e606a4db755fdd42716fb0f031475: echter PE32-x86-Build aus15 Übersetzungseinheiten; beide Entwicklungsclients mit geladenem Hash und Join bestätigt. Der600,0086-s-Funktionstest auf Skulls ist beendet: keine neuen Logfehler, alle acht Bots bewegt, maximal3,04s unbegründeter Stillstand. Die Kampfabnahme ist fehlgeschlagen: BotA-Feueraktionen219/289/220/75, BotB1/5/1/1; alle vier BotB-Scores blieben unverändert trotz zahlreicher sichtbarer Ziele.17 Todesfälle insgesamt. Diagnose und erneute Verhaltensprüfung sind erforderlich. Keine native Gesamtfreigabe; keines der formalen3600/3600/7200-s-Gates abgeschlossen oder begonnen.

Der Adapter berücksichtigt jetzt das originale opt-in bAvoidPits und den aktuellen Navpunkt. Körper-/Gravitationsbasis, begrenzte Ausweichbewegung und endliche Actionachsen sind portabel geprüft. Native invertierte Schwerkraft, alle fünf Kartenfunktionen und originaler Retail-Gameplaybeitritt bleiben offen.

Build009 scheiterte bei der ersten Installation mit zehn SYNCBAD und einem Clientdisconnect. Ein erneuter gemischter008/009-Versuch blieb120,85s ohne erkannte Logfehler;180 vergleichbare passive Sync-Paare waren identisch.48 ungepaarte Checks vor dem Beitritt und nicht reassemblierte Transportformen verhindern eine vollständige Vergleichsaussage. Die Fehlerursache ist nicht geklärt. Dieser Kontrollversuch qualifiziert010 nicht.

Alle fünf Produktionsinstanzen bleiben unverändert. Historische Kurztests anderer DLLs sind keine Abnahme dieses Kandidaten.

## Sauber wiederholte Ressourcenbaseline vor Installation
360,56 s, 72 Samples, keine neuen Fehler; während dieses Fensters keine Builds oder CPU-Tests. BotA Median6,58/P95 7,59 Prozent eines Kerns; BotB6,79/7,59; Dedicated5,19/5,99. Host Median38,77/P95 40,72 Prozent. Die vorab festgelegte Grenze von maximal20 Prozent zusätzlicher Botprozess-CPU bleibt unverändert. Maschinenlesbare Werte: baseline-clean-summary.json.

## Nachtrag: serverseitiger Versandrückstand und LAN-Konfiguration
Die native Diagnose lokalisierte den BotB-Rückstand im serverseitigen Versandpuffer bei effektivem Clientlimit4000B/s. Explizite bestehende LAN-Werte100000/6000 im Startup plus B-Neustart mit unveränderter010-DLL beseitigten den beobachteten Rückstand; eigener Action-Feedbackmedian sank von2,15s auf0,05s. Serverlimit8000 unverändert. Details und Kontrollgrenzen: [nativer Diagnosebericht](2026-11-07-native-client-stream-lag.md).

Die abgeschlossene300,00485-s-Kontrolle zeigt alle8 Bots mit Bewegung, Combat-Feueraktionen und Scorezuwachs,41 Todesfälle mit ebenso vielen Respawnzähler-Inkrementen, keine neuen Logfehler und maximal7,05s unbegründeten Stillstand. Die erste600-s-Kampfabnahme bleibt als fehlgeschlagen dokumentiert. Kein Langzeitgate, keine saubere Ressourcenvergleichsmessung (parallel isolierte Stopfixture), keine vollständige Map-/Waffen-/Respawnfreigabe. Maschinenlesbar: lan010-summary.json. A wurde anschließend auf dieselben expliziten Netzwerkwerte gebracht. Passive Kontrolle19:46:19UTC bestätigt bei beiden Clients und beiden Server-Sessions100000/6000, Versandrückstand0, Latenz0,050/0,056s; Serverlimit8000 unverändert. Die finalen Gates verwenden einheitliche Konfigurationen.
