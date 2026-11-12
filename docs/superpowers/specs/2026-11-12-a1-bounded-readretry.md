# A1: begrenzte Wiederholung inkonsistenter Leseversuche

## Auftrag und Befund

Root beauftragt ausschließlich einen Offline-Fix im isolierten Worktree `/srv/tse-milestone-a-a1-readretry-20261112` und einer neuen deaktivierten privaten V3-Kopie. Basis: `e8e1f4c7de84adc292207e1299a9cf0361c68a1a`; privates V2-Manifest: `1df916e64fb2c2575929195e83d52bd258aa3fe931cf95ddd42d5694437d1faa`.

Native V2 vom 12.11.2026, 08:41:24 UTC scheiterte nach genau rechter Eingabe und normalem Vorwärtsschritt. Die letzten zwei von 16 Paar-Leseversuchen meldeten `EvidenceError('state changed during read')`; der anschließend verlangte frische Datensatz fehlte. Es gab keine linke Eingabe. Root meldet vollständiges normales Schließen und Wiederherstellung; dieser Auftrag verändert keine Runtime.

## Abnahme

- Nur die exakten EvidenceError-Texte `state changed during read` und `tick changed during read` dürfen eine erneute passive Erfassung zulassen.
- Alle übrigen Readerfehler sowie Prozess-, Modul-, Hash-, Life-, Frische- und Policyfehler brechen sofort ab. Kein Retry nach einem erfolgreich gelesenen, aber ungültigen Paar.
- Höchstens acht Paar-Leseversuche pro Anforderung, einschließlich eines etwaigen Reads im unveränderten `periodic()`; zusätzliche Deadline 0,2 Sekunden nach dessen Rückkehr, 10 ms Pause zwischen transienten Fehlschlägen.
- Jeder fehlgeschlagene oder teilweise gelesene Versuch bleibt im vorhandenen Raw-Receipt. Kein Cache-Paar darf als neue Erfassung zurückkehren.
- Angeforderter neuer Zeitstempel, gleiche Prozess-/Life-/Modulbindung, Frische <=0,2 s, lokale strikte 2-s-Grenzen sowie globale 85/90-s-Grenzen bleiben bestehen.
- Genau das bestehende begrenzte Diagnoseprogramm bleibt erreichbar; keine Wiederholung von Eingaben, Route, Fire oder Lockerung von Gain-/View-/Return-Grenzen.
- V2, Frozen-Pakete und tatsächliches Fixture bleiben bytegleich. Beide V3-Gates bleiben False.
- Reproduzierbare RED/GREEN-Tests der tatsächlichen Controllerfunktionen, ganze kleine private Suite, normalisierter Delta, SHA-Closure, Bericht und Commit. Keine Builds und keine nativen Versuche.

## Prüfgrenze

Erfolg bedeutet offline geprüfte passive Wiedererfassung. A1, Runtime-Erfolg und die ursprüngliche Ursache der doppelten Gegenrotation bleiben unbewiesen. Root besitzt Integration, unabhängiges Review, Freeze und jede spätere Runtime.
