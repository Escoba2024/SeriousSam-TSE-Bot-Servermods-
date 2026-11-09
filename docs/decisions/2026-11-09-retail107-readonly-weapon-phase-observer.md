# Retail1.07: Waffenwechsel durch rein lesende native Phasen beobachten

Entscheidung09.11.2026. Der Cecil-Port muss tatsächliche Waffenwahl, gesendeten Select-Impuls und native Wechselanimation getrennt belegen. Die bisherigen1Hz-Statusfelder reichen dafür nicht. Ein kleiner getypter Observer im modifizierten BotClient liest unter dem vorhandenen Netzwerk-/Weltmutex nach dem endgültigen `SetAction` vorhandene Zustandsfelder; Original-Engine/Entities, menschliche Clients und Server bleiben unverändert. Diese Entscheidung ist keine native Wirksamkeits- oder Gesamtqualifikation.

## Tatsächliche Werkzeuge und Referenzen

In dieser Sitzung stehen keine benannten Ghidra-/Frida-MCP-Funktionen zur Verfügung. Gezielte lokale PE-Auswertung und `objdump` an den tatsächlich vorhandenen Originaldateien liefern die nachstehenden begrenzten statischen Gegenprüfungen. Weder ein Ghidra-Smoke/E2E-Nachweis noch Runtime-Hooks oder Speicheränderungen werden daraus behauptet. Der bekannte fehlerhafte GUI-Endpunkt auf8080 wird nicht benutzt; kein Dienst wird gestoppt. Serious-Engine1.10 ist keine Ersatz-ABI.

| Originaldatei | SHA256 |
| --- | --- |
| Engine.dll |`b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f` |
| EntitiesMP.dll |`7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350` |

| Funktion oder Struktur | Beleg und Bedeutung |
| --- | --- |
| CPlayer::GetPlayerWeapons, bevorzugte VA603f6b90 | Originalgetter liest den bereits vorhandenen Waffenpointer; keine neue Entitysuche. |
| SelectWeaponChange6041cec0/ChangeWeapon6041d3d0 | Originalfelder Current+F8/Wanted+FC/Previous+100/Available+104/Change+108; Current wird bereits vor BringUp gesetzt, Change bereits vor beiden Animationen gelöscht. |
| PutDown6041d990/BringUp6041de70 | Generierte ursprüngliche Switchfamilie01920007..0192001c einschließlich übergeordneter ChangeWeapon-Frames im vollständigen begrenzten State-Stack. Beide Modelle sind für DoubleColt relevant. |
| BringUp-Fortsetzung6041e210 | Original nutzt CAnimObject::GetAnimLength über IAT6048b4b0 und setzt seine native Timerwartephase. Der Observer ruft weder PlayAnim noch SetTimerAfter auf. |
| CAnimObject::GetAnimLength600c3c30 | Main und unabhängige Gegenprüfung: liest nur AnimData, Anzahl/Array und Framedauer×Frameanzahl; keine API-Calls oder Objekt-Stores. Nichtnegative gültige Animationsindizes und vorhandenes Animationsarray sind vor jedem Observeraufruf nötig; die Originalfunktion sichert negative Indizes nicht ab. |
| CNetworkLibrary::GetGameTime6019c8d0 | Originale sieben Originalbytes lesen Network+20/Session+4c und geben den Float zurück, ohne Stores oder Calls. Nicht mit dem threadlokalen Timer-CurrentTick oder lokalem Bot-Tick gleichsetzen. |
| CRationalEntity-Timer+ D8/State-Array+ E0/UsedCount+ E4 | Öffentliche107-SDK-Felder und Original-HandleEvent601c31b0/Timerpfad gegengeprüft. Beobachten, nicht Push/Pop/Call/Jump/Return auslösen. |

Adressen sind bevorzugte statische PE-Adressen, keine behaupteten aktuellen Prozessadressen. Der neue Code verwendet vorhandene getypte107-SDK-Zeiger und Felder; kein manueller Heap-/VTable-/Prozessspeicherscan.

## Begrenzte Beobachtung und Aussagegrenzen

Der Observer verändert ausschließlich seine eigene Diagnosedatenkopie. Keine Policy-/Selector-/Dwell-/RNG-/Ziel-/Action-/Physikänderung, kein zusätzlicher Ray oder Weltscan. Vorhandene Quellen-/Welt-/Entity-/Generation-/Ownerbindung, lebender gültiger Zustand und monotoner nativer Zeitbezug begrenzen eine Messkette. Fehlende Frames, fremde Owner, geänderte gewünschte Waffe, tiefer/ungültiger Stack, ungültige Modelle und fehlende Animationsteile bleiben offen oder zensiert.

Bis16 vorhandene Stackeinträge werden vollständig betrachtet. Modell-/Timer-/Phasenfelder werden nur gelesen; die beiden reinen Animationslängengetter höchstens einmal pro Modell und ausgegebenem Ereignis. Ereignisse bleiben begrenzt; verworfene Beobachtungen dürfen keine erfolgreiche Timingkette erzeugen. Anhaltende Attackanimations-Neustarts außerhalb einer Messkette werden nicht fortlaufend protokolliert.

`Current==Wanted`, `Change=false` oder ein ausgegebener Feuerbutton allein beweisen kein Ende von BringUp und keinen Schuss/Treffer. Eine korrekte positive Kette benötigt tatsächliche finale Wahl, tatsächlich übernommenen Gruppenimpuls, richtige native Wanted-/Phasenreihenfolge und beobachteten vollständigen Switchfamilienabschluss im selben Leben. Verdeckte, bereits vor der Auswahl laufende Auto-Wechsel und unterbrochene Wechsel werden nicht nachträglich zu kausalen Erfolgen.

Gemessen werden ausdrücklich Auswahl→Impuls→native Annahme und native Wechselphasenintervalle. Ein früherer nicht protokollierter Policy-Opportunity-/Dwellbeginn bleibt offen. Normal-Preset `fWeaponCD=3s` ist von `fTargetCD=1s`, Select-Retry0,5s und nativen Modellanimationsdauern zu trennen; keine geschätzte Animationsdauer von einem1Hz-Sample abziehen. Geänderte DLL erhält neue Gates einschließlich CPU/RSS; statische Getterprüfung und portable Observer-Tests ersetzen keine native Abnahme.

Private statische Nachweisdateien binden Originalhashes, Funktionsfenster, SDK-Deklarationen und Gegenproben. Keine Originalbinaries, Modell-/NAV-Inhalte oder privaten Rohlogs werden veröffentlicht. [Toolrichtlinie](2026-10-17-tse-ai-tools-mcp-policy.md) und [044-Nativbericht](../reports/cecil-full-20261107/2026-11-09-candidate044-native-results.md) bleiben maßgeblich.
