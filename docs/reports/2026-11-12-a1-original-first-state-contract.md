# A1 – Originalvertrag für den ersten gültigen Respawnzustand

Stand: 2026-11-12 UTC. Eigentümer: /root/finish_names_transaction.
**Statische Untersuchung abgeschlossen; vorhandene Entwürfe für eine native First-State-Abnahme BLOCKED.**
Kein Native-Lauf, Build, Attach, Spielzustandswrite oder Zugriff auf aktuelle Labdateien. Ausschließlich neue Dateien in /srv/tse-a1-first-state-contract-20261112. Kein neuer Fehler der produktiven Spawnschutzkonfiguration ist damit bewiesen.

## 1. Unveränderte Anforderung und Ergebnis

Der Originalauftrag verlangt, dass ein gültiger Treffer bereits im ersten serverseitig verarbeiteten Zustand nach dem Respawn Schaden verursachen und bei hinreichendem Schaden töten kann. Das ist für Bots und verfügbare Vanilla-Clients sowie nach Mapwechsel und Neustart zu wiederholen. Tote und ungültige Entitäten bleiben ausgeschlossen. Spawnverzögerung, Start-HP und sonstige Schadensregeln werden nicht geändert. Ein Konfigurationswert 0 allein ist kein Laufzeitnachweis. Quelle: request.md, Abschnitt 3, Zeilen 81–92 [R].

Der Originalcode prüft den zeitlichen Spawnschutz nur bei einem positiven Schutzintervall. Bei 0 wird diese gesamte Zeitprüfung übersprungen, also auch bei Alter 0. Daraus folgt weder, dass ein beliebiger Zeiger schon ein gültiger Spieler ist, noch dass jede beobachtete HP-Abnahme ein fremder Original-Bullettreffer im ersten verarbeiteten Zustand war. Genau diese zweite Nachweiskette ist in beiden Entwürfen unvollständig [P, DG].

Die bloße Gleichheit von Spawnclock und CurrentTick, der erste PostMoving-Aufruf und die erste zufällig gelesene Probe sind jeweils unzureichende Kennzeichnungen. Die Entwürfe behaupten ausdrücklich first_processed_state_proven=false; diese Grenze bleibt bestehen.

## 2. Nachvollziehbarer Originalablauf

| Originalstelle | Festgestellte Semantik | Bedeutung für den Nachweis |
|---|---|---|
| InitializePlayer | Behält nur INITIALIZED, LEVELSTARTED und RESPAWNINPLACE (Maske 0xa01), setzt Stand-/Physik-/Kollisionszustand und ENF_ALIVE, initialisiert Animator/Waffen; ruft am Ende TeleportPlayer(WLT_FIXED). | Der tatsächliche neue Lebensbeginn muss beobachtet werden. Init räumt NOTCONNECTED und APPLIEDACTION weg; ein zusätzlich abgewartetes ApplyAction ist deshalb keine allgemeine Voraussetzung für ursprüngliche Treffbarkeit. |
| TeleportPlayer innerhalb InitializePlayer | Führt den normalen Originalspawn aus und schreibt m_tmSpawned mit CurrentTick. | Der Spawnclock-Store liegt im Callee, nicht direkt im Init-Body. Das ist kein Init-Defekt. Ein Controller darf TeleportPlayer weder selbst aufrufen noch Placement/HP schreiben. |
| ApplyAction | Ohne INITIALIZED sofortiger Rücksprung; gegebenenfalls SetConnected; dann APPLIEDACTION setzen und normale Alive-/DeathActions. | Der erste vorhandene normale Aktionsaufruf ist ein Ordnungsbeleg. Er darf nicht künstlich als Wartepflicht eingeführt werden. |
| SetUnconnected | Setzt NOTCONNECTED, stoppt Bewegung und entfernt Teile der Gravitation/Kollision; bei bereits getrenntem Zustand keine Wiederholung. | Ein Objekt kann noch existieren und trotzdem nach Originalvertrag nicht treffbar sein. |
| SetConnected | Entfernt NOTCONNECTED und stellt Original-Gravitation/Kollision wieder her. | Ein späterer echter Verbindungsübergang muss mit seiner Reihenfolge erhalten bleiben. |
| PostMoving | Ruft Grundfunktion und normale Updates auf; ohne APPLIEDACTION SetUnconnected; löscht anschließend APPLIEDACTION. Kann auch außerhalb eines gültigen lebenden Aktionszustands auftreten. | PostMoving-Ordnungsnummer 1 ist allein kein Beweis. Damage muss nicht innerhalb dieses Callbacks liegen und es darf nicht erst dessen Rückkehr abgewartet werden. |
| ReceiveDamage | Prüft unter anderem Verbindung, gewöhnliche Immunitäten/Schadensregeln und den positiven Spawnzeitwert; danach normale Schadens-/Armorverarbeitung. | Nur der zeitliche Spawnschutz soll wegfallen. Andere Originalregeln bleiben für die Bewertung sichtbar. |

SDK-Belege: Player.es 229–241, 2717–2805, 3013–3110, 3567–3742, 4964ff., 5306, 5861, 5908 und 6548ff. [P]. Entity.h definiert DELETED=4 und ALIVE=8 [E].

Vorhandene Retail-Belege wurden mitgelesen, ohne neue vollständige Disassemblierung:
- InitializePlayer: VA 60402C40, 383 Bytes; AND 0xa01 bei 60402CD5, ALIVE bei 60402D8D, Call TeleportPlayer 60402F80 am Ende, Rückkehr 60402DBE [LI].
- Spawnclock-Store: VA 604039BA, 20-Byte-Guard, tatsächlicher Store nach player+0xc14 bei 604039C8 [DG].
- ApplyAction: VA 603FE900; INITIALIZED-Test 603FE924, NOTCONNECTED-Test 603FE92C, Call SetConnected 603FC540 bei 603FE931, APPLIEDACTION danach [AA].
- PostMoving: VA 603FC320, 354 Bytes; APPLIEDACTION-Test 603FC45F, gegebenenfalls Call SetUnconnected 603FC490, anschließendes Löschen des Flags [LP].
- ReceiveDamage: VA 603FD380, vollständiger 1395-Byte-Guard; positive Session-Einstellung und CurrentTick minus player+0xc14 [DG].

Die vollständigen Retail-Bodies von SetConnected, SetUnconnected und des autoritativen Tick-Dispatchers sind in dieser geprüften Hookclosure noch nicht gebunden. SessionState.h benennt ProcessGameTick, ProcessPredictedGameTick, ses_iLastProcessedSequence und ses_tmLastProcessedTick, liefert aber keine Implementierung oder validierten Retail-Offsets [S]. Diese Lücke darf nicht durch geratenen ABI-Zugriff geschlossen werden.

## 3. Exakte Zustandsdefinition ohne zusätzliche Spielregel

Ein Leben ist durch eigenen Serverprozess mit Startidentität und Modulen, Session-/Weltepoche, Slot, Entitäts-ID und -Zeiger sowie den tatsächlich beobachteten Original-Init-Lebenswechsel bestimmt. Nur ein gleichbleibender Spawnclock-Wert ist kein Lebensschlüssel.

Der erste gültige verarbeitete Zustand ist der früheste autoritative Original-Verarbeitungszustand nach dem normalen Lebensbeginn, in dem das Objekt vollständig initialisiert, nicht gelöscht, lebend mit positiven HP und nach Originalverbindung gültig ist. Die übrigen für den konkreten Treffer einschlägigen Originalregeln gelten weiter. Ist das Objekt bei Init-Rückkehr bereits gültig, darf der Nachweis keinen weiteren Tick, keine zusätzliche Aktion und keinen abgeschlossenen PostMoving-Aufruf verlangen. Ist es tatsächlich ungültig, zählt kein Treffer auf dieses Objekt als gültiger Treffer; der echte Übergang und seine Ursache bleiben im Ereignisverlauf erhalten.

Für eine ausführbare Einstufung fehlt noch die eindeutige Bindung dieser Ereignisse an die tatsächliche Server-Verarbeitungsreihenfolge. Ein Original-ProcessGameTick-Zähler oder ein ebenso vollständig belegtes originales Ordnungsmerkmal kann diese Beweislücke schließen. Das ist eine Messanforderung an die vorhandene Formulierung, keine neue Warte- oder Gameplaybedingung. Die genaue Retail-Eintrittsstelle und ABI müssen vor Implementierung noch statisch belegt werden. Ein Client-Prädiktionstick, ein numerischer Zeitwert oder die erste erfolgreiche Lesung ersetzt das nicht.

Ein gültiger Damage-Eintritt darf im ersten so identifizierten Zustand vor, während oder nach PostMoving stattfinden, solange der Lebens-/Gültigkeitsübergang bereits erfolgt ist. Ein späterer Treffer wird nicht durch gleiche numerische Zeit nachträglich zum ersten Zustand.

Keine zusätzlichen A1-Gültigkeitsbedingungen sind: Bodenkontakt, Stillstand, Colt als Waffe, ein bestimmter Spawnpunkt, konstante Blickrichtung oder der Frischeabstand einer externen Leseprobe. Solche Bedingungen können die normale Colt-Vorbereitung absichern, sind aber kein allgemeiner Original-Schadensvertrag.

## 4. Was ein echter fremder Original-Bullettreffer belegen muss

Der vollständige passive Beleg verbindet eine normale Eingabe/Serveraktion mit dem ursprünglichen Waffen- und Trefferpfad:
1. Eingabeversuch samt tatsächlichem Request/ACK und serverseitig verarbeiteter Aktion; kein Hook löst Input oder Damage aus.
2. Original FireColt/FireOneBullet, zugehörige Waffe und frische Shooter-Identität.
3. Original PrepareBullet, Bullet-Identität und Owner; LaunchBullet und tatsächlicher Cast-/Trefferpfad.
4. Tatsächlicher InflictDirectDamage-Aufruf auf das aktuelle Opfer mit fremdem Owner, Original-Damageart und -betrag.
5. Zugehöriger ReceiveDamage-Eintritt/-Austritt im aktuellen Opferleben und ersten gültigen Serverzustand; normale HP-/Armoränderung. Bei hinreichendem Originalschaden zusätzlich tatsächlicher Originaltod.

Die Zuordnung erfolgt über wirkliche verschachtelte Aufrufe oder belegte Ereignis-/Objektidentitäten; zeitliche Nähe allein genügt nicht. Inflictor, Shooter und Opfer müssen frisch auf ID, Welt, Lebens-/Prozessidentität geprüft werden. Ein einmal registrierter Pointer genügt nicht.

SDK PlayerWeapons.es 2105–2154 und 4092–4104: PrepareBullet setzt Owner; FireOneBullet ruft LaunchBullet(TRUE,FALSE,TRUE) und zerstört anschließend das Bullet; FireColt vermindert den Clip nach dem Originalpfad. Bullet.es 121–156 macht CastRay/ContinueCast mit bis zu zehn Casts und ruft bei tatsächlichem Treffer InflictDirectDamage mit Owner auf [W, B]. Deshalb darf der Nenner nicht pauschal ein Input = ein Bullet = ein Damage sein. Vorhandene Original-FireColt/FireOneBullet/PrepareBullet-ASM und statische Verifikation wurden verwendet [F]; die komplette Retail-LaunchBullet-/InflictDirectDamage-Bindung fehlt in den geprüften Damage-/Lifecycle-Entwürfen.

Clipabnahme und HP-Verlust auf beiden Clients sind ein begrenzter normaler Vorbereitungserfolg. Sie allein beweisen weder den fremden Bulletpfad noch den ersten Serverzustand.

## 5. Tatsächlicher Umfang und konkrete Lücken der Entwürfe

### Damage Dual V2

Der deaktivierte Entwurf bindet genau zwei eigene Originalspieler. Server, Rolle botA und Vanilla müssen alle die Original-GameMP tragen. Der Name botA macht diese Rolle daher nicht zu einem tatsächlich gesteuerten AI-Bot. Der Host ist auf die gepinnte RedStation-Welt begrenzt [D].

Stärken: voller Original-ReceiveDamage-/Getter-/TLS-Guard, doppelte Damagezustandslesung, eigener Mainthread-/TLS-Bezug, separate Zähler für unbekannte oder fremde Aufrufe, Overlap-/Abbruch-/Drop-Erkennung, begrenzte Queue und TTL, unabhängige Detachversuche und sticky Fehler. Der Same-Spawn-Tick-HP-Test ist ausdrücklich enger Tracebefund, keine First-State-Qualifikation.

Offen:
- keine Initialisierung, Verbindungs-/Aktionsfolge oder echte Serverzustandsordinal;
- keine Original-Fire-/Bullet-/Collision-Provenienz;
- Inflictor wird lediglich über registrierten Pointer aufgelöst, ohne dessen frische ID-/Welt-/Lebensprüfung;
- unbekannter Inflictor darf als Trace erhalten bleiben; der Finalizer ist bewusst kein Foreign-Bullet-Klassifizierer;
- Nenner sind Damageaufrufe, nicht vollständige Input-/Spawn-/Fire-/Bullet-/Treffergelegenheiten;
- kein ausführbarer eigener Zwei-Client-Attach-/Input-/Cleanupcontroller. Vollständiger externer Byte-Restore nach Unload/Detach bleibt Controllerpflicht.

### Lifecycle Draft

Der separate Entwurf erweitert Init und PostMoving mit vollen Originalbodyguards und begrenztem, geordnetem Lebensregister. Seine Records behalten Initgeneration, erste Postordinals, aktuelle Flags und Damage-Zuordnung. Auch hier bleibt first_processed_state_proven=false [L].

Offen:
- keine ApplyAction-/SetConnected-/SetUnconnected- oder Serverstepbindung;
- Postordinals zählen Aufrufe, keine vollständig qualifizierten gültigen Zustände;
- gemeinsame Queue und separate Lifecycle-/Damagezähler brauchen einen vollständigen gemeinsamen Endvalidator;
- kein eigener source-manifest.json, kein integrierter dual_evidence.py und kein fertiger Runtimecontroller;
- der unveränderte strikte Dual-V2-Finalizer lehnt Lifecycle-Record plus zusätzliche Snapshotfelder als unerwartetes Schema ab. Felder wegzulassen wäre keine Lösung.

Die vorhandene Datei green-lifecycle.log enthält ausdrücklich FAIL generations: 4 == 5. Die Ursache ist konkret: Die synthetische Fixture setzt max_records=4, der Fall erwartet fünf Lifecycleereignisse ohne Drain. Die eigene enge VM-Gegenprobe bestätigt: vier Plätze ergeben vier Records, einen Drop und Disable; bei zulässigen 64 Plätzen entstehen fünf Records ohne Drop. Das ist ein Testfixture-/Erwartungskonflikt bei korrekt ablehnender Queue, kein bewiesener nativer Lifecyclefehler. Alte Datei und Autorquellen blieben unverändert.

### Einordnung der Befunde

Critical: 0 neue konkrete Sicherheitsbefunde an einem ausgeführten System.
Important, vor einer First-State-Nativequalifikation zu erledigen:
- I1: vollständige Lebens-/Gültigkeits-/autoritative Zustandsordnung samt echter Bot- und Weltvariante;
- I2: kausaler Original-Fire-/Bullet-/Inflictorpfad mit frischen Identitäten;
- I3: versionierter gemeinsamer Endvalidator mit allen Nennern und Null-/Abbruchfällen;
- I4: begrenzter Zwei-Spieler-Controller, unverändert uninstrumentierte Kontrolle und vollständiger externer Originalbyte-/Prozess-/Dateirestore.

Diese Punkte sind fehlende Bausteine der erklärten Drafts, kein Anlass, deren bisherige false-Gates zu lockern.

## 6. Restore, Tests und Beweisgrenzen

Die bestehende Wiederherstellungsprüfung muss mindestens Getter 22 Bytes, ReceiveDamage 1395 Bytes, InitializePlayer 383 Bytes und PostMoving 354 Bytes sowie jeden zukünftig tatsächlich gehookten Originalbody umfassen. Alle Detach-/Drain-/Unload-/externen Vergleichsversuche müssen unabhängig erfolgen; ein früher Fehler darf spätere Cleanupversuche nicht überspringen. Ein später wieder gleicher Bytebereich löscht keine bereits dokumentierte Fehlermeldung. Modulbase, Prozessstart und Originaldateihash bleiben bindend. Interne JavaScript-Bytesameness ersetzt nicht den abschließenden externen Hostvergleich.

Ausgeführt wurden nur zwei konkrete Offline-Grenzproben: bestehendes Finalizerschema/Null-Inflictor und die Queue-4/64-Grenze. Beide Prozesse exit0; Details in probe-receipt.json, schema-probe.json und lifecycle-queue-probe.json. Keine Wiederholung der vollständigen alten Suites, kein Frida-Attach und keine native ABI-/Trampolin-/x87-/Zeitqualifikation.

68 unveränderliche Quell-/Belegdateien wurden in source-pins.json aufgenommen (864887 Bytes). Alle 37 Einträge der vorhandenen Damage-Manifestclosure stimmen. Dessen fünf Runtime-/Qualifikationsgates sind false. Dem Lifecycle-Draft wurde hier kein nachträglicher Autorenmanifest verliehen: source-pins.json ist nur dieses Reviewinventar.

## 7. Nächster Schritt

Die Root-gemeldete normale Colt-Vorbereitung 2026-11-12 17:10:44 brach vor Fire an opposite pitch gain does not reproduce ab. +12 px ergaben −3°, −12 px +6°; Root meldet Übereinstimmung beider Rollen, sechs versuchte Aktionen und bestätigten Restore. Diese Laufdaten wurden im Vertragsauftrag nicht eigenständig neu ausgewertet. Es gibt deshalb weiterhin keinen normalen Kontrollschuss, auf dessen Erfolg der First-State-Plan bauen könnte.

Zuerst die geschlossene Pitchursache getrennt anhand dieser echten Daten untersuchen und die normale Vorbereitung erneut unabhängig qualifizieren. Parallel bzw. danach kann ein neuer deaktivierter Entwurf die vier konkreten Beweislücken schließen. TRIAL-PLAN.md legt die begrenzten normalen Versuche und ihre offenen Voraussetzungen fest. Dieses Dokument genehmigt oder startet keinen Lauf.

## Quellenzuordnung

Alle exakten SHA-256 und Dateigrößen stehen in source-pins.json.

- [R] /srv/tse-milestone-a-evidence-20261111/request.md
- [P] /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
- [W] /srv/tse-sdk-20261021/Sources/EntitiesMP/PlayerWeapons.es
- [B] /srv/tse-sdk-20261021/Sources/EntitiesMP/Bullet.es
- [E] /srv/tse-sdk-20261021/Sources/Includes/Engine107/Engine/Entities/Entity.h
- [S] /srv/tse-sdk-20261021/Sources/Includes/Engine107/Engine/Network/SessionState.h
- [D] /srv/tse-combat-a1-damage-dual-v2-draft-20261112/{source-manifest.json,damage_readonly.js,damage_host.py,host_binding.py,dual_evidence.py,record_guard.py,damage_policy.py}
- [DG] /srv/tse-combat-a1-damage-dual-v2-draft-20261112/original_guards.json
- [L] /srv/tse-combat-a1-lifecycle-draft-20261112/{compose.py,lifecycle_body.js,damage_readonly.js,lifecycle_guards.json,static-proof.json,test_lifecycle.js,test_damage.js,green-lifecycle.log}
- [LI] /srv/tse-combat-a1-lifecycle-draft-20261112/initialize_player-private.txt
- [LP] /srv/tse-combat-a1-lifecycle-draft-20261112/post_moving-private.txt
- [AA] /srv/tse-a1-colt-preparation-20261112/evidence/ApplyAction.original.asm.txt
- [F] /srv/tse-a1-v5-flight-deadline-analysis-20261112/{entities-FireColt.asm.txt,entities-FireOneBullet.asm.txt,entities-PrepareBullet.asm.txt,original-static-index.json,original-static-verification.json}
