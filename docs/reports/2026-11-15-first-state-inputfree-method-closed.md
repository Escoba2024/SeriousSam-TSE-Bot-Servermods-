# Inputfreier Originalclient-Methodenvergleich: Control begrenzt bestanden, Trace fehlgeschlagen

Am 15.11.2026 wurden in der isolierten Retail-1.07-Fixture zwei echte
Originalclients mit einem unveränderten Dedicated Server geprüft. Die produktive
Flotte wurde nicht verändert. Der erste Arm war vollständig uninstrumentiert;
der abhängige zweite Arm sollte nur die neue Beobachtermethode qualifizieren.
Keiner der Arme ist ein Nachweis für Erstzustandsschaden oder A1-Abschluss.

| Arm | Ergebnis | Tatsächlich beobachteter Umfang |
|---|---|---|
|Control 05:11:15|PASS_LIMITED_UNINSTRUMENTED_TWO_ORIGINALS_ONLY|10,000165s aktives Fenster, kein Input, kein API-/Frida-Worker|
|Trace 05:13:07|FAIL|Armierung vor Attachloop abgebrochen, kein aktives Messfenster, keine beobachteten Callbacks, kein Input|

Beide Arme verwendeten denselben Rootfreeze mit Manifest
`b86615c13475f9e7dd430c4f1154b025f83fef8061865d1f7c9990de7f1c9336`.
Die Vorbereitung und alle Paketpins waren zuvor in Delta068 vollständig extern
rückgelesen und in Dateimetadaten rekonstruiert worden. Der unveränderte
Kontrolllauf braucht keine feingenaue Originalclient-Eingabe und löst die alten
Pitch-/ACK-Fehlschläge nicht auf.

## Konkreter Tracefehler

Frida läuft im Linux/Wine-Prozess. `Process.getModuleByName('Engine.dll')`
warf `unable to find module 'Engine.dll'`, obwohl die separat gepinnten
Windows-PE-Abbilder über die vorhandenen Host-Mappings lesbar waren und alle
38 vollständigen Originalbereiche vor der Armierung exakt übereinstimmten.
`moduleIdentity()` steht vor dem Attachloop; die Prüfung scheiterte somit vor
der Installation der Beobachter. Fridas Linux-Modulliste ist in diesem Pfad
keine geeignete Identifikation der eingeblendeten Wine-PE-Dateien.

Der Nachlauf blieb ebenfalls fehlgeschlagen: Die erst im Attachloop angelegten
`by_kind`-Zähler waren noch nicht vollständig vorhanden. Diese Folgeabweichung
wird nicht durch ein gelockertes Schema verborgen. Stop, Unload und Detach
wurden ausgeführt; der Worker wurde erst nach den drei normalen Spielrollen-
Closes beendet. Es gibt keinen automatischen Retry und keinen ABI-Pass aus
einem vorzeitig abgebrochenen Arm.

Root prüfte zusätzlich rein offline sämtliche 38 gespeicherten Vorher-/Nachher-
Codebereiche gegen die unveränderte vollständige HIGHLOW-Policy. Bytes und
Identität stimmen überein. Die drei zuvor festgehaltenen Beobachterfehler bleiben
bestehen; dieser enge Rücksicherungsbefund akzeptiert nicht den Tracevalidator.

## Abschluss und nächster Schritt

Für beide Fälle wurden unabhängig je 664 wiederhergestellte Dateien, neun
Abwesenheiten und drei geschlossene Logs geprüft. Die gestarteten Prozess-
generationen und Units sind beendet, Displays154/155 entfernt und alle vier
technischen Sperren frei. Die äußere Ressourcenbeobachtung zeigte im Control
51 und im Trace43 Stichproben ohne Budgetverletzung; dies sind keine formalen
60-/60-/120-Minuten-Gates. Der Trace bleibt auch im äußeren Gesamtstatus FAIL.

Der nächste eng begrenzte Fix ersetzt ausschließlich die ungeeignete
PE-Modullistensuche durch schreibgeschützte Headerprüfungen an den unabhängig
gepinnten Hostbasen. Erwartet werden exakt die Originalwerte für MZ/PE32/I386,
Headerposition und Imagegröße. Hostdatei-/Mappingidentitäten, 38 vollständige
Codebereiche, elf IAT-Prüfungen, Hookumfang und Limits bleiben bestehen.
Neue deaktivierte Vorbereitung, VM-Fehlerfälle, Rootreview und ein gesicherter
neuer Einzelfall müssen die Korrektur erst bestätigen.

Private Fälle: `a1-first-state-method-enabled-root-control-20261115-051115`
und `a1-first-state-method-enabled-root-trace-20261115-051307` unter
`/srv/tse-milestone-a-evidence-20261111`.
Resultat-SHA256: Control
`7c4bf5af2c885e74e478ff4cf4e475cd2cddf38f69095ad4cd80fe64b0c2859d`, Trace
`e682374f91601d831cccbf6f7fcf67aba3bfd84f12903546da9fe4f2e7551406`.
Zusätzlicher Rootbeleg:
`first-state-method-trace-closed-region-audit.json` im privaten Root-Belegordner.
A bleibt offen, B nicht begonnen. Keine Produktionspromotion.
