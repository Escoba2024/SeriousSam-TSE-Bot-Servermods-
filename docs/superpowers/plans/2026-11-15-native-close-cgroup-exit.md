# Enger Abschlussfehler: verschwindende Cgroupdatei

Status: acht gezielte Quelltests bestanden, unabhängiger Review angefordert; keine Runtimefreigabe. ON071200 bleibt FAIL; genaue
Fehlerstelle mangels Traceback unbekannt. Eine mögliche Fehlerklasse ist das
TOCTOU zwischen exists() und read_text() in RuntimeBackend.empty().

1. Gepinnten tatsächlichen Backendbody verwenden. Verschwinden zwischen
   Exists und Read deterministisch reproduzieren; RED unverändert erhalten.
2. Nur diese Methode in neuer Quelle transformieren: einmal lesen; ausschließlich
   FileNotFoundError für exakt diese Datei bei danach fehlender Datei als leer
   behandeln. Wiedererschienene Datei bleibt nichtleer; fremde Fehler propagieren.
3. Reale transformierte Methode mit Busy/Empty/Missing/Disappearing/Reappearing,
   Permission/I/O/fremdem Fehlpfad testen. Vollständige Quellinverse und fremde
   Methoden unverändert. Keine Identitäts-, Log-, Cleanup- oder Restorelockerung.
4. Neue Quelle committen/reviewbar sichern. Alte gefrorene Pakete unverändert;
   Einbindung und tatsächliche Native-Abnahme separat. Kein automatischer Retry.

Abnahme dieser Quellarbeit: tatsächliche Race-Reproduktion, alle gezielten
Gegenfälle und komplette Quellinverse. Sie beweist nicht die konkrete ON-Ursache,
keinen regulären alten Serverclose und kein fehlendes Abschlusslog.

Deaktivierte Backendkopie ohne Runner/Activation: `/srv/tse-native-cgroup-exit-disabled-20261115`.
Manifest6ce198408fcadf2bdaf99c84a1eada8ac2a4078fa099d6a18448c7c36a6b2dff;
Backend51c25f2fcf6232bbc4bd4e05d08762f6edae9e97ab7a2064f4d9a9f860e884cb.
Alte gefrorene Controller wurden nicht verändert.
