# GroundedReplan: überprüften Bodenhint trotz veraltetem Anker übernehmen

Der belegte portable Handshakefehler ist behoben: Die echte SDK107-Brücke
besteht **3440 Checks ohne Fehler**, normal und mit ASan/UBSan. Es ist ein
Quellkandidat für einen späteren Build; kein Retail-/Native-/A4-PASS und keine
Erklärung des konkreten Diagnostics1-Lebens. DLL, Runtime und Livebestand wurden
hier nicht verändert.

## Enger Produktionsdiff

Nur `BotCecilGroundedReplan` in `BotSupplyNative.h:1254` ändert sein Verhalten:
Der frische Kandidat muss nicht mehr mit dem veralteten `s.anchor` übereinstimmen.
Nach allen bisherigen Prüfungen und erfolgreicher gerichteter Suche wird
`s.anchor=candidate` unmittelbar vor dem bestehenden Navigatorreset gesetzt.
Der erfolgreiche Replan übernimmt damit einen aktuell gültigen Hint; er
behauptet keine Ankunft am Bodenpunkt.

Alle übrigen Guards bleiben bytegleich im Körper: tatsächlicher committed
Source/Hop, Blockmaske und Specials, laufende Interaktion/Use, Körperframe,
Welt, WorldBase-Support samt Entityidentität, ruhiger endlicher Kontakt,
Gravity/Höhe/Horizontalbereich, frischer LOS-Cast, aktuelle Blockierung und
Erreichbarkeit des unveränderten Ziels. Kein neuer persistenter Kontext entsteht.
Die gemeinsame Rayreserve, ursprüngliche Radien, Holdzeit, Item-/Avoiddeadlines
und nachfolgende SafeMotion bleiben unverändert.

Der Helper setzt weder `acquiredAnchor`/Zeit noch Reached-/Floorautorität.
Nach dem Reset sind aktuelle Navwerte gelöscht. Der nächste echte Navigatortick
muss den Bodenhint innerhalb seines ursprünglichen Radius tatsächlich
anlaufen, bevor ein neuer Edgefortschritt entstehen kann. In den frischen
Erfolgsfällen bleibt Item311 mit ursprünglicher Deadline12 erhalten; der
Helpercast braucht weiterhin genau einen Ray bei Budget16→15.

## Tests vor und nach der Quelländerung

| Stand | Checks / Fehler | Ergebnis |
|---|---:|---|
| Unveränderte Basis | 3274 / 2 | Vorhandener Handshake-RED erneut bestätigt |
| Zusätzliche Gegenfälle vor Produktion | 3431 / 5 | Nur neue Erfolgserwartungen rot |
| Erster Quellstand | 3435 / 1 | Alter Fall25 noch fälschlich als Veto erwartet |
| Fallnummerdiagnose | 3435 / 1 | Exakt Fall25, gültiger Alternativanker1 |
| Abschließend normal | 3440 / 0 | PASS, Exit0 |
| Abschließend ASan/UBSan | 3440 / 0 | PASS, Exit0, kein Sanitizerbefund |

Die neue Matrix prüft 31 Gegenfälle mit behaltenem hohen Anker69. Blockierte
Source-/Hop-/Kandidaten, echte physische Locks, Specials, fehlender gerichteter
Suffix, falsche Höhe/Horizontalposition, ungültiger Support, Velocity/State,
fehlendes Budget/LOS, Use/Interaktion, Navigator-/Ziel-/Weltverlust bleiben
Vetos. Gescheiterte Prüfungen ändern weder Anker noch Zieldeadline oder
vorhandene Navautorität. Die bisherigen Lebens-/Reset-/Deadline-/SafeMotion-
und Gravitykontrollen laufen weiter in derselben vollständigen Brücke.

Zwei alte Erwartungen waren ausdrücklich Proxys für die entfernte
Anker-Gleichheit und wurden nachvollziehbar umgestellt:

- Fall18 setzte allein den gehaltenen Anker auf die hohe Source. Das ist jetzt
  bei sonst gültigem frischem Bodenhint eine positive Kontrolle.
- Fall25 verschob nur Bodenpunkt0 aufY5. Bodenpunkt1 blieb innerhalb des
  ursprünglichen Nearest-Höhenbereichs und hatte weiterhin den gültigen
  Suffix1→2→3. Die instrumentierte Ausgabe belegte genau `case=25 anchor=1`.
  Dieser legitime Alternativhint bleibt positiv. Ein zusätzlicher Gegenfall
  verschiebt **alle** Bodenhints aufY5 und belegt das unveränderte Höhenveto.

Der zwischenzeitliche 3435/1-Lauf bleibt fehlgeschlagen archiviert. Keine
Produktionstoleranz oder Höhenprüfung wurde geändert, kein Fehler versteckt.

Zusätzlich liefen die zwölf bestehenden C++-Parentprogramme und vier gezielte
Python-/SDK-/Export-/Observerprüfungen seriell mit Exit0. Sie prüfen Aimtrace,
Arena/Rotation, Frames, Head/Body, Human, Integration, Itemretention, Motion,
Nav, Regeln und Supply sowie `test_cecil_action_native.py`,
`test_cecil_items_native.py`, `test_cecil_rules_exports.py` und
`test_supply_observer_native.py`. Exakte Commands/Outputs sind privat gespeichert.
Keine breite Discovery, keine parallelen Compiler oder neue Langzeitschleife.

## Reproduktion, Pins und Handoff

```sh
nice -n 15 python3 -B poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
nice -n 15 python3 -B poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es --sanitize
```

Eigener Worktree `/srv/tse-a4-grounded-acquire-fix-20261114`, Basis
`6d07a9b2123723071eaac760131be8e7ff11b2fa`.
Plan/Claim: `46ab037`; adversarialer RED: `783ee95`;
Produktionsfix und abschließende Guardkorrekturen:
`40691e6ad5aedd1e45e80148289ea7c0d1895654`.

Header-SHA256 `c32160c88777d9581c2649ff2db81e11f28cac73a43ca374fa48be47b0da5378`;
Test-SHA256 `5bee70ded0d2fe8705fdda71c87b9b7ecb37c59b7c95b17e2f89855657af42c1`.
`cecil_motion.h`, `cecil_rules.h`, `BotCecilItems.h` und `BotDriver.cpp`
blieben bytegleich zur Basis.

Private Quittung `.codex/evidence/grounded-fix/final-receipt.json`, SHA256
`9726c1329ecd6f44de367e447f6c1d0add7cb662885d7b36c1d2b6a2a52eecf5`,
pinnt sämtliche RED-/Zwischen-/Finaloutputs, Quellen, SDKverträge und die
16 Parentprogramme. Dateien0600/Verzeichnis0700. Keine Retailbytes oder
privaten Rohidentitäten im öffentlichen Repository.

Die Reprogrenzen bleiben erhalten: gültiger Retained-Zielkontext vorgegeben,
synthetische Bodenroute und ältere Fixturepose, keine exakt rekonstruierte
Nativewelt oder tatsächliche native Ray-/Support-/Velocitywerte. Native
Wirksamkeit, Sync-/Ressourcenstabilität und tatsächliche Waffenaufnahme sind
noch unbewiesen. Root reviewt, integriert und entscheidet separat über Build024
und ein eigenes begrenztes Nativefenster. Alle eigenen Jobs sind beendet.
