# Isolierter eigener Syncpaketvergleich

> executing-plans; Root allein Runtime. Neuer getrennter A4-Worker-Worktree für begrenzte Capturevorbereitung; bisheriger Resetstand bleibt erhalten. Keine öffentlichen Prozesse oder fremden Teilnehmer instrumentieren.

**Auslöser:** Zwei öffentliche Instanzen zeigen neue externe Sync-Disconnects nach018-Rollout; eigene Bot-only-Rückrolls sind belegt. Ursachen unbekannt. Lokale020-Beobachtungsfenster sind kein WAN-/Determinismusnachweis.

**Vorhandene Belege:** `tools/analyze_retail_sync_pcap.py` versteht den belegten Retail16B-Synccheck. Frühere eigene Captures binden teilweise zwei Botports, ein anderer auch Original/PIDstarts/NetNS, aber mehrere Kartenepochen. Keine alte Datei belegt die aktuellen Fehler. Keine neue Fridaarchitektur vor reproduzierter Paketabweichung. Toolverfügbarkeit ist kein Capture-/Netemnachweis.

## Enger erster Scope

Ein fester isolierter Yodeller-Lauf mit acht eigenen Bots und einem hashverifizierten unveränderten Originalclient; explizit Build018 wie beim öffentlichen Incident. Eigene Dedicated-/Engine-/Entities-Rollen unverändert. Vorhandenen Hard-Singlemap-/Pause-/Join-/normalenClose-/Host-/FileTransaction-Controller wiederverwenden, statt neue Runtimearchitektur zu bauen. Festes600sFenster, Hard2/diag0/Map/8Bots und bisherige physischen Gates erhalten. Fehlende A4-Aktivität bleibt im Controller FAIL, wird nicht durch erfolgreichen Capture zu PASS. Kein Kartenwechsel, keine automatische Wiederholung, keine Versionsmischung.

Der Originalclient bleibt in diesem ersten Protokollversuch stationär; normale aktive Steuerung erst nach A1-ACK-Klärung. Dieser neue Versuch misst erstmals die aktuellen018-CRC-Paare einschließlich Original; keine weitere Stärkeabnahme behaupten.

- [ ] Neuer deaktivierter018-Singlemapdiagnosefork mit vollständigen Herkunfts-/Build-/Konfigurationspins. Capture als begrenztes Addon, keine zusätzlichen Gameplayeingaben oder Inventoryreads. Qualifikationsflags bleibenfalse.
- [ ] Am fertigen Neuner-Pausenbarrier VORRelease exakte eigene Server/A/B/Original-PID+Start/CWD/Cgroup/NetNS und jeweiligeUDPsocket-FDinodes∩UDPtable binden; keine Portwahl anhand späterer CRC-Ergebnisse. Feste explizite Rollenportzuordnung. Initialhandshake ist nicht erfasst und bleibt als Grenze markiert.
- [ ] Eigener tcpdump über die nachgewiesene private Server-NetNS, Interface lo und ausschließlich UDP27850. Eigener Capture-PIDstart/Namespace/Command, frische private Ausgabepfade, feste Größen-/Paket-/Zeitgrenzen. Boundzeit muss das ganze Gameplay abdecken; vorzeitigesEnde/Drop/ambigueOwnership/fehlendePaare als unvollständig oder FAIL erhalten.
- [ ] Capturestart/Readiness im pausierten Zustand beweisen. Reguläres SIGINT und begrenztes Wait, Exit-/Dropstatistik/Datei-SHA vor normalem Schließen aller vier Rollen dokumentieren. Nur nach Timeout den eindeutig eigenen Captureprozess beenden und den Cleanupfehler festhalten. Keine fremden Prozesse anfassen.
- [ ] Drei unveränderte Offlineauditoraufrufe A↔B, A↔Original, B↔Original; exakteTickbits/Sequence/Level/CRC, vollständige Nenner/fehlende/konfliktierendePaare. Ergebnis höchstens `first_differing_SAMPLED_synccheck`; kein erster20HzSimulationstick. Serverfehlerdelta und eigene Peerports dazu archivieren.
- [ ] RED→GREEN: tatsächlicheSocketowner-/Portmehrdeutigkeit/PIDreuse/namespacewechsel, vorzeitigerCaptureexit, Startfehler/Timeout/Dropstatistiken, Größenlimit, normaleSIGINT-Endquittung und Cleanup nachTSE-Teilstart. ReineStubs beweisen keineNativecapturefähigkeit. BestehendeController-/Rules-/Restoreprüfungen und Paketpins ergänzen.
- [ ] Unabhängiges Review, neue Rootcopy/Preflight, sämtliche paralleleCPUarbeit beenden; genau einRootlauf. VollständigeSchlusslogs/Byte-/Datei-/Metadatenrestore/PID-/Displayende unabhängig prüfen. Private Rohpakete/Adressen nicht veröffentlichen.

Erst nach diesem Ergebnis entscheiden: aktiveOriginaleingaben bei geklärtemA1, oder getrennt begründeter eigener Latenztest mit nachgewiesenem Restore innerhalb eigenerNetNS/Veth. Kein Host-/Produktions-qdisc, keine Kick-/Syncfrequenzänderung, kein WAN-PASS aus Netem. NativeCRC-Hooks erst bei reproduzierter Differenz und gesondertem belegt107-ABI-/Methoden-/BoundedWorkerplan.
