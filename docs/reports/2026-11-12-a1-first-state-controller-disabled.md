# A1: deaktivierter First-State-Endvalidator und normales Eingabeprogramm

## Umsetzung und Grenze

Die normale Colt-Vorbereitung und passive Schadensaufzeichnung genügen nicht für den geforderten ersten serverseitig verarbeiteten gültigen Respawnzustand. Dieser getrennte private Entwurf implementiert einen gemeinsamen strikten Endvalidator, einen begrenzten Normalinputcontroller und eine Offline-CLI. Er verwendet die unveränderte geprüfte Colt-Vorbereitung und das finale Observer-V2-Interface. Alle Laufgates bleiben deaktiviert.

Ein vollständig beobachteter gültiger InitializePlayer-Return darf unmittelbar der erste Anker sein. Es gibt keine zusätzliche Tick-, Action-, PostMoving-, Boden- oder Standbedingung. Außerhalb eines echten ProcessGameTick liegende Anker werden nicht dem nächsten Tick zugeschrieben. Die tatsächliche Original-EEnd-/Dispatch-/Init-Kette ist ausschließlich für behauptete normale Todesrespawns relevant und wird mit alter Lebensgeneration, kopiertem Ereignis und vollständigen Originalcaller-Bindungen verknüpft.

Die ausführbare Anfangsstufe umfasst zwei getrennte Originalclients, Vanilla/warm, zwei vorab erklärte Wiederholungen und je einen uninstrumentierten/instrumentierten Arm. Die Zielrolle beweist keine KI. Der feste Inputplan enthält normale Fire-/Release-Eingaben; Hookdaten dürfen keine Eingaben auswählen oder wiederholen. Ohne tatsächlich erfolgreiche unveränderte Colt-Vorbereitung wird das neue Programm nicht begonnen. Diese praktische Vorbereitung ist weiterhin offen.

## Fehlerverhalten und Vollständigkeit

85 Sekunden Policy, 90 Sekunden Controller, 48 Gesamtaktionen und 20 Sekunden Aim bleiben erhalten. Frische Doppelreads und letzter Budgetcheck erfolgen unmittelbar vor tatsächlicher Requestemission nach langsamen Guards und erneut nach der dauerhaften Quittung. Bereits begonnene Requests behalten sicheren Release und Cleanup. Die bestehenden Prozess-/World-/Input-/Host-/Close-/Dateirestoreguards werden übernommen.

Alle Eingaben, Zensierungen, anfänglichen und neuen Leben, Miss-/Unknown-/Fire-/Bullet-/Hit-/Damage-/Tod-/Respawnereignisse bleiben erhalten. Vorbereitung, Capture, Transport und Cleanup ersetzen keine A1-Abnahme. Ein terminaler FAIL wird nicht aus guten Teilfeldern aufgewertet.

Der Kontrollarm importiert Frida nicht. Im instrumentierten Arm werden vollständige Raw-RPCs, unabhängige Prozessidentitäten und sämtliche finalen Originalregionen erfasst. Stop, finaler Drain, Unload, Detach und externe Byteprüfung werden unabhängig versucht. Zusätzlich verlangt die Auswertung Root-eigene vollständige normale Prozess- und Dateirestorebelege.

Die daraus abgeleitete festgelegte Abnahmematrix umfasst zwölf Kontrollpaare bzw. 24 Fenster über Vanilla/echte KI und warm/Kartenwechsel/Neustart mit je zwei Wiederholungen. Die Adapter dieses Anfangspakets decken ausschließlich Vanilla/warm ab. Fehlende Zellen bleiben unvollständig. Prozesslokale Weapon-/Animatoradressen bleiben innerhalb jedes Fensters bindend, werden aber nicht künstlich zwischen getrennten Prozessen gleichgesetzt.

## Verifikation und Fortsetzung

76 tatsächlich ausgeführte fokussierte Offline-Tests sind grün. Sie prüfen den gepinnten realen Emissionspfad, späte Requestgrenzen, Cleanup trotz Fehler, Raw-/Lebensnenner, Prozess-/Registrybindung, externe Originalregionen, beide tatsächlichen V2-Respawnfixtures einschließlich Queueumzug und Original-Caller-Gegenfälle. Unveränderte Colt-/Observer-Gesamtsuiten wurden nicht wiederholt. Native ABI, praktische frühe Fremdtreffer und ausreichender tödlicher Schaden sind damit nicht nachgewiesen.

Der lokale Executor fiel während der Arbeit aus. Der persistente Zwischenstand einschließlich seines damaligen synthetischen Testfehlers blieb unverändert erhalten. Spätere tatsächliche Remote-Offlinetests und Korrekturen sind getrennt dokumentiert. Frühere private Pakete, Belege und Produktivdateien wurden nicht geändert.

Root übernimmt unabhängiges Review, getrennte Freeze-Kopie und gegebenenfalls einen einzigen vorab begrenzten Folgeversuch. Vorher müssen normale Colt-Vorbereitung und alle unveränderten aktuellen Runtime-/Fixturepins separat belegt werden. Private Pfade, Originalbytes und Rohbelege stehen ausschließlich im privaten Handoff.

## Enger V2-Nachtrag nach unabhängigem Review

Das V1-Review fand einen konkreten Zählfehler bei einer scheiternden Journalablage nach erfolgreichem Drain. V2 erfasst dasselbe zurückgegebene Paket genau einmal vor diesem falliblen Aufruf. Der eigene RED belegte tatsächlich zwei Pakete/20Ereignisse gegenüber nur einem Paket/null Ereignissen im kanonischen Nenner; GREEN stimmt mit zwei/20 überein.13 unmittelbar betroffene Prüfungen bestehen. Das unabhängige Folgereview bestätigt dieselbe Reproduktion, Reihenfolge1–20 ohne Duplikate, sticky FAIL und alle fünf Cleanupversuche: READY,0Critical/0Important für diese Integration. Alle173 V1-Dateien bleiben unverändert. Die historischen76 V1-Tests wurden nicht als neue vollständige V2-Suite wiederholt. Sämtliche Lauf-/ABI-Gates und die offenen praktischen Voraussetzungen bleiben unverändert. Details und neuer nativer Vorbereitungsfehllauf: [aktueller Abnahmecheckpoint](2026-11-12-build018-acceptance-checkpoint.md).
