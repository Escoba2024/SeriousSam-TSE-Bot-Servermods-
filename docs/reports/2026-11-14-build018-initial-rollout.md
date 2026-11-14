# Build018: initialer Rollout auf sechs Instanzen

Stand: 2026-11-14T08:23:15.454108+00:00. Alle zwölf Botprozesse laden SHA256 `6db89204e33dc7d76ecdfed68055d2b75bde4950475793a57101fd0cefcb8e4a`; Quelle `1802fb3f0720b53feb032abfe2c2a83407bfea6e`. Dedicated-DLLs und Prozesse blieben dabei unverändert. Die vorhandene Einstellung war Serious, nicht Hard; die nachfolgende kontrollierte Korrektur wird gesondert belegt.

| Instanz | Port | Map | Bots | Fenster s | Fragzuwachs | Tod / Respawn | Neue Syncfehler |
|---|---:|---|---:|---:|---:|---:|---:|
| redstation | 25600 | Red Station | 8/8 | 91.45 | 30 | 35 / 42 | 0 / 0 |
| yodeller | 25610 | Yodeller | 8/8 | 91.51 | 51 | 48 / 48 | 0 / 0 |
| skulls | 25620 | We Got Skulls'n'Bones Too | 8/8 | 91.22 | 31 | 33 / 41 | 0 / 0 |
| trouble | 25630 | Little Trouble | 8/8 | 91.50 | 40 | 46 / 46 | 0 / 0 |
| hole | 25640 | Hole | 8/8 | 91.43 | 19 | 31 / 34 | 0 / 0 |
| development | 25650 | Red Station | 8/8 | 91.30 | 26 | 35 / 36 | 0 / 0 |

Alle acht Slots je Instanz zeigten Bewegung und Feueranforderungen. Query-Fragzuwachs ist davon getrennte tatsächliche Spielaktivität; er ist keine individuelle Schadenszuordnung. Cecil-CRC-Bindung und DEMON/arena-v1 wurden in beiden Clientlogs nachgewiesen. Namen und GUID-Dateien sind unverändert;48 sichtbare Namen sind kollisionsfrei. Die vorhandenen Profile enthalten40 unterschiedliche GUIDs: acht werden auf zwei getrennten Instanzen wiederverwendet. Keine Identität wurde neu vergeben.

Die kurzen Betriebsfenster ersetzen weder A1-Erstzustandsschaden noch vollständige Karten-/Waffenversorgung, formale60/60/120-Minuten-Gates oder B. Der historische23/24-A4-Fehler bleibt FAIL. Sessions und Botchat sind nicht implementiert.

Die nativen Sessionfelder bestätigen UnlimitedAmmo1, Blumenblut3, Gibs0, Frag-/Zeitlimit0 und Respawnschutz0. GameSpy gibt InfiniteAmmo invertiert als0aus; Schwierigkeit3/Serious ist dagegen real. Hard2 wird in einer eigenen Transaktion korrigiert.

[Maschinenlesbare Messwerte](milestone-a-20261114/build018-initial-rollout.json). Private Rohlogs, Profile und Rückrollstände liegen unter `/srv/tse-cecil-rollout-evidence-20261114` und dem dort dokumentierten privaten Runverzeichnis. Der vorhandene Restorehelfer prüft zuerst Backuphashes und verlangt vor Änderungen ruhende eigene Botprozesse.

Delta022 wurde extern hochgeladen und vollständig zurückgeprüft:101451161Byte, SHA256`e88caecf53ed94ddbac6ade1b3c638a637b50459d4dc4ff699dec50513861196`. Delta023:35086463Byte, SHA256`189f8186d0ca9180d851fb75f9e3dfe5b5e06d9994b1edecbde84b40c35724d9`. Beide im bestehenden privaten Drive-Projekt; neue Rolloutbelege brauchen einen eigenen Nachtrag.
