# Öffentliche TSE-Flotte während AI2-Entwicklung deaktiviert

Der Nutzer hat am 25.10.2026 die kontrollierte Abschaltung auf `ubuntu-4gb-nbg1-2` ausdrücklich autorisiert. Diese Anweisung ersetzt die frühere Pflicht, öffentliche Prozessgenerationen während privater Tests unverändert weiterlaufen zu lassen. Eine Wiederinbetriebnahme ist weiterhin ausschließlich nach ausdrücklicher Benutzerentscheidung zulässig.

Frische Abfragen: acht bekannte Bots, keine Menschen. Zwei Viererclients per WM_DELETE_WINDOW beendet; Dedicated mangels erreichbarer Konsole per SIGTERM. Kein Force-Kill, Host-Reboot, DLL-Austausch oder Eingriff in fremde Prozesse. Konfigurationen, Profile, Prozessbindungen und Hashes vorher privat gesichert. Zwölf eindeutig zugeordnete aktuelle/alte Overlays und zwei cgroups bereinigt; 415 geschützte Dateien und Rückfallarchiv unverändert.

Der lesende `tse-public-health.service` ist deaktiviert. Ein aktiver Spielesupervisor/Restart-Timer wurde nicht gefunden. `/srv/tse-public-disabled.json` hält den Zustand dauerhaft fest. Der vorhandene öffentliche Launcher verweigert Starts bei vorhandenem Marker. Der private Session-Harness unterstützt einen ausdrücklich gewählten Offline-Modus mit unverändertem Markerhash, Prozess-/Portcensus, eigenem Netzwerknamespace und unveränderten Ressourcenreserven. Das ist keine allgemeine Abschaltung von Sicherheitsprüfungen.

Weiterhin ausschließlich Hetzner, bestehender AI2-Worktree, keine Subagenten oder Shadow-Aufrufe. Toolauswahl und Qualitätsebenen aus der Richtlinie vom 17.10. bleiben bestehen. Der öffentliche Zustand wird im [AI2-Bericht](../reports/2026-10-25-bot-ai2.md) fortgeschrieben; Rohbelege verbleiben privat auf dem Host.
