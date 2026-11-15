# Reset031: bekannte Respawnsemantik, Pickupverursacher weiterhin unbekannt

Dieses Addendum ergänzt den [geschlossenen Picker-Audit](2026-11-15-reset031-picker-closed-audit.md) für Phase 0, BotA:1/global 2, Sourcegeneration 6. Es selektiert ausschließlich acht bereits archivierte `CecilSupplyDiagUnavailable`-Zeilen aus dem gepinnten abgeleiteten Receipt. Kein Native-Log oder Inventar wurde erneut gelesen; keine neue Probe oder Verhaltensänderung.

Die vier Weaponzeilen haben tatsächlich `weapon_metadata_valid=1`, `player_index=2`, `picked_mask=0`, `picked_for_player=0`, `pickup_once=0`, `dropped=0`, `respawn=1`, `weapons_stay=0`, `render=5` und owned/usable 3/3. Die Maske ist hier bekannt, nicht wegen des frühen Render-Vetos unbekannt.

|Sourcezeile|Sourcetick|Item|raw_weapon_type|Waffenziel endet|
|---|---:|---:|---:|---|
|648|395|544|7|unavailable/render_type|
|740|421|248|9|unavailable/render_type|
|1404|821|243|5|unavailable/render_type|
|1893|1058|267|10|unavailable/render_type|

Die weiteren vier Zeilen betreffen Healthziele 368/369/370/345 (Zeilen 1458/1498/1531/1561). Dort sind `weapon_metadata_valid=0` und die waffenspezifischen Werte −1; `picked_mask=0` ist lediglich der initialisierte Platzhalter. Daraus wird keine gelesene Health-Pickupmaske abgeleitet.

`BotCecilReadItem` verwirft Render5 vor dem typisierten Weaponpfad (`BotCecilItems.h:58–76`). Der separate Diagnosepfad (`BotSupplyNative.h:691–706`) prüft dagegen lebendes WeaponItem/Weapon-Item-Klassenobjekt und liest dessen Metadaten ohne diesen Renderfilter. Ein eigener früher Fehler einer Funktion namens `ReadWeaponMetadata` liegt daher nicht vor. SDK107 `Entity.h` bezeichnet Render5 als `RT_EDITORMODEL`, nicht `RT_NONE`.

Der vorhandene SDK107-Vertrag erklärt, weshalb Maske 0 nicht zwischen fremder Aufnahme und eigener Aufnahme mit fehlendem Inventarbeleg unterscheidet: `WeaponItem.es:391–416` setzt `MarkPickedBy` nur bei WeaponsStay **und** weder PickupOnce noch Respawn. Bei den beobachteten Respawnitems wäre dieser Maskenpfad selbst bei WeaponsStay an nicht aktiv; hier ist zusätzlich der tatsächliche Sessionwert aus. Nach erfolgreichem `ReceiveItem` führt der globale Pfad zu `CItem::ItemReceived`; dessen `SwitchToEditorModel` und anschließender Respawn stehen in `Item.es:282–307`. Das ist ein Quellenvertrag und eine dazu passende Darstellung, kein nachträglich gemessener Retail-Pickupaufruf.

Auch die GameSpy-Inversion ist bekannt: die tatsächliche Sessionmeldung ist `weapons_stay=0`; `SessionProperties.cpp:341` serialisiert `sp_bWeaponsStay?0:1`, somit wäre der entsprechende rohe Querywert 1. Dieses Addendum hat keine tatsächliche GameSpy-Antwort neu gelesen und behauptet diese Sourceableitung nicht als Querymessung. Der Deathmatchzweig setzt den effektiven Sessionwert auf FALSE; ein allgemeiner Default für `gam_bWeaponsStay` beweist keinen anderen Laufzeitwert.

Das ist ausdrücklich **kein neuer Ursachenfund**. Der [bestehende A/B-Plan vom 11.11.](../superpowers/plans/2026-11-11-milestones-a-b.md) dokumentiert um Zeile 141 bereits Build004, globale Weaponrespawns/Render5 und die inverse rohe GameSpy-Semantik. [Build004-Diagnosekontrollen](milestone-a-20261111/build004-diagnostic-controls.json) belegen 25 Render5-Ablehnungen, darunter 17 bestätigte Waffen mit Respawn1 und Maske0 sowie Sessionwert0. Build031 bestätigt diese bekannte Semantik an den vier konkreten Zielen des langen Lebens. Kein Filter wird entfernt, kein Rivalenradius geändert.

**Der tatsächlich fehlende technische Beleg** ist die kausale Kette derselben Iteminstanz in derselben Welt/Epoch: aufnehmender Actor mit stabiler Identität/Life → akzeptiertes `ReceiveItem`/`ItemReceived`-Ereignis → dessen nativer Inventarübergang. Für eine Behauptung „Self hat akzeptiert, Inventar fehlt“ wären beide Seiten dieser Kette nötig; für „Rivale griff ab“ der entsprechend gebundene andere Empfänger. Vorhandene 313 Aliveproben mit Maske3 belegen den fehlenden Usefulbesitz des fokalen Lebens, identifizieren aber keinen Empfänger und keinen Inventarfehler. Zielnähe, Navankunft, SourceSubmit, Render5 oder die hier nicht gepflegte OwnPickedMask ersetzen diesen Pickup-ACK nicht. Auch vier beobachtete +10-HP-Übergänge sind keinem einzelnen Healthitem kausal zugeordnet. Eine präzise qualifizierte Item-/Empfängerbeobachtung wäre der fehlende Messpunkt; hier wird weder ein neuer Hook noch ein weiterer Nativefall implementiert oder gestartet.

Die 145 Leben/63 Usefulbesitz-Leben und alle 24 aktiven Slotphasen des vollständigen031-Audits schließen in diesem Fall die konkrete frühere 018-Lücke mit 23/24 Phasen. Das ist ein begrenzter Abnahmebeleg für diesen Fall. Die 030→031-Änderung ist diagnostisch und das Fenster verschieden: kein kausaler Gameplayfix, keine vollständige A4-Abnahme, keine Promotion. A bleibt offen, B nicht begonnen.

Privater deterministischer Selektor: `.codex/evidence/reset031-unavailable-addendum/select.py`; Aufruf mit genau einem frischen Ausgabeziel. Er verlangt den vollständigen Receipt-SHA `d14c561071ee738469871b64394e140105da606f7a117a77d74b6a31b254b201`, bewahrt alle acht Zeilenfelder, liest Quellen mit NOATIME/NOFOLLOW und schreibt exklusiv0600 mit 128KiB-Kappe und 8GiB+64MiB Reserve. Erzeugter Receipt: 9.286 Bytes, SHA `465347eae0fb4fa9f05f362c58c8e55d4c0c647fc1689e5962e52b1f9db3be62`; enthält tatsächliche Source-/SDK107-/Build004-Pins. Kein neuer Testlauf, Logreplay oder Nativevorgang.
