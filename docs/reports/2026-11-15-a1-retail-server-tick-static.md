# A1: originale Game-Tick-Grenze statisch eingegrenzt

Die vorhandene originale Engine.dll wurde erneut gegen SHA256
`b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f`
geprüft. GNU objdump und ein lesender PE-Exportparser liefern die folgenden
bevorzugten virtuellen Adressen. Dies ist eine lokale statische Prüfung,
kein Ghidra-, Hook-, Runtime- oder First-State-PASS.
[Tatsächliche Toolentscheidung](../decisions/2026-11-15-local-retail-state-static-inspection.md).

| Originalexport | Adresse | Inspektierter linearer Body bis einschließlich RET |
|---|---|---:|
| CSessionState::ProcessGameTick | 601A6140 | 643 Bytes |
| CSessionState::ProcessPredictedGameTick | 601A63D0 | 257 Bytes |
| CSessionState::HandleTimers | 601A5930 | 193 Bytes |
| CSessionState::HandleMovers | 601A56E0 | 580 Bytes |

Die Bodygrenzen wurden anhand der tatsächlichen Rücksprünge und anschließenden
NOPs gelesen, nicht bloß anhand des nächsten Exports. Ausnahmehandler sind
separate Bereiche im Image; daraus entsteht noch kein vollständiger Hookguard.
ProcessGameTick endet bei601A63C0 mit `ret 8`, der Prediction-Pfad bei601A64CE
mit `ret 12`. Der normale Aufruf bei601A7028 innerhalb des ebenfalls original
exportierten ProcessGameStreamBlock übergibt zwei Stackargumente und ECX.
Die SDK107-Deklaration nennt CNetworkMessage-Referenz und Float-Tick; die
tatsächlichen Argumentloads und Rücksprünge passen dazu. Aktuelle Prozessbasen
oder ABI-Freigaben werden aus diesen bevorzugten Adressen nicht abgeleitet.

Innerhalb des normalen Game-Ticks ist die statische Reihenfolge:

1. Original SetCurrentTick bei601A617F.
2. Schleife über aktive Playertargets und Call601A61EC nach601A0350.
3. Original HandleSentEvents bei601A621F.
4. Original HandleTimers bei601A622A, dann HandleMovers bei601A6231.
5. Weitere Ereignisverarbeitung und Original MakeSynchronisationCheck bei601A6351.
6. Update des Floatfelds `this+0x50` bei601A6372 und normaler Rücksprung.

Die Namen der direkten Calls auf SetCurrentTick, HandleSentEvents und
MakeSynchronisationCheck wurden zusätzlich gegen die Original-Exportadressen
aufgelöst. Der innere Call601A0350 ist **nicht exportiert**. Seine Klassifikation
als bestimmter CPlayerTarget-Methodenname wurde deshalb nicht als bewiesen
übernommen. Er verarbeitet48Byte-Aktionsdaten und erreicht bei601A04A4 einen
virtuellen Spieleraufruf an Vtableoffset120h, nachdem DELETED ausgeschlossen
wurde. Die vollständige Zuordnung zur konkreten CPlayer-ApplyAction und deren
Lebensfolge braucht weiterhin eine gebundene Vtable-/Identitätsgegenprüfung.

Wichtig für den verbleibenden A1-Nachweis: Auch der getrennte Prediction-Pfad
ruft Timer und Movers auf und schreibt dasselbe Feld `this+0x50` bei601A64AC.
Dieses Feld ist daher allein kein eindeutiger autoritativer Zustandszähler.
Auch gleiche Spawn-/CurrentTick-Werte und ein PostMoving-Aufruf ersetzen keine
vollständige Original-Reihenfolge. Ein künftiger passiver Ordinalbeobachter
müsste den tatsächlich gebundenen eigenen Dedicatedprozess, diese originale
Funktionsgrenze und die Init-/Verbindungs-/Damagefolge gemeinsam erfassen.
Das würde keinen zusätzlichen abzuwartenden Spielzustand erlauben: Der erste
nach Originalregeln gültige Zustand bleibt maßgeblich.

Private reproduzierbare Reader und Disassembly liegen unter RootEV/
`a1-server-state-static-20261115`. Die erste Hilfsauflösung scheiterte an der
unzulässigen Erwartung eines Exports für601A0350; dieser FAIL bleibt erhalten.
Eine erste Metadatenquittung enthielt zudem irrtümlich den letzten Bodyhash als
Hash dieses verworfenen Readers; sie ist separat erhalten, die aktuelle
Quittung liest den tatsächlich gespeicherten Readerhash. Keine Binärdatei oder
Runtime wurde verändert. Der ursprüngliche zu breite objdump-Ausgabeversuch
war keine zusätzliche Analyse und wird nicht als Funktionsnachweis verwendet.

Die Input-/ACK-Kalibrierung und die kausale fremde Original-Bullet-/Damage-
Kette bleiben offen. Kein neuer Hook wurde vorbereitet oder gestartet.
A1 ist weiterhin nicht abgenommen.
