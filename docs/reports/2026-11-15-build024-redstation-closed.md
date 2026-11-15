# Build024: Red-Station-Beobachtung geschlossen, keine Promotion

Der einmalige isolierte Lauf mit Hard, acht DEMON-Bots, unverändertem
Originalclient bei 20 FPS und ausgeschalteter Supply-Diagnose endete nach
600,020550 Sekunden. Ergebnis: `PASS_LIMITED_A4_OBSERVATION_FUNCTIONAL_REVIEW_REQUIRED`.
Resultat-SHA256: `c6bcb9ae7e9798fe1f8ffc0178fc25bed78ecf97e4c3fb222d2edc30421fd1bc`.
Die DLL war `192169fe8396bfe1fb9c49419657b9146120c64eb3ac15095ac50a6f8659753c`
(438272 Bytes), aus Quellbaum `a1c049f440ed1600a718c07ef3fcd5477668250f`.
Die Liveflotte wurde dabei nicht geändert.

Alle acht Bots zeigen Bewegung, brauchbare Waffenbeschaffung und native
Fernwaffenfeuer-Samples. Der unveränderte Lebensanalysator validierte 13989
Leseversuche einschließlich 391 protokollierter Fehlversuche: 186 beobachtete
Leben, 90 Leben mit beobachtetem brauchbarem Waffenbesitz und 121 Erwerbsereignisse.
125 Leben sind linkszensiert, sieben rechtszensiert; einmal bleibt die
Health-Reihenfolge mehrdeutig. Es gab 172 tatsächlich geparste Server-Killzeilen.
Diese Zahlen stammen aus einer einzelnen Arena und sind kein direkter
Stärkevergleich zu Build018 oder Build023 und kein Nachweis menschlichen Niveaus.

Die längste beobachtete lebende Spanne ohne brauchbare Zusatzwaffe beträgt
50,137786865 Sekunden. Auch dieses Leben ist linkszensiert; daraus folgt keine
lückenlose Aussage über jeden Zustand des gesamten Lebens. Die neun
Grounded-Replan-Ereignisse werden getrennt vollständig den Leben zugeordnet.
Die letzte vorherige Zustandszeile hatte jeweils bereits denselben Anker wie
den später geloggten frischen Hint. Der unmittelbare Zustand vor dem Reset
fehlt; damit ist gerade die neue Stale-Anchor-Verzweigung noch nicht belegt.
Die vier längsten NoUseful-Spannen enthalten keinen solchen Replan. Der
portable, reproduzierte Ankerfehler ist korrigiert; seine konkrete native
Wirksamkeit und die Ursache der verbleibenden Beschaffungslücken bleiben offen.

Vier Rollen wurden regulär geschlossen. In ihren geschlossenen Logs gab es
keine neuen Syncabweichungen, Sync-Disconnects, CRC-, Crash-, Join- oder
Invalid-Action-Fehler. Root prüfte unabhängig alle 640 restaurierten Dateien
einschließlich Dateimengen, Inhalt, UID/GID/Modus, vier Loghashes, die beendeten
Prozessgenerationen und das entfernte isolierte Display. Diese Fixturequittung
belegt keine exakte Wiederherstellung von Datei-Mtimes.

Der unabhängige äußere Hostbeobachter deckte Start bis Parentende mit 685
Proben ab, maximaler Abstand 1,003362 Sekunden. Gemessene maximale CPU-Nutzung
72,4051 Prozent, mindestens 2520121344 Bytes verfügbarer RAM und 9640255488
Bytes freier Datenträger; keine Grenzverletzung im beobachteten Fenster.
Ergebnis `PASS_HOST_OBSERVATION_ONLY`, ausdrücklich keine formale A-/B-
Ressourcen- oder Dauerqualifikation. Der interne Beobachter allein hatte beim
Start eine 46,63-Sekunden-Lücke; diese wird durch den äußeren Verlauf nicht
aus seinem eigenen Ergebnis entfernt.

Die 1-/4-/8-Bot-Dauergates, Originalclient-Schadensabnahme, vollständige
Kartenmatrix und belastbaren Schwierigkeitsvergleiche bleiben offen. Build024
wird nicht auf Public oder Dev promoviert. A ist offen, B nicht begonnen.

Private Belege bleiben außerhalb des öffentlichen Repository: geschlossener
Fall `nav20-024-root-redstation-20261114-235458`, Root-Restorequittung,
unveränderter vollständiger Lebensanalysator-Auszug und äußerer Hostverlauf.
Das vor dem Lauf vollständig rückgelesene Delta057 sichert dessen Vorbereitung;
die neuen geschlossenen Rohdaten gehören in Delta058.
