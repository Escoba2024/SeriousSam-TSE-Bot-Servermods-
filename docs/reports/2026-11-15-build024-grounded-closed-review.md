# Build024: neun GroundReplans vollständig geschlossen ausgewertet

**Der neue Stale-anchor-Zweig ist nativ weiterhin nicht eindeutig belegt.**
Alle neun Ereignisse lassen sich eindeutig auf acht eigene Nativeleben binden.
Bei9/9 entspricht der letzte protokollierte Voranker dem frischen Hint.
Diese Vorzustände liegen2–19 Policyticks zurück; der unmittelbare Anker vor
Zuweisung ist9/9 UNKNOWN. Auch der bereits vorher mögliche positive Replanfall
bleibt somit9/9 mit den Daten vereinbar. Kein Wirksamkeits-, Routen-, A4- oder
Promotionsnachweis wird daraus abgeleitet. A bleibt offen, B nicht begonnen.

Root schloss das600,020550285s-Fenster mit0neuen BAD/Disconnects und vier
regulären Closes. Status unverändert
`PASS_LIMITED_A4_OBSERVATION_FUNCTIONAL_REVIEW_REQUIRED`, Result-SHA256
`c6bcb9ae7e9798fe1f8ffc0178fc25bed78ecf97e4c3fb222d2edc30421fd1bc`.
Root prüfte die Wiederherstellung640Dateien/vierLogs samt Prozess-/Displaycleanup.
Diese Analyse änderte keinen Livebestand und startete keine Tests oder Runtime.

## Vollständiger Nenner und Zielketten

Drei Ereignisse stammen von botA, sechs von botB. Ihre SourceSpawns,
Generationen und Entities passen eindeutig zur festen Ownslotregistry,
Welt und Phase0/PIDstart-Epoch. Source-WPO-/PlayerObserve-Nativezeiten werden
mit ihren ganzen Druckintervallen genau einem kanonischen Nativeleben
zugeordnet. Die Root-V3-Inputhashes bleiben identisch; die186Lebensnenner wurden
zusätzlich mit dem bestehenden reinen Summarizer unabhängig nachgerechnet.
Kein SourceTick wurde durch20 in Nativezeit umgerechnet oder interpoliert.

Die Tabelle nennt reine Source-Policyticks. „Native Radius“ bedeutet einen
kanonischen Positionswert strikt innerhalb der ursprünglichen ersten Kugel,
konservativ nach einem späteren Source-Nativeclockwert des Replans und vor
einem früheren Source-Nativeclockwert des Zielendes. UNKNOWN bedeutet keine
negative Bewegungs-/Ankunftsbehauptung.

| Fall | Rolle:Local / Gen | Tick | Source→Hop / Hint | Ziel | Native Radius im sicheren Zielfenster | Ende des ursprünglichen Ziels |
|---|---|---:|---|---|---|---|
| 1 | A:1 / 8 | 2068 | 69→74 / 61 | Health309 | UNKNOWN | unavailable2121 |
| 2 | A:2 / 11 | 2728 | 20→14 / 179 | W7/243 | UNKNOWN | timeout3075 |
| 3 | A:2 / 14 | 5799 | 73→74 / 61 | Health309 | Ja | unavailable5928 |
| 4 | B:2 / 14 | 4055 | 94→91 / 54 | W11/248 | Ja | unavailable4196 |
| 5 | B:0 / 17 | 6912 | 69→73 / 67 | Armor310 | UNKNOWN | timeout7070 |
| 6 | B:0 / 17 | 7048 | 69→73 / 68 | Armor310 | UNKNOWN | timeout7070 |
| 7 | B:2 / 22 | 8385 | 69→73 / 67 | W7/243 | Ja | unavailable8705 |
| 8 | B:0 / 22 | 9522 | 69→73 / 67 | Armor310 | Ja | timeout9542 |
| 9 | B:1 / 30 | 12017 | 90→91 / 54 | W12/267 | UNKNOWN/rechtszensiert | unavailable12114, nur Closed-Source-Nachlauf |

Vier Ziele waren Waffen, zwei Health und drei Armor. Fälle5/6 gehören zum
selben Leben und Zielversuch; ihre Folgebelege dürfen nicht doppelt als
unabhängiger Erfolg gezählt werden. Kein Fall endet im ursprünglichen
Sourcefenster erneut mit `unreachable_hold`; das beweist die neue Verzweigung
wegen der fehlenden unmittelbaren Vorankerwerte dennoch nicht.

## Radius, Bewegung und Aufnahme getrennt

In4/9 Fällen liegen konservativ zeitlich zuordenbare Native-Erstkugelbelege
vor: Fälle3/4/7/8, erste entsprechende Readserials6613/4808/9950/11123.
Originalradien bleiben3/2/3/3; keine EPS, vergrößerten Kugeln oder
Vorbeifahrtfreigaben. Weitere Nativepunkte liegen in breiten Eventclockfenstern
oder erst später im Leben. Sie bleiben separat erhalten und gelten weder als
sicher nach dem Reset noch automatisch als Teil desselben Zielversuchs.
Insbesondere wären die bloßen fünf späteren Lebens-Radiustreffer des ersten
Auswerteschritts kein sauberer Zielfenster-Nenner.

Die gerundeten Sourcepositionen belegen innerhalb desselben Zielversuchs in
Fällen4/5/7 eine ganze Druckbox strikt innerhalb der ersten Originalkugel.
Source `nav_source=Hint`, anderer Hop und `nav_travel=1` sind für2/4/5/6/7
protokolliert. Andere Folgen zeigen bereits spätere Sourcepunkte; ausgelassene
Zwischenschritte werden nicht erfunden. Der interne committed State wurde
nicht unabhängig als atomischer Nativezustand gelesen. Positionsänderungen,
Navownership-/Movefelder und Fire-request-Beobachtungen bleiben getrennte
Belege; Knockback, Kampf oder andere Bewegungsanteile werden nicht exklusiv
dem Replan zugeschrieben. Die zweite Kugel wäre wegen nur gerundet geloggter
Gravity eine bedingte Rechnung, kein zusätzlicher unabhängiger Nativebeweis.

In sieben Ereignisketten/sechs verschiedenen Leben folgen Sourceinventargewinne,
mit jeweils genau einem passenden kanonischen Maskenänderungsintervall. Häufig
geschieht das erst nach Zielabbruch bei einem anderen Versuch. Nur Fall4 zeigt
während des noch gehaltenen ursprünglichen W11-Ziels einen passenden W11-Bitgewinn:
SourceTick4196, `11→1035`, kanonischer Gewinn bei Native209,508178711; zugleich
endet248 als `unavailable`. Zuvor wurde dort bereits W4 erworben, später W12.
Das belegt echte Waffenbits, aber keine exklusive Pickupcallback-ID von Item248.
`unavailable` wird nicht pauschal als Versagen oder konkurrierende Aufnahme
ausgelegt: konkrete Readgründe fehlen bei Diagnostics0.

Für alle neun Fälle bleiben **attributierter Schaden und Kills UNKNOWN**.
Es fehlen genaue Damage-/Tick-/Life-/Killerrecords. Source-Schusszähler,
Native-Fire-request-Muster und globale Serverkills sind kein Ersatz für diese
Zuordnung; Query-Fragdeltas werden dafür nicht verwendet.

## Zensierung und längste unversorgte Leben

Final-/Closed-Logs sind exakte Fortsetzungen der während der Beobachtung
archivierten Sourcepräfixe und enthalten ebenfalls genau3+6Replans.
Fall9 bekommt im Closed-Source-Nachlauf Zielende12114/unavailable und später
SourceDeath12221/Generation30, anschließend eine neue Generation. Ein expliziter
Source-Hintexit54→53 ist dort ebenfalls sichtbar; direkte Source-Radiuspositionen
wurden nicht beobachtet. Diese zusätzlichen Sourcezeilen haben keine neuen
kanonischen Nativeframes. Das Nativeleben bleibt rechtszensiert; weder Todzeit,
Radiusankunft noch Kill werden nachträglich als nativ gemessen ausgegeben.

Die vier größten vollständig beendeten NoUseful-Beobachtungen enthalten
keinen GroundReplan:

| Eigener Slot / Rolle:Local / Gen | NativeSpawn | Beobachtete Alive-Spanne ohne Useful |
|---|---:|---:|
| 0 / A:0 / 31 | 508,649322510 | 50,137786865s |
| 5 / B:0 / 14 | 267,208282471 | 48,138244629s |
| 4 / A:3 / 22 | 408,273834229 | 40,790039063s |
| 7 / B:2 / 18 | 268,008087158 | 35,991210938s |

Die vollständigen Ziel-/Endketten bleiben privat erhalten. Waffenversuche
enden mehrfach `unavailable`, andere Ziele mit `connector` oder Tod.
Diagnostics0 erklärt die jeweiligen Gründe nicht. Es gibt keine nachträgliche
Erklärung der früheren023-Leben oder kausale Verbesserungsaussage aus diesem
Einzelfenster.

## Minimale nächste Messinformation und Reproduktion

Es fehlt konkret **`anchor_before_reset`**, gelesen aus `s.anchor` im bestehenden
bereits erfolgreichen `CecilGroundReplan`-Aufruf unmittelbar vor dessen Zuweisung.
Das vorhandene Logfeld `anchor` enthält bereits den frischen Kandidaten.
`anchor_before_reset != anchor` würde die neue erfolgreiche Stale-anchor-
Verzweigung desselben Calls unmittelbar belegen; Gleichheit bliebe der alte
positive Fall. Kein neuer Probe-/Gameplayweg, Retarget oder Runtimevorgang wurde
hier implementiert. Über einen weiteren Schritt entscheidet Root getrennt.

Eigener Worktree `/srv/tse-build024-grounded-closed-review-20261115`, Basis
`c2e551ce0d832ec5cc17bdebfd8b4ad553dbd198`. Privates reproduzierbares Rezept,
aus diesem Worktreeroot mit den jeweiligen privaten Skriptpfaden:

```sh
nice -n 15 python3 -B .codex/evidence/grounded024/analyze.py
nice -n 15 python3 -B .codex/evidence/grounded024/enrich.py
```

Erster vollständiger Nenner `final-receipt.json`, SHA256
`93d09e736982c9649478023920d5f9ca3cff5c0b3c27dc127356923bd8b54efc`;
abschließende Vollquittung `complete-receipt.json`, SHA256
`464857b51acf2147737bc1f598e6ad94936be15f0e786b4b60a46789483627b6`.
Beide Reader und ihre Eigenhashes sind in der vollständigen Quittung enthalten;
keine nachträglichen ungeskripteten Metadaten erforderlich. Root reproduzierte
beide Dateien unverändert und byteexakt. Acht vollständige gebundene Native-
lebensdatensätze, neun Sourceketten samt Closed-Nachlauf, alle Treffer-/Unknown-
Nenner und Hashes bleiben privat0600/0700. Keine Rohspieleridentitäten imGit.
Alle Analysejobs sind beendet. Keine Produktions-/Harnessänderung oder Tests.
