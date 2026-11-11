# Selektive Power-up-Entfernung: isolierter Dev-Test vom 11.11.2026

## Auftrag und Abgrenzung

Explizit genehmigte Dev-Ausnahme: Serious Damage und Unsichtbarkeit vorübergehend serverseitig entfernen, Cecil048 und individuelle Farbnamen erhalten. Die fünf Produktionsserver und der gesicherte Rollout sind geschützt. Dieser Bericht qualifiziert keine neue Bot-DLL und keinen allgemeinen Produktionsrelease.

## Implementierung und Provenienz

`tools/build_dev_powerup_gamemp.py` erzeugt einen getrennten Server-Overlay. Der neue Schalter `dev_bRemoveDamageAndInvisibility` ist standardmäßig 0. Bei explizitem Wert 1 entfernt der ausschließlich im autoritativen `CGame::NewGame` aufgerufene Filter bestehende `PowerUp Item`-Entitäten mit Retail-Typ 0 oder 2. Client-Join und Demo-Wiedergabe führen keine Mutation aus. Vor jedem `Destroy()` wird der Container-Iterator freigegeben; danach wird neu gesucht. Andere und unbekannte Typen bleiben erhalten. Die Zählungen vor/nach dem Eingriff werden protokolliert. Erfasst sind neue Dedicated-Sessions und der getestete erneute Start; generischer dynamischer Coop-Levelwechsel oder später per Spawner erzeugte Items werden nicht zugesichert.

- Tatsächlich gebauter lokaler Quellcommit: `4046a59c419d1a3a6323b8516f20cc5bfddf5203`.
- Vollständiger Quell-Tree: `ca088e12060689d531c4ddc1d909dfa635e802e3`.
- Veröffentlichter Spiegel derselben vollständigen Quellbytes: `df9a637d8a1dfc0952808430870728f44e385462`, exakt derselbe Tree. Commit-Metadaten unterscheiden sich; nicht als identische Commits ausgegeben.
- Server-DLL: `fe4a77bd1eae15a25cfeb67cf5dfdd6643cba59661f2ca3e99467a9fb15b06e0`.
- Buildmanifest-SHA256: `b3bbd208089a41271a518142de707429732c860761e8a2c4188efdc107b0bb7f`.
- MSVC/Wine-Build: 15 tatsächliche Übersetzungseinheiten, Retail-1.07-SDK und Engine107/EntitiesV-Bindungen, PE32/x86. Ursprüngliche Cecil048-Quellen und DLL-Artefakte wurden nicht überschrieben.
- Unveränderte Cecil048-Client-DLL: `ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530`.
- Original-Engine: `b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f`; Original-Entities: `7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350`.

Die historische Rockets-Forever-Fassung wurde nicht ausgeführt. Die eigene Variante benötigt keine veränderte Entities-DLL und verändert keine Karten- oder NAV-Dateien. Die originale Dedicated-EXE bleibt unverändert; allein GameMP ist die ausdrücklich genehmigte Servermod-Ausnahme.

## Prüfungen

Portable Selektionsfälle: aktiv/inaktiv, Client/Server, Demo, Nicht-Power-ups, Typen -2 bis 8. Der Test wurde zunächst rot beobachtet. Die tatsächliche Filterfunktion wurde zusätzlich mit einem mutationsprüfenden Container ausgeführt: mehrere Ziele, Typen 1/3/4/unbekannt, leere Welt, Idempotenz und Freigabe des Iterators vor Löschung bestanden. Die vorhandene Botcore-Suite sowie abschließend 176 Python-Tests bestanden.

Unabhängige statische Prüfung fand keine kritischen oder wichtigen Fehler. Der einzige Hinweis betraf eine künftig mögliche Verlagerung des Build-Hooks durch geänderte Quellformatierung. Der zusätzliche Regressionstest wurde rot/grün durchgeführt und eine Positionsprüfung auf `NewGame` ergänzt. Der gehärtete Builder erzeugt nach vollständigem Hashvergleich genau denselben Overlay wie der gebaute Kandidat; es wurde dafür keine neue DLL gebaut.

Der erste isolierte Harness-Versuch deaktivierte GameSpy und bekam deshalb keine Statusantworten. Der Server hatte die Welt und die unveränderte Kontrollzählung geladen. Der Versuch endete normal; Fehlerbericht und Log bleiben erhalten. Im zweiten Versuch ist GameSpy ausschließlich im getrennten, routenlosen Netzwerk-Namespace eingeschaltet.

| Tatsächlich beobachteter Lauf | Ergebnis |
| --- | --- |
| Default-off, originale Red Station | vor/nach: Invisibility 1, Damage 1 |
| Explizit aktivierter Filter | vorher 1/1, entfernt 2, danach 0/0 |
| Original-Retail-Preflight zweimal unmittelbar vor Start | vier Originaldateien verifiziert, keine Belegung, frische exakte Ein-Bot-Antwort, `canStart=true` |
| Original Retail + ein Cecil048-Bot | 120,897657 s, 116 gültige Abfragen, Population 2 |
| Acht unveränderte Cecil048-Bots | 180,238088 s, 172 gültige Abfragen, Population 8 |
| Erneuter Serverstart mit aktiviertem Schalter | wieder vorher 1/1, danach 0/0 |
| Cleanup | ausschließlich eigene PID/Start-gebundene normale Fenster-Schließung beziehungsweise SIGINT, keine Force-Fallbacks, leere eigene Cgroups |

Geladene GameMP-Inodes und Datei-Hashes wurden pro eigenem Prozess geprüft. Die vier Original-Retail-Komponenten blieben erhalten; der Originalclient meldet einen Join und ist in einem privaten Screenshot tatsächlich in Red Station sichtbar. Normale Bewegungs-/Schusseingaben wurden PID-gebunden gesendet. Alle acht Bots zeigen Positionsänderungen und Schüsse, sieben von acht positive Scoreänderungen; ein Bot bleibt ohne positive Scoreänderung. Dies ist kein formaler Acht-Bot-Aktivitäts- oder Funktions-Gate-PASS. In den beobachteten Laufzeitfenstern wurden keine SYNCBAD-, Bad-Sync-Disconnect-, CRC- oder Joinfehler gefunden. Andere Power-up-Typen sind auf dieser Karte nicht vorhanden; deren Erhaltung ist hier durch portable Tests, nicht durch native Kartenfälle belegt.

Native Ergebnisdatei-SHA256: `b7c661244fdf43e5474aed698f079acfc20bb4364cd25f65e55cd95af27a3e25`. Rohlogs, Bildschirmaufnahme, Profile, Binärdateien und Spieldaten bleiben privat. Ergebnis: `PASS_LIMITED_WINE_SERVERMOD_RETAIL_AND_CECIL048`, `qualified=false`. Keine native Windows-, WAN-, Stunden-, Rotations- oder 24/7-Abnahme. Die ursprünglichen Cecil048-Qualifikationspflichten bleiben unverändert.

## Öffentlicher Stand und Sicherung

Am 11.11.2026 um 18:18 UTC waren alle sechs öffentlichen Prozessidentitäten und geprüften Binär-/Konfigurationspins gegenüber dem Beginn unverändert. Dev enthält acht eigene Bots plus einen zusätzlichen menschlichen Spieler; deshalb wurde vor jeglichem Live-Prozessstopp angehalten. **Die beiden Power-ups bleiben live aktiv.** Es gibt keinen unbeaufsichtigten Rollout-Auftrag. Der vorbereitete Wechsel prüft erneut Belegung und exklusive Flotten-/Runtime-Locks.

Private zusätzliche Sicherung `20261111T181858Z-dev-selective-powerups-prepared`: Kandidat, tatsächliches Manifest, verifiziertes Git-Bundle, isolierte Belege, unabhängiger Review und aktuelle originale Server-DLL/Konfiguration als Rückweg. 31 Dateien wurden nach dem Kopieren vollständig nachgehasht. Die vollständige Cecil048-Sicherung und das separate Farbnamen-Delta bleiben unberührt. Ein tatsächlicher Restore ist nicht getestet.
