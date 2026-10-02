# Serious Sam TSE 1.07 – Vanilla Bot Clients

Ziel dieses Repositories ist ein Bot-System für **Serious Sam: The Second Encounter v1.07**, bei dem der Dedicated Server und menschliche Spieler unverändert bleiben. Bots joinen über separate modifizierte Bot-Client-Prozesse als reguläre Netzwerkspieler und erzeugen ihre Eingaben ausschließlich über die normale `CPlayerAction`-/`CPlayerSource::SetAction`-Pipeline.

## Verbindliche Architektur

- Primärpfad: separater Bot-Client mit GameMP-only-Anpassung.
- Dedicated Server, `EntitiesMP.dll`, Engine und Vanilla-Observer bleiben unverändert.
- CecilBotMod ist Referenz für spätere KI-/Navigationslogik, nicht der produktive Netzwerkspieler-Pfad.
- Maximal vier lokale Spieler pro normalem Client-Prozess; Multiprocess-Skalierung ist eine spätere Phase.
- Vanilla-Kompatibilität, CRC/Join und Synchronität sind harte Runtime-Gates.

Die verbindliche Designspezifikation liegt unter:
`docs/superpowers/specs/2026-09-30-vanilla-server-bots-design.md`.

## Aktueller bestätigter Runtime-Stand

Der Windows-/Retail-PoC läuft gegen echte TSE-1.07-Retail-Binaries. Bestätigt sind derzeit:

- reproduzierbarer x86-`GameMP.dll`-Build mit Engine-Allocator-Anbindung;
- echter CRC-/Joinpfad gegen unveränderten Dedicated Server;
- unveränderter Vanilla-Observer gleichzeitig verbunden;
- native Bewegung, Rotation und Fire-Actions über den normalen Action-Composer;
- realer Schaden und Frag des Bots gegen den Vanilla-Observer;
- vier Bot-Death-/Respawn-Zyklen mit fortgesetzten Actions danach;
- zwei Session-/Mapwechsel mit kontrolliertem Reconnect und erneuter CRC-/Join-Abnahme;
- regulärer Shutdown von Bot, Observer und Dedicated Server.

**Phase 1: BESTANDEN.** Gates A–E sind für den Ein-Bot-Pfad bestätigt, einschließlich aktiver 10-/30-/60-Minuten-Sync-Prüfungen und einer unabhängigen 60-Minuten-Wiederholung. Ressourcen, Restore, Crashdiagnostik und DLL-Hashes sind dokumentiert.

## Nächste Phase

Phase 2 – **2 bis 4 lokale Bots pro BotClient-Prozess**. Zuerst zwei eigene Spielerprofile und native Split-Screen-/Join-Konfiguration prüfen; danach Slot-/GUID-Eindeutigkeit, Aktionen aller Bots und Sync. Phase 2 ist noch nicht abgenommen. Kontrollierter Reconnect nach Mapwechsel ist belegt; nahtloses Autoreconnect bleibt nicht belegt.

## Einstieg für Entwickler / KI

1. `CODEX_WINDOWS_POC_REPORT.md` – aktuelle Runtime-Evidenz, Buildpfad, Hashes, Tests und offene Gates.
2. `docs/superpowers/specs/2026-09-30-vanilla-server-bots-design.md` – Architektur und Phasenmodell.
3. `poc/RUNBOOK.md` – reproduzierbarer Build-/Testablauf.
4. `poc/VERIFIKATION.md` – Quellcode- und Protokollverifikation.
5. `poc/patch/gamemp/` – GameMP-seitiger BotDriver und Retail-Allocator.
6. `poc/scripts/` – Build-, Runtime-, Telemetrie- und Lifecycle-Tests.

Lokale Retail-Kopien, Buildprodukte, Screenshots/TGAs und Runtime-Evidenz unter `.codex/` gehören nicht ins Repository.

## Aktueller nächster Meilenstein

Phase 2 mit zwei lokalen Bots beginnen, anschließend auf drei/vier erweitern und separat abnehmen. Aktuelle Phase-1-Evidenz im technischen Bericht und Testprotokoll.
