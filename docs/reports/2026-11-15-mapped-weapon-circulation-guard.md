# Begrenzter Schutz gegen erneute Kantenrunden: Source-/SDK-Abschluss

Der neue Schutz merkt sich höchstens acht gerichtete Kanten derselben gültigen gemappten Waffen-Attemptdomäne. Eine bereits besuchte Kante erhält beim Rückwechsel keine neue10s-Allowance. Nur eine neue gültige Kante oder neue≥0,75m-Bestdistanz gegen **denselben** gespeicherten Kantenbezug zählt als Fortschritt. Die bisherigen Einzelkantenberechnungen und die feste Zieldeadline bleiben erhalten.

Im echten sequenziellen SDK-Reproducer endet die vorher bis19,95s gehaltene20s-Attempt nun nach12,800s. Das ist ein portabler Mechanismusnachweis mit geskripteten Positionen/Casts, keine native Versorgungsverbesserung. Die erste physische Ablehnung im geschlossenen032-Fall bleibt UNKNOWN. Kein neuer DLL-/Retail-/Native-/Rolloutnachweis und keine A4-Abnahme.

## Konservative Grenzen

World/Map/Actor/Generation/Item/Goal/GoalSince/Deadline bilden die Domäne. Pro Kante bleiben Source/Hop und beide Koordinaten/Radien gebunden; geänderte Bezugspunkte können keine falsche Bestdistanz liefern. Fehlende Accepted-/CurrentPoint-/Ownershipbelege, Locks/Spezialkontext, Gravityänderung, Rückwärtszeit und Beobachtungslücken disarmen den zusätzlichen Schutz für den Rest derselben Domäne. Die Rückkehr zu alten Werten armiert ihn nicht erneut. Echte neue Domäne bzw.ClearGoal/Reset beginnen eigenständig; unveränderte Deadline und Legacywatchdog bleiben zuständig.

Beim neunten neuen Abschnitt werden keine alten Fakten verdrängt: Der Zusatzschutz wird konservativ disarmed, damit eine legitime längere Route nicht allein wegen begrenzten Speichers verworfen wird. Keine neue Radius-/Timer-/CD-/Floor-/Pit-/NAV-Ankunftsfreigabe, keine Engine-/Ray-/Clock-/RNG-Abfrage oder Allokation. `observedWorld` kopiert ausschließlich das Ergebnis des bereits bestehenden Eligibility-GetWorld-Aufrufs.

Der neue Abbruch verwendet vorhandenes RejectItem/ClearGoal/neutral-Verhalten. Die Quittung `CecilItemTransitEnd reason=revisited_edges` benennt den neuen Pfad; `since` ist dann dessen gemeinsamer letzter qualifizierter Fortschritt, `best_distance` bleibt ausdrücklich die gegenwärtige Einzelkantendistanz. Der bisherige Grund `no_hop_progress` bleibt für die alte Grenze erhalten.

## Tatsächliche Prüfungen

| Stufe | Ergebnis |
|---|---|
| Reproducer, Produktion unverändert |4181 Checks/1 gezielter RED|
| zusätzliche12 Unterbrechungsfälle, Produktion unverändert |4193/1, identischer RED|
| Fix +21 History-/Gainbase-/Domain-/Overflow-/Metadatakontrollen |4214/0, normaler SDK107-Lauf|
| vollständige Headerinverse |exakt Parent`641334f6885e5c5d6517659374f0c32f933a01e5a78c4116f19193aa94b28bc8`|
| ASan/UBSan, dieselbe Header-/Testquelle |4214/0, Exit0, keine Sanitizerfehler|
| Retail/Native/Rollout |PENDING, ausschließlich Root|

Die alten4175 Checks sind in beiden vollständigen RED-Stufen und im GREEN-Lauf enthalten. Echter59→27-Ankunftspositivfall, unveränderte Inventare/Deadline/Raybudgets, legitime neue Kanten, gleichbezogene akkumulierte Viertelmetergewinne, kein Zusammenrechnen verschiedener Hops und keine Eviction bestehen. Die reine Historykomponente hat im Fixture0 zusätzliche Rays/Worldlookups/Heapallokationen.

```sh
TMPDIR=/dev/shm nice -n 15 python3 -B poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
# nach Root-Resume tatsächlich separat ausgeführt, dieselbe Quelle:
TMPDIR=/dev/shm nice -n 15 python3 -B poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es --sanitize
```

Private vollständige Logs/Inverse unter `.codex/evidence/mapped220-circulation/`. Die erste private Inverseprüfung hatte einen zu breiten verbotenen Textvergleich `new `, der lediglich einen Kommentar traf; nach Entfernen dieses untauglichen Kommentarscanners ist die vollständige Headerinverse tatsächlich erfolgreich. Kein Produktionsfehler wurde dabei umetikettiert. Keine erneuten Rawreplays; Quellcheckpoint ist von späterer Sanitizer- und Nativequalifikation getrennt.

Finale Quittung `final-source-receipt.json`, SHA`bbc9039e651788ef1e11c9e10d80de9d6486906f3b1372f5a8448f9de0a700a9`,4903B, wurde mit frischem O_EXCL-/0600-Ziel bytegleich reproduziert. Privater Reproducer `make-final.py` SHA`ea589002489eb0557177a7377ebdeb3b630ac669246abe64756134c24583d358` akzeptiert als einziges optionales Argument einen frischen Receiptpfad; er liest nur vorhandene eigene Source-/Logbelege, keine nativen Raws. `verify_inverse.py` SHA`ca355d472d978db968aff32102ee9a775186ce1b550fe235107a52d28373ce0c` prüft die ganze Headerinverse separat.

Sourcecheckpoint`43d8632f49bb1078678de1a0d2d3091ae3c8a62b`: Header`49229af92892fe030f74b7a09815647c90ec0572f4a1065c1ed20fc4f0590b3d`, SDK-Test`47319cd97ee30ff790053f94a1f69d37a20f7a562345d5cae77255675e4a9f79`. Normallog`96e28b42703db4c09e13a0ae9c8e1ecc1bda6286a70b2b16c63178e99d740128`; ASan/UBSan-Log`684558cc4b581afe09d57a2eb92f7f41f170f05e1c143e09325d256754016407`. Die Fixture-Summary liest nach ClearGoal die bereits gelöschten Legacy-Uhren(-1); deren rechnerisches `clock_age` ist ausdrücklich kein Abbruchzeitbeweis. Der Zustandswechsel `ended=12.800` ist der tatsächlich geprüfte Endpunkt.

Alle Compiler-/Testjobs natürlich beendet, tmpfs-Wegwerfverzeichnisse vom geerbten Harness entfernt; keine Rawhandles oder Hintergrundjobs. Ausstehend sind unabhängiger Rootreview, neuer Windowsbuild und native Wirksamkeits-/Regressionsbelege. Keine Integration/Promotion durch den Autor.
