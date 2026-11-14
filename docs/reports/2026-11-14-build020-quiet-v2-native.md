# Build020: geschlossener A4-V2-Teillauf

Der einzelne Quiet-Lauf `a4-fire020-v2-quiet-20261114-103229` endete nach 432,397 Sekunden mit `PASS_LIMITED_BOT_RESET_FRESH_OBSERVER_REVIEW_REQUIRED`: alle 24 Slotphasen bestanden. Live bleibt Build018 auf allen sechs Instanzen. Eine vollständige A4- oder Build020-Freigabe folgt daraus nicht.

Kandidat: Quelle `e5f7a65502fbea683014ef8fcc95ecdd2a927b6a`, DLL-SHA256 `094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0`. Freeze `0094121be382680971b132806bee0afa0b49dd2f7a8fd6e209ff3aea177a0b71`; Ergebnis `e6a2143fc942e211ee5e94b9c23c94595ccbc2706b5e8943672eda8ba746c0c4`.

Jede Slotphase enthält einen tatsächlich beobachteten brauchbaren Inventarzuwachs und natives Feuer mit Source-Zählerwachstum im selben gebundenen Spielerleben. Minimum: 15 native Feuerproben und ein Inventarzuwachs je Slotphase. Die vollständigen bereinigten Werte stehen in [der Ergebnisdatei](milestone-a-20261114/build020-quiet-native-v2-result.json).

405 Ressourcenproben: maximal 60,494 % Host-CPU, mindestens 2.788.114.432 Bytes verfügbarer RAM und 10.712.571.904 Bytes freier Datenträger. Die maximale Probenlücke im Gameplay betrug 2,107 Sekunden. Die getrennte Startlücke von 47,549 Sekunden bleibt sichtbar; dies ist keine formale Stundenabnahme.

Alle vier Rollen wurden regulär geschlossen. Root prüfte unabhängig 643 Dateien, fünf ursprüngliche Absenzen, Metadaten und vier Schlussloghashes: PASS; keine neuen Fehler in diesen Schlusslogs. Frischer Preflight 10:41:09 UTC: Rollen, Displays und beide Locks frei.

Grenzen: Serious3 statt Hard2; je Phase neuer Originalobserver, kein automatischer Rejoin; `qualified=false`, `functional_pass=false`, `map_reset_proven=false`. Keine Erstzustands-/Schadensabnahme, Kartenparität oder Langzeitqualifikation. Die fünf beobachteten Transit-Enden waren Zwischenziele: der neue terminale Watchdog wurde weiterhin nicht positiv nativ ausgeübt. Ältere 23/24- und CPU-FAILs bleiben unverändert dokumentiert.

Nächste Entwicklungstests wurden wegen eines neuen Red-Station-Syncbefunds zurückgestellt. Dieser wird getrennt untersucht; die eigenen aktuellen Botlogs waren beim frischen Flottencheck fehlerfrei. Die zusätzlichen Teilnehmer werden weder entfernt noch ungefragt instrumentiert.
