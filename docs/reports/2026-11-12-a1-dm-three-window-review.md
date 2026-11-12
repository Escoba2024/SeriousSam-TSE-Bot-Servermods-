# A1: drei begrenzte DM-Fenster, unabhängige Dateiprüfung

Die gespeicherten Original-Retail-Beobachtungen belegen normalen Fremdschaden **vor drei Sekunden** bei Spawnschutz 0. Sie belegen **keinen Schaden im Spawn-Tick und keine A1-Abnahme**. Es wurde ausschließlich vorhandene Evidenz ausgewertet; keine Runtime gestartet oder verändert.

| Fensterende im Evidenznamen | Schutz / Hook | echte Wandzeit | vollständige Damage-Aufrufe | lebende Fremd-BULLET-Aufrufe / mit HP-Verlust / tödlich | Vanilla-Leben / Respawns / FIRE-Pulse |
|---|---|---:|---:|---:|---:|
| 011052 | 0 / aus | 90,117 s | nicht beobachtet | nicht beobachtet | 2 / 1 / 3 |
| 011501 | 0 / an | 90,120 s | 85 | 45 / 45 / 10 | 4 / 3 / 7 |
| 011747 | 3 / an | 90,032 s | 146 | 80 / 75 / 14 | 4 / 3 / 7 |

Bei Schutz 0 liegen drei aufeinanderfolgende normale Fremd-BULLET-Aufrufe desselben Kandidatenlebens bei **2,6999836 s**: HP 100→80→60→40, Armor jeweils 0. Bei Schutz 3 liegen fünf entsprechende Aufrufe eines Kandidatenlebens bei **1,5000916–1,7001038 s**, jeweils HP 100→100 und Armor 0→0. Die fremden Spieler sind durch unterschiedliche registrierte Spieleridentitäten belegt; gleiche Clientgruppe bedeutet keine Selbstverletzung. Diese natürlichen Gelegenheiten sind keine paarweise identischen Trefferexperimente. Keine Aussage über frühere nicht beobachtete Treffer oder den ersten verarbeiteten Zustand.

Alle 85 beziehungsweise 146 Records liegen vollständig innerhalb der jeweiligen realen Messfenster. Registry-ID/Pointer, Hauptthread-TLS, positive unveränderte Spawnclock und unveränderter CurrentTick bei Eintritt/Austritt wurden erneut geprüft; jedes Record-Leben ist im Inventory enthalten. 14 beziehungsweise 49 Aufrufe treffen bereits tote Spieler und sind aus dem lebenden Fremdtreffer-Nenner ausgeschlossen. Alle HP-Abnahmen einschließlich Leichen wären 85 beziehungsweise 141 und somit ein irreführender A1-Nenner. Tödliche Treffer auf bei Eintritt lebende Spieler zählen separat. Armor-only zählt nicht als HP-Nachweis. In beiden instrumentierten Fenstern: **0 gültige HP-Abnahmen bei CurrentTick == SpawnClock**.

Die Retail107-Enum definiert `DMT_BULLET=4`, `DMT_IMPACT=6`, `DMT_TELEPORT=10` (`Sources/Includes/Engine107/Engine/Classes/BaseEvents.h:108–126`). `Bullet.es:44,155` setzt BULLET und übergibt den Schützen als Inflictor an den normalen direkten Schadenspfad. Der bereits statisch gegen Original-Entities `7f595…` geprüfte `ReceiveDamage`-Pfad `0x603fd380` verwendet den Schutzvergleich bei `0x603fd445–0x603fd47a`; siehe [Original-Lifecycle-Beleg](2026-11-12-a1-original-spawn-lifecycle.md). Type 4 grenzt hier den normalen Bullet-Pfad ein, identifiziert aber ohne weitere Hookstelle nicht die konkrete Waffe. RequestedDamage 10 und effektiver HP-Verlust 20 werden nicht gleichgesetzt.

Alle gespeicherten Sessionproben zeigen in allen vier Rollen den jeweiligen tatsächlichen Schutzwert 0 beziehungsweise 3. Die letzte Launch-Identität belegt Kandidat012 `e049…` in botA und bisherigen048 `ec820…` in botB, Originalserver und Vanilla `1c41…`; vollständige Hashes stehen im JSON. Lokale BotDriver-Zuordnung ergibt botA/global 0,2,3,4, botB/global 5,6,7,8 und Vanilla/global 1. Sampling-Gruppennamen wurden nicht als Spielerzuordnung verwendet.

| Fenster | Kandidatenleben / mit nützlichem Waffenbesitz | 048-Leben / mit nützlichem Waffenbesitz | beobachtete nützliche Besitz-Zunahmen Kandidat / 048 |
|---|---:|---:|---:|
| 011052 | 12 / 9 | 8 / 6 | 10 / 9 |
| 011501 | 12 / 5 | 8 / 4 | 5 / 7 |
| 011747 | 10 / 8 | 13 / 7 | 14 / 8 |

Vollständiger beobachteter Lebensnenner: Slot/Entity/positive Spawnclock, Inventory-Gruppen vereinigt und nach tatsächlichem GameTick dedupliziert. Nützliche Besitzmaske `0x3df8`; beobachtete Zunahmen sind Untergrenzen, kein vollständiger Pickup-Eventzähler und kein Schussbereitschaftsnachweis. Vanilla hat in keinem Fenster beobachteten nützlichen Waffenbesitz. Vanilla-Tode: 1/4/4, am Fensterende lebend rechtszensiert: 1/0/0. Pulse sind Eingabeversuche; insbesondere sieben Pulse beweisen keine sieben Respawns. Der letzte release-only-Aufruf ist jeweils separat und kein FIRE-Puls.

Kosten: Controller-CPU 13,611 / 17,694 / 17,751 CPU-s; Originalserver 2,97 / 3,28 / 3,30 CPU-s. Server-End-RSS 49,14 / 101,83 / 101,89 MiB. Maximale Beobachtungslücke 0,794 / 0,870 / 0,871 s. Die normalen Fokus-/FIRE-/Release-Aufrufe blockieren zusammen einschließlich Schlussrelease 2,539 / 5,190 / 5,196 s; jede Schlussfreigabe bestätigt Button1 released. Inventory: 2213/1832/1817 gültige und 55/46/52 wegen Änderung verworfene Proben. Unterschiede in Inputs, tatsächlichen Lebensverläufen und Probezahl verhindern eine isolierte kausale Frida-Overheadzahl. Dies ist ein begrenzter uninstrumentierter Kontrolllauf, kein Lastbudget- oder A3-Leistungsnachweis.

Erneut abgeglichen: vier normale Closed-Receipts pro Lauf, SHA256 aller gespeicherten Closed-Logs, keine gemeldeten BAD/Disconnects, fehlerfreie Finalisierung. Instrumentiert zusätzlich vollständiger Record-Nenner, Hauptthreadbindung, Listener-Abdeckung des ganzen Fensters, 0 Fault/Drop/InFlight, keine Detachfehler und gespeicherte exakte Wiederherstellungsprüfungen für Original-Getter (22 Bytes) und ReceiveDamage (1395 Bytes, HIGHLOW berücksichtigt). Eine Dateianalyse wiederholt nicht die damaligen Live-Speicherlesungen. Rohrecords, Speicheradressen und Konfigurationen bleiben privat; [JSON](2026-11-12-a1-dm-three-window-review.json) enthält bereinigte Zählungen und Artefakthashes.
