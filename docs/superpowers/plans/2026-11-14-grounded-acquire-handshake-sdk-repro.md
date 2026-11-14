# GroundedReplan-Acquire-Handshake: SDK107-Reproduktionsplan

> Umsetzung durch a4_diagnosis mit executing-plans, systematic-debugging und TDD. Keine Delegation.

**Goal:** Prüfen, ob die echte ChooseGoal-/Nearest-Kette nach einem committed hohen 69→71-Schritt und Landung einen frischen Bodenanker erhält oder ihn zugunsten des gehaltenen hohen Ankers verliert.

**Architecture:** Bestehende SDK107-Brücke extrahiert die tatsächlichen Produktionskörper. Eine neue sequentielle Fixture verwendet die hohen Originalpunktpositionen und die schon vorhandene kleine Bodenrouten-Fixture. Sie setzt nach Landung keinen Anker; die vorhandene `groundedReplanFixture` bleibt unverändert als getrennte Positivkontrolle. Nearest-/LOS-/Budget-/Support-/Velocity-Werte sind kontrollierte portable Eingaben, keine nachträglich behaupteten Nativefakten.

**Tech Stack:** Python-Harness, bestehende deterministische Welt-/Raystubs, tatsächliche C++14-Produktionskörper, gepinnte SDK107-Aktions-/Raydeklarationen.

**Spec:** Rootauftrag und geschlossener Bericht `docs/reports/2026-11-14-supply-diag1-typed-unavailable-closed.md`; Quelle `BotSupplyNative.h`, `BotCecilChooseGoal`, `BotSupplyNearest`, `BotCecilGroundedReplan` und vorhandene `groundedReplanGuards`.

## Grenzen und Reviewfokus

- Nur Reproducer und Diagnose; kein Produktionsfix, DLL-Build oder Nativefenster.
- Reale Navigator-Commitbildung auf hoher Quelle, FALL→STAND und gemessene Bodenposition; keine Zuweisung `s.anchor=0` nach Landung.
- Hohe Punktmetadaten unverändert; Bodenpunkte sind die vorhandene Testumgebung, keine vollständig rekonstruierte Nativewelt.
- Budgetdefer und wirklich blockierte LOS sind getrennte Eingaben. Support, Geschwindigkeit, Flüssigkeit und Locks behalten ihre Vetos.
- Ursprüngliche Zielzeit/Deadline, Item-ID und Generation bleiben beobachtbar; kein Aufweichen von Holdzeit, Radien oder Floorfreigabe.
- Falls eine faire frische ChooseGoal-Akquisition den Bodenanker korrekt übernimmt, ist das ausdrücklich ein bestandener Kontrollfall, kein erzwungener RED.

## Aufgaben

- [x] Bestehende relevante Körper und Originalfixture lesen, sauberen Parent mit dem SDK107-Brückenkommando prüfen.
- [x] Reproducer vor Produktionsänderung schreiben: Commit hoch erzeugen, unten landen, echte ChooseGoal und GroundedReplan sequenziell aufrufen; Zustand, Nearestresultat und Budget protokollieren.
- [x] Unbekannte Eingaben eng variieren: ausreichendes Budget, Aufschub/erschöpftes Budget und LOSwechsel; gültiger/ungültiger Support und Geschwindigkeit als Gegenfälle.
- [x] Erwartung und tatsächliches Verhalten abgleichen. Echten RED einschließlich genauer Guardursache erhalten, oder vorhandenes korrektes Verhalten ehrlich dokumentieren.
- [x] Produktionsheader bytegleich nachweisen; private Logs/Quittung und bereinigten Bericht mit reproduzierbaren Kommandos liefern.
- [x] Nur Reproducer/Plan/Claim/Bericht committen; Root entscheidet über einen etwaigen Fix.

Ergebnis: Parent3223/0, finale echte SDK-Brücke3274/2. Zwei neue REDs bei
retained69/fresh0, alle anderen Kontrollen und bisherigen Checks bestanden.
Produktionsquellen unverändert; kein Fix/ASan/Native. Bericht und private Quittung
sind fertig; Rootreview/Fixentscheidung folgt getrennt.
