# Native013 Skulls: saubere Sitzung, funktionaler FAIL

`a4-013-skulls-20261112-022140` absolvierte600,117 s mit vier normal geschlossenen Rollen, akzeptierten Post-close-Logs und vollständigem Restore. Keine protokollierten Sync-/Crash-/InvalidAction-Fehler, Host-CPU maximal62,162 %, verfügbarer RAM mindestens1,736 GiB. Der Controllerstatus ist begrenzte Beobachtung mit erforderlicher Funktionsprüfung. **Die unabhängige Navigations-/Erwerbsbewertung ist FAIL:** Zwei Bots verbringen über200 s desselben Lebens ohne nützlichen Waffenbesitz in jeweils konkret belegten Zielverlust-/Reacquire-Verläufen. Alle acht aggregierten Aktivitätsminima ändern diesen Befund nicht.

Alle acht Clients verwenden Kandidat013 `3a8d84c9…a81f93` und kanonisch migriertes DEMON/tier3. Tatsächliche Slots: BotA0/2/3/4, BotB5/6/7/8, Vanilla1. Beide Loadmarker bestätigen296Knoten, WorldCRC`42d03dd2`, NavCRC`70b554dd`; Pfadhash`9b573405` ist kein Weltdatei-CRC. [Bereinigte JSON](2026-11-12-native013-skulls-analysis.json) enthält sämtliche Lebensnenner, Watchdogereignisse, Positionsgrenzen und Abschluss-Hashes. Rohinventar/Spielernamen bleiben privat.

## Alle beobachteten Leben

| Kohorte | Lebend beobachtete Leben | Tod / rechtszensiert | Nützlicher Besitz / aktuelle Waffe / Feueranforderung | Tod / zensiert ohne nützlichen Besitz |
|---|---:|---:|---:|---:|
| BotA |104|100 /4|42 /42 /42|59 /3|
| BotB |101|97 /4|49 /48 /45|51 /1|
| Gesamt |205|197 /8|91 /90 /87|110 /4|

Maske`0x3df8` schließt Double Colt und Nahkampf aus. Keine zusätzliche nur tot beobachtete positive Spawn-Epoche wurde gefunden. Die 91 erfolgreichen Erwerbsleben haben Median5,050 s und Maximum34,891 s; diese erfolgsbedingten Werte dürfen die114 erfolglosen oder zensierten Erwerbsleben nicht verdecken. Feueranforderung ist kein Treffer-/Schadensbeweis. 13766 Inventarproben wurden akzeptiert,526 zerrissene verworfen; die Doppelablesung bleibt nicht atomar. Kürzere unbeobachtete Lebensphasen sind dadurch nicht ausgeschlossen.

## Zwei konkrete lange Fehlerverläufe

**BotA local3/entity1853/generation11:** Spawnclock53,049477;223,706 s bis beobachteter Tod, niemals nützlicher Besitz. Minigun965 wird bei DriverTick1245 gewählt und1261 unavailable. Rocket1025 folgt1301 und endet1548 unavailable (botA-closed.log:1273/1291/1319/1501). Danach208 lebende States1560–5700 über207 s (1513–4754): durchgehend NAV1, keine Sicht, goal/hop/source=-1; reacquire137 und148 jeweils104-mal. Position bleibt bei X−121,476…−120,501, Y−23,998, Z−12,149…5,623. Der Bot bewegt sich wiederholt seitwärts, SafeMotion162-mal Alternative/24-mal Original/22-mal neutral, aber erreicht keine neue Route oder Waffe. HP90 und shots87 bleiben in diesen States konstant. Dies ist ein bewegter Wiederaufnahmezyklus nach Itemverlust, kein stationärer Timerbeweis und keine nachgewiesene Todesursache.

**BotA local1/entity1851/generation25:** Spawnclock337,841034;262,886 s bis Messende rechtszensiert, ebenfalls niemals nützlicher Besitz. Nach Verlust von Waffenitem1027 und zwei anderen Zielen wird Item917 bei7332 gewählt (6045), Frist389,098.18 States7440–7780 zeigen129→248; Timeout7782 (6404). Danach220 States7800–12180 über219 s (6425–10038): NAV1, keine Sicht, goal/hop/source/reacquire=-1, owned3, shots830. Position bleibt in einem Bereich3,136×1,495×2,839 m; zuerst Support-ID1, später357, häufig neutrale Bewegung und gelegentliche bereits geprüfte Alternative. Support357 ist eine beobachtete Identität, **keine belegte Klasse oder Beweglichkeit**. Cleanup-States nach der nativen Messgrenze sind ausgeschlossen.

Die erste Episode zeigt erfolglose Wiederaufnahme trotz wechselnder Kandidaten137/148; die zweite zeigt nach Timeout überhaupt keinen gespeicherten Wiederaufnahmeknoten. Ein gemeinsamer spekulativer Support-/Radius-/Timeoutfix wäre durch diese Daten nicht gerechtfertigt. Der Item-Transitwatchdog ist nach `goal_entity=0` nicht zuständig.

## 129→248 und tatsächliche Watchdogfolgen

24 Leben enthalten beobachtete129→248-States mit Zielitem917. Knoten129 liegt bei(−36,−71,5,8), Hop248/stabileID250 bei(−56,−63,5,8), Radius2; beide Flags0. Ziel271/stabileID273 gehört Item917. Mehrere Anfahrten dauern in periodischen States17–18 s ohne Erreichen; NAV-/Sichtunterbrechungen und fehlende Aktion-für-Aktion-Frische erlauben keinen pauschalen Schluss, dass jede davon dieselbe ununterbrochen berechtigte10-s-Uhr hätte.

Fünf tatsächliche `CecilItemTransitEnd` beenden genau diesen Abschnitt nach10 s ohne genügend Fortschritt; beste Distanzen11,594…11,657 m:

| Rolle/local/Generation | Tick aus Ereigniszeit | Folge im selben Leben |
|---|---:|---|
| A/0/7 |1169|Nützlicher Besitz bereits vor Abbruch; später andere Ziele, kein belegter neuer Waffenpickup danach.|
| B/0/25 |9240|Bis Tod kein nützlicher Besitz, keine weitere Zielwahl protokolliert.|
| B/0/33 |11644|Nützlicher Besitz bereits vor Abbruch; spätere Feueranforderung ist kein neuer Erwerb.|
| B/1/30 |9827|Später Waffenitem1027 gewählt, Tod ohne nützlichen Besitz.|
| B/3/8 |1475|Ziel964→unavailable1591, dann DoubleShotgun1762; tatsächlicher Pickup1667, Besitz3→19; erster nativer Erwerb23,851 s nach Spawn, Feueranforderung27,901 s.|

Die fünf Abbrüche sind positive Ausübung der passiven Begrenzung, nicht fünf erfolgreiche Befreiungen. Insbesondere bereits vorhandener Besitz unmittelbar nach Abbruch wird nicht als Pickup gezählt.

## FALL, Flüssigkeit und Teleportgrenzen

Die205 Leben enthalten3662 lebende STAND- und784 FALL-States, keine SWIM/DIVE-States. PlayerState4 heißt FALL; SafeMotion`floor`0/1/2 beschreibt dagegen Auswahl/Neutralisierung einer Bewegung.448 abgetastete FALL-Episoden enden427-mal mit beobachtetem STAND/CROUCH desselben Lebens,20-mal mit Tod vor beobachtetem Ausstieg, einmal rechtszensiert. Längste beobachtete Spanne9 s (BotB local3/generation16,5480–5660), anschließend STAND. Das belegt weder dauerhafte sichere Landung noch die Ursache der20 Todesfälle.

TELEPORT32 ist an NAV-Slots221–224 annotiert; beispielsweise erscheint source224→hop160 vor dem langen A3-Leben. Es gibt in den gültigen aufeinanderfolgenden lebenden Inventarproben desselben Lebens keine Positionsdifferenz>50 m innerhalb≤300 ms. Diese rein beschreibende Suche ist kein originaler Teleportdetektor. Metadaten, Fallbewegung oder Kantenwechsel belegen weder originale Entityklasse noch erfolgreichen Teleport. Eine Teleport-Funktionsabnahme bleibt offen; Flüssigkeit wurde hier nicht ausgeübt.

## Freigabegrenze

Keine Karten-/A4-/Releasefreigabe und kein Inprocess-Mapreset aus dieser Sitzung. Für eine vorübergehende Kartenbeschränkung darf Skulls nicht als bestanden geführt oder fälschlich an RedStation-NAV gebunden werden. Ein Fallback muss die tatsächlich geprüfte andere Welt mitsamt korrekter eigener Bindung wählen. Weitere Karten und konkrete Whitelist sind separat zu prüfen. Diese Analyse ändert weder Gameplay noch Harness oder aktive Ressourcen; alle größeren Auswertungen liefen in eigener CPUQuota25%-Unit.
