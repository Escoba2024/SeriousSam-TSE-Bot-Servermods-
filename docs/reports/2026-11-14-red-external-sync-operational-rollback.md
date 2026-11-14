# Red Station: neuer externer Sync-Disconnect und betrieblicher Rückroll

Status: **offener Betriebsfehler, Ursache ungeklärt**. Der initiale Build018-Rollout war auf sechs Instanzen durchgeführt und kurz geprüft. Nach einem neuen Sync-Disconnect wurde am 14.11.2026 nur Red Station betrieblich auf den gesicherten vorherigen Botstand zurückgerollt. Der Gesamtauftrag bleibt unvollständig; fünf Instanzen laden Build018.

## Befund und Zuordnung

Der frische Flottencheck 09:51:48 UTC hatte im aktuellen Red-Serverlog keine Syncfehler. Der stabile private Präfix 10:54:01 UTC enthält 15 SYNCBAD und einen `Too many bad syncs`-Disconnect für genau einen zusätzlichen externen Peer. Erste Abweichung: Sequenz144807, Tick7230,38. Nach zwischenzeitlichen OK-Resets folgt eine Serie1→10 bis Tick7242,93 und der Disconnect in Zeile20499. Nach erneutem Join wurden vier weitere einzelne BAD beobachtet.

Serverpräfix: 1.183.107 Bytes, SHA256 `8335e3d5d62bd5930ef7a25525517822de2b53b9d3172b6201521e0ba9848870`. Die beiden eigenen Clientpräfixe haben null BAD/Sync-Disconnects. Die privat verglichenen Joinadressen beider eigenen Gruppen entsprechen dem anderen OK-Peer; sie entsprechen niemals dem fehlerhaften Peer. Eigene PID/Start/CWD und Module wurden gebunden. Die unverbundenen UDP-Sockets beweisen allein keine Zieladresse. Root und unabhängiger Analyseagent bestätigen die Zuordnung; Rohadressen und Teilnehmernamen bleiben privat.

Ein fremder Teilnehmer ist damit belegt, sein menschlicher/Originalclient-Status hingegen nicht. Die Ursache der abweichenden Prüfsummen und ein möglicher Einfluss der Bot-DLL sind weiterhin offen. Ein fehlerfreies eigenes Botlog schließt eine Divergenz bei einem anderen Client nicht aus.

## Rückroll und kurze Nachprüfung

Vor Änderungen wurden aktuelle Build018-Dateien, Konfigurationen, Identitätsdateien, Metadaten und Dienste gesichert sowie separat rekonstruiert/hashgeprüft. Unter den bestehenden Flotten-/Deployment-/Instanzlocks wurden ausschließlich beide eigenen Red-Botclients regulär geschlossen. Der Dedicated-Prozess, seine geladenen Module und seine Eingaben blieben unverändert. Keine fremde Sitzung wurde beendet oder instrumentiert.

Die wieder laufenden Botmodule wurden gegen den gesicherten vorherigen SHA256 `7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835` geprüft. Acht eigene Bots verbunden, Profile/GUID-Dateien unverändert. Das ist ein bewusster Rückroll wegen des neuen Betriebsfehlers, keine neue Freigabe dieses älteren Stands.

11:02:55 UTC, 116,91 Sekunden nach Rückrollabschluss: acht eigene Bots und ein zusätzlicher Teilnehmer, unveränderter Dedicated-Prozess, null neue SYNCBAD/Sync-Disconnects ab dem gesicherten Serverlogoffset. Für alle acht eigenen Slots wurden 23–41 verschiedene Navigationspositionen beobachtet; 744 Kampftelemetriezeilen. Diese kurze Beobachtung beweist weder die Syncursache noch dauerhafte Fehlerfreiheit oder Waffenbeschaffung jedes Slots.

Private ausführbare Operation: `/srv/tse-cecil-rollout-evidence-20261114/rollback-red-sync.py`. Vollständiger Vorher-/Rückroll-/Nachherbeleg unter `/srv/tse-cecil-full-20261107/.codex/evidence/restart-fleet-20261111-red-sync-rollback-20261114-105950/redstation`. `current018` enthält den geprüften Rückweg zum vor dieser Operation aktiven Payload; eine erneute Promotion benötigt die aktuelle Betriebsentscheidung und frische Locks/Preflight. Der allgemeine `restore-instance.py` stellt den Stand **vor** dem initialen Rollout her und ist kein Build018-Restore.

## Spielbarer Flottenstand

Frische Modul-/Queryprüfung um 11:03 UTC, Adresse `91.99.75.33`. „Zusatz“ bezeichnet ausschließlich ungeklärte Teilnehmer; keine menschliche Klassifikation. Sessions/Botchat sind überall weiterhin nicht implementiert.

| Server | Port | Map | Bot-DLL | Eigene/Soll | Zusatz | Fehlerstand |
|---|---:|---|---|---:|---:|---|
| Red Station |25600|Red Station|Gen2 `7fc94a39…`, Rückroll|8/8|1|15 neue BAD/1 Disconnect vor Rückroll; kurze Nachprüfung0 |
| Yodeller |25610|Yodeller|Build018 `6db89204…`|8/8|0|letzter vollständiger Fehlercheck0 neue |
| Skulls'n'Bones |25620|We Got Skulls'n'Bones Too|Build018 `6db89204…`|8/8|0|11 BAD/1 Disconnect nachweislich vor initialem Rollout |
| Little Trouble |25630|Little Trouble|Build018 `6db89204…`|8/8|0|letzter vollständiger Fehlercheck0 neue |
| Hole |25640|Hole|Build018 `6db89204…`|8/8|0|letzter vollständiger Fehlercheck0 neue |
| Dev |25650|Red Station|Build018 `6db89204…`|8/8|0|letzter vollständiger Fehlercheck0 neue |

Hard2 gilt erst für Dev/Red, auf den übrigen vier bleibt die dokumentierte Serious3-Abweichung offen. Native Respawnschutzwerte waren zuletzt überall0. Die aktuelle Modul-/Belegungsprüfung ersetzt keine erneute Kampf-/Fehler-/Ressourcenabnahme aller Instanzen.

Nächster Schritt: Syncbefund im eigenen isolierten Originalclient-/Kandidatenaufbau reproduzieren und den ersten abweichenden Zustand messen. Der fehlende Original-Actionpfad und die Eingabeverdopplung blockieren weiterhin A1; eine neue passive Timerguardbeobachtung ist separat vorbereitet. Keine Instrumentierung fremder Clients, kein Abschalten des Sync-Kicks und keine Umwertung historischer FAILs. A3/A4-Vorbereitungen bleiben getrennt, B beginnt erst nach belegtem A-Abschluss.
