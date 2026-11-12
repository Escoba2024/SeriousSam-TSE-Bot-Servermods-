# Public013 MITTEL: beide gekreuzten Fenster, negatives Ergebnis erhalten

Die beiden abgeschlossenen120-s-Fenster belegen **keine Verbesserung von MITTEL gegenüber Public7fc**. Swap1 fällt günstiger aus, hebt den starken Rückstand in Swap0 aber nicht auf. Der [ungünstige Einzelbefund](2026-11-12-native-public013-mittel-swap0-damage-audit.md) bleibt unverändert; [dieses Paar-JSON](2026-11-12-native-public013-mittel-damage-pair.json) enthält sämtliche84 beobachteten Leben und beide vollständigen Hooknenner.

| Native Beobachtung | Swap0 Public | Swap0 MITTEL | Swap1 Public | Swap1 MITTEL |
|---|---:|---:|---:|---:|
| Leben |28|13|27|14|
| Tod / Fensterzensierung |25 /3|10 /3|23 /4|10 /4|
| Nützlicher Waffenbesitz |4|9|1|10|
| Beendet ohne nützlichen Besitz |21|3|22|3|
| Zensiert ohne nützlichen Besitz |3|1|4|1|
| Nützliche aktuelle/besessene Waffe |1|9|1|9|
| Nützliche aktuelle Waffe mit Fire-Request |1|6|0|9|
| Bekannte lebende Fremd-Damagecalls |102|38|52|77|
| HP-Verlust, auf Vorhit-HP begrenzt |3307,855|801,410|1787,269|1835,000|
| Tödliche Fremdaufrufe |28|8|12|20|
| Letzter Query-Fragdelta |+27|+8|+12|+18|

Zusammen MITTEL27 Leben/19 Erwerbe/6 abgeschlossene und2 zensierte Leben ohne Erwerb; Public55/5/43/7. Hinzu kommen zwei separat ausgewiesene Vanilla-Leben, beide beendet ohne Erwerb. Kein Erwerb wird aus ausschließlich toten Proben abgeleitet. Erfolg-only-Mediane sind wegen der unterschiedlichen Fehlschlagsnenner keine All-Life-Erwerbszeit. Spätester Kandidatenerwerb20,901 s in Swap1; „sofortige“ vollständige Waffenbeschaffung ist damit nicht nachgewiesen.

Gesamt-MITTEL: **2636,410 begrenzter HP-Verlust,28 tödliche Fremdaufrufe und Querydelta+26**; Public5095,124/40/+39. Die Differenz zwischen Query-Frags und Killaufrufen berücksichtigt unterschiedliche letzte Abtastzeitpunkte/Gameplayfolgen; die Größen werden nicht gleichgesetzt. Treffer auf andere Bots derselben KI-Kohorte zählen als normale Nicht-Selbst-Fremdtreffer; es handelt sich nicht um Teams.

Der zweite Hooknenner lautet166 Records =129 bekannte lebende Fremdaufrufe+34 Leichenaufrufe+3 unzuordenbare Inflictors. Zusammen mit Swap0 bleiben alle355 Records erhalten. Die36 bzw32 nativen Fremdkillmeldungen im jeweiligen Endfenster-Serverlog stimmen für jedes Schütze-/Opfer-Slotpaar exakt mit sämtlichen tödlichen Fremd-Damagecalls überein. Keine Faults/Drops/unknown-victim/non-main/Restaufrufe/Detachfehler; volle Fensterüberdeckung und ursprüngliche Getter-/Damagekörperrestaurierung sind archiviert. Vier normale Closings, Postclose-Syncprüfung und vollständige Dateirestaurierung je Fenster bestätigt.

Aktuelle Local-/Global-Slots, Entity-/Pointerregistry, jede native Inventarprobe, Cecil-Lebensereignisse, Originalhashs und beide Konfigurationen wurden unabhängig erneut geprüft. Beide unveränderten Initialreferenzen und raw-first/first-neutral-Archive sind durch vollständigen Policyreplay reproduziert. FirstProcessedState bleibtfalse; SameSpawnTick-HP-Witnesses0.

Das Feuer-/Trackingbild bleibt eine begrenzte Diagnose: In Swap1 steigt der finale Combat-Fire-Inputcounter um472 statt193 in Swap0. Die47/46 groben BotHuman-Proben zeigen11/20 sichtbare Zielzustände, davon10/16 mit Residualfehler>1,5° und1/3 mit HumanFire. Diese alle200 Driverticks geschriebenen Zeilen decken nicht die20Hz-Triggerhistorie ab. Es gibt keinen durch diese Proben belegten allgemeinen Supply-Unterdrückungsfehler. Der tatsächliche MITTEL-Arenapfad und seine gegenüber STARK langsameren Dreh-/Tracking-/Reaktions-/Settlingparameter sind im Einzelbericht belegt; daraus folgt noch kein eindeutig lokalisierter Bug.

Auch Swap1 zeigt im definierten Gap≤0,5-s-/SameLife-Maß keine lange Kandidatenresidenz: Slots0/2/3/4 maximal0,45/1,90/1,10/0,75 s innerhalb1 m eines festen Ankers. Das schließt ineffiziente Wege oder Waffenwahlverzögerungen nicht aus. Physische Startseite und nachfolgend auseinanderlaufende Gegner-/Waffenverläufe sind reale Störgrößen für eine isolierte Parameterkausalität.

Der nächste kleine Diagnoseentwurf kann bei unveränderter013-DLL ausschließlich den schon vorhandenen Candidate-LogEvery-Wert für ein begrenztes Fenster verdichten. Geprüft werden müssen Zielkontinuität, reale aktuelle/gewünschte Waffe, Residualwinkel, aufeinanderfolgende Ausrichtung, HumanFire und FinalFire zusammen. Keine zusätzliche Hookstelle und keine vorschnelle Änderung von Toleranz, Reaktion, Physik, Radien oder Deadlines. Die Diagnostik wäre wegen zusätzlicher Logkosten ausdrücklich kein weiterer vergleichbarer Leistungslauf; Originalreferenz/Cleanup/Ressourcengrenzen bleiben bestehen.

Fenster: `arena013public-damage-checked-swap0-trial-1-031704`120,055 s und `arena013public-damage-checked-swap1-trial-1-032500`120,052190 s. Gesamte Dateiauswertung unter eigener CPUQuota25%/Nice10; private Reproduktionsquellen in `/srv/tse-combat-a3-mittel-audit-20261112`. Kein Runtime- oder Produktionszugriff. A3gesamt/013-Qualifikation bleiben offen; STARK-Ergebnisse werden nicht auf MITTEL übertragen.
