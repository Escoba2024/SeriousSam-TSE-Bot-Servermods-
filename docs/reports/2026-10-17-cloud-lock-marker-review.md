# Cloud-Fortsetzung: State-/Lock-Grenzen

17.10.2026. Isolierter Branch `codex/cloud-lock-marker-validation-20261017`, Basis PR #12 `3acf2dc00b147ac8681823d1a0de0284f72e1468`. Fix-/Test-Commit `93d0f5be0edc1806081eec5440cbfb58317ec976`.

Vor Beginn alle Remote-Branches und Pull-Refs neu abgerufen; main weiterhin `39662e3757154540c1220fef0ebfcba67f5291eb`, keine neuen PR-12-Kommentare. Die dortigen Deadline-/UDP-/Guardian-/Capture-Korrekturen bleiben gemeinsam enthalten. Aktuelle main-AGENTS-/MCP-Vorgaben beachtet; keine aktive Shadow-/Hetzner-Runtime oder Spielprozesse verwendet.

## F5 – P3: beschädigte Markerstruktur wird überschrieben

`Enter-PopulationClientLocks` prüfte nach `ConvertFrom-Json` nur `$old.format -ne <bekanntes Format>`. PowerShell entpackt ein einzelnes Arrayelement, projiziert Properties über Arrays und behandelt den Vergleich mit mehreren Werten als Filter. Deshalb akzeptierte der Reader sowohl ein Array aus bekannten Markerobjekten als auch ein Array bekannter Strings im `format`-Feld. Abweichende Groß-/Kleinschreibung wurde ebenfalls akzeptiert. Diese Dateien wurden anschließend mit einem neuen Marker überschrieben.

Auf unverändertem PR #12 mit echten temporären Dateien reproduziert: Array-Root und Array-format akzeptiert, Dateibytes verändert; eine tatsächliche neuere Version `v2` dagegen verweigert und erhalten. Die neue Regression war zunächst RED mit fünf akzeptierten Formvarianten (einfaches/mehrfaches Root-Array, einfaches/mehrfaches Format-Array, abweichende Schreibweise).

Der Befund betrifft das Versprechen, unbekannte beziehungsweise beschädigte Lock-Marker unverändert zu lassen. **Kein Nachweis einer fremden Prozessbeendigung, PID-Adoption oder aufgehobener OS-Exklusivität.** Marker-PID und -Zeitstempel sind weiterhin informativ; das geöffnete exklusive Dateihandle bleibt die Lock-Grundlage.

## Minimale Korrektur und Regression

Vor dem Schreiben müssen nun alle Bedingungen erfüllt sein: Rohtext beginnt nach führendem Whitespace mit einem Objekt, geparster Root ist ein PSCustomObject, `format` ist ein einzelner String und entspricht exakt `SeriousSamPopulationClientLock/v1`. Die Rohtextprüfung ist wegen des Array-Unwrappings auch bei einem einzigen Arrayelement notwendig. Unlesbares JSON wird weiterhin abgewiesen. Leere Marker bleiben wie bisher zulässig, damit eine vor dem ersten Schreiben unterbrochene Akquisition wieder aufgenommen werden kann.

`Test-PopulationLockMarker.Tests.ps1` führt **51 Checks** auf neuen temporären Dateien und echten Dateihandles aus:

- 15 ungültige Varianten: Verweigerung, unveränderte Dateibytes und erfolgreiche Wiederakquisition des zuvor erworbenen ersten Locks nach Fehler am zweiten Lock.
- Leerer, bekannter und mit Whitespace umgebener bekannter Marker: gültige Akquisition und verweigerte zweite Akquisition bei noch gehaltenem Handle.

Diese Suite startet keine Prozesse und ersetzt keine prozessübergreifende Windows-Lock-Abnahme. Der unabhängige Reviewer fand keine umsetzbaren Befunde und führte die 51 Checks und `git diff --check` selbst erfolgreich aus. Statisch keine neue PowerShell-5.1-Inkompatibilität; Windows/5.1 wurden hier nicht ausgeführt.

## Tatsächlich ausgeführte Matrix

Debian 13, PowerShell 7.5.4, Python 3.12.14.

| Prüfung | Ergebnis |
|---|---|
| Neue Marker-Suite gegen unverändertes PR #12 | FAIL / Exit 1: fünf Struktur-/Formatvarianten akzeptiert und überschrieben |
| Neue Marker-Suite nach Fix | PASS, 51 Checks |
| Gemeinsamer Publication-Umfang nach Fix | 27 PS PASS / 0 FAIL / 7 SKIP; Python 44 PASS; Provenance-/Quellhashes 13 PASS; Exit 0 |
| Neuer separater Clone von `93d0f5b` | 27 PS PASS / 0 FAIL / 7 SKIP; Python 44 PASS; Provenance-/Quellhashes 13 PASS; Exit 0; Working Tree sauber |
| Unabhängiges Review | keine umsetzbaren Befunde; 51 Marker-Checks selbst PASS |
| Schutzprüfung | keine Änderung unter `poc/patch` oder `poc/release` gegenüber PR #12 |

Die sieben SKIPs bleiben die fünf Windows-Suiten und zwei native/private Gates aus [PR-12-Integrationsbericht](2026-10-17-cloud-supervisor-integration.md). Kein neues SKIP. Der Publication-Runner ist gegenüber PR #12 unverändert. Seine bereits geprüfte Negativprobe wurde ohne neue Runneränderung nicht erneut ausgeführt. [Bereinigte Einzelstatus](2026-10-17-cloud-lock-marker-review.json).

```powershell
pwsh -NoProfile -File poc/scripts/Test-PopulationLockMarker.Tests.ps1
pwsh -NoProfile -File tools/Test-Publication.ps1 -Evidence /new/private/evidence -Python python3
```

## Separat bestätigte Recovery-Grenze: ununterbrochener Query-Ausfall

Eine reine Loop-Probe mit synthetischen Samples bestätigte: Bereits aktive Gruppe, einmal gültiges Sample mit Readiness, danach bei weiterlaufendem Prozess nur fehlgeschlagene Queries. Über simulierte Sekunden 0 bis 60 wurden **eine Readiness-Prüfung, null ReadinessLost-Ereignisse und null JoinTimeout-Ereignisse** beobachtet. Der einzige Stop lag bei Sekunde 60 im normalen Cleanup des auf 61 Iterationen begrenzten Tests. Es gab keinen automatischen 45-Sekunden-Stop.

Grund: Eine neue Readiness-Prüfung und das erstmalige Scharfschalten einer Recovery-Deadline setzen ein gültiges Sample voraus. Eine bereits scharfe Deadline läuft bei Query-Ausfall weiter; ein zuvor bereiter Client ohne scharfe Deadline erhält durch den Query-Ausfall allein keine neue. Bei unbegrenztem Loop und ausschließlich solchen Queryfehlern ist daher keine zeitlich begrenzte Recovery zugesichert.

Dies wird als tatsächliche Policy-/Nachweisgrenze dokumentiert, ohne einen neuen Kill bei bloßem Query-Ausfall einzuführen. Cloud liefert keinen Beleg, dass ein UDP-Ausfall einen nativen Client-Disconnect beweist. Der Runtime-Agent soll vollständigen Query-Ausfall nach Readiness getrennt von gültig beobachtetem Readiness-Verlust prüfen und die offene Grenze ausdrücklich berichten. Eine universelle 45-Sekunden-Garantie ab jedem Netzausfall ist nicht gegeben.

## Wiederaufnahme, Rollback und nächstes Runtime-Paket

Keine Änderung an den bestehenden Sicherheitsgrenzen: aktiver Controller übernimmt keine alte Fleet-State-Datei; ObserveOnly steuert keine Prozesse; beschädigte Start-Receipts lösen vorhandenes Rollback aus. Der in PR #8 dokumentierte direkte Post-Launch-Rollback identifiziert weiterhin eine Menge aus EXE/Elternprozess/Startzeitgrenze, keinen einzelnen Launch. Das ist kein neuer Nachweis eines Fehlstops im begrenzten sequenziellen Controller; der Guardian verwendet für seine Kinder weiterhin gehaltene Launchobjekte. Diese Grenze wurde hier nicht durch breiteres Prozess-Suchen erweitert.

Für das nächste W1/W2-Paket aus dem Integrationsbericht **jetzt den gemeinsamen Fixstand `93d0f5be0edc1806081eec5440cbfb58317ec976`** auschecken. Zusätzlich die neue Marker-Suite unter Windows PowerShell 5.1 ausführen und echte prozessübergreifende Lockkonkurrenz, beschädigten Marker sowie freigegebene Teil-Locks belegen. Danach bleiben die begrenzten nativen Guardian-/Hard-Exit-/Deadline-/Recovery-/Human-Race-/Cleanup-Prüfungen mit unveränderter 61DC-DLL erforderlich. Den vollständigen Query-Ausfall als getrennten Fall aufnehmen. M4-Harnessquellen und Lowrender-/Vanilla-Voraussetzungen bleiben separat offen.

Der neue Fix-PR bleibt Draft; keine zusätzliche Mergefreigabe aus diesem Cloud-PASS. Keine Quell-PRs oder main remote gemergt, keine DLL verändert/qualifiziert und keine Retail-Dateien, privaten GUIDs, Credentials oder Rohlogs veröffentlicht.
