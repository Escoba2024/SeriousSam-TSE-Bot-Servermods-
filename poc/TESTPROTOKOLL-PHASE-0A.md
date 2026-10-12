# Testprotokoll – Phase 0A: Vanilla-Netzwerk-Baseline

**Datum:** ____________  **Tester:** ____________  **Server-Version:** 1.07 (Build 10000.7) ☐ verifiziert
**Server-IP:Port:** ____________________  **Map:** ____________________  **Spielmodus:** Fragmatch ☐ / sonst: ______

> Zweck: Testumgebung beweisen (noch **kein** Bot). Alle Zellen „Ergebnis/Notiz“ ausfüllen, Server-Log (`Dedicated_*.log`) und ggf. Wireshark-Pcap beilegen.

| # | Prüfung | Erwartung | Ergebnis (PASS/FAIL) | Notiz / Beweis |
|---|---|---|---|---|
| 1 | Server startet reproduzierbar | Konsolenfenster/„ALL OK: Dedicated server is now running!“ | | |
| 2 | Observer-Join ohne Mod/Fehler | Lädt Map, keine Downloads, keine MOD:-Meldung | | |
| 3 | Playerliste/Scoreboard | Observer erscheint mit Name | | |
| 4 | Bewegung | flüssig, synchron | | |
| 5 | Schießen | Projektilwahl/Sounds sichtbar | | |
| 6 | Schaden/Frag/Respawn | gegen 2. Client oder Selbstschaden; Frags zählen, Respawn funktioniert | | |
| 7 | Mapwechsel | Server wechselt Map, Clients folgen | | |
| 8 | Disconnect/Reconnect | sauber, Spieler erscheint wieder (ggf. Score-Reset je nach Regeln) | | |
| 9 | Server-Log vollständig | Join/Leave/Aktionen nachvollziehbar | | |
| 10 | 15+ min Stabilität | kein Kick, kein Desync, kein Crash | | |

**Ergebnis Phase 0A:** ☐ GATE BESTANDEN → Phase 1 starten  ☐ FAIL → Ursache & Wiederholung:

________________________________________________________________

**Notizen/Randbeobachtungen (z. B. Server-Reset-Verhalten bei Leerstand, `ded_bRestartWhenEmpty`):**

________________________________________________________________
