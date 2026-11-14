# Vorbereiteter Stabilitätsadapter für den aktuellen Kandidaten

**Ziel:** Die bereits vorgeschriebenen 1-/4-/8-Bot-Gates mit 3600/3600/7200 Sekunden für denselben geprüften Kandidaten und das beauftragte Hard2 vorbereiten. Kein Laufstart durch Vorbereitung oder Tests.

**Ausgangspunkt:** privater, früher unabhängig geprüfter `stability013-root-frozen-20261112`. Dessen Lifecycle, tatsächliche N+1-Population einschließlich Originalobserver, normale Closes, Modul-/Prozessbindung, vollständige FileTransaction, 75%-CPU-/1,5-GiB-RAM-/8-GiB-Disk-Grenzen und alle Dauer-/Aktivitätskriterien bleiben erhalten. Kandidat013 und seine Ergebnisse werden nicht umetikettiert.

**Enger Änderungssatz:** neue deaktivierte Kopie und eigener Namespace; Kandidatenherkunft/DLL/Buildmanifest/alle tatsächlichen Buildquellen frisch prüfen; ursprüngliche Konfiguration bis auf `gam_iStartDifficulty=2` erhalten; Hard2 nicht nur aus der Vorlage, sondern aus unveränderten nativen Sessionbytes aller Peers vor Freigabe und während jeder ohnehin vorhandenen Sessionprobe sowie aus den bestehenden Queries prüfen. Keine zusätzliche Samplingrate oder Gameplayeingabe. Der gemeinsame Kandidaten-Kampfprofilstand bleibt bytegenau kanonisch mit den physischen RosterOffsets0/4 und bereits bestehender Diagnose1.

**Abnahme der Vorbereitung:** fokussierte RED/GREEN-Prüfung für Hard2, unveränderte übrige Regeln, falsche/fehlende native Sessiondaten, Kandidatenpins, deaktivierte Runtimegates und unveränderte formale Dauern. Normalisierte Controller-/Policyänderungen vollständig vergleichen. Anschließend unabhängiger Review durch einen der vorhandenen beiden Worker; Root allein darf eine separate eingefrorene Runtimekopie erzeugen und nach frischem Exklusivitäts-/Ressourcenpreflight starten.

**Laufreihenfolge:** zunächst die offenen kurzen A1-/A3-/A4-Prüfungen und Karten-/Hardfunktion klären. Dann jeweils nur einen erforderlichen formalen Lauf durchführen; keine parallelen Compiler oder breiten Tests. Geschlossene Rohbelege, tatsächliche Laufzeiten/Last/Fehler und unabhängiger Restore sind Pflicht. Ein enger Red-Stabilitätsnachweis ersetzt weder andere Karten, First-State-Schadensnachweis, menschliches Spielniveau noch den vollständigen A-Abschluss.

**Status:** Vorbereitung begonnen, kein nativer Langlauf gestartet. Build020 bleibt experimentell, Public/Dev weiterhin Build018. Der Adapter darf vor endgültiger Kandidatenwahl nicht als Qualifikation bezeichnet werden.

**Review Focus:** keine 013-/048-Ergebnisübernahme; keine verkürzte Dauer oder gelockerte Aktivitätsgrenze; tatsächlich Hard2 statt nur Vorlagenwert; keine Dedicated-Bot-DLL-Verwechslung; kleine Population darf leere Inventar-Paddingplätze nicht als Spieler zählen; Cleanup bleibt nach jeder Teilstart-/Mess-/Budgetverletzung unabhängig ausführbar.
