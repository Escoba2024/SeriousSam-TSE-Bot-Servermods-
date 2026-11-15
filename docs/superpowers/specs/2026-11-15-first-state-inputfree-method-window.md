# Inputfreier Zwei-Original-Methodenvergleich

## Herkunft und Abgrenzung

PitchRoot /srv/tse-a1-pitch-feedback-root-frozen-20261115, Manifest a2fa65092236f1b16a8fe3f2a93199e22a530ee7c61da82cfa9599e8e7d66aa7, Runner5b348963edd8333aa500bde864675fc167cc0d4fdae07445dae3de5c2fc0051a. MethodenAPI /srv/tse-a1-first-state-method-adapter-final-disabled-20261115 Manifest1e59d3268806f0ce92780c42548c876eb0ee4a09b25cb08d46532f091f86f707. Alle Eltern unverändert. Neuer privater Fork; keine Retailbytes öffentlich.

Rootentscheidung: ein Methodenvergleich besteht aus genau einem separat gestarteten control- und einem trace-Arm. Je zehn Sekunden inputfreie Beobachtung nach normalem Join; je90s Gesamtbeobachtungsgrenze mit85s innerer Grenze. Kein Retry/Autostart und keine Umwertung alter FAILs. Die Uhr parent_started wird beim Eintritt in main gesetzt; Setup verbraucht dieses Budget. Vor Beginn muss die vollständige10s-Spanne in85s passen. Ein langsamer bereits begonnener Startupaufruf kann zum gebundenen FAIL-Abschluss überlaufen; auch normaler Cleanup/Restore bleibt wie vorher separat begrenzt und regulär. Kein Roleparent wird blind beendet. Keine PASS≤90s-Gesamtlaufbehauptung ohne gemessene Gesamtdauer.

## Enger Runnerdelta

Neuer mode first-state-method mit verpflichtend festem arm control|trace; PREFIX ssam-a1-first-state-method-disabled-20261115-<arm>, Evidence a1-first-state-method-disabled-<arm>-YYYYMMDD-HHMMSS. Nur neuer Mainbody anstelle PitchPreparation, passende Initialisierung/Finalisierung und Entfernung unbenutzter Worker-/Recorderimporte. action_step/read_rotation_pair/launch/query/own_identity/normalclose/FileTransaction und Original-/Map-/Host-/Configguards bleiben unverändert. Die geerbten Eingabefunktionen werden nie aufgerufen. Endpoints/X11Transport werden nicht konstruiert, kein Fokus-/XTest-/Pointeraufruf. Stattdessen werden dieselben eigenen PID-Fenster rein über die vorhandenen xwininfo/xprop-Checks gebunden und regelmäßig unverändert verglichen. MIP/NIP-Installation, passiver EffectiveControlscheck und readonly Inventoryreader bleiben wie geerbt.

Control importiert weder Frida noch irgendeinen Worker oder MethodenAPI. Trace importiert die API erst im Arm. Genau serverOriginal + zwei eigene Originalclients vanilla/botA, kein AI-/Populationsadapter. Alter FirstStateRunner sowie ungenutzter BaseWorkerCLI und sechs geerbte Eingabe-/Collector-Gates bleiben false. AuthorRunner und Manifest false; weitere MethodenAPIgates ebenfallsfalse, Root aktiviert später separat.

## API und Cleanup

Neue authored Helperklasse MethodWindow: __init__ ist nebenwirkungsfrei; run() hält alle Handles bereits im Parentobjekt, bevor ein Start fehlschlagen kann; finish_before_roles() stop/finaldrain/unload/detach/externe38Regionen vor normaler Rollenbereinigung; finish_after_roles_closed() wird im Parentfinally NACH frischem quiescent und belegten Normalcloses+Units aller exakt3Rollen aufgerufen. Nur dann eigener Workerreap. Kein Signal an Original-/Displayrollen durch den Adapter.

NativeContext, LegacyWorkerPorts und ObserverSession unverändert übernehmen. Tracecfg:64Records/8192Calls/16384Events/1024Damage/256BindingCalls/2000msBinding/15000msTTL. Absolute Deadline=min(parent_started+85,arm_now+15); Arm3s, Drain.1s, Cleanup2s unverändert. Ein Loop mit geerbtem periodic/sample beobachtet genau10s; beide Arme ohne Input. Sämtliche Packets/Raw/Counters/Cutoff/Cleanup bleiben privat vollständig;2MiBPayload+16KiBHülle unverändert. Die72Methodenpins werden vollständig auf den eigenen method-api-Unterpfad abgebildet, externe Quellen exakt übernommen.

Eigene Finalisierung: control nur PASS_LIMITED_UNINSTRUMENTED_TWO_ORIGINALS_ONLY; trace nur PASS_LIMITED_FIRST_STATE_METHOD_OBSERVED_CALLBACKS_ONLY, wenn tatsächlich TLS gebunden, mindestens ein kompletter ProcessGameTick-Enter/Leavecall vorhanden, alter TraceValidator vollständig akzeptiert, externe38Regionen restored und alle3Normalcloses+Units/Transaktion/Logs/Hostguards erfüllt. GenericTrialEvidence ist zusätzlich, nie Ersatz oder Upgrade eines sticky FAIL. observed_callback_kinds listet ausschließlich echte Events; keine18-ABI-/Init-/Bullet-/A1qualifikation.

Rootruling: parent_started am Main-Eintritt bleibt; abgelaufenes Budget verhindert Worker/Observerarm und aktive Beobachtung sticky, kein Reset nach Join. Die unveränderten Startup-/Closebodies und deren Fristen werden nicht umgebaut.
