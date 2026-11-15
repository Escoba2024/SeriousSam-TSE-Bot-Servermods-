# Build026 – passiver Reacquire-Diagnosekandidat

Build025 aus `f905962ff5dab94c757518d9109f6a0ae0818a69` scheiterte tatsächlich
an MSVC C2059: Das vorhandene Windowsmakro `far` entfernte den neuen
Diagnoseparameter. Der fehlgeschlagene Build einschließlich Logs bleibt erhalten.
Der [minimale Makrofix](2026-11-15-reacquire-windows-far-macro-fix.md) hat einen
echten Compiler-RED sowie3532/0 normale und Sanitizerprüfungen; Root hat den
vollständigen Diff, die einzige Headerzeilenänderung und3532/0 selbst geprüft.

Der separate Build026 kompiliert15 MSVC-Übersetzungseinheiten und linkt mit
Exit0. Root hat47 Quell- und28 Overlaydateien tatsächlich gehasht; gegenüber
Build024 ist in beiden Mengen ausschließlich `BotSupplyNative.h` verändert.
Die DLL und das Manifest stimmen mit den Buildquellen überein.

| Artefakt | Wert |
|---|---|
| Quellcommit | `05e1708abc8b886895157b57a28e35d7375c4f29` |
| Quellbaum | `1f96c7a6d439f9f894de0dca214d56a846ddc5c5` |
| DLL-SHA256 | `2c9a238191b9642bf7f9613f01a461cf711f97fe62e581bdd7c93b5f58a9bcdd` |
| DLL-Größe |443392Bytes|
| Manifest-SHA256 | `be0513a059e2dcf5bda364ea70c4f2dee800fb084d2c44861912eaa22e186fd3` |
| Header-SHA256 | `92712d4e626fdc3a4b027aa964226b4dca5a3b89684148a36df1826ee9c6b635` |

Die neue Beobachtung protokolliert bereits erreichte Entscheidungen bei der
Wiederaufnahme der Navigation. Sie führt keine zusätzliche Suche oder
Physikprobe aus und ändert keine ursprünglichen Guards oder Aktionswerte.
Ein angenommener Wegpunktvorschlag beweist weder Bewegung noch Waffenaufnahme.
Zweck ist die Eingrenzung des [geschlossenen Skulls-Gegenbefunds](2026-11-15-build024-skulls-closed.md),
bei dem ein Bot über242,49 beobachtete Sekunden keine Zusatzwaffe hatte.

Build026 ist noch nicht nativ geprüft oder freigegeben. Es gibt daraus keinen
Skullsfix-, A4-, A1- oder Dauerstabilitätsnachweis und keine Liveänderung.
Ein eigenes deaktiviertes Skulls600s-Paket mit diag1,Hard2,achtDEMON-Bots und
unverändertem Originalbeobachter20FPS wird separat vorbereitet und geprüft.
Ein erster Root-Closurechecker suchte Compilerlogs fälschlich unter Sources/Game;
die tatsächlichen Logs liegen im Buildroot. Der Checker wurde korrigiert,
Kandidat und Manifest blieben unverändert.
