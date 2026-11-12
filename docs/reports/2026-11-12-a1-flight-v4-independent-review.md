# A1 V4: unabhängiger Review blockiert den nativen Start

Stand: 12.11.2026 15:03:29 CET

**BLOCKED: 0 Critical, 1 Important/P1. V4 wurde nicht nativ gestartet.** Die 174 bestandenen Autorentests und 19 erneut bestandenen unabhängigen Zieltests ersetzen den konkreten Gegenbefund nicht.

`preparation_policy.py` zeichnet nach einer positiven Route-Eingabe eine frische `route-after-input`-Probe auf, führt sie aber nicht der Route-/Ankerpflege zu. Drei ausdrücklich synthetische Gegenfälle durch die tatsächliche PP-/RD-/Route-Orchestrierung reproduzieren die Lücke: Eine neuere Same-Tick-Probe mit Support 0, außerhalb des Original-Node12-Radius oder außerhalb des Approachkorridors steht im Receipt, wird jedoch übergangen. Der nächste Flugzustand wird über den älteren günstigen Pre-emission-Anker akzeptiert.

Die enge erforderliche Korrektur führt auch diese neueren Route-Proben der Ankerpflege zu. Sie dürfen ältere günstige Proben nicht stehen lassen. Zusätzliche Eingaben, verlängerte Fristen oder eine Korridorerweiterung sind kein Bestandteil der Korrektur. Der Autor erstellt ein separates V5-Paket; V4, sein Review und die tatsächlichen Nativebelege bleiben unverändert.

Der unabhängige unveränderte 111716-Replay verbrauchte 27 RD-Paare, 66 Rollenframes und 16 Originalquittungen, ohne 17. Down. Er endet weiterhin vor nicht aufgezeichneten Folgezuständen. Der enge Cancel-/Releasepfad, Exceptionursprung und die unveränderten Fristen waren im Restreview konsistent. Root hat alle 44 eigenen, 96 Evidenz- und 48 Runtime-Pins sowie beide deaktivierten Gates direkt geprüft.

[Maschinenlesbarer Reviewbeleg](milestone-a-20261112/a1-flight-v4-review.json). Privater vollständiger Review: `/srv/tse-a1-flight-v4-independent-review-20261112/REVIEW.md`; SHA256 `bfe3dee9a8ee83b41805ebf5f17bcee60a4dfb5857b41f97285df840e197dcf6`. Der tatsächliche ursprüngliche Nativeversuch bleibt FAIL. A1 und Gesamt-A sind nicht abgenommen; B bleibt unbegonnen.
