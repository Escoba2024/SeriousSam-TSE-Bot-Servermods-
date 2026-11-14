Owner a4_diagnosis; neuer Worktree `/srv/tse-a4-grounded-acquire-fix-20261114`,
Branch `codex/20261114-grounded-acquire-fix`, Basis
`6d07a9b2123723071eaac760131be8e7ff11b2fa`.

Claim ausschließlich `BotSupplyNative.h`, `test_cecil_native_bridge.py` im
Kandidatenverzeichnis `poc/candidates/redstation-supply-20261107` sowie neuer
Plan/Bericht. Alter Reproducerworktree bleibt sauber erhalten. Root integriert
und besitzt Runtime, DLL-/MSVC-Build und Livebestand. Hier nur Quellfix plus
gezielte portable SDK107-/ASan-Prüfungen, nice15 und keine parallelen Compiler.
Keine Delegation; STATICONLY von Root gilt unmittelbar nach regulärem Jobende.

Abgeschlossen: Quellen/Tests geprüft und committet, eigener Worktree sauber
übergeben. Keine laufenden Jobs/Compiler; keine Runtimebefugnis genutzt.
Root übernimmt Review/Integration und etwaigen Build024.
