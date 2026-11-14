# A4: lokale Konkurrenz bei der ersten Waffenbeschaffung

Stand: 14.11.2026. Status: **portabler Fixkandidat; native Wirkung NOT_TESTED**.

## Historische Ursache und Grenzen

Das unveränderte Build018-Fenster `a4-reset018-extended-20261112-202210` bleibt FAIL mit23/24 bestandenen Slotphasen. Der fehlgeschlagene Slot in Phase1 hatte acht inventarbeobachtete Leben, sieben HP-Tode und keinen brauchbaren zusätzlichen Fernwaffenbesitz. Sein einzelnes Pickup `owned=3→7` ist ein Doppelcolt und erfüllt das Waffenversorgungsziel nicht.

Sechs der acht `unavailable`-Abbrüche lassen sich ohne prozessübergreifende Uhrenannahme einer tatsächlichen Waffenaufnahme durch einen anderen eigenen Bot desselben Prozesses zuordnen. Jeweils stimmen Prozess, Tick, neu gewonnenes Waffenbit und Waffenort überein:

| Tick | Ziel-Entity | Waffen-ID | Abstand des aufnehmenden Bots zum Zielort |
| ---: | ---: | ---: | ---: |
|3109|544|9|2,37|
|3125|401|13|2,48|
|3778|243|7|2,81|
|4129|267|12|2,18|
|4246|311|14|3,71|
|4743|544|9|2,32|

Zwei lokale Slots wählten bei2918 dieselbe Waffe544; der später aufnehmende Slot hatte die kürzere berechnete Route. Nach dem ersten Verlust wählte der fehlgeschlagene Slot Waffe401, die ein anderer lokaler Slot bereits seit2918 verfolgte und16 Ticks später aufnahm. Die Auswahl prüfte bisher nur den eigenen gerichteten Weg und Bedarf.

Alle sieben vorhandenen Unavailable-Diagnosezeilen melden `reason=render_type`, `render=5`, `picked_for_player=0`, `weapons_stay=0`. Engine107 nennt5 `RT_EDITORMODEL`; der Referenzpfad `CItem::ItemReceived()` wechselt erfolgreiche aufgenommene Items in diese Darstellungsart. Die Zuordnung der Aufnehmer ist für die beiden übrigen Entity267-Verluste bei3325 und5307 offen. Eine Eigentumsbitänderung erfasst zudem nicht jede erneute Aufnahme bereits besessener Waffen.

Die separate North68→6-Spur des fehlgeschlagenen Slots zeigt im43-Sample-Fenster3619–3661 den echten Übergang6→7. Daraus folgt keine allgemeine Navigationsabnahme. Der frühere vollständige Lebensabgleich bleibt separat dokumentiert; das frühe zusätzliche Clientlog-Leben eines anderen Slots lag vor Beginn der Inventarabtastung und wird nicht verworfen.

Private Rohdaten bleiben außerhalb des Repository. Das geschlossene historische Botlog wurde gegen seinen bestehenden SHA256-Pin `6d86ad7239a6485d18acc74bf9cd435b314adf841147a2830a5e671efc1d68c3` nachgeprüft; das Originalresultat hat weiterhin `40ec26b7c4987a05931f4ca09f90df25f19157b61a64874f04951e0feb584f45`.

## Begrenzte Änderung

Neue mapped-first-weapon-Auswahl bevorzugt eine andere zulässige Waffe, wenn ein näherer lebender lokaler Bot das ursprüngliche Ziel bereits aktiv verfolgt. Der Vergleich verwendet vorhandene gerichtete Suchkosten plus Abstand zum Suchanker, für beide Bewerber ohne finalen Itemconnector, mit mindestens einer Welt-Einheit Vorsprung. Das ist eine lokale Kostenschätzung, keine garantierte Ankunftszeit.

Die Beobachtung gilt ausschließlich in den vier vorhandenen lokalen Slots. Sie ist an Welt, Mapserial, Entity-ID, Generation, Ziel und unveränderten Versuch samt Deadline gebunden, höchstens0,25s alt anhand der gemeinsamen `GetGameTime()`-Beobachtungsuhr und verfällt nach5s ohne Positionsänderung von mindestens0,75 Einheiten in der eigenen lokalen Uhr des Eigentümers. Dessen Deadline wird ebenfalls ausschließlich mit dessen zuletzt beobachteter lokaler Zeit geprüft; lokale Slotticks werden nicht miteinander verglichen. Der Vergleich prüft zusätzlich die tatsächliche Player-Entity, Lebenszustand, Welt und weiterhin fehlende brauchbare Fernwaffe. Tod, Reset, Zielverlust, veränderte Generation/Map und Stillstand lösen die Präferenz. Es gibt keine IPC- oder Dateisperrbehauptung zwischen Prozessen.

Das konkurrierende Ziel bleibt im bestehenden begrenzten Connector-Prüfablauf ein Fallback. Konkurrenz erzeugt keine Itemablehnung oder30s-Blacklist. Bei nur einem übrigen Connectorbudgetplatz sowie in der letzten der acht vorhandenen Auswahlgelegenheiten bleibt die ursprüngliche Rangfolge maßgeblich; die Präferenz darf das ursprüngliche erreichbare Ziel nicht durch blockierte Alternativen verdrängen. Verborgene Items und gerichtete unerreichbare Alternativen bleiben ausgeschlossen; ein physisch blockierter Alternativconnector führt zum ursprünglichen erreichbaren Ziel zurück. Suchgraph, Itemzustand, native Inventare, Bewegungssicherheit und Versuchslaufzeiten werden nicht verändert. Bereits laufende Routen werden allein wegen einer neu beobachteten Konkurrenz nicht abgebrochen; insbesondere die ursprüngliche gleichzeitige Doppelwahl ist damit nicht vollständig gelöst. Auch Konkurrenz aus anderen BotClient-Prozessen bleibt außerhalb des Fixes.

## Verifikation

Baseline des unveränderten Bridge-Codes:2763 Checks,0 Fehler. Nach Hinzufügen der Verhaltensregression:2807 Checks,2 erwartete Fehler bei der Alternativauswahl und deren Wiederaufnahme nach Bewegung. Der ursprüngliche Näherungs-Kontrollfixture versetzte nur den Startknoten; für die beabsichtigte nähere Spielerposition wurde anschließend auch die zugehörige Spielerposition versetzt. Erwartung und Toleranzen blieben unverändert.

Die Regression führt echte `BotCecilChooseMappedWeapon`-/`BotSupplyTick`-Funktionskörper mit zwei lokalen Slots gegen die vorhandenen deterministischen Welt-/Physik-Stubs aus. Der SDK107-Vertrag prüft Button- und Raykonstanten; dies ist keine Retail-ABI- oder Runtimeabnahme. Die vollständige portable Prüfung ist beendet; der unten genannte bereits vorhandene Harnessfehler bleibt ausdrücklich FAIL.

Bisher ausgeführt:

```sh
python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sanitize --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
```

Final nach Reviewkorrekturen: normal und ASan/UBSan jeweils2833/2833 Checks, keine Sanitizer-Laufzeitdiagnose. GCC meldet beim großen bestehenden Testmain lediglich das Überschreiten der Debug-Variablenverfolgungsgröße und wiederholt diese ohne `-fvar-tracking-assignments`.

Kein Spielprozess gestartet, keine DLL gebaut oder ersetzt, kein Dienst verändert. Eine neue DLL wäre ein neuer Kandidat. Dev-Retail-Waffenaufnahme, Aktivitätsfelder aller Slotphasen, Kartenwechsel und verbleibende A-/Langzeitgates sind weiterhin erforderlich. Der historische A4-Fehler wird durch diesen Quellfix nicht als bestanden umetikettiert.


| Prüfung | Ergebnis | Grenze |
| --- | --- | --- |
|12 Kandidaten-`test_*.cpp`, jeweils `g++ -std=c++14 -O2 -Wall -Wextra` und Ausführung|12/12 PASS|Synthetische Koordinaten; keine Retail-Abnahme|
|Actual-body Bridge, normal und ASan/UBSan, SDK107-Vertrag|je2833/2833 PASS|SDK-geformte Stubs; kein nativer Game-/DLL-Lauf|
|AimTrace, Action, Itemdecoder, Playerobserver, Cecil-Exporte, Rotationsepochen, Supplyobserver|PASS|Portabel|
|`test_cecil_weapon_observer.py`|FAIL, Compilerfehler|Bereits auf Basis3558022 reproduziert; siehe unten|
|`python3 -m unittest discover -s tools -p 'test_*.py'`|344/344 PASS in190,122s vor den Reviewkorrekturen; Tools seither unverändert|Tool-/Fixtureprüfungen|
|`git diff --check`|PASS|Whitespaceprüfung|

Der gesamte Kandidaten-Prüflauf ist wegen des Weaponobserver-Harnessfehlers **nicht vollständig grün**. Sein Integrationsausschnitt übernimmt seit der AimTrace-Erweiterung zusätzlich fremde Diagnoseblöcke nach `SetAction`; die begrenzten Observer-Stubs definieren unter anderem `aimTraceCaptured`, `botcore::AimTrace` und entsprechende Playerfelder nicht. Der Fehler wurde mit dem exakten Basiscommit `35580222aaf05608a90402d140948ad80198bb67` separat reproduziert. `BotDriver.cpp` (SHA256 `75cf99356b70ec1150e3af1316c8bae2d989c37b1608f2d0e64ec056e5e71551`) und der Observer-Test (SHA256 `b7222d441313d575aa7166ec47923875b6a52b6695c9ae5de95bc15b01e5f9e3`) sind gegenüber der Basis unverändert. Der unabhängige Fehler wird nicht durch Abschalten des Tests oder Änderung seines Ergebnisses verdeckt.

## Handoff und nächste Abnahme

Worktree `/srv/tse-a4-contention-20261114`, Branch `codex/20261114-a4-local-supply-contention`, Basis3558022. Geänderte Produktionsdatei: `BotSupplyNative.h`, SHA256 `9d2cd8b06147b80e18e077dcd603977a5838a402a271531245cb13539a870717`; zugehöriger Bridge-Test SHA256 `70aaf0ad21ed21c1b4e3571617e6bc266247bca8afc22b8e951cecc37c5e5782`.

Nur der Hauptagent integriert und führt einen eventuellen neuen Kandidaten durch Build-/Dev-/Native-Abnahme. Zunächst diesen Diff unabhängig prüfen und den getrennten Observer-Harnessfehler behandeln. Danach die bisher fehlgeschlagene Red-Resetprüfung mit unveränderten Aktivitätsfeldern und angemessener vollständiger Lebenskorrelation wiederholen. Alle acht Slotphasen je Epoche müssen Waffenaufnahme und native brauchbare Fernfeuer-Samples wirklich zeigen. Konkurrenz über Prozessgrenzen, simultane Doppelwahl und die beiden nicht zugeordneten267-Verluste bleiben konkrete Beobachtungsziele. Keine eigene Compiler-/Test-/Spielausführung bleibt nach dieser Übergabe aktiv.


## Korrekturen aus unabhängiger Review

Die erste Fassung `be467729dafd2c30f1469c81e9d27acdacad1c9d` enthielt zwei wichtige Fehler und ist durch die folgenden Korrekturen überholt:

1. `SBotState::bs_iTick` wird bei neuer Spielerquelle pro Slot zurückgesetzt (`BotDriver.cpp:1138`). Daher waren Frische-, Fortschritts- und Deadlinevergleiche mit der lokalen Uhr des jeweils anderen Slots falsch. Die neue Regression veröffentlicht Claims mit lokalen Zeiten0,05 und50, gemeinsamer Beobachtungszeit80 und prüft beide Joinrichtungen, den tatsächlichen `BotSupplyReset`-/Rejoinpfad, gemeinsame Staleness/Uhrenrücksprung sowie Fortschritt ausschließlich anhand der Eigentümeruhr. RED:2824 Checks/6 Fehler; nach Korrektur2824/2824.
2. Eine blockierte bevorzugte Alternative konnte bei Raybudget3 die einzige Connectorgelegenheit verbrauchen; mindestens acht blockierte Alternativen konnten zudem die gesamte bestehende Versuchskappe ausschöpfen. Regressionen mit Budget3/4 und neun blockierten Alternativen ergaben RED2833 Checks/3 Fehler. Die Präferenz gilt nun nur bei mehr als drei verbleibenden Raybudgetplätzen und vor der letzten der acht vorhandenen Versuchsgelegenheiten. Andernfalls wird die ursprüngliche Rangfolge verwendet. GREEN2833/2833; weder Raybudget noch Versuchskappe wurden erhöht.

`CNetworkLibrary::GetGameTime()` ist im gepinnten Engine107-Header `Sources/Includes/Engine107/Engine/Network/Network.h:274` deklariert und wird im vorhandenen Driver bereits bei602/660 verwendet. Die Korrektur führt kein neues ungeprüftes ABI-Feld ein. Die Claimfrische verwendet diese gemeinsame Uhr; ein separat gespeicherter Eigentümerzeitpunkt bewertet ausschließlich dessen eigene Deadline und Stillstandsperiode. Damit wird keine Gleichheit der Slottickursprünge vorausgesetzt und keine Uhrtoleranz zur Umgehung einer fehlgeschlagenen Probe vergrößert.


Finaler relevanter Wiederholungslauf nach beiden Korrekturen:12/12 C++-Programme und8/9 Python-Kandidatenskripte bestanden, normale Bridge2833/2833, ASan/UBSan-Bridge2833/2833. Der unveränderte Weaponobserver-Harnessfehler ist erneut FAIL; keine neue Fehlermeldung durch diese Änderungen. Die gemeinsame Suite ist daher weiterhin nicht vollständig grün. Die344 Tools-Tests wurden vor diesen reinen Bridge-/Fixturekorrekturen bestanden und danach nicht unnötig wiederholt; diese Tooldateien wurden nicht geändert. `git diff --check` erneut bestanden. Die Wiederholung lief mit jeweils einem Compiler und begrenzten Kindprozess-Timeouts. Keine Testausführung bleibt aktiv.
