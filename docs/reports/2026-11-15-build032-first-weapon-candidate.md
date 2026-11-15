# Build032: atomischer Wechsel zur ersten brauchbaren Waffe

Build032 enthält gegenüber Build031 ausschließlich die geprüfte Korrektur in `BotSupplyNative.h`: ein gehaltenes gewöhnliches, nicht dringendes Health-/Armorziel darf die Suche nach der ersten brauchbaren Schusswaffe unter den dokumentierten Bedingungen freigeben. Das alte Ziel bleibt bis zur vollständigen Ersatzvalidierung erhalten. Erfolgreicher Wechsel protokolliert das Ende des alten Ziels vor dem neuen Versuch. Radien, Bewegungs-/Bodensicherheit, Raybudgets und bestehende Fristen bleiben gleich.

Die nativen Versorgungslücken aus Build031 bleiben offen. Ein erfolgreicher Build oder SDK-Test belegt keine Verbesserung im Retail-Spiel; Build032 ist noch nicht freigegeben oder live.

| Artefakt | Nachweis |
|---|---|
| Quellcommit | `1e0077a9b7c9c4696f10afdb3155d8d0cb911306` |
| Quellbaum | `2e1cbcb92ce777f30e228ee5bb82088598d9aabe` |
| DLL-SHA256 | `403fa89e6be18642cc5a699ced5cca484031eb310d56b211537f077995bdf3ce` |
| DLL-Größe | 463.360 Bytes |
| Buildmanifest-SHA256 | `e71f11802e83e5b1743597da48e4579cdb201ddc541fa968abb0be188877ddf6` |
| Build | 15 MSVC-Kompiliereinheiten und Link erfolgreich; Win32/Retail1.07-SDK |
| Vollständige Dateiprüfung | 49 Source-, 30 Overlay-, DLL- und Manifestpins: 81 passend |
| Änderung gegenüber031 | Nur `BotSupplyNative.h`, alle übrigen Source-/Overlaydateien identisch |
| Root-SDK-Gegenprüfung | 4.175 Prüfungen, 0 Fehler, Exit0 |
| Autor-Speicherprüfung | 4.141 ASan/UBSan-Prüfungen vor zusätzlichem Logmarker; unverändert getrennt ausgewiesen |

Die vollständige Headerinverse rekonstruiert Parent-SHA `0e7ee9d160afcca4c26b88169411d578a55d3fd82103be6fade1c95ca03381a3`. Der neue Header hat SHA `641334f6885e5c5d6517659374f0c32f933a01e5a78c4116f19193aa94b28bc8`. Root fand im engen Source-/SDK-Review keine offenen kritischen oder wichtigen Befunde. Grenzen des Welt-/Physicsstubs bleiben bestehen.

Nächster Nachweis: ein neuer isolierter Little-Trouble-Lauf unter derselben 600s/Hard2/8DEMON3/DIAG1/Original20FPS-Bedingung wie031, mit tatsächlich geladenem032-Modul, echten Zielwechsel-/Waffen-/Bewegungs-/Kampfbelegen, vollständigem Close und unabhängiger Wiederherstellungsprüfung. Kein automatischer Retry. Danach Versorgungslücken und Regressionen anhand vollständiger Slot-/Lebensnenner beurteilen. A offen, B nicht begonnen; Live-Mischstand bleibt erhalten.
