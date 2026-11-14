# Build023: einmaliges180s-Supplydiagnosefenster

> REQUIRED: executing-plans/TDD, eigenerWorktree; Root allein Integration,
> Freeze und Runtime. Keine zusätzliche Nutzerfreigaberunde.

**Goal:** Einen deaktivierten023/RedStation/180s/Diagnostics1-Controller zur
Beobachtung bereits vorhandener Supply-unavailable-Gründe bereitstellen.
**Architecture:** Exakter023-600s-diag0-Parent bleibt unverändert. Neuer rein
prüfender Diagnosepolicytyp erlaubt ausschließlich180s/diag1/RedStation/023.
Im neuen Runner werden beide bisherigen Optionsaufrufe auf diesen separaten
Typ umgebunden; bestehende Hardmap-/Vergleichspolicys selbst bleiben bytegleich.
Alle übrigen Readers, Inputs, Gameplay-, Aktivitäts-, Ressourcen-, Cleanup- und
Restoregates bleiben unverändert. Jeder Quelldelta muss exakt reversierbar sein.
**Tech Stack:** Pythonstandardbibliothek, AST-/Byte-/Hashchecks, Offline-unittest.
**Spec:** Rootauftrag nach geschlossenem023-Review ee891d3, keine Promotion.

## Globale Grenzen

- Genau EIN Fenster: Build023 unverändert, RedStation,180s,Hard2,8DEMON/tier3-
  Bots plusOriginalclient20FPS; Diagnostics1 ist ausdrücklich andereBedingung.
- Parent /srv/tse-nav20-023-red600-disabled-20261114,
  Manifest51d72a2cf233ff87d2f0cac0d3ad2a532f6f287e6ef62bd154b43e6e4ba8e5e8.
- Buildmanifest a7b057ba42cfe60eff057bddfde40436720074aa9247515990f9f92944b23080,
  DLL4dec2aa434c50ad602f1f9f136bf7f8663e9d16c5896a17ea1d343db8faf4883.
- runtime_reviewed/qualified/functional_pass/native_started bleibenFalse;
  RootreviewfreigabenFalse. Kein Retry, kein automatischer Folgearm.
- Keine DLL-, Konfigurationsregel-, Botlogik-, Memorydecoder-, Grenz- oder
  zusätzliche Inventory-/Query-/Input-/Sleepänderung. Vorhandene Diagnostics1-
  Zuweisung erfolgt ausschließlich über unverändertes cohort(role,diag).
- Zusätzliche Read-/Format-/Logkosten vonDiagnostics1 ehrlich ausweisen;
  alte600/diag0-Vergleiche, Budget-/A4-/Strength-/Syncabnahmen nicht daraus ableiten.

## Reviewfokus / spätere Belegbindung

- NeuePolicy darf ausschließlich den neuen180/diag1-Kontext zulassen; alte
  fixed600/diag0Policys müssen weiter180/diag1 strikt ablehnen.
- Namespace und Ergebnis-Scope/PASSbezeichnung eindeutigDiagnose; bisheriger
  Finalizer und alle Fehl-/Aktivitäts-/Hostgates bleiben unverändert hart.
- Vollständige139Runtime-/47Source-/28Overlaybuildpins prüfen, frisches Ziel,
  alterParentbytegleich, exakt reversiblezweiQuelldeltas; kein Runtimeimport.
- BotCecilSupplyDiagUnavailable nennt Itementity, nicht Botentity: spätere
  Auswertung muss role/local→Ownslot/Registry undgeneration→CecilState/WPO/
  nativesgleichesLeben/World/Epoch streng binden. reason/since/deadline und
  Goal-/GoalEndkontext behalten; keine tick/20-Zeitinterpolation/EPSlockerung.
- Ein gedrosselter Logtyp proSekunde/Local kann Gründe überspringen. Fehlende,
  ambige oder ungetypteBelege bleibenUNKNOWN. Kein identischer103s-Lebenslauf
  wird im neuen180s-Fenster vorausgesetzt; Zweck ist Beobachtung neuer Fälle.

## Dateien und Aufgaben

NeueDateien tools/build023_supply_diagnostic_policy.py,
tools/prepare_build023_supply_diagnostic.py,
tools/test_build023_supply_diagnostic.py; eigenerPlan/Claim/Report.
Keine Änderungen an bisherigenPolicies/Buildern/Controllern/Produktionsdateien.

- [x] NeuerWorktree/Claim vonRoot9afe402; Parent und bestehende zweiOptionsgates lesen.
- [x] RED: neuePolicy fehlt; ausschließlich180/diag1 zulässig, alle anderen
  Werte einschließlichBool/NaN/Inf abweisen; alte600/diag0Gates weiterhart.
- [x] RED: neuerBuilder fehlt; feste Quelldeltas/reverseBytes, ASTgleiche
  unveränderteFunktionen, Scope/CLIdefault180/diag1, alleFalsegates, frischePins.
- [x] MinimalerBuilder und neuePolicy; Ergebnislabel nurDiagnose vor bestehendem
  unverändertenFinalizer, keine A4-/Vergleichsfreigabe.
- [x] ZielgerichtetesGREEN mit geerbten7Build023-/6Observer20-/9Vergleichschecks;
  frischerDisabledfork, unabhängigeByte-/Pin-/Reversenachprüfung.
- [x] Report/Belege/Quittung/saubereCommits; alleJobs beenden. Rootreview und
  nativeDiagnose bleiben offen, kein automatischerStart.

Offlinefertig:29/29Tests+Generator/separaterPaketcheckPASS,69Parentquellen
bytegleich/zweiReversenexakt,140/76/46Pins. Rootreview/Freeze/nativeDiagnose
bleibenoffen; Details imVorbereitungsbericht. KeinNativeprozessgestartet.
