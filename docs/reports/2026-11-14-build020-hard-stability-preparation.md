# Deaktivierte Vorbereitung der vorgeschriebenen Stabilitätsgates

Der reproduzierbare Vorbereiter `tools/prepare_build020_hard_stability.py` erzeugt ausschließlich eine neue private, deaktivierte Kopie des vorhandenen013-Stabilitätscontrollers. Es wurden keine Spielrollen gestartet, keine Lab-/Public-Dateien verändert und keine Dauerabnahme behauptet.

Paket `/srv/tse-stability-build020-hard-controller-20261114`, Manifest SHA256 `a7afdf0ea6bae78da0c8399d945c59c6811a0bd147f032c7d996ba5182569d09`,57Runtimepins. Alle56 geerbten Abhängigkeiten vor Kopie passend; Build020-DLL/Manifest und75 Quell-/Overlaypins frisch überprüft. Der Adapter bleibt bis zum unabhängigen Review und einem eigenen Root-Freeze deaktiviert.

Änderungen gegenüber dem ursprünglichen Controller: genaue020-Herkunft und eigener Namespace; Hard2-Vorlage; reine Prüfung derselben nativen Sessionbytes aller Peers vor Pausefreigabe und während der bereits vorhandenen Sessionproben; exakte Hard-Abfrage im vorhandenen Querypfad. Modul-/Prozessbindung, normale Closes, Restore, Originalobserver und sämtliche vorhandenen formalen Zeit-/Aktivitäts-/Ressourcenkriterien bleiben erhalten. Die1/4/8-Bot-Dauern bleiben3600/3600/7200Sekunden.

Fokussierte Offlineprüfung: sechs neue Regelnprüfungen, zunächst fehlendes Modul RED, danach GREEN; gemeinsam mit fünf benannten geerbten Testmodulen31Tests PASS in2,808s. Das vollständige1/4/8-Replay ist synthetisch und kein nativer Zeitlauf. Die erste private Kopie enthielt die alte Queryfixture ohne Difficultyfeld und scheiterte mit sieben entsprechenden Fehlern; sie bleibt getrennt erhalten. Ausschließlich die synthetische Fixture wurde um Hard ergänzt; die echte Queryprüfung bleibt strikt.

Nächster Schritt: unabhängiger Review des erzeugten Controllerdiffs und der unveränderten Kriterien. Vor tatsächlichen Langläufen zuerst Kandidaten-/Hardfunktion und die offenen kurzen A-Prüfungen klären. Kein weiterer nativer Lauf parallel zu A1/A4, Compiler oder breiten Tests.
