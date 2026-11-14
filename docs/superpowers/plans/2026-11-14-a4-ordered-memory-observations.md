# A4: geordnete Speicherbeobachtungen statt falscher Tickidentität

Gesamtauftrag unverändert. Root allein Runtime; keine neue DLL und keine nachträgliche Freigabe alter FAILs.

## Konkrete Grundlage

Hard600112608: acht Crossgroup-Gesamtrowkonflikte. Canonical600120936: drei Within-group-Konflikte in den ersten Leben derselben botA-Gruppe; gleicher Sessiontick/Spawnclock0,9000001549720764 bei 33,491ms auseinanderliegenden Readcalls. Physikflags/Position ändern sich, Identität/HP/Inventar/Firewerte bleiben gleich. Der Reader bezeichnet seinen Vertrag ausdrücklich als two_equal_reads_not_atomic. Deshalb ist (Leben,Sessiontick) keine eindeutige Beobachtungsidentität. Der zweite Lauf bleibt FAIL935f6d88.

## Entscheidung und Kosten

Ein Speicherread ist eine geordnete Beobachtung und kein atomarer Simulationssnapshot. Alle kanonischen Beobachtungen werden erhalten, ohne Tickdeduplizierung oder günstige Rowauswahl. Neue eindeutige Identität aus PID/Start/Epoch/Gruppe und monotonem globalem Readserial. Vertrag und feste Gruppenzuordnung vor dem ersten Read archivieren. Jede Hülle erhält monotone Readstart/-endzeiten; keine Nutzdaten-/Tick-/Ergebnisfilterung. Gleiche Seriennummer/ID oder Zeit-/Identitäts-/Epochwiderspruch bleibt harter Fehler, auch im ausgeschlossenen Overlap.

Das beseitigt eine empirisch falsche Datenidentität, erweitert aber weder Lebenszeit noch EPS noch Waffenkriterium. Die Messgrenze bleibt sichtbar: beobachtete native FIRE-/Owned-/Buttonflags im konsistenten Leseintervall plus Sourcewachstum sind kein exakt zeitgebundener Waffenfunktionsaufruf. A1-Erstzustandsschaden und A3-Schaden-/Killabnahme bleiben eigene offene Eventnachweise. Bei falscher Entscheidung könnten beobachtete Flags fälschlich als atomar gelesen werden; deshalb Aussage und Feldnamen ausdrücklich begrenzen.

## Aufgaben und Abnahme

1. Diagnose aller drei kanonischen Konflikte mit bereinigten Belegen committen; Roharchive/hashgesichert erhalten. Neue gezielte Regression zunächst RED, die echte widersprüchliche Reihenfolge reproduzieren.
2. Separater V3-Auditor für geordnete Beobachtungen, V2-Dateien bytegleich erhalten. Keine Tickmap/first-row-/best-row-/Feldwhitelist. Alle Rows der vorab festen Gruppe streng in Beobachtungsreihenfolge auswerten. Clock/World/Entity/Epoch prüfen. Kontradiktorische gleiche ObservationID oder rückläufige Sequenz/Zeit scheitert vor Evidenz.
3. Exakte Source-Lifetimejoins, Decimal-Rundungsintervalle und Counter-/Resetgrenzen unverändert. Inventargewinne weiter ausschließlich bei strikt oldTick<newTick und demselben gesunden Leben. Same-tick-Inventaränderung wird nicht als Pickup gewertet. Keine EPS/Grace-/Fristlockerung; keine Source-/FIRE-/Pickupbeweise aus Overlap.
4. Deaktivierter Controller: derselbe600sHard2-Ablauf, identische Readersamples/Abfrageraten/Gruppen/Rollen/Logs/Hostgates/Close/Restore. Nur geloggte Readidentität/-zeit und neuer Auditorpfad. Alle Rohhüllen vor Filter validieren, derselbe kanonische Stream für FIRE und Pickup. Neue Belegfelder benennen ausdrücklich flag_observations, nicht aufgerufene FIRE-Aktionen.
5. Gezielte Negativfälle: gleiche ID mit anderen Rows, rückläufige Nummer/Zeit, NaN/Inf, fremde Entity/World/Epoch/PID, falsche Gruppe/Slots, Crossgroup-Fallback, SameTick-Pickup, fehlender Sourcegrowth, ambige Source-Lifebindung, Counterreset. Historische Archive nur OFFLINE_DESIGN_CHECK, keine Qualifikation.
6. Root prüft Diff/Pins/Gates und führt nach Review/Freeze/Preflight genau einen begründeten neuen600sRed-Lauf aus. Alte FAILs unverändert. Erst Ergebnis/Cleanup/unabhängiger Restore erlauben nächsten Kartentest, keine automatische Wiederholung.

## Status

- [x] Falsche SameTick-Gesamtrowidentität im echten Lauf widerlegt und unabhängig bewertet.
- [ ] Diagnosebeleg/RED-GREEN/Quellen.
- [ ] Deaktiviertes Paket und unabhängiger Review.
- [ ] Neue prospektive native Prüfung und tatsächliche A4-Kartenabnahme.
