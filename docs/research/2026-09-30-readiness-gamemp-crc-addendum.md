# Readiness-/PoC-Addendum – GameMP-only, CRC und verbleibende Gates

Dieses Addendum ergänzt die Design-Spezifikation vom 30.09.2026. Bei Widerspruch hinsichtlich des **ersten Bot-Client-Eingriffspunkts** gilt für den aktuellen PoC der hier beschriebene Stand.

## BESTÄTIGT

- Der CRC-Pfad nimmt `Classes\\Player.ecl`, die zugehörige Entity-Class-DLL (`EntitiesMP.dll`) sowie geladene relevante Spieldaten in die Prüfung auf. Bei CRC-Abweichung trennt der Server die Verbindung.
- `GameMP.dll` ist nicht Teil dieser CRC-Liste.
- `SeriousSam.exe` lädt die Game-DLL separat über `LoadLibraryA` und den Export `GAME_Create`.
- Der normale lokale Action-Pfad liegt in `CGame::GameHandleTimer`: `CControls::CreateAction(...)` → `CPlayerSource::SetAction(paAction)`.
- `NET_MAXLOCALPLAYERS = 4`; der Server verarbeitet pro Client höchstens vier lokale Action-Slots.
- 1.07 und 1.10 haben unterschiedliche Netzwerk-Build-Versionen; der Server prüft Major/Minor beim Connect.
- Der vorbereitete BotDriver-PoC ist GameMP-only und die isolierten `botcore`-Tests bestehen.

## Konsequenz für Phase 0/1

**Primärer Erstweg ist jetzt GameMP-only.**

Bot-Testaufbau:
1. unveränderter TSE-1.07 Dedicated Server,
2. separater TSE-1.07 Bot-Client mit ausschließlich getauschter `GameMP.dll`,
3. vollständig unveränderter TSE-1.07 Observer-Client.

Der frühere Plan, zuerst die Exporttabelle der Retail-`EntitiesMP.dll` für einen `ctl_ComposeActionPacket`-Hook zu untersuchen, ist für den Primärpfad nicht mehr erforderlich. Ein EntitiesMP-/Binary-Hook bleibt nur Fallback, falls der 1.07-GameMP-Build praktisch scheitert.

## Implementierungskritische Action-Semantik

- `pa_vTranslation` ist Geschwindigkeit; vorwärts entspricht negativer Z-Richtung.
- `pa_aRotation` und `pa_aViewRotation` sind absolut akkumulierte Winkel; nicht auf ±180° wrappen.
- Game-Tick: 20 Hz.
- `CPlayerSource::SetAction` setzt `pa_llCreated` selbst.
- Vanilla-Clamps begrenzen Translation/Tempo.
- Periodisches Fire kann nach Tod den normalen Respawn-Pfad auslösen.

## OFFEN / noch zu testen

- echter 1.07-ModSDK-GameMP-Build und ABI gegen Retail/Steam-Binary,
- Runtime-Beweis: GameMP-only joint, EntitiesMP-Abweichung scheitert wie erwartet am CRC-Gate,
- 60-Minuten-Sync ohne `MSG_SYNCCHECK`-Kick,
- Schaden/Frag/Respawn,
- Mapwechsel und Reconnect,
- 2–4 lokale Spieler und eindeutige GUID/Profile,
- Live-Query/333networks,
- Ressourcenlast bei mehreren Bot-Client-Prozessen,
- Serververhalten bei ausschließlich Bot-Clients.

## Architekturstatus

Pfad D bleibt Primärpfad. B2 bleibt Fallback. CecilBotMod bleibt KI-/Navigationsreferenz, nicht Netzwerkarchitektur. End-to-End-Vanilla-Kompatibilität ist erst nach dem echten 1.07-Runtime-PoC bestätigt.
