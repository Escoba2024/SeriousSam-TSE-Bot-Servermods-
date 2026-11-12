# A1: normale Colt-Vorbereitung nach frischer Originalkalibrierung

Status: OFFLINE READY FOR INDEPENDENT REVIEW, Runtime deaktiviert.
Owner: /root/review_names_transaction. Base 47a819ab9b48244847fd43f401c7902c1b059d27.
Worktree /srv/tse-milestone-a-a1-colt-preparation-20261112.
Privater Entwurf /srv/tse-a1-colt-preparation-20261112.
Nur Root integriert und startet native Fenster. Alte V5-Pakete und alle FAILs bleiben erhalten.

## Ziel

Mit den beiden bestehenden Originalclients normal und begrenzt auf den jeweils anderen eigenen
Spieler ausrichten und mit dem tatsächlich vorhandenen Colt feuern. Reale ursprüngliche
Waffen-/HP-Zustände archivieren. Kein Bouncer, Minigunpickup, Engineaufruf, Zustandswrite oder Hook.
Eine Vorbereitung beweist weder vollständige Bullet-/Fremdschadenprovenienz noch First-State.
Fehlender Feuer-/HP-Nachweis bzw. ungeklärte Sicht-/Trefferlinie bleibt ausdrücklich FAIL/offen.

## Designentscheidung

Der bereits von RD geprüfte Vanilla-Originalclient wird Schütze; der zweite Originalclient bleibt
Ziel und erhält keine neue Eingabe. Die vorhandene RD-Yawkalibrierung bleibt unverändert.
Der aktuelle Reader enthält nicht genug Geometrie: benötigt werden der tatsächlich gelesene
Original-Viewpoint, Animator-EyesYOffset, aktuelle Coltparameter und der gebundene Original-Zielmittelpunkt.
Ein neues explizites Opt-in liest nur belegte Retailfelder und prüft sie im selben doppelten Read.
Default-Reader und bestehende Diagnose bleiben unverändert.

Die native Originalkette ist CalcWeaponPosition -> PrepareBullet -> FireOneBullet -> CBullet.
Die Mündung enthält aktuelle Waffen-X/Y/FOV-Parameter und EyesYOffset; Fußposition + geschätzte
Augenhöhe ist nicht zulässig. SDK-Referenz muss durch Original-Retail-Instruktionen/Datentabellen
gegengeprüft werden. Falls Pitch korrigiert werden muss, wird sein Gain separat mit begrenzten
normalen Gegenimpulsen und frischen beiden Lesern bestätigt; Yawgain wird nicht geraten als Pitchgain.
Alle normalen Mausimpulse bleiben auf maximal 12 Pixel pro Achse und alle Aktionen gemeinsam auf 48 begrenzt.
Ein quantisierter Mausimpuls ist keine Exactly-once-Kugelbehauptung.

## Arbeit

- [x] 1. Original-Viewpoint/Animator/Coltparameter/Zielmittelpunkt/Pitch-ACK/Coltclip statisch binden;
      genaue Byteguards, SDK-/DLL-Pins und Grenzen festhalten. Keine neuen Prozesslesungen.
- [x] 2. Enges Spec fertigstellen: notwendige Leserfelder, Normalinputablauf, feste Budgets,
      Aussagen zur quantisierten Ausrichtung, Sicht-/Treffer-/HP-Grenzen.
- [x] 3. Reproduzierbare RED-Fälle gegen tatsächliche neue Reader-/Controller-/Endpointfunktionen:
      falsche/fehlende Geometrie, zweiter Read verändert, falsche Gainrichtung/ACK, Leben/Welt,
      alte/verspätete Probe am tatsächlichen Request, abgelaufene lokale/globale Deadline,
      kein Fire ohne gültige neue Ausrichtung, fehlender Feuer-/HP-Beleg, kein weiterer Input nach Fehler.
- [x] 4. Minimale Implementierung in neuem deaktiviertem privaten Paket.
      Bestehende Bootstrap-, Identitäts-, Namespace-, World-, Ressourcen-, Release-, Close- und Restorehülle erhalten.
- [x] 5. GREEN und relevante erhaltene Regressionen wirklich ausführen; nur konkrete notwendige Erweiterungen.
      Tests sind reine Speicher-/Dateitests ohne native Eingabe, Prozessattach oder Compiler.
- [x] 6. Originalpakete bytegleich prüfen; Manifest/Importclosure, normalisierter Delta und Testquittung einfrieren.
      Runtimegates false. Dokumentation im isolierten Worktree committen; Root übernimmt Review/Freeze/Native.

## Harte Abnahme für den Entwurf

- Keine Callbacks/Imports mit nativen Seiteneffekten vor der bestehenden vollständigen Closure.
- Nur unveränderte Originalmodule/selbe tatsächliche eigene Spieler, Process/start, Life/World und Modulidentität.
- Frische explizit angeforderte doppelte Server-/Originalclientbelege; niemals ältere günstige Proben auswählen.
- Langsame Endpoint-/Display-/Focusguards vor dem letzten Zustands-/Budgetcheck unmittelbar vor XTest.
- Safe Release unabhängig von abgelaufenen Deadline- oder Zielzuständen.
- Controller 90 s / Policy 85 s / Host75% und bestehende Ressourcenminima unverändert.
- Jede versuchte Aktion, Requestgrenze, Fehler-/Teilprobe und Releasequittung erhalten.
- Clip-/Firezustand und HP-Veränderung als beobachtete Zustände ausgeben, nicht als erfundene Bullet- oder First-State-Coverage.
- Die spätere echte A1-Abnahme bleibt wiederholt Bot/Vanilla, Mapwechsel/Neustart und lückenloser erster Zustand.

## Abschlussbelege

223/223 private Tests in 2,674 s; 32/32 bestehende Readertests gegen den neuen privaten Reader in 0,059 s. 50 vorhandene Schutz-/Lifecyclefunktionen AST-identisch, neun wesentliche Dateien bytegleich. Alle 172 Dateien des V5-Autorenpakets, 172 des Root-Freeze und 684 des ursprünglichen CPU-FAILs exakt erhalten; Resultat153533 ebenfalls unverändert gepinnt. 14 Original-Byteguards gegen Originaldateien und Relokationen geprüft. Frische Posen/LOS/Trefferwirkung sind ausschließlich im späteren Root-Fenster zu beobachten. Kein Native/Build in dieser Vorbereitung.

Der einzige zulässige nächste Ausführungsschritt nach unabhängigem Review ist eine getrennte Root-Freeze-Kopie mit frischem Preflight. Ein späterer fehlender HP-Beleg bleibt FAIL/LOS offen; keine automatische Bewegung oder Eingabewiederholung. Der eigentliche First-State-Damage-Auftrag bleibt gemäß HANDOFF.md offen.
