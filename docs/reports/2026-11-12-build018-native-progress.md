# Build018: erster vollständiger Kampf-Messlauf und offener A1-Start

Stand: 12.11.2026 20:19:45 MEZ.

Build018 wurde aus dem geprüften Gameplay-Commit 1802fb3f0720b53feb032abfe2c2a83407bfea6e gebaut. Die DLL-Prüfsumme ist 6db89204e33dc7d76ecdfed68055d2b75bde4950475793a57101fd0cefcb8e4a. Der exakte Quellbaum wurde als GitHub e53d6c601a80f627047c7a3aa6b3b36b81983b8a veröffentlicht und tatsächlich wieder gefetcht. Build018 ist noch nicht für Dev oder die öffentliche Flotte abgenommen.

## Abgeschlossene A3-Fenster

| Fenster | Beobachtung | Anfangszustand | Schadensaufzeichnung | Abschluss |
| --- | ---: | --- | --- | --- |
| Kontrolllauf 185712 | 120,101417 s | alle neun Spieler streng passend | keine Instrumentierung | vier normale Closes, 640 Dateien exakt restauriert |
| MITTEL, normale Starts, 191256 | 120,035109 s | alle neun Spieler streng passend, Erfassung in 0,159560 s | 206 zugeordnete Ereignisse, null Drops/Faults, keine Spielzustandsschreibzugriffe | Originalkörper restauriert, Beobachter getrennt, vier normale Closes, 640 Dateien exakt restauriert |

Beide Fensterausgänge sind begrenzt bestanden; sie beweisen noch keine Gesamtqualität. Die Erfassung ist eine frische doppelt gelesene neutrale Anfangsphase, kein Beleg des allerersten Simulationszustands. Der Vergleich mit vertauschten Starts läuft separat als Index2. Die Lebens-, Waffen-, Schadens- und Frag-Auswertung sowie beide höheren Tiers folgen erst aus vollständigen geschlossenen Fenstern. Alte Initial-Capture-FAILs bleiben unverändert.

## A1: belegter Startfehler und begrenzte Korrektur

Der V2-Lauf 190240 scheiterte vor jeder Eingabe und vor dem Targetstart. Die Original-Konsole meldete in PersistentSymbols.ini Zeile447 einen Type mismatch beim Vergleich der FLOAT-Mausempfindlichkeit mit dem ganzzahligen Literal1. BEGIN und BASELINE_REJECTED wurden erhalten; das gewünschte Eingabeprofil wurde nicht bestätigt. Die zusätzliche strenge Schlussprüfung meldete wegen nur zwei gestarteter Rollen weiterhin roles_mismatch:cleanup. Dieser FAIL wird nicht umgewertet.

Root hat die beiden tatsächlich gestarteten Rollen, alle vier ruhenden Labverzeichnisse, beide entfernten Displays, 664 Dateihashes mit Modus/Owner/Gruppe und neun Absenzen unabhängig geprüft. Beide geschlossenen Teillogs sind gehasht. Keine Schuss-, Treffer- oder Erstzustandsaussage folgt.

Der separate deaktivierte V3-Entwurf setzt ausschließlich den Vergleichsoperand ausdrücklich auf (FLOAT)1 und verwendet eine neue Unitkennung. Die bestehende Payloadassertion ist entsprechend angepasst. 70 bestehende betroffene Tests sind bestanden. Diese Python-Prüfungen führen die Original-Konsole nicht aus. Der unabhängige Review und ein separat freizugebendes Root-Fenster stehen noch aus.

## A4 und nächste Schritte

Der Build018-Resetcontroller ist unabhängig READY mit null kritischen/wichtigen Befunden. 65 Runtime-, 41 Source-, sechs Verifikations- und 75 Buildsourcepins sind durch Root erneut geprüft. Der Root-Freeze erlaubt genau ein 480-Sekunden-Fenster mit Red → Red → Red und unveränderten 24 Slotphasen. Dieses neue Fenster ist noch nicht gestartet.

Root besitzt alle nativen Ausführungen, Builds und Integration. identify_latest_codex implementiert ausschließlich den passiven A1-Observer und Originalbindungen. finish_names_transaction prüft ausschließlich den V3-Startvergleich; anschließend sind die getrennten A1-Endvalidator-/Controlleraufgaben vorgesehen. Höchstens zwei Worker sind aktiv.

A2 bleibt abgeschlossen. A1-Erstzustand, vollständige A3-/A4-Abnahme, die 3600/3600/7200-Sekunden-Gates sowie der gesicherte Dev-zuerst-Rollout bleiben offen. B bleibt unbegonnen. Delta021 ist vollständig restauriert und von Drive zurückgeprüft; dieser spätere Stand benötigt Delta022.

[Maschinenlesbare Quittung](milestone-a-20261112/build018-native-progress.json).
