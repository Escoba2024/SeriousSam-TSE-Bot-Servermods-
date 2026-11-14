# XRes QueryClients: Serverrange0 eng behandeln

**Ziel:** Die belegte ungültige Positivannahme für JEDE QueryClients-Range
korrigieren; eigene Zielverbindungen weiter ausschließlich positiv und eindeutig
binden. Kein Native/Retry/Display/Input; alter Methoden-FAIL bleibt unverändert.

**Claim:** Nur `tools/xres_pid_method.py`, zugehörige gezielte Tests sowie dieser
Plan und ein neuer bereinigter Bericht. Eigener Worktree ab Root6d07a9b.
Keine Änderungen an Nativeworker, Controller, Builder oder alten Paketen.

**Befund:** Die echte erste Antwort enthält Base0/Mask2097151 plus vier normale
positive Ranges. Alle sechs abgefragten eigenen Resource-/Basepaare liefern die
richtige positive PID und sind freigegeben. Die pauschale Forderung base>3
verwirft die Hintergrundrange vor den erfolgreichen Zielprüfungen. Der spätere
12-Frees-Fehler ist Folge des Abbruchs nach einem Snapshot; tatsächliche6/6Frees
und normale vier Closings sind unabhängig erhalten, aber kein MethodenPASS.

**Protokollvertrag:** CLIENTXIDRANGE enthält CARD32-Base/Mask. Xserver
ProcXResQueryClients iteriert ab Index0 über vorhandene clients und liefert deren
clientAsMask. Die0-Range darf im vollständigen Hintergrundarray verbleiben;
keine XResQueryClientIds(0)-Wildcard hinzufügen. Für jede eigene Zielresource
weiter genau eine Range, deren Base>3, beide Resource-/Basequeries mit Success0,
Maske2/Länge4/exakter positiver OwnPID und identischer Prozessgeneration.
Bool/negative/zu große Werte, Mask0, BaseMasküberschneidung, Duplikate und
ambige Zielranges bleibenFAIL. Keine Ausnahme anhand erwarteter PID.

- [x] Primärquelle und geschlossene Antwort pinnen, genaue Positionen festhalten.
- [x] RED realistische Base0-Hintergrundrow; dazu ungültige Ranges,
  doppelte0, ambige Bereiche und falsche eigene0-Zuordnung negativ prüfen.
- [x] Minimaler Policyfix: Base0 als Hintergrund zulassen; positive eigene Base
  unmittelbar nach eindeutigem Matching ausdrücklich fordern.
- [x] Gezielte GREEN und vorhandene enge Method-/Lifecycle-/OwnChildregressionen.
- [x] Geschlossenen Snapshot ausschließlich offline gegen Policy prüfen;
  fehlender zweiter Snapshot bleibtFAIL, keine Nativeumwertung.
- [x] Bereinigten Bericht und private echte RED/GREEN-/Quellenquittung sichern;
  saubere Commits zur Rootintegration. Kein neues Ausführungspaket/Freeze.

Nächster Nativefall bleibt allein Rootentscheidung nach unabhängiger Prüfung.
Alte U UNKNOWN; keine lückenlose Lifetime-/A1-/Retailqualifikation.

Offlineabschluss: 31 gezielte Fälle PASS, keine Skips; Bericht und private Quittung
liegen vor. Kein neuer Nativefall oder Ausführungspaket erzeugt.
