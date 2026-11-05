# SSAM.AI – Generation-2-Kampfkorrektur (5. November 2026)

## Ziel / Arbeitsschutz
Kleiner Combat-Fix auf der verifiziert laufenden Retail-1.07-Generation 2, ohne Änderung am DedicatedServer oder Vanilla-Client. Isolierter Worktree `ssam-gen2-combat-20261105` und Branch `agent/chat/20261105-gen2-combat`. Keine fremden Arbeitsstände überschrieben.

## Umsetzung und Abnahmekriterien
- [x] Gen2-Live-Version anhand A/B-DLL-SHA und vorherigem 600-s-Live-Smoke ermittelt.
- [x] Colt-Fire auf <=18 m begrenzt, Colt-Anlaufdistanz bis 3 m; andere Waffen und Nahkampf unberührt.
- [x] C++-Testkampflogik: 0 Fehler; BotCore-AI: PASS; Human-AI: 555 Checks/0 Fehler; Hindernisnavigation: PASS.
- [x] Exakter Gen2-Sourcevergleich: 38/38 Quellen geprüft, einzige Abweichung `bot_combat.h`.
- [x] MSVC/Wine x86 Retail-1.07 neu gebaut: `e8152fae2c62dc2da81a0c0ad7fcf7ebeec431da63de69f0c1d2a748c3498a55`, privater Build-003, Manifest `build_ok=true` / `qualified=false`.
- [x] Backup beider vorhandener GameMP.dll mit verifiziertem Hash, transaktional gesicherter BotB-Canary.
- [x] BotB-Canary fehlgeschlagen und automatischer Rollback ausgeführt. Konkreter Joinfehler: `Player character ... already exists in this session`; nach 110 s keine vier neuen Bots mit dem Kandidaten.
- [x] Beide produktiven DLLs nach Rollback wieder Gen2-Hash `7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835`.
- [x] Öffentlicher Gameserver und BotA/B Services wieder aktiv; 8 Botnamen durch Client-Logs abgeglichen (GameSpy 2026-11-05T21:57:09Z). Vier neu verbundene BotB-Spieler steigerten Frag-Scores; Kampf-/Bewegungslogs.
- [ ] Ursache für Identitätskonflikt im laufenden Server reproduzierbar bestimmen und beheben.
- [ ] Neue DLL in echtem Retail-Wine-Gameplay inkl. Respawn, Bewegung, Waffenwahl und Sync erfolgreich abnehmen.
- [ ] Erfolgreiche Live-Canary 5–10 min, dann kontrollierte A/B-Produktion; bis dahin **nicht ausrollen**.
- [ ] Langzeit-M1-Gates und zuverlässige Auto-Recovery gesondert nachweisen.

## Entscheidungen
Bestehender nativer Isolations-Runner verlangt `no_game_processes()` und kann nicht neben den laufenden öffentlichen Clients/Servern eingesetzt werden. Kein Umgehen dieses Hostsicherheits-Gates. Der kontrollierte BotB-Live-Canary wurde anhand 8 exakt nachgewiesener Botnamen ohne fremde Spieler gestartet, schlug beim Rejoin fehl, beide DLLs wurden zurückgerollt und der reale Acht-Bot-Betrieb geprüft. Keine neuen Live-Gameplay-Verbesserungen als bestätigt ausgeben.

## Artifacts
- Branch-Implementierung `8b07e88`
- Privater Kandidat: `/srv/tse-gen2-combat-20261105/build-003/Sources/Game/GameMP.dll`.
- Rollback/Canary-Belege: `/srv/tse-gen2-combat-20261105/release-colt-20261105/`.
- Öffentlicher Server: `91.99.75.33:25600`, Red Station.
- Nächste Iteration: Identitäts-/Session-Join-Semantik testen, dann abgesicherten Canary wiederholen.
