# A1 V5: Beobachtungsbindung nach einer normalen Eingabe

Der V4-Flugnachweis darf ausschließlich die jüngste geeignete tatsächliche Approach-Beobachtung verwenden. Jede neuere gelesene relevante Route-Probe muss diese Grundlage ersetzen oder verwerfen, auch bei gleichem nativem Tick. Der Vollreplay des unabhängigen Reviews ist der verpflichtende Fehlernachweis.

Die Route-Verarbeitung nach einer abgeschlossenen Eingabe darf Zustand und Fristen aktualisieren, jedoch keine weitere Eingabe emittieren. Eine Rückgabe mit Handlungsvorschlag ist dort kein Ausführungsauftrag. Vor einer noch nicht begonnenen Eingabe bleibt die bestehende Vergleichsprüfung auf die exakt geplante Aktion bzw. den eng typisierten Flugabbruch bestehen.

Ein schon in der After-Input-Probe beobachteter zulässiger Flugübergang wird unmittelbar verarbeitet und dauerhaft an den bisherigen jüngsten gültigen Anker gebunden. Spätere Beobachtungen dürfen keinen günstigeren Startpunkt ersetzen. Alle Geometrie-, Prozess-, Life-/World-, Zeit-, Mengen- und Cleanup-Regeln bleiben bestehen. Andere tatsächlich gelesene Proben auf demselben Weg werden auf identische Auslassung geprüft; neue Funktionsziele sind ausgeschlossen.

Lieferung: neues privates deaktiviertes V5-Paket, enge tatsächliche Runtime-Diffs, RED/GREEN- und Regressionsbelege, Closure und unveränderte Parent-/Review-/Raw-Pins; nur neue V5-Docs im isolierten Worktree. Kein nativer Versuch, Build oder Eingriff in Produktion.

## Konkretisierung aus tatsächlichen Gegenfällen

Der zusätzliche periodic/sample-Lesepfad wurde im vollständigen echten Controller-Speicherpfad reproduziert. Native Rollenframes tragen deshalb den Index des tatsächlichen letzten erfolgreichen Paars und den exakten Vorgängermarker. Der native Aufruf verlangt den Vertrag. Jede Erfolgslücke seit dem letzten PP-Frame verwirft den alten Approachanker; keine nachträgliche Rawqualifikation. Eine folgende frische vollständige PP-Bodenprobe bildet regulär die neue Basis. Sequenz-/Zeitfälschungen und Markerwegfall bleiben fatal.

Ein ursprünglicher Deadline-Grenztest belegte durch Subtraktionsrundung 7.999999999999999 am absoluten 8-s-Ende einen Fehler. Der Ausdruck wurde auf value + reserve < flight_started + 8 umgestellt. Deadline und Epsilon bleiben unverändert. Alle übrigen Route-/Input-/Resource-/Close-Regeln bleiben bestehen.

Die aktuelle vollständige Regression umfasst 187 Tests; der zusätzliche strikte Replay nutzt die tatsächliche Folge von 203 erfolgreichen Reads des geschlossenen 111716-Laufs. Der Replay endet an Raw 212 und behauptet keinen weiteren Zustand. Alte Pakete und alle Review-/Rawbelege bleiben unverändert.
