# Deaktivierter FirstStateV2-Methodenadapter

## Vertrag

Nur zwei eigene unveränderte Originalspieler, Rollen server/vanilla/botA. Kein AI-/Populationsadapter, kein Native-Start und kein A1-Erfolgsnachweis. Der bestehende successor-Observer bleibt hinsichtlich I1/I2, 18 Calllistener, 38 privaten Bindings, exakt zwei Registryeinträgen und sämtlichen Limits (64/8192/16384/125s einschließlich Bindingfrist) unverändert. Retailbytes bleiben privat.

Zulässige Observeränderungen: Getter+15 als echte function-Probe; host stop beendet nur neue Admission; bereits zugelassene Leaves dürfen ausschließlich innerhalb unveränderter TTL/Identitätsgrenzen fertiglaufen. Fehler, Drops und abgebrochene Leaves bleiben sticky. Separate status/finishstop-RPCs detachen erst außerhalb aller Callbacks und nach vollständiger Idle-Lage. Erfolgreiche Getter-Selbstablösung bleibt wie beim qualifizierten A3 erlaubt.

Drain und striktes I1/I2-Schema bleiben unverändert. LegacyPorts.stop antwortet erst nach admission→Idle innerhalb derselben absoluten Deadline→finishstop. Kein Timeout-Reset oder stilles Verwerfen. Ein neuer FreshExec-Worker besitzt sämtliche Fridaoperationen; der Rollenparent besitzt nur begrenztes IPC und eigene unveränderte Original-/Rollenprüfungen. Explizites finish_after_roles_closed bietet späteres Worker-Reaping; der alte Runner bleibt bytegleich und nicht ausführbar freigegeben.

Transport: maximal 2 MiB tatsächlicher Observerpayload plus höchstens 16 KiB feste IPC-Hülle. Größere Payload/Hülle wird fail-closed behandelt, niemals abgeschnitten. Vollständige rohe Antworten werden vor semantischer Validation privat archiviert. Worker-/IPCfehler bleiben sticky; sichere Originalbyte-/Unload-/Detachbereinigung wird dennoch versucht. Nach blockierendem Worker zuerst normale Rollenbereinigung, anschließend ausschließlich eigener identitätsgebundener Worker.

## Quellen

Observer: /srv/tse-a1-first-state-respawn-completion-20261112/successor/observer_body.js; Manifest 766485c5b28200b8523e74b1c597146eb2dfc905c087855d1dcc8c7f39701c00. Bindings 6cc163c5f171f013d25026f659f00b3c596b8c11e931eca32c8cfa8c951245c8. Controller: /srv/tse-a1-first-state-controller-v2-completion-20261112, Manifest fdd1b2598e21b4367e8a406d13ba3b64a22814fc40072e9377f05cbf20c8a8b3. FreshExec-/Quiescencevorbild: qualifizierter A3-Instruction-Probe-Worker. Kein Überschreiben dieser Elternpakete.

## Entscheidungsledger

Root bestätigte am 15.11.: Drain unverändert, status/finishstop separat; stop erst nach Idle/finishstop. 2 MiB+16 KiB Transporthülle, 2 MiB Payload, größere Daten FAIL. Alte Runnerintegration bleibt separater Rootauftrag. Keine zusätzliche Nutzerfreigabe erforderlich; Sourceadapter bleibt deaktiviert und ist allein kein startfähiges Nativefenster.

Rootreviewentscheidung: importierte alte WorkerProxy-Basisklasse bytegleich zur qualifizierten A3-Version mit ausschließlich True→False-Gateinverse; der ungenutzte CLI und der alte Runner bleiben auch in einer späteren Rootableitung false. Ein inputfreier Originalsmoke kann nur tatsächlich ausgeführte Callbacks qualifizieren, keine implizite 18-ABI-/Init-/Bulletabnahme.
