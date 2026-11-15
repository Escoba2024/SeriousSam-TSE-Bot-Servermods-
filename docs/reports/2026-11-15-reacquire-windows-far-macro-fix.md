# Reacquire-Diagnose: Windowsmakro `far`

Root-Build025 aus `f905962ff5dab94c757518d9109f6a0ae0818a69` ist tatsächlich
an `BotSupplyNative.h(962)` fehlgeschlagen. Der neue Diagnoseparameter `far`
kollidiert mit dem leeren Windowsmakro aus der vorhandenen Toolchain:
`Windows Kits/10/Include/10.0.19041.0/shared/minwindef.h:94` definiert `far`.
Eine Makroexpansion entfernt damit den Parameternamen und den rechten Operanden
in `farHint=far;`. Der Windowsfehler bleibt ein fehlgeschlagener Build.

## Enger Umsetzungsplan

1. Den bestehenden SDK107-Harness um `#define far` ausschließlich vor dem
   extrahierten tatsächlichen Produktionssource ergänzen. Vor Ownershipfixture
   und synthetischen Tests folgt `#undef far`; deren alte Variablennamen
   bleiben erlaubt. Am unveränderten Header einen echten Compiler-RED sichern.
2. Ausschließlich den kollidierenden Diagnoseparameter und dessen Verwendung
   umbenennen. Keine Suche, Getter, Guards, Steuerung, Logfelder oder API ändern.
3. Den bestehenden vollständigen SDK107-Harness mit derselben Makroumgebung
   einmal normal und einmal ASan/UBSan seriellnice15 ausführen. Die vorhandene
   Byteinverse/Guardmutation und3532Prüfungen bleiben bestehen. Keine erneute
   Ausführung der16 schon abgenommenen Parentprogramme bei unverändertem Scope.

## Tatsächliche Ergebnisse

Der unveränderte Header scheiterte im neuen permanenten Makrotest genau in
`SCecilReacquireDiagnostic::Geometry`: `expected primary-expression before
';' token` bei `farHint=far;`. Der Header hatte zu diesem Zeitpunkt keinen Diff
gegen die Build025-Quelle. Der tatsächliche Produktionsbody wurde kompiliert,
keine Modellfunktion. Der bisherige plattformbezogene Loaderausschluss des
SDK-Harness bleibt bestehen; dies ist kein vollständiger Windowsbuild.

Die einzige Produktionsänderung lautet Parameter `far` → `farValue` und dessen
Verwendung in derselben Zuweisung. Ein vollständiger Bytevergleich bestätigt:
Nach genau dieser Ersetzung ist der Header ansonsten bytegleich zur Basis.
Es gibt kein Makro-`undef` im Produktionsheader und keinen Gameplay-/Diagnose-
Verhaltenswechsel.

Mit dem weiterhin aktiven leeren `far`-Makro um den tatsächlichen Source bestehen
**3532/0 normal** und **3532/0 ASan/UBSan**, beide Exit0 ohne Sanitizerbefund.
Die ursprüngliche Reacquire-Byteinverse
`88950482f46137a5af41a6214451221855be8aa5c4c41ac25f443ddea06493df`,
die Guardmutation und die konservative Formatgrenze2029Bytes+NUL<2048 wurden
in beiden Läufen erneut tatsächlich geprüft. Compiler liefen seriellnice15.
Die16 Parentprogramme wurden entsprechend dem engen Rootauftrag nicht erneut
gestartet; deren vorherige Ergebnisse bleiben getrennt erhalten.

## Reproduktion und Pins

```sh
nice -n 15 python3 -B poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
nice -n 15 python3 -B poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es --sanitize
```

| Pin | SHA256 bzw. Commit |
|---|---|
| Basis/Build025-Quelle | `f905962ff5dab94c757518d9109f6a0ae0818a69` |
| Makro-RED/Claim/Plan | `5c6b2cf8f8328b2a26d552fa75f2835cef14997a` |
| Einzeiliger Produktionsfix | `06a14b3cc27bf8103b7385234848705790f79386` |
| BotSupplyNative.h | `92712d4e626fdc3a4b027aa964226b4dca5a3b89684148a36df1826ee9c6b635` |
| test_cecil_native_bridge.py | `d07147f295fa18312a1656fd9dd08476b35d633c448f371eaf7bda3d335ed178` |
| Toolchain-minwindef.h | `461317a41265014fb829ab3d6fc9de1949e128ea791a26a1352c065d1025e5b4` |
| Private final-receipt.json | `f036122487e794626a555fca3c6c63725cfc0491343af4f297a05e20be5d6de4` |

Eigener Worktree `/srv/tse-a4-reacquire-winmacro-fix-20261115`, privater Ordner
`.codex/evidence/reacquire-winmacro/`: fehlgeschlagenes `red.log`,
`green-normal.log`, `green-asan.log`, Quittung und O_EXCL-Metadatenfinalizer.
Alle privaten Dateien0600, Ordner0700. Kein ursprüngliches Build025-Artefakt
wurde durch diesen Agenten verändert. Alle eigenen Jobs sind regulär beendet.
Root integriert und baut026 als neuen Kandidaten separat. Kein Retailbuild,
Native-/ABI-/Skullsfix-/A4-Abnahmeclaim aus diesem Portabletest.
