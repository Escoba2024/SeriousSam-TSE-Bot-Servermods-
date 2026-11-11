# Normal044: autonome Luft-NAV beobachtet, Wegpunktschleife verhindert Gesamtfreigabe

Normal044 ist nicht für den öffentlichen Rollout qualifiziert. Quelle `3c09c21c56c18a846873bcb4c5766d9399ba8b87`, Tree `9734ea4e089b5460ddfb0ebd64c366292185b083`, DLL `eb9201ebf36c8ae3374c9d095aaaf135801cebce0584b7d73ac68ad20f161509`. Alle15 MSVC-Einheiten/Link und855 finale SDK-ASan/UBSan-Prüfungen bestehen; Main und unabhängiger vollständiger Quellreview bestätigen die beiden geänderten Dateien. Safe34/Supply33/Retail20/Featureindex16 reine Prüfungen bestehen. Der frische portable Neun-NAV-Roundtrip samt unabhängigen193×193-Pfadvergleichen besteht mit221682 Prüfungen ohne Fehler. [Bereinigtes Buildmanifest](build044.json). Diese Nachweise ersetzen keine native Gesamtqualifikation.

## Getrennte Freigabe für ungebundenen Flug

Ein separates aktuelles Luftbewegungstoken entsteht ausschließlich bei tatsächlichem FALL, akzeptiertem Supply-Vorschlag, fehlender gebundener NAV-Kante, Originalstandard `bAvoidPits=0` und wirklicher Sichtprüfung eines ursprünglichen NAV-Hinweises. Die abschließende Bewegung prüft Lebens-/Welt-/Frame-/Gravitations-/Graph-/Zeit-/Zielbindung erneut und nutzt einen frischen physischen Wandtest. Horizontales Limit0,3/up0, ursprüngliche Hint-Grenzen, maximal16 Rays, Locks und feste Fristen bleiben bestehen. Unbekannter Support wird weder Bodenbeleg noch Anker; es gibt keine neue tiefere Bodenprobe, Physicsänderung oder künstliche Sprungaktion. Der vorhandene Ground-Escape-Hold wird nicht als Luftbewegung fortgeführt.

## Skulls600: numerische Grenzen erfüllt, Route funktional offen

Der vollständige neue Acht-Bot-Lauf erreicht600,008936462s und595 gültige Statusabfragen bei vollständiger Abdeckung. Alle acht Bots zeigen positiven Scorezuwachs; keine neuen erkannten Monitor-/Sync-/CRC-/Fatalfehler. Alle drei eigenen Prozesse schließen normal.

| Slot | Maximaler unbegründeter Stillstand |
| --- | ---: |
| BotA:0 |3,023s |
| BotA:1 |1,021s |
| BotA:2 |2,021s |
| BotA:3 |1,013s |
| BotB:0 |2,020s |
| BotB:1 |2,022s |
| BotB:2 |4,041s |
| BotB:3 |1,012s |

Die10s-Grenze bleibt unverändert und ist eingehalten. Innerhalb des tatsächlichen Monitorfensters sind57 gesundheitskorrelierte Todes-/Folgegeneration-Respawns belegt (34+23), ohne überschrittene deklarierte Respawnfrist; das ist kein100er-Gate. Geordnete gleiches-Leben-Pickup-/Auswahl-/Current-/Inputketten auf dieser Karte fehlen weiterhin für Flamer/Cannon. Ein Current-Feld allein beweist insbesondere kein Ende der nativen BringUp-Animation.

Sechs überprüfte Beispielketten zeigen nach akzeptierter Luftsteuerung im selben Leben echte Positionsänderung und anschließende autonome NAV-Wiederaufnahme mit `nav=1`, `vis=0`, `target=-1` und unverändertem Schusszähler. Gegenbeispiele und unzureichende Fälle bleiben ebenfalls ausgewiesen. Die1Hz-Messung trennt nicht jede Zwischenaktion oder geerbte Geschwindigkeit; der Bericht behauptet keine alleinige physikalische Verursachung aus einem Logtag.

Getrennt davon bleibt BotA:0 während203s innerhalb des Monitorfensters beziehungsweise207s im vollständigen Rohlog einschließlich4s normalem Cleanup-Nachlauf auf demselben gültigen ursprünglichen gerichteten Edge ohne Annäherung an den Hop: etwa441,6m aufaddierter Messpunktweg im vollständigen Rohlog innerhalb einer kleinen Positionsbox, wiederkehrende Ausweichaktionen, unveränderter Ziel-/Hopkontext und Schusszähler. Der abschließende90s-Abschnitt im Monitorfenster (94s einschließlich Nachlauf) wiederholt sogar exakt drei Messpositionen. Die Hopdistanz bleibt ungefähr39,1–39,8m; die ursprüngliche Höhendifferenz liegt bei35m. Das ist tatsächliche Bewegung und kein nachträglich umetikettierter numerischer Stillstandsfehler, aber eine reale funktionale Wegpunktschleife. Nativer Zustand ist STAND; `immersion=1` bedeutet hier kein SWIM, und `floor=2` ist der SafeMotion-Escape-Status, kein NoFloor-Befund. Der konkrete Wandablehnungsgrund ist in diesen erfolgreichen Escape-Zeilen nicht protokolliert. Aus der ursprünglichen Kante allein wird weder ein Jumppad noch dessen Triggeridentität behauptet.

Die Integration hält eine einmal gebundene Kante auch bei periodischer Neuberechnung fest, während tatsächliche0,75m-Weltbewegung den bisherigen Fortschrittsdetektor zurücksetzt. Der Original-Cecil-Pfad prüft alle5s erneut den nächsten Anker. Diesen belegten Unterschied untersucht der nächste eng begrenzte Fix, unter Erhalt echter Flug-/Liftbindungen, Originalradien, Locks und Zielfristen. Keine formalen Stunden oder öffentliche Installation vor Klärung. Main-Verdict-SHA256 `738e1055589054684b44b7a8dbafd6fe7e47ed971339cbc18f73e502b813182f`; unabhängiger vollständiger Rohreview `45c931155087342768ae27d5c9e5a32b91e447caea8788373f710b87b8f0f338`.

## Versorgungv17: begrenztes Gate mit erhaltenem Cannon-Fehler bestanden

Zehn prospektive frische Einzelbotfälle ergeben605 korrekte Ein-Bot-Abfragen, zehn unterschiedliche PID-/Kernelstart-Kontexte und zehn feste Initialleben ohne Tod/Ersatzspawn. Von den unverändert festen ersten zehn Waffenzielen sind9 korroboriert. Rang3 in Fall1, Cannon, endet nach tatsächlicher einmaliger Relokationsbudgetierung nativ mit Timeout ohne passendes Besitzbit. Er bleibt ein Fehler und wird durch keinen späteren Erfolg ersetzt.

Die Initialleben benötigen9,55/9,65/9,65/3,00/2,55/3,15/2,60/3,90/9,90/12,90s bis zum ersten sinnvollen Pickup: Median6,725s/P9512,90s, innerhalb der vorab festgelegten15s-/30s-Grenzen. Die geforderten9/10 sind erreicht; alle Grenzen und das feste Kollektiv bleiben unverändert.

Alle30 tatsächlichen Starts bleiben ausgewiesen:28 mit passendem typisiertem Waffenbit am gleichen nativen Zielendtick, ein Timeout, ein späteres rechtszensiertes Cannon-Ziel auf Rang20/Fall7 ohne beobachtetes Ende. Keine nachträgliche Auswahl oder Censor-Erfolgswertung. Main und unabhängiger Review prüfen vollständige Rohdaten, typisierte Entity/Weapon-Zuordnung und gleiches-Leben-Trajektorie. Erhöhte Cannon-/Flamer-Pickup-Ursprünge bleiben als native Beobachtung erhalten, ohne allgemeinen2,5m-Pickupradius oder ReceiveItem-Hook zu behaupten; `goal_picked=0` ist kein Alleinbeweis.

Alle633 nativen Zustandsproben haben kein sichtbares Gegnerziel. Elf normale eigene PID-/Start-gebundene Abschlüsse, zehn echte Leerslotantworten, zehn Renderer-Cleanup-Marker und17 unveränderte Original-/Konfigurationspins sind überprüft; Bot-Exitstatus1 bleibt erhalten. Begrenzter Supply-Verdict-SHA256 `b9d1ac961c65d6f478d959ed9fffb54a6c9dfedba3f249bdf53cf26610ff239d`; unabhängiger Review `40ef7a1f4c85e504ea69583aff97a24aed428823d29262c200f945b9581799aa`. Gesamtkandidat weiterhin `qualified=false`.

## Weitere getrennte Beobachtungen

### Hole600: begrenzte Funktionsbeobachtung bestanden

600,009415375s/595 Abfragen, vollständige Abdeckung, keine erkannten neuen Monitorfehler, maximal3,016412s unbegründeter Stillstand. Alle acht zeigen positive Scoreänderungen. Das bedeutet ausdrücklich nicht acht positive Nettoscores: Dev7 endet nach zwei positiven und drei negativen Änderungen bei−1. Alle drei eigenen Prozesse schließen normal.

77 native Todesereignisse und76 gesundheitskorrelierte Folgegeneration-Respawnpaare liegen im tatsächlichen Monitorfenster. Ein weiterer A0-Spawn ist erst im normalen Rohlog-Nachlauf vorhanden und erhält keinen Monitorpaar-Kredit. Zusammen mit Skulls sind133 unterschiedliche gültige Paare desselben DLL-Hashes über getrennte PID-/Start-/Kartenkontexte belegt; kein Paar wird doppelt gezählt oder einem künftigen DLL-Hash übertragen. Die vollständige Karten-/Sonderaktions-/Waffenqualifikation bleibt offen. Begrenzter Hole-Verdict-SHA256 `5f2edd3ec7f4f8286e8733d274ba08091fd7d694dbcb541b17f680a846479070`, unabhängiger Rohreview `6dc4c22c946dd128ac9286031b0661615e487e09c7fcb97141bc70465cb97651`.

### Original-Retail/Wine: tatsächlicher Join und Gameplay beobachtet

Der unveränderte Retail1.07-Client nimmt120,184946294s an der eigenen isolierten Zwei-Spieler-Session teil:107 vollständige korrekte Roster-/Map-/Port-/Versionsabfragen, fünf tatsächlich PID-/Fenster-gebundene reguläre Eingaben und keine erkannten neuen Fehler. Main und unabhängiger Review betrachten die tatsächlichen direkt benachbarten First-Person-Bilder vor/nach normalem3s-Vorwärtseingang: sichtbare Szenen-/gerundete HUD-Positionsänderung, beide Bilder Gesundheit100 und beide Scores0/0. Vor-/Nachabfragen begrenzen dasselbe Bewegungsfenster ebenfalls mit0/0. Aus gerundeten HUD-Koordinaten wird keine genaue Meterdistanz behauptet.

Später im120s-Gesamtlauf stehen zwei Cannon-Todesereignisse des Originalclients im nativen Feed und getrennte Bot-Scoreänderungen. Das gesamte Fenster ist ausdrücklich nicht todesfrei. Alle vier eigenen Prozesse inklusive Originalclient und privatem Display schließen normal, Cgroups sind leer und alle vier Originaldateihashes unverändert. Begrenzter Retail-Verdict-SHA256 `ea5b211ec0ff8af2d504363628adb0021b1d33cc98dc0a9c4ce2b99314b53450`, unabhängiger Review `3c6045ae80d20f4cb178497e4a31b822645fe7967571ae4f3f4727049b774f8f`. Dieser Beleg gilt nur für Original-Retail unter Wine/Xvfb, nicht für native Windows-/GPU-/WAN-Abnahme oder Gesamtqualifikation.

Die tatsächlichen zusätzlichen Preflights für Skulls/Hole bestanden jeweils vor dem zugehörigen Start mit289 Dateipins. Nach vollständigem normalem Ende bestätigt ein neuer ausdrücklich als POST_RUN markierter289-Dateien-Snapshot nur die erklärte Skulls→Hole-Kartenwahl und ansonsten unveränderte Dateien; er ist ausschließlich Grundlage künftiger Stagingprüfungen. Die frühere043-Zusatzprüfungsfehlbedienung bleibt im Vorgängerbericht erhalten und wird nicht rückwirkend korrigiert. Die sechs öffentlichen Instanzen laufen unverändert; keine043/044-DLL ist dort installiert.

Alle übrigen Karten-/Waffen-/Sonderaktions-/3600/3600/7200s-/Ressourcen-/Rotations-/Recovery-Gates, der autorisierte All6-Rollout mit900s-Flottenprüfung und die reguläre Integration bleiben offen. Die Transfermatrix bleibt bis tatsächlicher vollständiger Neubindung039-Snapshot. Nach jeder Verhaltensänderung ist neue native Evidenz des neuen DLL-Hashes erforderlich.
