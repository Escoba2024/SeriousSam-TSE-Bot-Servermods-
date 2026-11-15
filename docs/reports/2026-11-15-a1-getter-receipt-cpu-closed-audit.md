# A1 Getterreceipt-Trace 093359: CPU-FAIL, vollständiger Rawabschluss

Der Fall mit Resultat-SHA256
`d5064191e403a018384c6354a4ab2afd836f4915476c668df53023b771f2f3b8`
bleibt **FAIL**. Er wurde in `OBSERVING` nach 1,160161 s aktiver Beobachtung
wegen `host CPU delta exceeds75%` geschlossen. Die geplanten 10 s wurden
nicht abgeschlossen. Keine neue Getterursache oder A1-Abnahme ist belegt.

Der einmalige vollständige Audit bindet alle **13 Worker-Wires** an ihre
archivierten Längen und SHA256-Werte, alle enthaltenen Payloads bytegenau an
die ursprünglichen Journalranges und anschließend an die unveränderte reine
Packet-/Tracevalidierung aus dem eingefrorenen Paket. Ergebnis:

| Nachweis | Geschlossenes Ergebnis |
|---|---|
| Journal-/Wire-Captures | alle Serialnummern 1–28 genau einmal, kein Loch |
| Stop-/Finalgrenze | `S=27`, `F=28`, 28 validierte Pakete |
| Events | 406, lückenlose Sequenz; Cutoff 397, 9 Cleanup-Tail-Events |
| Calls | 203 ENTER/LEAVE-Paare, keine offenen Aufrufe; Reihenfolge/Nesting gültig |
| Getter | ein Main-TID-Binding; **0 Faults, keine Mismatchdetails** |
| Verlustzähler | 0 Drops, AbortedLeaves, RejectedEntries, ErrorsLost, DetachFailures |
| Callbacktransport | `OBSERVER_TRANSPORT_COMPLETE_ONLY`, keine Gameplayfreigabe |
| Originalrestore | alle 38 Regionen = Vorherbytes = erwartete HIGHLOW-Rebasierung; Identität gleich, Unload/Detach bestätigt |

Der erste Capture hatte noch keine Events und kein Getterbinding. Event 1 ist
ProcessGameTick ENTER, wall_ms `1794735268018`; das TLS-Binding folgt bei
`1794735268019`. Letztes Event ist ProcessGameTick LEAVE bei
`1794735269427`: 1409 ms Event-Wallspanne. Diese Wallwerte werden nicht in
Host-Monotonic-Zeiten oder native Simulationsticks umgerechnet.

Alle 18 Kindzähler sind ausgewertet. Tatsächlich aufgerufen wurden:

| Kind | Vollständige Calls | Einordnung |
|---|---:|---|
| ProcessGameTick | 29 | Ordinale 1–29, native Tickwerte 9,150016785 bis 10,550022125 |
| ApplyAction | 58 | zwei registrierte eigene Originalakteure |
| PostMoving | 58 | dieselben registrierten Akteure |
| CastRay | 58 | sämtlich `unregistered`, außerhalb einer beobachteten Colt-Launchkette |
| Übrige 14 Arten | 0 | insbesondere kein Init, Respawn, Bullet oder ReceiveDamage |

Jeder Call ist privat an unveränderten PID/start/Epoch/Session-/Worldkontext,
Main-TID, Parentcall und Eintritts-/Austrittstick gebunden. Die zwei beobachteten
Playerkontexte behalten Generation 0, `init_call_id=null` und keinen gültigen
Initanker. Das sind bestehende warme Sessions, kein First-State-/Respawnordinal-
Beleg. CastRay allein beweist weder Schuss noch Schaden.

Der finale Stopgrund lautet `host requested`; es gibt genau einen Stop-,
Status- und Finishstop-Record und keinen Schedulerfehler. Der kürzlich korrigierte
**Nicht-Host-Faultstop-Pfad ist in diesem Fall nicht nativ ausgeübt**.
Die größte Capturelaufzeit beträgt 0,054472 s, der größte Startabstand
0,074880 s; die bestehenden 100-ms-Grenzen wurden im vorliegenden Stream
eingehalten. Das belegt keine harte Echtzeitgarantie.

Die CPU-Überschreitung ist konkret auf das Host-Monotonic-Intervall
`1361666.249204419` bis `1361667.408481180` gebunden: **77,50556793 %** über
1,159276761 s. Aktive Beobachtung begann bei `1361666.248320294`, der Stopbefehl
bei `1361667.411608829`. Die Messung ist ein Host-Gesamtmittel einschließlich
anderer Lasten, kein Instantanpeak. In den fünf Hostrecords befindet sich
außerdem eine Startupmesslücke von 25,678533 s; eine lückenlose Reserveabnahme
wird daraus nicht abgeleitet. RAMminimum 2745737216 Byte und freier Datenträger
mindestens 9059078144 Byte blieben oberhalb der unveränderten Grenzen.

Es gibt keine Prozess-CPU-Deltas für Worker, Spielrollen oder andere Lasten.
Worker-Startbindung und IPC-Wandzeiten sind vorhanden, ersetzen aber keine
CPU-Messung. **Workeranteil und Ursache der Host-CPU-Erhöhung bleiben UNKNOWN**.
Der neue uninstrumentierte Kontrollfall ist separat und macht diesen Trace
weder zur gültigen 10-s-Abnahme noch zu einem kausalen Overheadvergleich.

Private Reproduktion im bestehenden Audit-Worktree:

```sh
python3 .codex/evidence/a1-getter-receipt-cpu-audit/analyze.py /neuer/exklusiver/receipt.json
```

Der Reader importiert nur die SHA-gepinnten reinen Framing-/Observervalidatoren,
keinen Controller und kein Frida. Die exklusive 0600-Quittung enthält alle
13 Wirehashes, Capture-/Call-/Ticknenner, Original-/Sourcehashes und Grenzen;
SHA256 `8279eef3572e83b8e5f96650657c6a0add64c8af005efff07b4aa98df9c6d708`.
Keine Tests, Runtime, Wiederholung, Sourcekorrektur oder Grenzlockerung wurden
für diesen Audit ausgeführt. Rohidentitäten und Rawbytes bleiben privat.
