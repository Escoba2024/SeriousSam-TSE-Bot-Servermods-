# Passiver Inventarreader: Geschwindigkeit und Support

Der bestehende originale Retail-Reader erhält vier zusätzliche private
Spielerfelder im selben zweifach verglichenen Snapshot:

| Ausgabe | Originales Entity-Offset | Interpretation |
|---|---|---|
| `current_translation_absolute` | `+0x104`, drei FLOATs | Aktuelle absolute Translation/Velocity XYZ, alle endlich |
| `support_pointer` | `+0x11c`, DWORD | Roher Supportzeiger; null ausdrücklich erhalten |
| `render_type` | `+4`, DWORD | Unveränderter roher Renderwert |
| `physics_flags` | `+8`, DWORD | Unveränderte rohe Physikbits |

Ein Nichtnull-Supportzeiger muss mindestens `0x10000` und auf vier Byte
ausgerichtet sein. Er wird **nicht dereferenziert**. Sein Wert beweist allein
keine gültige Kontaktgeometrie oder den Typ des referenzierten Objekts. Render-
und Physikwerte erhalten keine erfundene Enum- oder Geschwindigkeitsbegrenzung.
Alle neuen Reads laufen über das vorhandene `take()` und werden im zweiten
Pass einschließlich Velocity, Support, Render und Physik erneut verglichen.
Die Ausgabe bleibt nichtatomar; zwischen zwei gleichen Reads kann sich Zustand
ändern und wieder zurückkehren. Fehlende Zwischenereignisse sind kein
Nichtauslösen-Beweis.

## Originale Binärbelege

Engine SHA256
`b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f`:
FakeJump bei VA `0x6021860f` bildet `Entity+0x104`, schreibt die drei Komponenten
bis `0x6021864a`; `0x602186e2` liest Support `+0x11c`, `0x6021870e` löscht ihn.
Die drei neuen kurzen Reader-Signaturen an RVA `0x15860f`, `0x1586e2`,
`0x15870e` sind jeweils sechs Byte lang und enthalten keine absoluten Operanden.

EntitiesMP SHA256
`7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350`:
JumpFromBouncer bei `0x6035e87a` prüft Render `+4` auf3, liest bei `0x6035e880`
Physik `+8` und prüft Bit `0x200`; bei `0x6035e888` liest es Support `+0x11c`
und verwirft null. Neue relokationsfreie Signatur: RVA `0x4e87a`, 24 Byte.
Das zeigt notwendige Eingangszustände dieses Pfades, nicht dessen vollständige
Auslösebedingungen.

Alle bisherigen und neuen Fingerprints wurden direkt aus den beiden
hashgeprüften Originaldateien über ihre PE-Sektionen gegengeprüft. Kein
1.10-ABI-Schluss und kein Funktionsaufruf in einem Prozess. Der Reader prüft
auch die neuen exakten Muster beim Öffnen und pro Sample. Zusatzkosten im
vollbesetzten Vierer-Snapshot: 24 Datenbytes pro Spieler je Pass, insgesamt
192 Datenbytes plus 42 Fingerprintbytes gegenüber vorher. Die nächste native
Messung muss tatsächliche Laufzeitkosten und verworfene Samples weiter erfassen.

## Regression und Abgrenzung

RED: Der alte Reader fehlte im neuen Ausgabecheck; 19 Negativfälle für nichtendliche
Velocity, ungültigen Support und Änderungen zwischen den zwei Reads wurden
fälschlich angenommen. GREEN: 19 portable Tests bestehen, einschließlich aller
15 vorherigen Tests, aller drei Velocityachsen, gleicher-Tick-Änderungen von
Support/Render/Physik und des bewusst nicht dereferenzierten Supportzeigers bei
fehlender Waffe.

```sh
python3 tools/test_retail_inventory_readonly.py
```

Keine laufenden Prozesse oder Root-Dateien wurden gelesen oder verändert.
Die bisherigen nativen007-Zahlen von 19 neuen und 34 alten Leben bleiben
unverändert. Die neuen Felder sind dort nicht nachträglich verfügbar. Erst ein
neuer eigener Lauf kann Bouncer-Zustand, Velocity und Support zugleich liefern;
kein neues natives PASS aus dieser portablen Erweiterung.
