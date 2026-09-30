# Gemini Deep Research – projektseitige Bewertung

## Quelle
Gemini Deep Research: „Vanilla-kompatible Server-Bots in Serious Engine 1“, bereitgestellt am 30.09.2026 und im Google-Drive-Projektordner als eigene Quelle abgelegt.

## Was übernommen wird

### BESTÄTIGT / mit anderen Quellen konsistent
- Serious Engine 1 arbeitet synchron/deterministisch auf Basis von Spieleraktionen (`CPlayerAction`).
- CecilBotMod ist als Vanilla-Produktionsarchitektur ungeeignet, weil es eigene Bot-/Player-Logik und modifizierte Multiplayer-DLLs einführt.
- Für Vanilla-Kompatibilität sollen Bots wie reguläre Netzwerkspieler erscheinen und normale Player-Slots/Actions benutzen.
- `GetPlayersCount()` darf nicht global künstlich erhöht werden, wenn keine entsprechenden echten PlayerBuffer/PlayerTarget-Strukturen existieren.
- Bot-KI sollte von der synchronisierten Bot-Entity entkoppelt und auf „Weltzustand lesen → `CPlayerAction` erzeugen“ reduziert werden.
- Die vorgeschlagene Testmatrix (Join, Sichtbarkeit, Schaden/Frag, Langzeit-Sync, Slot-Verhalten) ist sinnvoll.

## Was NICHT als bestätigte Tatsache übernommen wird
Gemini beschreibt einen eleganten serverinternen „virtuellen Loopback-Client“-Pfad so, als sei dafür bereits ein nativer Engine-Einspeisepunkt vorhanden. Die spätere Originalcode-Verifikation (Perplexity/Projektprüfung) fand keinen fertigen dokumentierten Loopback-/Virtual-Client-Hook im öffentlichen Server-Netcode.

Projektstatus daher:
- **Pfad D**: echter, leicht modifizierter Bot-Client mit regulären lokalen Netzwerkspielern = Primärpfad.
- **Pfad B2**: synthetische PlayerBuffer/PlayerTarget direkt im Server = denkbarer Fallback, aber nur mit tiefem Engine-Patching/Reverse Engineering.
- Die konkrete Gemini-Loopback-Implementierung wird nicht als vorhandene Engine-Funktion betrachtet.

## Nutzen der Gemini-Quelle
Der Bericht war architektonisch hilfreich, weil er die richtige Kernidee früh herausarbeitet: KI und Netzwerkspieler-Darstellung müssen getrennt werden. Seine konkrete Server-Loopback-Ausgestaltung ist jedoch schwächer belegt als der inzwischen verifizierte Pfad D.

## Offene experimentelle Gates
- echter TSE-1.07-GameMP-Build und ABI
- Runtime-Join mit GameMP-only-Swap
- 60-Minuten-Sync und Mapwechsel/Reconnect
- 2–4 lokale Spieler/GUIDs
- Live-Serverbrowser/333networks
- Multiprocess-Ressourcen
