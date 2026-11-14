# Eigene XRecord-Metadatenbindung begrenzt bestanden

Genau eine tatsächliche Methode auf einem eigenen leeren Display167:
**PASS_OWN_XRECORD_METADATA_BINDING_ONLY**, abgeschlossen14.11.2026 gegen20:12UTC.
Keine TSE-/Wine-/Fridaprozesse und keine Zeiger-, Tastatur- oder Spieleingaben.
Das ist weder eine A1-Abnahme noch ein Fix der Eingabeverstärkung.

Der unveränderte geprüfte Methodenkörper öffnete zwei eigene X-Verbindungen,
erstellte ein ungemapptes1×1-Fenster und prüfte DefaultGC/GContext sowie
Resource→Clientbase-Auflösung in deaktivierten XRecord-Kontexten. Unterschiedliche
Verbindungsbasen wurden strikt verlangt. Das öffentliche Requestintervall war
16→26. Ein solcher Clientbasewert bezeichnet eine X-Verbindung, keinen Prozess.

| Nachweis | Ergebnis |
|---|---|
| Fehler |0|
| Metadatenworker |Exit0, normal geschlossen und eingesammelt|
| Eigener Xvfb |Exit0 nach normalem SIGTERM, eingesammelt|
| Erzwungenes Cleanup |nein|
| Display/Lock nach Ende |tatsächlich abwesend|
| Wandzeit |0,338262s|
| Elternprozess-CPU |0,006242s|
| Kinder-CPU gesamt |0,372391s|
| Kinder-MaxRSS |166732KiB|
| Freier Datenträger am Ende |9022939136B|

Alle drei Funktions-AST-Fingerprints und das unveränderte Native-Modul stimmen
mit dem zuvor geprüften deaktivierten Adapter überein. Anschließend wurden beide
eigenen Prozessgenerationen unabhängig als beendet, Displays154/155/167 als frei
und alle drei Sperren erneut exklusiv prüfbar bestätigt.

Resultat SHA256:
`81c402edfb083d957daa21b12d9901303fea97204c8b661506d2a1fce9dd8135`.
Privat: RootEV/a1-passive-metadata-method-root-20261114/result.json und
RootEV/a1-passive-metadata-root-closed-review.json. Die fehlgeschlagene erste
Root-Vorprüfung bleibt dokumentiert: Sie startete kein Kind und verlangte
fälschlich Root-Eigentum auch für die legitime gemeinsame Lab-SperreUID65534.
Der getrennte Parentv2 prüft deren bestehende Inodes/UID/GID/Modi und verwendet
weiterhin exklusives flock; die Sperren wurden nicht verändert. Drei echte
Vorprüfungen und vier abgewiesene Metadatenänderungen sind belegt.

Vor Ausführung waren alle Quellen in045/046 gesichert und vollständig aus dem
bestehenden Driveprojekt zurückgelesen. Delta045:34565395B,
SHA`b1dbe4e97f971c59519640f940c375be84c779952b84b0b72883d941180d4fbb`,
2305Dateien/Metadaten zweimal geprüft. Delta046:100296B,
SHA`f64d3d562062978b0abdd0052a950c4f0f7ef7faa6f513b9261e794e89afd27b`,
10Dateien/Metadaten zweimal geprüft. Keine vollständige Retail-Wiederinbetriebnahme
aus dem Archiv behauptet.

Nächster Schritt: eine separate Rootkopie für die bereits vorgesehenen eigenen
Originalclient-Kalibrier-/Aim-Eingaben, ergänzt um passive XRecord-Beobachtung.
Keine zusätzlichen Eingaben, kein Feuer und keine Änderung der CP-/ACK-/Gain-
Toleranzen oder Zeitgrenzen. Mainfreeze vorbereitet, Review/Sicherung noch offen.
Live bleibt gemäß Nutzerwunsch Dev048, RedGen2 und vierPublic018.
