# A1-Kontrollprobe und passive Diagnose: geprüfter Root-Freeze

Quellen integriert bis6b2c260, unabhängiger Gesamtreview durch candidate_audit ohne kritische/wichtige Restbefunde. Root führte63 gezielte Offlinefälle aus:31Python-Controller-/Worker-/Analyzerfälle,11Collector-/Originaldateifälle,21synthetische JS-Callbackfälle; alle bestanden. Dies sind keine Retailmessungen.

Root-Freeze `/srv/tse-a1-input-trace-root-frozen-20261114`:

- Hauptmanifest `2e3bf79b98e76edad4ef04a78539a58dbe85a380a4689bd8f48a23defffc7eff`.
- Librarymanifest `8b35089195147d80e6e59aa9ad6f15f86e8e556286a8fa4b677a961b9e45dbce`.
- Runner `76558198fdced59201b52dedb5e9cb923579cb8f404991711f2f2319eb93a784`.
- Worker `176343c0864292dc40ba6d92d3dbde32f5807cc80866e8d9fb16e91d619e1448`.
- Collector `a0323bc47a6a24b3fa18c89ea3894df85e2090a69750a95f4637a58de7a7b0b0`.

a4_diagnosis prüfte den Root-Freeze anschließend unabhängig ausschließlich lesend:68Runtime-/13Library-/46Diagnosequellpins korrekt, alle Funktionskörper unverändert, zwei tatsächlich identische Quellduplikate dedupliziert. CP, JS und Originalguards bytegleich. Änderungen ausschließlich Ausführungsgates, eigener Namespace, gefrorene Pfade und entsprechend aktualisierte Metadaten. Veraltete Fire-/Einfensterbeschreibungen sind ausdrücklich als geerbte Historie erhalten; aktueller Scope zwei feste NoFire-Modi. Keine verbleibenden Quellen-/Metadatenbefunde.

Root darf genau eine uninstrumentierte Kontrollprobe und eine getrennte passive Instrumentierung ausführen, jeweils derselbe bestehende90s-Controller/85s-CP-Deckel und dieselben Eingaben bis zum zwingenden Return vor Fire. Keine Gain-/ACK-/EPS-/Zeitlockerung. Die Instrumentierung muss echte Originalsites, Timer-TID, Kontrollprofil, Spielerleben und anschließend Originalbytes belegen; sonst FAIL. Ein reproduzierter Gainfehler bleibt FAIL und liefert höchstens zusätzliche Ursachenbelege. Ein erfolgreicher NoFire-Ablauf ist ebenfalls keine A1-Schadensabnahme. Der Vergleich muss tatsächliche Kosten und gemeinsame Eingabeabschnitte ausweisen, keine passende Dauer unterstellen.

Vor jedem Start frischer Originalpreflight und Ressourcenexklusivität. Während der Messfenster keine Root-Publikation, Archive, Compiler oder parallelen Test-/Dateileser. Nur normale Rollencloses, erhaltene Schlusslogs und unabhängiger Dateirestore erlauben den nächsten Lauf. Laufende Owner-/Ended-Dateien tragen `a1-input-uninstrumented-control` bzw. `a1-input-instrumented-trace` im privaten Rootbelegordner.

Delta027 sichert vor Start den geschlossenen V2-CPU-FAIL, beide geprüften Vorbereitungen/Frozencontroller, den eigenen Frida-Methodsmoke und Quellbundle bis9da0b24.6584985Archivbytes, SHA256b00f86e20799062ec4cdb894f80826134eba2157c2465afc5f48812dba02f1fb;971Dateien/19943529Bytes separat samt Metadaten restauriert. Drive-ID1R3uP8vjbq4HItIElGP3i0RQ_NhH96vXn vollständig zurückgeladen, Größe/Hash identisch. Kein nativer Gesamtarchivrestorestart. Neue Messdaten benötigen weiteren Nachtrag.

Build018 bleibt auf allen sechs Instanzen live. A unvollständig, B unimplementiert; noch kein A1-Collector an einen TSE-Prozess angehängt und keine neue Kontrollprobe gestartet.
