# Neuer Methodenvertrag: registrierte Erstzustands- und Schadensketten

**Status: Entwurf, keine Implementierung oder Native-Freigabe.** Claim ausschließlich dieses Dokument. Root entscheidet nach Review. Der abgeschlossene NaturalAI030-FULL18-Lauf bleibt FAIL: Queue64/drop1,175 akzeptierte von183 Captures. Kein bisheriger Event wird rückwirkend herausgefiltert. Zweck des neuen Vertrags ist eine vollständige, kleinere **relevante** Messdomäne; eine bestandene Methodenprobe wäre keine A1-Abnahme.

## 1. Messdomäne und unveränderte Grenzen

Neue explizite Kennung `REGISTERED_FIRST_STATE_DAMAGE_V1`, neues Raw-/Scopeschema und eigener Validator. Alle18 bestehenden Hookstellen, Originalfingerprints, echte Callbacks, per-Role-Hashes, PID/Start/Namespace, zwei Serverakteure, Source-Ownership, Welt/Leben und Mainthread/TLS bleiben Voraussetzung. Erhalten werden alle registrierten Init-/SetConnected-/SetUnconnected-/Death-/EEnd-/Rebirth-Fakten, erste gültige GameTick-Zustände nach vollständig beobachtetem Init, ApplyAction/PostMoving/ReceiveDamage und registrierte Colt→Prepare/Fire→LaunchBullet→Cast/Continue→DirectDamage→ReceiveDamage-Ketten. Fehlender Init, unbekannter Waffenbesitzer, nicht gebundene Lebensgeneration oder nicht belegte Nachkommen ergeben INCOMPLETE/FAIL, niemals Ersatzannahmen.

Unverändert: Queue64 voller Rowpayloads;10s Beobachtung/15s TTL; TLS2s/256Calls; inneres85s/Runner90s; Frameakquisition8Attempts/.2s; IPC-Frame2MiB;8192 Order-/1024 Damagecalls/16384 native Eventkanten und bestehende Stackgrenze. Keine zusätzlichen Casts/RNG/Engineabfragen, keine Gamewrites. Der vollständige Emissionguard wird auch für jede ausgelassene Kante in derselben Auswertung und zum selben Zeitpunkt ausgeführt: Getter-Originalvergleich, globales16384-Limit, TLS, Lifetime, Stack und sämtliche bisherigen Clock-/Lifeprüfungen. Keine bedingte Guardersparnis.38 Originalregionen, Quieszenz/Unload/Detach und S/F-Cutoff bleiben bindend. Jede Verlust-, Guard-, Kapazitäts- oder Cleanupverletzung bleibt sticky. Excluded ist kein Nebenpuffer; es gibt ausschließlich die bestehende Queue64.

## 2. Einzige mögliche Auslassung, mit konservativer Grenze

Nur Mainthread-`cast_ray`/`continue_cast`, die **keinen beliebig tiefen beobachteten LaunchBullet- oder Colt-Vorfahren** haben, sind Kandidaten für Weltcast-Auslassung. Ein bloßer Blick auf den unmittelbaren Parent genügt nicht: alter Observer `observer.js:352–360` klassifiziert nur den unmittelbaren Launch-Parent; dies darf keine neue Auslassungsautorität werden. Ein beobachteter, aber ungebundener Launch-/Colt-Vorfahr bleibt erhalten und INCOMPLETE. Andere Hookarten werden nicht ausgeblendet.

Alle Aufrufe erhalten weiter am tatsächlichen Eintritt ihre echte, globale CallID, Thread-/Parentbindung und einen Frame im bestehenden begrenzten Stack (`:435–475`). Für einen Weltcast-Kandidaten wird zunächst nur dieser vorhandene Frame als „Auslassung noch offen“ markiert. Erst sein echter, geordneter Leave ohne relevanten Nachkommen bestätigt die Auslassung. **Taucht darunter irgendein sonst zu erhaltender Callback auf, ist die Probe sofort INCOMPLETE/FAIL:** dessen benötigter Vorfahr wäre bereits ohne volle Eintrittsrow; nachträglich erfundene/umsortierte Eintrittsrows oder gekürzte Parentketten sind verboten. Ebenso niemals auslassen: Nonmain/Threadwechsel, unsichere Stackbindung, fehlender Leave oder unklare Relevanz.

Das ist eine bewusste Erfolgseinschränkung. Sie vermeidet einen zusätzlichen Nebenpuffer und verspricht nicht, jede Verschachtelung erfolgreich aufzeichnen zu können. Falls ein echter relevanter Nachkomme im Weltcast auftritt oder dieser Relevanzbeweis im Sourcevergleich nicht gelingt, diese Optimierung verwerfen. Konkrete Alternative: eigener A3-artiger registrierter ReceiveDamage-Teilnachweis mit vollständigem Before/After/Inflictor, ausdrücklich **ohne** Init-/Bullet-/A1-Vollständigkeitsbehauptung; fehlende Ketten separat offen halten, keine Grenzerhöhung.

## 3. Nenner, Roharchiv und Beweispflicht

Native Entered/Completed/Active und Hook-/Threadzähler zählen weiter **alle** tatsächlichen Aufrufe. Für bestätigte Weltcasts kommen exakte Entered/Completed/Active/Excluded-Edge-Zähler und je Capture ihre Deltas hinzu. Globale16384-Kantengrenze zählt auch ausgelassene Kanten; Auslassung ist weder Drop noch ein neues Zusatzbudget. Jede offene Auslassungsentscheidung, Reentry und Nicht-LIFO-Rückkehr ist sichtbar; am akzeptierten Ende keine offenen Frames. CallIDs werden nie wiederverwendet/umgeschrieben. Volle Eventrows bekommen eine eigene lückenlose Rowsequence; sie darf nicht als vollständige Native-Kantensequenz bezeichnet werden. Parentreferenzen müssen vollständig auf erhaltene Frames auflösbar sein; andernfalls FAIL nach Abschnitt2.

Akzeptierte Pakete müssen einschließlich Pending-Übertrag exakt erfüllen: `entered_all=entered_full+entered_excluded+pending`, `completed_all=completed_full+completed_excluded`, `active_all=active_full+pending`, `native_edges=full_rows_attempted+2*completed_excluded+pending`. `entered_excluded` ist erst am **echten Leave** finalisierte Excluded-Entered-Zahl; `completed_excluded` wird ebenfalls erst dort erhöht. `pending` zählt ausschließlich aktuell offene, unentschiedene Kandidaten, die noch nicht in `entered_excluded` enthalten sind. Separate physische CandidateEntered/Completed-Zähler dürfen diese Gleichungen nicht doppelt zählen. Bestätigte ausgeschlossene Calls sind geschlossen; offene Kandidaten bleiben Pending. Rowverluste werden separat gezählt und sind fatal, niemals Excluded.

Raw-before-parse archiviert unverändert jedes tatsächliche neue Packet mit Schema/Scope, vollständigen Zählern, Status, offenen Frames und Terminallast; keine Rekonstruktion verlorener Callbackdaten. Wrapper/IPC/Archivebounds und all-attempted1..F bleiben streng. Der neue Validator verwirft FULL18 und umgekehrt; keine stillen Defaults oder Mischreplays. S/F frieren auch ausgeschlossene Nenner ein. Keine Events/Nenneränderung nach Cutoff; Tails, failed Raw,38Byte-Restore und Fehler werden vollständig geprüft.

Vor Codeabnahme erforderlich: ganzer Source-/Guardvergleich zum gepinnten FULL18, identische Relevanzklassifikation **aller erhaltenen** registrierten Ketten, identische bereits vorhandene Snapshot-/Lifeupdates und single-eval-Reihenfolge. Auslassung darf keine bisher in `emit(:124–137)` liegende Prüfung überspringen. Keine zusätzlichen Spielabfragen. Reiner Differenzial-Replay muss für jede erfolgreich zugelassene synthetische Kette exakt dieselben relevanten Callbackdaten, IDs, Parents und Lebensgrenzen zeigen; ein möglicher relevanter Verlust widerlegt den Vertrag.

## 4. Erforderliche adversariale Offlinefälle

| Fall | Zwingendes Ergebnis |
|---|---|
| Weltcast ohne Nachkommen; verschachtelte reine Weltcasts | Exakte native/excluded Nenner, keine volle Weltcastrow, echte Returns/Stackabbau |
| Colt/Launch beliebig tief vor Cast/Continue; Reentry | Vollständige ursprüngliche Kette; keine Auslassung nach bloß unmittelbarem Parent |
| Relevanter Callback innerhalb offenen Weltcasts | Sticky INCOMPLETE; keine nachgereichte Eintrittsrow/Parentfälschung |
| Unbekannter Owner/andere Waffe, Actorwechsel | Kein Damage-/Firststate-PASS, keine ungeprüfte Rollen-/Ownerübertragung |
| Fehlender Leave, Threadwechsel, Nonmain, falsche Life/Welt | FAIL; kein Zählerausgleich oder synthetischer Return |
| Sequenz-/CallID-/Nennerfehler, Drop, Queue-/Eventlimit, TTL | FAIL; alle Grenzen einschließlich ausgeschlossener Kanten wirksam |
| Interleavte registrierte Akteure, Init/Death/erste valide Zustände | Exakte getrennte Generationen und erste gültige Ticks; keine Interpolation |
| Raw-/S/F-/Restorefehler oder verspätete Kante | Sticky FAIL trotz eventuell vorhandener Schadensbeispiele |

## 5. Späterer echter Erstzustands-Schadensfall, getrennt

Erst nach erfolgreicher eigener Methodenqualifikation und Rootreview eine **neue** Spielbedingung: Original als echtes Opfer normal durch AI beschädigen/töten lassen; anschließend normale, gebundene Fire-/Respawn-Eingabe ausschließlich bei tatsächlich belegter MayRespawn-Freigabe. Keine HP-/Positions-/Winkelwrites und keine Aimkalibrierung voraussetzen. Init muss nach Arm vollständig beobachtet sein, danach erster valider Tick und tatsächliche normale/tödliche ReceiveDamage-Intervalle mit kompletter Ownershipkette. Ohne Beispiele im unveränderten Fenster: INCOMPLETE, kein automatisches Folgefenster.

Bot als Opfer braucht einen separat deklarierten gebundenen Schützenfall, etwa normale Original-Fireeingabe mit echtem Colt/Bullet/Cast-Treffernachweis. Aim-/Treffererfolg wird nicht aus Tastendruck abgeleitet. Diese Inputbedingung ist nicht Teil der inputfreien Methodenprobe und keine hier erteilte Firefreigabe. Original- und Botopfer, normal/fatal, Erstzustand und Projektilbesitzer bleiben getrennte Abnahmepunkte; vor Arm liegende Initialisierung bleibt linkszensiert.
