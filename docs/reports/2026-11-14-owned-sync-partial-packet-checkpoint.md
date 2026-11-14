# Eigener Originalclient:456 übereinstimmende Syncvergleichspunkte

**GesamtlaufFAIL**, weil der feste600s-Versuch vorzeitig abbrach.
Versuch`own-sync018-json-root-20261114-150433`, Result-SHA256
`75eb5fa3333f7962463f58df98030336f3e5538e038094689b20f14cd783880e`.

Die Pausebarriere wurde freigegeben und Build018/Yodeller/Hard2/Diagnostics0
mit acht eigenen Bots und einem stationären Originalclient tatsächlich
aufgezeichnet. Die laufende Bindungsprüfung traf später einen inzwischen
geschlossenen Linux-Dateideskriptor46 in botB. Das aufgelistete readlink-Ziel
existierte beim Lesen nicht mehr; seine frühere Art ist nicht archiviert.
Kein geänderter UDP-Socket oder Spielprozesscrash daraus abgeleitet.

Capture normal mit SIGINT und Exit0 geschlossen:58088Pakete erfasst,
116368vomFilterempfangen,0KernelDrops. PCAP18863432Bytes,
SHA256`3612c085169c6f6204602ca29a63dfc10255fc3bc8c9efd43f6ce6a807adfa6a`.

| Tatsächlich gebundene Rollen | Paare | Gleich | Abweichend | Fehlend/Unsupported/Fragment/Konflikt |
|---|---:|---:|---:|---|
| botA↔botB |456|456|0|je0|
| botA↔Original |456|456|0|je0|
| botB↔Original |456|456|0|je0|

Die drei unveränderten Auditorläufe melden jeweils
`MATCHING_SAMPLED_SYNCCHECKS_ONLY`. Das ist ein positiver Teilbefund für die
tatsächlich erfassten Vergleichspunkte. Kein vollständiger600s-PASS,
keine20Hz-Vollständigkeit, kein erster Simulationstick, kein aktiver
Originalinput-/WAN-/Stunden- oder allgemeiner Stabilitätsnachweis.
Die öffentlichen Red-/Yodeller-Syncvorfälle sind damit nicht reproduziert
oder erklärt. Ihre früheren Fehler bleiben bestehen.

Capture-/Setup-Kinder beendet; alle vier Spielrollen normalgeschlossen.
Root verifizierte unabhängig640Dateien mit Metadaten, vier Schlussloghashes,
Prozessidentitäten und Displayende:PASS_RESTORE.454Hostproben:
CPUmax64,020%,RAMmin2666876928Bytes,Diskmin8789520384Bytes,
Gameplay-Abtastlücke maximal1,151s. Startup-Lücke46,928s und
allgemeinerBudgetclaimfalse bleiben ausgewiesen.

Nächster enger Offlinefix gemäß [FD-Churn-Plan](../superpowers/plans/2026-11-14-owned-capture-fd-churn.md).
Keine automatische weitere stationäre Langzeitschleife.
