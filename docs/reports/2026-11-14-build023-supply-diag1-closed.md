# Build023: geschlossenes180s-Supplydiagnosefenster

Am14.11.2026 um22:47UTC wurde genau ein isoliertes Red-Station-Fenster mit
unveränderter Build023-DLL, Hard2, acht DEMON/tier3-Bots, Originalclient20FPS
und Diagnostics1 gestartet. Keine Liveänderung oder automatische Wiederholung.

Ergebnis `PASS_LIMITED_SUPPLY_DIAGNOSTIC_OBSERVATION_ONLY`,180,091179s.
Resultat-SHA256 `caaf0e72dc26f63044d1f27d1670335ff45d314a712a0dda77427f11158217e8`.
DLL `4dec2aa434c50ad602f1f9f136bf7f8663e9d16c5896a17ea1d343db8faf4883`.
Alle vier Rollen regulär geschlossen. Keine neuen BadSync-/Disconnect-/CRC-/
Crash-/InvalidAction-/Joinfehler in den geschlossenen Rollenlogs.
Unabhängige Rootprüfung:640Dateien einschließlich Besitzer/Modus/Inhalt,
vier Abschlussloghashes und beendete PID-Generationen/Displays bestanden.

Die unveränderte pure V3-Auswertung validierte alle Gruppen und4290Leseversuche
einschließlich119protokollierter Fehlversuche; der neue Diagnosestatus blieb
unverändert.61beobachtete Leben,30mit beobachteter brauchbarer Waffe,
41Inventarzuwächse,46links-/8rechtszensierte Leben, keine widersprüchliche
Alive-nach-Tod-Folge.49serverprotokollierte gegenseitige Abschüsse.
Alle acht eigenen Bots hatten Bewegungs-, Waffenbeschaffungs- und native
FIRE-Belege;100prozentige Waffenbeschaffung pro Leben ist nicht nachgewiesen.

Längstes beobachtetes Leben ohne brauchbare Waffe: Slot8, Spawn122,2528610,
erstes Alive122,3028641 bis letztes Alive179,1063232:56,8034592s;
erster Tod179,2063293. Weitere solche Spannen:39,3497200s/Slot2 und
31,4516487s/Slot0. Dies sind geordnete Stichproben, keine kontinuierlichen
Traces. Die frühere103,7246704s-Spanne im600s-Diag0-Fenster ist ein anderer
Lebenslauf und wird durch diesen Lauf nicht rückwirkend erklärt.

Hostintervalle: maximal55,1122Prozent CPU, mindestens2698301440B verfügbarer
RAM und10194526208B freier Datenträger.47,1388620s Startlücke verhindert eine
vollständige Budgetabnahme; maximale Gameplaylücke1,1749280s.
Diagnostics1 verursacht zusätzliche Reads/Formatierung/Logs: keine direkte
Leistungs-, Stärke-, A4- oder Dauerstabilitätsabnahme gegen600s/Diag0 ableiten.

Die konkrete Auswertung aller Unavailable-Gründe mit eigener Slot-/Lebens-/
Welt-/Zielbindung läuft separat. Fehlende oder gedrosselte Gründe bleiben
UNKNOWN. Kein Gameplayfix und keine Promotion aus diesem Beobachtungsstatus.
A1, A3/A4 und formale Stabilitätsgates bleiben offen; B ist nicht begonnen.

Privat: `supply023-diag1-root-redstation-20261114-224736`, Rootquittungen
`supply023-diag1-root-restore.json`, `supply023-diag1-life-summary.json` und
`supply023-diag1-closed-summary.json`. Keine Roh-Spieleridentitäten publiziert.

Vor Start war Delta054 vollständig auf Drive rückgelesen:3983562B, SHA256
`948e1b28afa4dbc713499c8c3b91e26203c01396583abe18b913287abe10bf9a`;
892rekonstruierte Dateien zweimal gegen Inhalt/uid/gid/mode/mtime_ns geprüft.
Das laufende Diagnosedatenpaket ist darin zeitlich noch nicht enthalten.
