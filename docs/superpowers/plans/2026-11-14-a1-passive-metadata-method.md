# A1: eigene Metadatenmethode vor passiver Retail-Beobachtung

Status: vorbereitet, noch nicht ausgeführt. Fortsetzung des [Adapterplans](2026-11-14-a1-passive-xrecord-adapter.md); Gesamtauftrag/A bleiben offen.

## Bindende Grenzen

Genau ein eigener leerer Xvfb auf :167. Keine TSE-/Wine-/Fridaprozesse,
keine XTest-, Warp-, QueryPointer- oder Gameplayeingaben. Der Root-Elternprozess
lädt keine X-Bibliothek. Zwei eigene X-Verbindungen und ein ungemapptes Fenster
prüfen ausschließlich vorhandenen DefaultGC, öffentliche Requestnummern und
XRecord-Resource→Clientbase-Auflösung. Der frühere Core-Inputmethodenlauf ist
kein Ersatz für diese neue Metadatenqualifikation.

## Aufgaben und Abnahme

- [x] Adapter92 Offlineprüfungen und unabhängigen77/69/14-Pinreview sichern.
- [x] Neue Rootkopie erstellen: nur Worker aktiv, zusätzlich fest auf mode=method
  begrenzt; Main/A1/Inputworker/Frida-Collector bleiben deaktiviert.
- [x] Bestehende qualifizierte OwnChild-/Display-/Cleanup-Helfer wiederverwenden.
  Neuer Parent ruft deren alte inputhaltige execute/run_method-Pfade nicht auf.
- [x] Unabhängiger statischer Review von Kopie, Parent, Fingerprints und Pins.
- [x] Quellen tatsächlich remote prüfen; Delta045 ins bestehende Driveprojekt
  sichern, vollständig zurücklesen und Dateihashes/Metadaten rekonstruieren.
- [ ] Frische Belegungs-/Ressourcenprüfung, Worker-STATICONLY und exklusive
  Lab-/Build-/Methodensperren; genau eine Ausführung ohne automatischen Retry.
- [ ] Ergebnis einschließlich beider normalen Prozessenden, tatsächlich
  freiem Display, Requestintervall, Fingerprints und Ressourcen sichern.

Erwarteter begrenzter Status: PASS_OWN_XRECORD_METADATA_BINDING_ONLY,
no_inputs=true, normal_closes=true, keine Fehler, identische AST-Fingerprints.
Timeout, Forcecleanup oder unvollständiger Beleg sind FAIL. Weder Gain,
Schaden, Respawnschutz noch A1-Retailabnahme werden dadurch bestanden.

Private Rootkopie: /srv/tse-a1-passive-xrecord-metadata-root-frozen-20261114,
Manifest0017b30c56c4da59f593111b548229596ec163ec2fd3760ec1feff7cf75c9dab.
Parent/Präparer liegen versioniert im privaten Restorearchiv unter RootEV.
Das deaktivierte Parentpaket bleibt bytegleich erhalten.

## Speicherentscheidung für Delta045

Die drei geschlossenen Navarme umfassen zusammen rund374MB Rohdaten. Statt
gleichzeitig zweimal die unkomprimierte Größe zu reservieren, wird stufenweise
geprüft: vor Archivierung mindestens8GiB+Rohgröße+64MiB frei; nach tatsächlicher
Kompression erneut mindestens8GiB+Rekonstruktionsgröße+64MiB. Keine Absenkung
der8GiB-Grenze. Bei Unterschreitung abbrechen, keine fremden Daten entfernen.

## Fortschritt20:10UTC

Remote435459310cd15c810778a6062132c784c59c74ff/Tree66fb7cba62901235e6fa34aceb2ee3172a1e351d exakt lokal d6f74c5. Delta04534565395B/SHA b1dbe4e97f971c59519640f940c375be84c779952b84b0b72883d941180d4fbb/Drive1Otywl1o6up7W7Zv3-YkMulRH8ampLtc0 vollständig rückgelesen;2305Dateien/388422514B samt uid/gid/mode/mtime_ns zweimal geprüft. Temporäre Rekonstruktion erst danach entfernt. Der erste Reservecheck stoppte vor Extraktion; ausschließlich frisch hashgeprüfte redundante043/044-Downloadkopien entfernt, Originalarchive und Drivekopien erhalten.

Rootparent erster Aufruf stoppte VOR jedem Kindprozess: Lablock legitimer UID65534, falsche neue Root-only-Annahme. Keine Metadatenmethode ausgeführt. Separater Parentv2 pinnt bestehende Inodes/UID/GID/Modi und nutzt unverändert exklusives flock; kein Eigentumswechsel. Exakter neuer AST-Lockblock: drei echte Sperren kurz exklusiv geprüft und freigegeben; vier manipulierte Metadatenfälle korrekt abgewiesen. Parentsha98d7fb230bbddf7de3a250a353944d613fc203c8ea45d3827015fa0f0803c166; ursprünglicher Parent und sein Review unverändert archiviert. Vor Ausführung noch Delta046 für engen Parentfix/Quittungen vollständig sichern. Kein automatischer Native-Retry und keine Toleranzänderung.
