# Herkunft und Lizenzen

Die veröffentlichten GameMP-Quellen basieren auf Croteam Serious Sam / dem SE1-ModSDK von DreamyCecil. Vorhandene Croteam-/Cecil-Hinweise bleiben erhalten. Die GPL Version 2 steht in `poc/release/LICENSE`. Die Bot-KI nutzt CecilBotMod als Referenz; übernommen/abgeleitet veröffentlichte Teile werden unter GPL-2.0-only geführt. Die Veröffentlichung enthält keine Retail-Binaries, SDK-Importbibliotheken oder kommerziellen Spieldaten.

GameMP-only-Anpassungen entstanden vom 08.–11.10.2026. Am 12.10.2026 wurden datierte GPL-Änderungshinweise hinzugefügt. `docs/reports/2026-10-12-source-verification.json` nennt für jede der 13 erfassten Dateien den ursprünglichen Abnahme-Hash, den veröffentlichten Hash und den exakt eingefügten Hinweisblock. Entfernen ausschließlich dieses Blocks ergibt die originalen, privat gesicherten Quelldateien. Die Bot-Funktionalität wurde für die Synchronisierung nicht geändert.

SDK: https://github.com/DreamyCecil/SE1-ModSDK (aa7869c2c2c4db0562281814d0ac3784e6b9d6f0; Includes 94ff8cd0e63941f8601294350b616472f772ed51).
CecilBotMod-Referenz: https://github.com/DreamyCecil/CecilBotMod.
KI-Referenz und Kartenkonvertierung vom 20.10.2026: Dreamy Cecil / CecilBotMod,
Commit `953b477`, GPL-2.0. Die neun erzeugten Wegpunktdateien unter
`poc/experiments/tactical-ai/maps/` sind abgeleitete Navigationsdaten.
Sie enthalten keine Retail-Spielbinaries. Der vollständige Lizenztext
liegt unter `poc/release/LICENSE`. Die neue taktische Entscheidungslogik
ist eigenständig implementiert und nennt ihre konzeptionelle Referenz.
Serious Engine-Referenz: https://github.com/Croteam-official/Serious-Engine.
