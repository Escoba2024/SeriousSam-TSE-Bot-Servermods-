# Kapazität: Messung und Hochrechnung strikt getrennt

Host: zwei vCPU, 3819 MiB RAM, keine GPU. Prozentangaben der Prozesse beziehen sich auf einen CPU-Kern; 200% entsprechen beiden Kernen. Es wurden keine größeren Flotten parallel zum öffentlichen Server gestartet.

## Tatsächliche Messung

Maximal acht aktive Human-Bots mit zwei Viererprozessen über 3600s und Originalclient. BotA 20,548%, BotB 20,505%, Server 14,686%; zusammen 55,739% eines Kerns für die drei Spielprozesse. Das sind rechnerisch 5,132% Client-CPU je Bot plus serverseitig 1,836% je Bot im beobachteten Acht-Bot-Szenario. Keine getrennte Messung des inkrementellen CPU-Anteils jedes einzelnen lokalen Spielers.

RSS: zwei Botprozesse 377936KiB =369,078MiB, Server 51568KiB =50,359MiB; zusammen 419,438MiB. Bot-RSS geteilt durch acht 46,135MiB/Bot; mit Server 52,430MiB/Bot. Gemeinsame Bibliotheksseiten sind dabei im RSS mehrerer Prozesse enthalten; dies ist kein PSS-/Allocatorbeleg.

Serverlast bei einem Bot plus Originalclient 8,423%, bei vier Human-Bots 10,255%, bei acht plus Originalclient 14,686%. Eine echte leere Server-Grundlast wurde nicht separat gemessen. Daher wird 8,423% nicht als Idlewert ausgegeben. Zusätzliche Instanzen verursachen jeweils eigene Server-/Wine-/Netz-/Xvfb-Verwaltung.

Originalclient im Stundenlauf zusätzlich 88,162% eines Kerns und 208,078MiB; er gehört zur Prüfgegenstelle und wird nicht dauerhaft für Bots benötigt. Gesamter Host während dieser strengen Probe 83,193% von zwei vCPU; neue cgroup-Drosselungen und Steal null. Differenz zu den summierten Spielprozessen umfasst Wine, Xvfb, OS und Hintergrunddienste, nicht pauschal zusätzliche Botkosten. Der öffentliche 600s-Backend-Smoke ohne Originalrenderer liefert eine eigene Betriebsmessung.

## Mathematische Szenarien, keine Laufzeitfreigaben

Je Instanz acht Bots, 16 Slots und damit bis zu acht menschliche Plätze. Hochrechnung kopiert das beobachtete Acht-Bot-Spielprozessbudget linear; sie enthält keine nichtlinearen Netz-/Physik-/Spieler- oder Winekosten.

| Bots | Instanzen à 8 Bots | Spielprozess-CPU, ein Kern | Anteil an 2 vCPU | RSS einschließlich Server | Bewertung |
|---:|---:|---:|---:|---:|---|
| 8 | 1 | 55,739% | 27,870% | 419MiB | Tatsächlich gemessen; konservative aktuelle Empfehlung |
| 16 | 2 | 111,478% | 55,739% | 839MiB | Nur rechnerisch möglich; zwei Instanzen und menschliche Last zuerst isoliert messen |
| 32 | 4 | 222,956% | 111,478% | 1678MiB | CPU-Budget bereits ohne OS/Wine/Menschen überschritten |
| 64 | 8 | 445,912% | 222,956% | 3356MiB | CPU weit überschritten, auch RAM ohne ausreichende Systemreserve |

Mindestens 30% der Host-CPU als Planungsreserve für OS, Wine, Lastspitzen und echte Spieler anstreben; dies ist eine konservative Zielreserve, kein gemessener Maximalwert. 16 Bots kommen rechnerisch in die Nähe dieses Gesamtbudgets, sobald zusätzliche Hintergrund-/Spielerlast berücksichtigt wird. Deshalb bleibt die Freigabe bei acht, ohne aus CPU-Restwerten eine ungetestete höhere Zuverlässigkeit abzuleiten. 16 Bots in derselben 16-Slot-Instanz lassen keinen Platz für Menschen.

## Langfristige Infrastruktur

Für 32/64 aktive Bots auf Basis dieser Architektur sind zusätzliche verlässlich verfügbare CPU-Kerne erforderlich; mehr RAM allein behebt den CPU-Engpass nicht. Ein größerer VPS könnte bei genügend tatsächlich verfügbarer CPU genügen. VDS/dedizierte Kerne werden technisch interessanter, wenn gemessener Steal oder Dauerlast Reserven unzuverlässig macht; ein eigener Dedicated Server erst, wenn mehrere Instanzen dauerhaft ausgelastet sind und Verwaltung/Preis pro qualifiziertem Bot dies rechtfertigen. Im aktuellen Test war Steal null. Ohne gemessene größere Flotte und aktuellen Tarif-/Auslastungsvergleich ist kein wirtschaftlicher Sieger belegt. Keine Bestellung, kein Upgrade und keine neue Lizenzannahme erfolgt.

Automatischer Supervisor, dynamische Population und unabhängige Mehrserver-Abnahme bleiben offen. Ein neuer Server oder Rebuild braucht eigene Hash-/Join-/Sync-/Stunden-/Browser-Gates.
