# Korrigierte A1-Probes: vollständige passive Actionpaare, Gameplayprüfung offen

Lauf130456 ist **FAIL**. Nach dem Attach scheiterte die bestehende Gleichheitsprüfung aller vorab gepinnten Modul-Mappingzeilen in strict_backend.py91. Der Verifier archivierte weder Rolle/Modul noch tatsächliche Abweichung. Daher sind diese Details unbekannt; Frida-bedingte Fragmentierung ist noch keine gemessene Ursache. Keine Prüfregel wurde übersprungen.

Der geschlossene Trace enthält zwei vollständige GetInput/CreateAction/Compose-Paare ohne Faults/Drops. Beide Entry-/Return-EDI-Werte passen zum gebundenen Gameobjekt. Damit ist die zuvor fehlende passive Actionkette jetzt tatsächlich beobachtet. Es gab noch keinen Gameplayinput und keine erfolgreiche Gain-, ACK- oder Schadenskalibrierung.

Ergebnis-SHA256 `3d33b79367b718bb9b38acc38bcf4634ed3493c23b566e27d18b464ce957fea5`. Expliziter vollständiger Originalbytevergleich, Scriptunload und Sessiondetach bestätigt. Alle drei eigenen Rollen regulär geschlossen, beide Displays und Worker beendet. Unabhängiger Rootrestore:664Dateien,8Absenzen,3Schlusslogs samt Metadaten bestanden. Kein A1-/Retailgesamt-PASS.

Der nächste Diagnoseschritt muss tatsächliche Mappingdifferenzen an der bestehenden Fehlerstelle archivieren und die unveränderte Assertion weiterhin auslösen. Erst anschließend darf eine belegte enge Lösung entworfen werden. Parallel ist der unabhängig vorbereitete A4-V3-Datenvertrag für genau ein neues600sHard-Red-Fenster bereit. Historische Fehlresultate bleiben unverändert.
