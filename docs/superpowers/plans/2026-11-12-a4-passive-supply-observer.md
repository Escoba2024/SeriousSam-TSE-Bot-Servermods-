# A4 – passiver Beobachter der Waffenversorgung

Basis: baec731b9e17adf0f43f22168d49a09a3d536bf7.
Worktree: /srv/tse-milestone-a-a4-passive-supply-observer-20261112.
Branch: codex/20261112-a4-passive-supply-observer.
Eigentümer: /root/identify_latest_codex. Root besitzt Integration, DLL-Build, native Läufe und Produktion.

## Ziel und Grenzen

Die zwei belegten, noch kausal offenen Bewegungsverzögerungen des A4-Build016-Laufs 104821 benötigen Beobachtungen der bereits tatsächlich berechneten Actions. Beobachtet werden nur die Kante 68→6 und die reine Annäherung an Quellpunkt 87 bei einem gemappten Waffenziel ohne Nutzwaffenbesitz. Der bestehende Schalter bot_bDiagnostics bleibt standardmäßig aus.

Die Erweiterung verändert keine Gameplayentscheidung, NAV-Daten, Casts, Zufallszahlen, Hooks oder nativen Spielerfelder. Sie benutzt die bestehende CRC-geprüfte RedStation-Bindung. Alle alten FAILs sowie die unveränderten Pickup-/Fire- und Runtime-Abnahmen bleiben bestehen.

Je Klasse und lokalem Slot gelten maximal 200 ausgegebene tatsächliche Actionproben innerhalb eines festen, strikt kürzeren 10-s-Fensters pro Mapepoche. Das ergibt maximal 1600 neue Zeilen pro Viererprozess und Mapepoche. Tod, ClearGoal, Goalwechsel und Aus-/Einschalten erneuern kein Kontingent. Ein höherer veröffentlichter Mapserial eröffnet eine neue Epoche. Identitätsbruch, rückläufige Zeit, abgelaufene Frist und nicht zugehörige Final-Aufrufe schließen das laufende Fenster.

## Umsetzung und Prüfstand

- [x] Neuer isolierter Worktree von der ausdrücklich vorgegebenen Rootbasis; persistenter Claim.
- [x] Bestehende SDK107-Bridge vor Änderungen: 2687 Checks, 0 Fehler.
- [x] Echte REDs im tatsächlichen Tick-/SafeMotion-/Final-Pfad: Aktivierung 6/2; Grenzen 50/24; Probe-Payload/Zeilenrahmung 66/2; rückläufige Zeit 68/2.
- [x] Genau 100 additive Produktionszeilen in BotSupplyNative.h; BotDriver.cpp und bestehende Tests bytegleich.
- [x] Aktivierung, beide Klassen, Identitäten, Weltwechsel, Mapreset, monotone Zeit/Ticks, 200/10-s-Grenzen, Tod/ClearGoal/echter Zielwechsel und finale Actiondaten geprüft.
- [x] Viererprozess: 2 Klassen × 4 Slots × 200 = 1600; keine Quota-Erneuerung in derselben Mapepoche.
- [x] OFF/ON-Parität über jeweils 240 Actions für beide Klassen bei freier und blockierter Safety; Bewegung, finale Action, Safety, RNG, Casts und Lookups unverändert.
- [x] Abschließender Beobachter mit SDK107 und ASan/UBSan: PID1193660, 68 Checks, 0 Fehler, Exit0, 35,48 s.
- [x] Abschließende bestehende Bridge mit SDK107 und ASan/UBSan: PID1193718, 2687 Checks, 0 Fehler, Exit0, 31,70 s.
- [x] Tatsächliche Driver-Action-Guards: PID1193697, PASS, Exit0, 1,09 s.
- [x] Source-Pins, Testreceipts, Bericht und deaktivierter Runplan vorbereitet; ausgewählte vier Dateien zur atomaren Commitaufnahme.
- [x] Native Start-/Review-/Qualifikationsgates false; kein DLL-Build, kein nativer Start, keine Runtime-/Produktionsänderung.

## Übergabe und nächste Schritte

Bericht: docs/reports/2026-11-12-a4-passive-supply-observer.md.
Private Belege: /srv/tse-a4-passive-supply-observer-evidence-20261112.
Quellpins: source-manifest.json; Root-Runplan: RUNPLAN-disabled.json.
Der abschließende Commit wird im privaten HANDOFF.json verzeichnet.

Root prüft den engen Diff unabhängig, integriert bei Annahme und baut eine neue DLL. Erst ein separat gepinntes, geprüftes natives Fenster darf die fehlenden Bewegungsdaten erheben. Eine portable Prüfung qualifiziert weder native Bewegung noch einen Pickup/Schuss; diese Abnahmen sind weiterhin offen.
