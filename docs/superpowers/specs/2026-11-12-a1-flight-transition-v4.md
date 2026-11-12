# A1 V4: gebundener Flugübergang und zurückgehaltener Pending-Input

Datum: 2026-11-12
Status: implementiert und offline geprüft; unabhängiges Review offen, Native/Integration ausschließlich Root.
Plan: docs/superpowers/plans/2026-11-12-a1-flight-transition-v4.md

## Gewähltes Verhalten

Die bis zum 111716-Fehler erfolgreiche Kalibrierung bleibt bytegleich. Der V4-Entwurf löst nur den belegten Routeübergang: Aus einer gültigen, gestützten Approach-Probe innerhalb des Original-Launchknotenradius folgt kurz darauf ein frischer, ungestützter Zustand mit den bereits bestehenden positiven x/y- und negativen z-Fluggeschwindigkeiten. Der x-Test der ursprünglichen direkten Signatur wird nicht pauschal entfernt. Eine spätere Probe außerhalb dieser x-Zone braucht zusätzlich den unmittelbar letzten gültigen Quellzustand, strikte Identität, Host-/Tickabstand <0.5 s, unverändertes Heading und Positionsfortschritt innerhalb der Originalkante zur Zielwaffe.

Der Anker darf keine ältere günstige Probe sein. Ein neuer gültiger Approachzustand ersetzt ihn auch dann, wenn er für den späteren Übergang ungeeignet ist. Geometrie, Zustandsbindung und Zeiten werden aus aktuellen Raw-Feldern geprüft; kein Lesen/Schreiben von Spielspeicher über die bereits vorhandenen Reader hinaus. Die spätere Beobachtung erhält ein konservatives Flight8-Budget ab dem Lesebeginn der letzten gültigen Bodenprobe. Das Intervall ist bekannt, der genaue physikalische Start nicht.

Die reguläre Routeentscheidung und beide Vorabprüfungen nutzen denselben aktuellen Zustandsautomaten. Approach → flight bedeutet, dass ein bereits geplanter Forward-Hold nicht mehr ausgeführt werden darf. Eine ausschließlich hierfür definierte Rücknahme reicht bis zum vorhandenen letzten XTest-Callback. Der Controller erkennt sie nur, wenn noch kein Request begonnen hat und der erlaubte botA-Forward betroffen ist. Andere Exceptions, Unsicherheit nach einem Request oder Cleanupfehler bleiben FAIL. Requestbeginn wird weiterhin ausschließlich unmittelbar vor dem tatsächlichen nativen Funktionsaufruf eingetragen.

Auf eine bestätigte Rücknahme folgt kein Inputretry. Versuch, Rohzustände und Rücknahmequittung bleiben erhalten; positive Inputreceipts bleiben bestätigten Anfragen vorbehalten. Sichere Freigabe ist unabhängig von neuem Zustand oder abgelaufenen Policyfristen.

## Verworfene Alternativen

- Größerer Approachkorridor oder pauschales Entfernen von x<−35: würde ungebundene Zustände akzeptieren.
- Früherer günstiger Rohread statt der neuesten Probe: verletzt den bestehenden Frische-/Belegvertrag.
- Nur höhere Pollrate oder weitere Forward-Wiederholung: beseitigt die tatsächliche Zustandsänderung während langsamer Guards nicht.
- Künstlicher Zwischenzustand, angenommene Bouncer-ID oder physikalisch berechneter exakter Start: von den Rohdaten nicht belegt.
- Markierter Flugstart erst beim späten Read: würde die unklare Zeit zusätzlich zum Flightbudget geben.

## Testvertrag

Der reale Replay verwendet unveränderte 111716-Frames/Quittungen und endet ausdrücklich am Ende des verfügbaren Beobachtungsfensters. Er darf einen Eingang ins passive flight bestätigen, keine spätere Waffenbeschaffung oder Feuerabgabe. Zusätzliche Grenzfälle sind als synthetische Tests bezeichnet.

Echte Route-, PP-, action_step-, Endpoint- und Transportfunktionen werden gegen einen ausschließlich speicherinternen XTest-Ersatz geprüft. Die zentrale positive Aussage ist: Die bekannte 211→212-Folge hält den pending Forward vor XTest zurück. Die zentrale negative Aussage ist: Falsche Geometrie/Identität/Frische/Deadline oder fehlerhafte Freigabe können weder eine Rücknahme als Erfolg ausgeben noch weiteren Input auslösen. Die vorhandene vollständige Regression bleibt erhalten.
