# Atomischer Erstwaffenwechsel aus nichturgentem Nebenitem – SDK-Beleg

Die echten produktiven SDK-Bodies zeigen den bedingten Fehler: Ein gehaltenes gewöhnliches Health-/Armorziel verhindert selbst dann jede mapped Erstwaffensuche, wenn keine brauchbare Usefulwaffe vorliegt und eine andere Originalmapped-Waffe frisch erreichbar und aufnehmbar geprüft werden kann. Der neue enge Admissionpfad behebt diesen Sourcefall; er beweist noch keine native Verbesserung und erklärt nicht rückwirkend alle langen Waffenlücken. Kein Build, Runtime, Deployment oder Livewechsel.

Ausgangspunkt ist der geschlossene Trouble031-Audit37063d9: A1/global2/g6 hält nichturgente Health/Armorziele, während `!goalEntity` den Normalpicker und danach `goalEntity!=0` den Mappedpicker kurzschließt. Ob damals gleichzeitig eine erreichbare freie Alternative existierte, bleibt UNKNOWN. Der SDK-Reproducer setzt diese fehlende Bedingung ausdrücklich als kontrollierte Weltfixture, ohne sie als natives Faktum auszugeben.

## Echter RED vor Produktion

`test_cecil_native_bridge.py` extrahiert weiterhin die vollständigen tatsächlichen Produktionsfunktionen. Der Fixture ruft reales `BotCecilChooseGoal`, reale typed Itemneed, origin nearest/LOS, echte Graphsuche und den vorhandenen Mapped-Connector auf. Nur Enginewelt/Physics werden wie im Parent deterministisch gestubbt; keine zweite Implementierung des Pickers.

Zwei ordinary gehaltene Fälle, Health70HP und Armor0, owned/usable3, Sideitem bei5m, mapped WeaponID4 bei20m (außerhalb des normalen16m-Suchradius). Beide Gegenkontrollen ohne gehaltenes Sideitem erreichen genau diese mapped Waffe über den Originalpfad. Mit Sideitem schlägt der Parent erwartungsgemäß fehl:4052 Checks/zwei Fehler. Anschließend32 echte Adversaries vor Produktion:4116 Checks/weiter ausschließlich diese zwei Fehler. Testcommit `c2ac6c1` bewahrt das RED unabhängig vom Fix. Die roten Assertionen betreffen Verhalten, keine Import-/Compilerfehler.

## Kleiner Fix, Erfolg erst nach voller Prüfung

Nur `BotSupplyNative.h`: neue eng begrenzte `BotCecilFirstWeaponReplacement`-Eligibility und der bestehende erste Mapped-Admissionguard. Zulässig sind ausschließlich live/needed, gewöhnliche, nichturgente Health-/Armorziele bei fehlender erlaubter Usefulwaffe, gültiger Actor-/Generationbindung, normaler Stand-/Crouchphase, endlicher aktueller Eingabe, erfülltem bestehendem Searchcooldown und Enemyabstand≥8. Alte12s-Laufzeit bleibt unverändert. Mapped-/relocationbudgetierte Ziele, Important-/Follow-/Interaction-/Flight-/Healthconnector-/Escape-/Groundstuck-Ownership sowie aktiver temporärer Avoid werden nicht präemptiert. Aktuelle Anchor/Goal/Source/Hop-Metadaten mit Flags/Important-/Lock-/Nextbinding oder blockierten Punkten bleiben Veto.

Die aktuelle Sideitem-Need wird einmal frisch gegen denselben vorhandenen Input geprüft. Danach verwendet der Code unverändert den vorhandenen mapped Kandidatenpool, typed Need, ursprüngliche Referenzen, Pfad-/Lockfilter, Connector≤8m/height≤3, lokale Contentionpräferenz, acht vorhandene Versuche, vorhandenen Raybudget und tatsächlichen Connectorcast. Der bestehende `ClearGoal`/neue Goalcommit steht weiterhin ausschließlich hinter erfolgreicher Ersatzvalidierung. Vorher bleiben alter Goal, Attemptbeginn, Deadline und Navigatorresetserie erhalten. Tatsächlich fehlgeschlagene Weaponkandidaten dürfen weiter ihre bestehende Ablehnungsquittung/Backoff erhalten; das alte Health-/Armorziel wird deswegen nicht künstlich rejected.

Erfolg erzeugt einen echten neuen Weaponversuch mit unveränderter mapped Deadlineformel; nachfolgende Scans verlängern ihn nicht. Keine zusätzliche Uhr-/RNG-Callsite, kein neuer Floor-/Arrival-/Radius-/Nav-/Pit-/Movementgrant, keine Item-/replicated Writes, kein Driver-/Rules-/Decoderwechsel. Neue Suchzulassung führt selbstverständlich die vorhandenen Kandidaten-/Castcalls aus; es wird keine globale Callzahlidentität zwischen altem und neuem Gameplay behauptet.

Rootreview verlangte zusätzlich kausale Logkustodie: ein erfolgreich ersetztes Sideitem braucht seinen bisherigen `CecilGoalEnd` mit `reason=first_weapon`, **vor** dem erfolgreichen ClearGoal und neuen Weaponcommit. Ein echter Folge-RED prüft Originalitem-ID und Reihenfolge:4175 Checks/zwei ausschließlich fehlende Marker. Die einzige Folgeproduktionszeile ist `if(s.goalEntity)BotCecilGoalEnd(slot,tick,s,"first_weapon");` nach erfolgreichem bestehenden Connector und vor ClearGoal.32 Fehlschlagsfälle prüfen gleichzeitig: kein Firstweapon-Endmarker und kein neuer Goalcommit bei Guard-/Budget-/Candidate-/Castfehler. Das ist Beobachtbarkeit des tatsächlichen Wechsels, keine Algorithmus-/Friständerung.

## Prüfung und Grenzen

Vor Markerergänzung: normal4141/0 und ASan+UBSan4141/0, beide Exit0. Enthalten sind echte positive Health-/Armorwechsel und voller BotSupplyTick,32 negative Guardfälle, exakte3-Ray-Connectorgrenze mit verbleibenden zwei finalen Rays, kein Reset bei Budget2, feste Folge-Deadline, Kandidatenlänge/-höhe/-Destlock, fehlende/ungeeignete Items, wichtige/spezielle Kontextmetadaten, Generation und nichtendliche Eingaben. Danach enger Marker-RED→GREEN mit denselben tatsächlichen Bodies; finaler Normalstatus und aktuelle Sourcehashes stehen in der privaten Abschlussquittung. Kein erneuter unveränderter ASanlauf allein für diese einzige vorhandene BotLog-Callsite; der ASanbeleg wird ausdrücklich als Prä-Marker-Source abgegrenzt.

Kommandos, seriell nice15:

```sh
nice -n 15 python3 -B poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
nice -n 15 python3 -B poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es --sanitize
```

Der bestehende Windows-empty-`far`-Makrotest und exakte geerbte Reacquire-Bodyinverse laufen mit. Private vollständige RED/GREEN/ASanlogs und zweistufige Headerinversen liegen unter `.codex/evidence/atomic-first-weapon-preemption/`. Die Prä-Marker-Headerinverse `1b76094f7e908d57b524164af8ae1ae92c0970c28fa17de773d50324d63a268c` bleibt unverändert; ein separater finaler Beleg enthält den zusätzlichen einzelnen Logmarker. Ganze Headerinverse ergibt den unveränderten Parent `0e7ee9d160afcca4c26b88169411d578a55d3fd82103be6fade1c95ca03381a3`; alle übrigen Candidate-/Connector-/Commit-/Safetybytes bleiben gleich.

A bleibt offen, B nicht begonnen. Root integriert/reviewt und baut gegebenenfalls einen neuen Kandidaten; erst ein begrenzter nativer Vergleich kann tatsächliche Waffenbeschaffung und Combat-/Supplyverhalten belegen. Die lange NoUseful-Lücke und fehlende Receiver-/Pickup-/Damage-ACKs werden nicht als durch SDK-Tests erledigt umetikettiert.

Finaler enger Markerfolgelauf: **4175 Checks/0 Fehler, Exit0**. Die32 Fehlerpfade liefern weiterhin keinen Endmarker/neuen Versuch. Alle Compiler-/Pythonjobs beendet; sämtliche `/tmp/cecil-bridge-*`-TemporaryDirectory-Artefakte regulär gelöscht. Keine weitere Testschleife.
