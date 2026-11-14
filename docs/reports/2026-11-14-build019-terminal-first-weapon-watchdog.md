# Build019 A4: erste Waffen-Endannäherung verliert ihr Fortschrittsbudget

Der geschlossene Quiet-Lauf bleibt **FAIL23/24**. Phase2/botB:0 ist globalSlot1/entity560. Das erste Leben hatte bereits eine nützliche Waffe: der Client protokolliert Tick5862 den Übergang3→8195, während die erste akzeptierte Inventoryprobe erst bei nativer Zeit7,700011 bereits8195 sieht. Dieser links zensierte Besitz bleibt Besitz; er wird nicht in einen serverseitig beobachteten Pickup umetikettiert.

Danach bleiben zwei vollständig beobachtete Leben und das letzte rechts zensierte Leben ohne nützliche Waffe: native Spawnclocks15,850042→Tod31,649803;31,849800→Tod89,800880;89,850883→letzteProbe139,453903. Deshalb ist die echte Beschaffungsstörung zusätzlich zur frühen Messlücke zu untersuchen.

## Konkreter Verlauf und Ursache

Im dritten Leben wählt B0 bei eigenem Tick6626 das gemappte WeaponItem544, Ziel175, bestehende Deadline351,3 bei Versuchsbeginn331,3 in seiner lokalen Botuhr. Der Weg erreicht die gewöhnliche Endkante111→175. Vierzehn Terminaldiagnosen von337,7 bis350,7 melden weiterhin akzeptierten aktuellen Navigationseigentümer, Standzustand, null Knotenflags und Abstände8,490697 bis16,011169m. Die protokollierten Zustandsanker zeigen weiterhin Besitz3, keinen sichtbaren Gegner, keine Fireaktion und Bewegung um den Endbereich. Der Versuch endet erst bei Tick7026 am unveränderten20s-Itemtimeout.

Beide bisherigen passiven Fortschrittswächter schließen Endpunkte mit `important_entity>=0` ausdrücklich aus. Damit kann die gewöhnliche Waffen-Endkante ihre10s-/0,75m-No-progress-Regel gar nicht verwenden. Das Item ist nicht generell unerreichbar: B1 nimmt dieselbe Waffe später bei eigenem Tick7072 tatsächlich auf. Weitere Ziele werden B0 während dieses Lebens vor Ankunft entzogen, unter anderem267 durch B3 und401 durch B2; die lokale Konkurrenzpräferenz ist keine flächendeckende Reservierung und garantiert keine Ankunft.

Der konkrete physische Ablehnungsgrund ist **nicht bewiesen**: Für dieses Leben liegen keine vollständigen Probe-/Rayfenster vor. Die vorhandenen beiden Detailfenster beobachten68→6 beziehungsweise87. Knoten111→175 ist davon nicht erfasst. Die [bereinigten Anker](../../poc/candidates/redstation-supply-20261107/fixtures/build019-terminal-111-175.json) enthalten14 echte Positionen sowie14 Terminaldiagnosen mit Beleg-SHAs. Unterschiedliche prozesslokale Tickzähler werden nicht als gemeinsame Wanduhr oder versetzter Kartenbeginn interpretiert.

## Enger Quellstand

`BotCecilItemTransitFailed` erlaubt zusätzlich ausschließlich ein gewöhnliches gemapptes erstes Waffen-Terminal: `hop==goal`, dessen Entitybindung exakt zur aktuellen Item-ID passt, Weapon-Typ, kein nützlicher Besitz oder nutzbare nützliche Waffe, Stand/Hocke, keine Flags/Locks/Follow-/USE-/Flight-/wichtige Interaktion. Die vertikale Grenze3m stammt aus der bestehenden abschließenden Itemconnector-Prüfung. Der alte Intermediatezweig bleibt erhalten.

10s,0,75m, ursprüngliche Deadline und30s-Itemablehnung bleiben unverändert. Bei Ablauf geschieht nur die bestehende lokale Itemablehnung mit neutralen aktuellen Achsen; der normale Selektor kann anschließend ein anderes zulässiges Item wählen. Es gibt keine neue Bewegungsfreigabe, Rayabfrage, World-Entitysuche oder Heapallokation durch den passiven Zweig. Bereits bewaffnete Bots und besondere/vertikale Übergänge bleiben ausgeschlossen.

## Tatsächlich geprüft

- RED gegen unveränderte Quelle:2919Checks,4 erwartete Fehler für Terminalabbruch, neutralen Finalinput und Fortschrittsreset.
- GREEN:2920Checks,0Fehler im bestehenden Bridgeharness einschließlich Intermediate-/Flight-/Lock-/Recoveryregressionen.
- Derselbe fokussierte Harness mit ASan/UBSan und tatsächlichem SDK107-Button-/Rayvertrag:2920Checks,0Fehler, kein Sanitizerbefund.
- Zusätzliche Negativabdeckung:26Terminalkontexte und12Kontextresets; echte Annäherung, exakte0,75m-Grenze, neutrale Finalachsen und normaler anschließender Selektor geprüft.

Die Portablereplays halten sparse native Posen mit **synthetischen20Hz-Zwischenbeobachtungen**. Das beweist den Mechanismus im tatsächlichen Quellcode, keine kontinuierliche native Kollisionsspur und keinen A4-Erfolg. Ein anfänglicher überschießender Test erwartete bei einer nahen Alternativwaffe speziell `mappedWeaponGoal`; der bestehende normale Selektor darf diese unmittelbar als gewöhnliches Item wählen. Die Assertion wurde auf das tatsächlich geforderte neue zulässige Ziel begrenzt; native Kriterien wurden nicht geändert.

[Quittung mit exakten Pins/Kommandos](milestone-a-20261114/build019-terminal-watchdog-portable.json). Keine neue Retail-DLL, kein Native-Start, kein Deploy. Root prüft und integriert diesen Quellstand, erstellt einen neuen Kandidaten und führt erforderliche echte Gates nach frischem Preflight aus. Die frühe Inventorylücke und weitere A-Abnahmen bleiben separat offen. A3-Designzwischenstand liegt unverändert auf Branch`codex/20261114-a3-tier-comparison-design`, Commit`0454337`.
