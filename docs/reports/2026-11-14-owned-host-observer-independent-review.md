# Unabhängiger Review der äußeren Hostbeobachtung

**Ergebnis: 0 Critical, 1 Important, 0 Minor.** Geprüft wurde Root-Basis
`627cf3427300b269f077c23df83a9de6914abceb`, einschließlich der sieben
Observer- und drei vorhandenen Budgettests als Quelltext. Keine Quellen oder
bestehenden Tests geändert, keine Runtime gestartet. Die bestehende Suite
wurde hier nicht nochmals ausgeführt.

## Important: Journalfehler kann Abschlussquittung überspringen

In `tools/observe_owned_host_budget.py:60` liegen `journal.write/flush` außerhalb
der Fehlerbehandlung von `sample()`. Ein nach Spawn auftretender Fehler wird
zunächst im äußeren Handler gespeichert. Der `finally`-Pfad wartet regulär auf
das eigene Kind und setzt `child_reaped`, ruft dann aber in Zeile 84 nochmals
ungeschützt `sample()` auf. Schlägt dasselbe Journal erneut fehl, entkommt die
Exception vor Quellenabschlussprüfung und `receipt.json` in Zeilen 86–92.
Damit fehlt die persistente sticky Fehler- und Reapquittung, selbst wenn die
separate Receiptdatei weiterhin geschrieben werden könnte. Das ist kein
beobachtetes Spielprozessleck; der Fehler liegt nach dem regulären `wait()`.

Die minimale portable Reproduktion ersetzt Popen vollständig durch einen
FakeChild und beschädigt ausschließlich das Samplejournal. Ein einzelner
Flushfehler ergibt korrekt `FAIL_HOST_OBSERVATION` mit Receipt. Ein wiederholter
Flushfehler ergibt eine entkommende `OSError` und keine Receipt; in beiden
Fällen wird der Fake zweimal gewartet. Ergebnis: **2 Tests, 1 PASS, 1 RED**,
0,004 Sekunden, null echte Kindprozesse. Der RED prüft die geforderte
Fehlerquittung, keine nachgebaute Observerlogik. Root behebt den Quellpfad;
dieser Review enthält keinen Fix.

Privater reproduzierbarer Aufruf aus dem Reviewworktree:

```sh
python3 -B .codex/evidence/host-review/journal_failure_repro.py
```

Reproduktion, RED-Ausgabe und Faktenquittung bleiben privat. Die zusätzliche
Rootquittung heißt `owned-host-observer-independent-review.json`, SHA256
`3c0cc72163ce2ba33a4589674e09e3feed8bab162621b16131dcc36c8a1c5339`.

## Übriger geprüfter Umfang

Der normale Pfad liest eine Baseline vor Popen und eine Endprobe nach
beobachtetem Exit. Quellenpins stehen vor/nach Spawn und nach Ende; die
PID-Startgeneration kommt aus `/proc`. Kein Shellstart, Signal, Thread oder
Retry ist vorhanden. Neue Evidenzdateien verwenden 0600/O_EXCL/NOFOLLOW, das
neue Verzeichnis 0700. Hostlesefehler, aufgezeichnete Ressourcenverletzungen,
Startfehler, Quellenänderungen und nichtnull Exitcodes bleiben im normalen
Fehlerpfad sticky. Der Controller behält seine eigene begrenzte Lebensdauer
und Cleanupzuständigkeit: Der Observer selbst wartet ohne eigenen Kill- oder
Timeoutpfad auf ihn. Er ist damit Beobachter, kein Prozesssupervisor.

`host_budget.py` ist unverändert, SHA256
`9a8132af6618173bf7150dbc96c50aaf653b4903e75b79a4e73f82d3fb7068e8`.
Die Grenzen bleiben 75 Prozent CPU, 1610612736 Byte verfügbarer RAM und
8589934592 Byte freier Datenträger. CPU ist ein Hostintervallmittel einschließlich
anderer Last, kein Spitzenwert. `qualified` und `budget_pass_claim` bleiben false.
Observer-SHA256:
`4d036d5c0469e9111722baca4200b34f361d30dc44753e35ec615e4dd5cf614e`.

Der bereits geschlossene eigene Python-Methodenbeleg wurde getrennt gelesen:
vier Proben, maximale Lücke 1,000839415 Sekunden, Baseline vor Spawn und Ende
nach beobachtetem Exit, Exit 0, reaped, keine Signale oder Wiederholung. Dieser
normale Methodenbeleg bleibt bestehen; er deckt den gefundenen Journalfehler
nicht ab und ist keine TSE-, Dauerstabilitäts- oder Budgetqualifikation.
