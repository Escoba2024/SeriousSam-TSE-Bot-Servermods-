# Build020: geordnete Hard-Beobachtung auf Red Station

Ergebnis: `PASS_LIMITED_A4_OBSERVATION_FUNCTIONAL_REVIEW_REQUIRED`. Kein vollständiger A4-/A-Abschluss, keine Livepromotion. Frühere fehlgeschlagene Läufe behalten ihren Status.

Ein isoliertes natives Retail-1.07-Fenster vom 14.11.2026, 13:12–13:23 UTC, beobachtete 600,129 Sekunden Hard2 mit acht eigenen Bots und einem unveränderten Originalclient. Beide tatsächlichen Botprozesse luden Build020 `094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0`; Dedicated und Originalclient behielten die originale GameMP-DLL. Beobachtete Respawnschutzwerte aller vier Rollen: 0.

| Botgruppe/Slot | Beobachtete Leben | HP-Tode | Tatsächliche brauchbare Inventargewinne | Gebundene Feuerflag-Beobachtungen |
|---|---:|---:|---:|---:|
| A/0 | 20 | 19 | 17 | 408 |
| A/1 | 30 | 29 | 15 | 428 |
| A/2 | 28 | 27 | 15 | 449 |
| A/3 | 25 | 24 | 15 | 391 |
| B/0 | 21 | 20 | 9 | 556 |
| B/1 | 24 | 24 | 13 | 406 |
| B/2 | 21 | 20 | 15 | 304 |
| B/3 | 23 | 22 | 17 | 442 |

Alle acht Slots haben Bewegungs-, Beschaffungs- und gebundene Feuerbelege; `missing_activity=[]`. Im Serverlog wurden 179 Killereignisse erfasst. Die längste gemessene stationäre Lebendphase betrug 9,051 Spielsekunden. Der V3-Observer behält sämtliche 13.691 erfolgreichen Gameplaybeobachtungen in tatsächlicher Leseordnung, davon 9.122 aus den fest gebundenen kanonischen Gruppen. 14.070 Leseversuche einschließlich Pausen-Smoke sind protokolliert; 376 fehlgeschlagene Versuche zählen nicht als Aktivitätsbeleg.

Feuerflags mit quellengebundenem Zählerwachstum sind keine atomaren Simulationssnapshots und kein Nachweis eines tatsächlichen Waffenfunktionsaufrufs. Die Beobachtung qualifiziert weder A1-Erstzustandsschaden noch die A3-Stufenordnung. Drei getrennte Slotphasen, positiver nativer Terminal-Watchdogpfad, Kartenwechsel-/Resetzustände und Gefahren-/Übergangsparität werden durch dieses einzelne Fenster nicht behauptet.

580 Hostmessungen: höchste gemessene CPU-Auslastung 56,818 %, mindestens 2.706.440.192 Bytes verfügbarer RAM und 9.670.295.552 Bytes freier Datenträger. Maximale Messlücke im Gameplay 1,166 Sekunden; einschließlich Startup 46,579 Sekunden. Der gespeicherte allgemeine `budget_pass_claim` bleibt **false**. Kein zusätzlicher Langzeitstabilitätsnachweis.

Alle vier Rollen wurden regulär geschlossen. Vollständige Schlusslogs enthalten keine neuen Sync-, Disconnect-, CRC-, Crash-, Invalid-Action- oder Joinfehler. Root prüfte unabhängig 640 Dateien mit SHA256 und Eigentümer-/Modusmetadaten, vier Schlussloghashes, das Ende aller gebundenen Prozessidentitäten und beider Displays: `PASS_RESTORE`. Ein Wiederanlauf aus dem Gesamtarchiv wurde nicht geprüft.

Private Evidenz: `/srv/tse-milestone-a-evidence-20261111/a4-020-hard-ordered-redstation-20261114-131207`; Ergebnis-SHA256 `fb668f2a42e51b809ba528aa6d6a3682ab699521e99ace054cdea6e3ccb1db1e`. Rootfreeze-Manifest `56f4c319551459d5c7a201d82ee75f03641232ec33d29eca7e2f86b71390fb65`, unveränderte prospektive Kriterien, 85 gezielte Offlineprüfungen bestanden. Rohlogs und Identitäten bleiben privat. Unabhängige funktionale Prüfung läuft; nächste Laufzeitoperation benötigt einen frischen Preflight.
