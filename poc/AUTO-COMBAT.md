# Optional automatische Kampfsteuerung – lokaler Meilenstein 10.10.2026

Die neue GameMP-Erweiterung verbindet die vorhandenen Botcore-Helfer mit
replizierten Spielern, nativer Sichtprüfung und der normalen Action-Pipeline.
Dedicated Server, Engine, EntitiesMP und menschliche Clients bleiben original.
Die vorherige lokale Stundenabnahme gehört weiterhin ihrer Recovery-DLL
`24053920C63E02F9883056331B246BEF2D08D645FFCCE2C74ED7EDC9B35B9ACF`.

## Verhalten

`bot_bAutoCombat` ist standardmäßig aus. Bei aktiviertem Botbetrieb und
automatischem Kampf wählt jeder lebende Bot den nächsten sichtbaren lebenden
Gegner. Eigene lokale Bots sind durch `bot_bCombatSkipLocals = 1` standardmäßig
ausgeschlossen. Automatischer Kampf ist auf Scorematch und Fragmatch begrenzt;
ein gesetztes `bot_iTestTarget` hat weiterhin Vorrang als bisheriger Testmodus.

Augenpositionen und Gesundheit stammen aus replizierten Spielern. Der
Engine107-`CCastRay` prüft die Strecke zum Gegner. Die reine Entscheidungslogik
erhält ausschließlich sichtbare Kandidaten. Sie begrenzt die Zielkorrektur,
pausiert Vorwärtsbewegung bis zur Ausrichtung und stoppt vor nahen Gegnern.
Ohne sichtbaren Gegner bleibt die bisherige Suchbewegung aktiv. Eine Wand
wird dadurch noch nicht automatisch umgangen.

Die vorhandene Entfernungstabelle wählt eine verfügbare Waffe. Leere
Munitionsvorräte werden ausgeschlossen; die Doppelflinte benötigt zwei
Patronen. Ein leerer Colt kann nativ nachgeladen werden. Waffen-IDs 1–14 sind
von den nativen Auswahlgruppen 1–8 zu unterscheiden: `CombatWeaponInput`
sendet vollständige Gruppenimpulse, wartet auf Loslassen und native Rückmeldung
und kann die alternative Waffe derselben Gruppe wählen. Der ältere rohe
`WeaponSelectButtons`-Helfer ist kein solcher Protokolladapter und wird hier
nicht verwendet. Schießen beginnt erst, wenn aktuelle und gewünschte native
Waffe mit der Entscheidung übereinstimmen.

Tote Bots greifen nicht an und verfolgen niemanden. Ein separater normaler
Fire-Press/Release-Impuls bedient den Retail-Respawn. Nach dem Respawn wird das
Ziel anhand frischer Daten neu gewählt. Alle Bewegungs-, Waffen-, Feuer- und
Respawn-Eingaben laufen durch `ctl_ComposeActionPacket` und `SetAction`.

## Einschalten und bauen

Für reguläre Bots die Symbole im eigenen BotClient setzen:

```text
bot_bEnabled = 1;
bot_bAutoCombat = 1;
bot_bCombatSkipLocals = 1;
bot_iTestTarget = -1;
```

`poc/scripts/Phase1AutoCombat.ini` ist ausdrücklich die QA-Konfiguration mit
zugelassenen lokalen Gegnern und dichter Telemetrie. Für normale Verwendung
die Ausschluss-Einstellung oben verwenden und Diagnostik reduzieren.

Der lokale reproduzierbare Aufbau setzt den erhaltenen abgenommenen Build
voraus. Er erstellt ein neues Verzeichnis und prüft dessen Ausgangs-DLL:

```powershell
./poc/scripts/Build-CombatGameMP.ps1 -BaseBuild .codex/shadow-20261010-reconnect-final -BuildDir .codex/combat-repeat-build
```

Der inkrementelle Patch `poc/patch/0004-gamemp-auto-combat.patch` setzt auf der
Treiberquelle nach Patch 0003 auf. Neue reine Header befinden sich unter
`poc/botcore/`. Nur GameMP wird als Win32/Release_TSE107 gebaut. Ein Build an
einem anderen Pfad kann wegen Buildmetadaten einen anderen DLL-Hash haben;
die Quellgleichheit wurde beim zweiten Aufbau geprüft.

## Frische Prüfungen

| Prüfung | Ergebnis |
|---|---|
| Fünf reine Core-Testprogramme, darunter Kampf- und Auswahlprotokoll | PASS; RED/GREEN für fehlende Funktion, Ein-Patronen-Fall, Gruppenimpulse und volle Auswahlmaske |
| Separater x86-Build und erneuter Aufbau aus Patch/Buildskript | PASS; neun relevante Quelldateien stimmen bytegleich überein |
| Zwei automatische Bots + Vanilla-Beobachter auf DM_LittleTrouble | 180,1372725 s, CRC 2, je 3388 Snapshots, sechs beobachtete Kills |
| Tod, nativer Respawn, erneute Zielaufnahme | Vier Zyklen für Bot 0, einer für Bot 1; PASS |
| Native Waffenauswahl | Zwei Colt-Gruppenimpulse repliziert und zur gewünschten Waffe abgeschlossen |
| Vier Bots im bisherigen Modus auf Fortress | 60,175512 s, CRC 2, je 929 Snapshots; Bewegung, Rotation, Fire-on/off; PASS |
| Deklarierte Standard-Einstellung zum Ausschluss lokaler Bots | 60,1082366 s, CRC 2; keine lokalen Ziele; PASS |
| Eigenständiger Combat-Auditor und sechs Positiv-/Negativ-Fixtures | PASS |
| Wiederherstellung | 30 Originalbinaries, 815 globale Dateizustände, ursprüngliche drei Quellhashes; 0 Prozesse/Ports/Crashs |

Native Kandidaten-DLL:
`28A32C6401928717FE8AA5619E490DE8A8CEB8713116368914D5CBBCEC646615`,
unter `.codex/shadow-20261010-ai-combat/Sources/Bin/vs2022.Release_TSE107/`.
Rohbelege und vollständiger Bericht:
`.codex/evidence/shadow-20261010/ai-combat/`.

## Grenzen und nächste Arbeit

Dieser Meilenstein bestätigt automatische Zielaufnahme, Kampf, Respawn und
den nativen Colt-Auswahladapter. Andere Auswahlgruppen und Munition sind in
reinen Tests geprüft; der finale native Kampflauf verwendet nur Gruppe 2.
Ein kontrollierter Wandtest, kooperativer Modus und native Tests aller
Waffenfamilien stehen noch aus. Die Sichtprüfung ist eingebaut, ihre komplette
Geometrieabdeckung wird damit nicht behauptet.

Navigation, Hindernisumgehung, Ausweichen und Item-Routen sind die nächste
Entwicklungsarbeit. Die Suchbewegung kann an Wänden stehen bleiben; im Lauf
gab es längere Abschnitte ohne sichtbares Ziel. CecilBotMod wurde als
GPLv2-Referenz unter Commit `953b477e53fdc5a5d84c8ae8d759c84fdf6c973c`
untersucht; dessen Entity-/Navmesh-System wurde nicht portiert.

Die neue DLL hat keine eigene Stunden-/Acht-Bot-Abnahme. Die kurzen Runner
verwenden harten Teardown und belegen keinen regulären Shutdown. Bestehende
Recovery-Quellen bleiben erhalten, aber die alten Runtime-Ergebnisse werden
nicht als neue Recovery-Abnahme ausgegeben. Externer Betrieb und dauerhafter
Supervisor bleiben separate Gates. Kein Commit, Push oder Drive-Sync.
