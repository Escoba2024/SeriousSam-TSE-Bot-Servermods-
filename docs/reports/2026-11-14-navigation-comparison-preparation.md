# Red Station: drei kontrollierte Vergleichsarme vorbereitet

Noch kein nativer Vergleich und kein Rangurteil über Navigation.
Der [Vergleichsplan](../superpowers/plans/2026-11-14-navigation-baseline-comparison.md)
wird inline durch Root umgesetzt. Die Flotte bleibt auf Dev-Cecil048 und
fünfmal Public-Gen2. Die Nutzerbeobachtung einer schlechteren Navigation
bleibt unbestätigt.

Aus dem unveränderten deaktivierten V3-Hardcontroller mit Manifest
`a4568cbe60716887e195f7996ffeed774c1035cadcb11660b644c1fe64b4b2d9`
wurden drei getrennte deaktivierte Arme abgeleitet. Jeder ist auf
Red Station/Hard2/600s/Diagnostics0 begrenzt. Controlleränderungen betreffen
nur Kandidatenpfad und eigene Unit-/Evidenznamen; der Adapter ändert nur
Kandidatenhash, die engere Optionsprüfung und die versionsgebundene
Profilprüfung. Reader, V3-Source-/Life-/Readattempt-Predikate, Rohdaten,
Start-/Pausebarriere, Ressourcenlimits, normale Closes und Restore bleiben
bytegleich beziehungsweise im Controller sonst vollständig unverändert.

| Arm | Bot-DLL-SHA256 | Deaktiviertes Manifest |
|---|---|---|
|048|`ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530`|`9d3f27501151176b4641e5521e37b2996e74eda1ed10271798648ee733180a14`|
|018|`6db89204e33dc7d76ecdfed68055d2b75bde4950475793a57101fd0cefcb8e4a`|`5acfe55ef475bc9529f87e919539ea38fdd3e4e72aefdad14cc7410f6bd2aa75`|
|020|`094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0`|`cbcffaab5964efe82d776938e46187b38de671c69e425d5fdf30b40a5fedae03`|

Jedes Paket hat138 Runtime-,57 Source- und36 Pythonpins. Zu jedem Kandidaten
wurden das fest gepinnte Buildmanifest, DLL und alle47 Quell-/28 Overlaydateien
frisch geprüft. Pfade:
`/srv/tse-nav-{048,018,020}-red600-disabled-20261114`.
Alle Gates/Qualifikationsflags bleiben deaktiviert.

Ruling: Der tatsächliche048-Quellcode schreibt **BOT-Expert-Rifle**, nicht
die im Plan verkürzte Bezeichnung Expert-Rifle. Die Prüfung verlangt exakt
BOT-Expert-Rifle/tier5/marksman ohne arena-v1;018/020 verlangen exakt
DEMON/tier3/duelist mit arena-v1. Unbekannte/malformed Attachments,
Fallbacks oder fehlende lokale Slots/Gruppen sind Fehler. Derselbe
Profilwert7 bezeichnet somit bewusst verschiedene vollständige Kandidaten;
dieser Vergleich isoliert keine einzelne Navigationsänderung.

TDD: zuerst reproduzierbares RED wegen fehlender neuer Module, anschließend
neun neue Vertragsfälle GREEN. Sie prüfen beide echten Profilschemata,
unzulässige Optionen, unveränderte AST-Körper des Adapters, vollständige
Rückführung der Controlleränderungen, fehlende/nicht eindeutige Anker und
manipulierte tatsächliche DLL-/Quelldateien. Gemeinsam mit24 vorhandenen
V3-,11 nativen Gruppen- und9 V2-Fällen:53 Tests PASS in0,226s, keine Skips.
Es liefen keine Spielprozesse.

Offen sind unabhängige Root-Freezeprüfung, feste gemeinsame Auswertung,
die drei vollständigen nativen Fenster und ihre Restorenachweise. Der
vorherige Yodeller-Spätjoin scheiterte an77,28% Host-CPU; dessen Grenzwert
wird nicht geändert. Ein erneut fehlgeschlagenes Fenster wird nicht als
vollständiger Vergleich ausgegeben oder mit anderen Bedingungen vermischt.
