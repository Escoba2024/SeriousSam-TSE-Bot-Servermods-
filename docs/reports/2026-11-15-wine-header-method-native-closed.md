# Wine-Headerpfad nativ erreicht; Methoden-Trace bleibt fehlgeschlagen

Der isolierte Retail-1.07-Trace vom15.11.2026,05:40:21 erreichte mit Rootfreeze
`92fff30d638ac3e73562ce02765bb0d3241ef8e403fe0d74bd4be978d9823a95`
die Armierung. Der vorherige Fehler der Linux-Modulliste trat nicht erneut auf.
Dies belegt die begrenzte Lesbarkeit der neuen Headerprüfungen in diesem echten
Wine-Prozess; es ist weder Methodenabnahme noch ein Nachweis für Erstzustandsschaden.

**Gesamtergebnis: FAIL.** Beim ersten TLS-Getter-Callback entstand
`getter restore mismatch after binding`. Im aufgezeichneten Ablauf stehen genau
zwei beobachtete Calls: Eintritt in `process_game_tick`, danach Eintritt in
`apply_action`, ein Getteraufruf, ein Fault und zwei abgebrochene Leaves. Es gibt
keinen vollständigen qualifizierten Callbackzyklus und kein aktives10s-Messfenster.
Die Folgefehler im Transport-/Stop-/Nachlaufvalidator bleiben erhalten.

Die unmittelbare Vollbytesprüfung steht nach dem eigenen `detach()` noch
innerhalb desselben Getter-Callbacks. Laut [offizieller Frida-Dokumentation](https://frida.re/docs/javascript-api/#interceptor)
werden ausstehende Änderungen beim Verlassen der JavaScript-Laufzeit oder
bei `send()` verarbeitet. Das macht einen zu frühen Prüfzeitpunkt plausibel;
der konkrete Lauf zeichnet keine interne Frida-Commitreihenfolge auf und beweist
diese Ursache daher noch nicht abschließend. Der bereits verwendete A3-Pfad
prüft nach dem eigenen Getter-Detach erst bei späteren Lifetime-/Drain-Grenzen.

Der nächste begrenzte Fix muss genau diese Commitgrenze in der tatsächlichen
Observer-VM nachbilden. Vollständige Originalgetterbytes bleiben vor jeder
späteren emittierten Beobachtung und vor jedem Drain erforderlich, auch nach
Stop oder ohne weiteren Callback. Keine Toleranz-, Limit-, Schema- oder
Gameplayänderung und kein expliziter unsicherer Flush sind vorgesehen.
Alte Pakete und beide nativen FAILs bleiben erhalten.

Alle drei gestarteten Spielrollen wurden normal geschlossen. Worker und Parent
sind beendet; Unload/Detach wurden ausgeführt. Root prüfte unabhängig664Dateien,
neun Abwesenheiten, drei geschlossene Logs, Prozessgenerationen, Units, Displays
und alle vier technischen Sperren: PASS_RESTORE05:41:28. Zusätzliche pure Prüfung
05:41:56: alle38 gespeicherten vollständigen Original-Codebereiche vor/nachher
exakt zur unveränderten HIGHLOW-Policy, Identität gleich. Dies akzeptiert keine
fehlgeschlagene Observerqualifikation.

Die äußere Hostbeobachtung umfasst44Stichproben, maximale gemessene CPU69,898%,
mindestens2.723.041.280Bytes verfügbaren RAM und10.898.923.520Bytes freien Speicher,
maximale Abtastlücke1,001422s. Keine Budgetverletzung wurde beobachtet; Childexit1
führt dennoch zu FAIL_HOST_OBSERVATION. Kein formales Langzeit- oder Budgetgate.

Der uninstrumentierte Control051115 wurde mit enger separater Quellenprüfung
weiterverwendet: Runner bis auf zwei private Namespaces bytegleich, zehn aktive
Helfer und aktuelle Original-/Welt-/Fixturepins unverändert. Das ist ein weiterhin
historischer begrenzter Kontrolllauf, kein neu ausgeführter Control.

Private Rohdaten: `/srv/tse-milestone-a-evidence-20261111/a1-first-state-wine-identity-root-trace-20261115-054021`.
Resultat-SHA256:
`2c0cdcd772864a3a97904dd04f6bfd954483163fe8a69e20267fb9f14ef8dd71`.
Rootbelege `first-state-wine-identity-trace-root-restore.json` und
`first-state-wine-identity-trace-closed-region-audit.json` liegen im privaten
Root-Belegordner. Die gesamte Vorbereitung war vor Ausführung in Delta070
vollständig extern rückgelesen und mit allen215Dateimetadaten geprüft worden.
Der neue geschlossene Fall muss separat in Delta071 gesichert werden.
A offen, B nicht begonnen; produktive Flotte unverändert.
