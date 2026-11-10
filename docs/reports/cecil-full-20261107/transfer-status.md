# Cecil-Transfer: aktueller Quellstand045

Quelle `7033ce290755f6cd819a18c2a38356370168c235`, Tree `0471a4476826c95770b9af187b4b99d39b2c2d99`. Alle41Originalbereiche tatsächlich neu gelesen,94aktuelle Quellanker und14Dateihashes gebunden.33Bereiche implementiert, eine vorhandene Human-LOS adaptiert, vier Architekturteile begründet ausgeschlossen, zwei im FFA-Scope nicht anwendbar; native Gesamtqualifikation weiterhin offen.

Diese Matrix bestätigt Verdrahtung und ausdrücklich genannte Anpassungen. Sie behauptet keine vollständige Originalmod-Laufzeitparität und überträgt keine früheren nativen Ergebnisse auf045. Aktuelle gemessene Resultate stehen im [045-Bericht](2026-11-09-candidate045-native-results.md); noch laufende oder nicht geprüfte Gates bleiben offen. Der vollständige039-Stand bleibt per unveränderlichem Commit/Dateihash in der [maschinenlesbaren Matrix](transfer-status.json) verlinkt.

| ID | Bereich | Quellstatus | Aktueller nativer Nachweisbedarf |
| --- | --- | --- | --- |
| T01 | NAV-Dateien | IMPLEMENTIERT | Exact current DLL/map/NAV-CRC load and successful native traversal on each required map. |
| T02 | Punktstruktur | IMPLEMENTIERT | Current native special-point, lock and important-entity behavior tied to original IDs. |
| T03 | Gerichtete Verbindungen | IMPLEMENTIERT | Native source/hop sequence and actual position progress on real directed paths. |
| T04 | Punktradien | IMPLEMENTIERT | Arrival matched to actual position/original radius; no action-only arrival inference. |
| T05 | A*-Suche | IMPLEMENTIERT | Reachable/unreachable and lock/teleport path behavior; no claim of identical original tie-breaking. |
| T06 | Nächster Navpunkt | IMPLEMENTIERT | Fresh actual original-node acquisition after offgraph/flight/relocation, with same-life autonomous path resumption. |
| T07 | Important-Ziele | IMPLEMENTIERT | Important target interaction effect and following original next-slot chain. |
| T08 | Switch-/Marker-Events | IMPLEMENTIERT | Actual USE pulse plus native switch/marker effect; 1Hz state can miss a pulse, keep OPEN without effect proof. |
| T09 | Locks | IMPLEMENTIERT | Actual supported fresh lock approach, later original arrival, and support-loss control on current DLL. |
| T10 | Teleport | IMPLEMENTIERT | Matched native teleport entry/exit/map/identity; movement request alone is insufficient. |
| T11 | Jump/Crouch/Override | IMPLEMENTIERT | Actual crouch/jump/override action and physical position follow-up. |
| T12 | Auto-NAV-Generierung | NICHT_ANWENDBAR_5_FFA_MAPS | No native implementation claim for the deliberately excluded/out-of-scope subsystem; verify unchanged vanilla boundary in current native integrity gates. |
| T13 | NAV-Editor/Netzbefehle | ARCHITEKTONISCH_AUSGESCHLOSSEN | No native implementation claim for the deliberately excluded/out-of-scope subsystem; verify unchanged vanilla boundary in current native integrity gates. |
| T14 | Per-Bot Pfadzustand | IMPLEMENTIERT | Native generation, death/rejoin and map state continuity without cross-bot leakage. |
| T15 | Stuck-Erkennung | IMPLEMENTIERT | Actual ineffective-hop cycle produces checkpoint, then genuine closer hop/arrival/path progress, not merely displacement. |
| T16 | Recovery-Bewegung | IMPLEMENTIERT | Actual safe escape displacement followed by autonomous navigation resumption; distinguish combat release/loop/wiggle. |
| T17 | Abgrundvermeidung | IMPLEMENTIERT | Current default0 unknown-support wall movement and opt-in1 floor behavior; narrow exact-contact proof and final action corroboration. |
| T18 | Schwimmen/Gravitation | IMPLEMENTIERT | Actual liquid transitions/leveling, rotated gravity, and air-hint steering followed by autonomous navigation. |
| T19 | Follow-Verhalten | IMPLEMENTIERT | Observed target memory expiry and reachable follow; no teleport claim. |
| T20 | Gegnerauswahl | IMPLEMENTIERT | Native selected entity/visibility/reaction/cooldown chronology. |
| T21 | Team-/Monsterauswahl | IMPLEMENTIERT | FFA team exclusions; monster/cooperative behavior remains outside scope. |
| T22 | Sichtprüfung | BEREITS_VORHANDEN_OFFLINE_GEPRUEFT | Current native LOS identity and bounded queries; no original TT_NONE equivalence assertion. |
| T23 | Zielgedächtnis/Timer | IMPLEMENTIERT | Native visible-to-hidden expiry/identity changes; no hidden-position use. |
| T24 | Waffentabellen | IMPLEMENTIERT | Native five required weapons owned and chosen using the current table/selector. |
| T25 | Waffenbewertung | IMPLEMENTIERT | Owned/wanted/current/actual emitted fire in safe range; unsafe range suppression and dwell evidence. |
| T26 | Waffenwechsel | IMPLEMENTIERT | Ordered actual choice -> emitted group -> native wanted -> complete whole-family exit per identity; drops/censoring OPEN. Earlier policy opportunity and exact CD/dwell upper bound remain OPEN even with completed observer chains. |
| T27 | Feuer/Granate/Scope | IMPLEMENTIERT | Actual emitted fire/grenade release/scope and final safe-range guards; hits require separate hit/damage evidence. |
| T28 | Aim/Vorhalten | IMPLEMENTIERT | Native angle/visible motion/settling chronology; no hit inference. |
| T29 | Strafing/Distanz | IMPLEMENTIERT | Actual movement near opponent, accepted owner and final safety action. |
| T30 | Itempriorität | IMPLEMENTIERT | Fixed first-ten selected typed goals and fixed ten initial lives under current DLL; no censored-attempt drop. Legitimate relocation budget and no checkpoint deadline renewal. |
| T31 | Itemkandidaten/LOS | IMPLEMENTIERT | Selected typed item/weapon-bit gain/GoalEnd correlated in same life, including incidental weapons and native pickup geometry. |
| T32 | Reisemesser | IMPLEMENTIERT | Actual final knife selection after >2s sighting delay and navigation arbitration. |
| T33 | Respawn | IMPLEMENTIERT | >=100 health<=0 -> same entity next generation Spawn pairs plus each-bot actual respawn activity <=6s using qualification timing definition. |
| T34 | Schwierigkeiten | IMPLEMENTIERT | Native preset/settings pin and actual behavior; source assignments alone are not runtime parity. |
| T35 | Configserialisierung | IMPLEMENTIERT | Current config hash/schema/invalid readiness controls. |
| T36 | Controller als Modul | IMPLEMENTIERT | Current source/DLL/PID/start/tick binding, ordinary action processing and all native gates. |
| T37 | PlayerBot/EntitiesMP | ARCHITEKTONISCH_AUSGESCHLOSSEN | No native implementation claim for the deliberately excluded/out-of-scope subsystem; verify unchanged vanilla boundary in current native integrity gates. |
| T38 | Netzpatch/Patcher | ARCHITEKTONISCH_AUSGESCHLOSSEN | No native implementation claim for the deliberately excluded/out-of-scope subsystem; verify unchanged vanilla boundary in current native integrity gates. |
| T39 | Lernen/Teamtaktik | NICHT_ANWENDBAR_5_FFA_MAPS | No native implementation claim for the deliberately excluded/out-of-scope subsystem; verify unchanged vanilla boundary in current native integrity gates. |
| T40 | Native Gleichwertigkeit/Last | OFFEN | Current five-map functionality; weapons/features; health respawns; 1h one-bot/1h four-bot/2h eight-bot; recovery; matched CPU windows <=1.2 and RSS; original Retail gameplay; rotation; six instances plus 900s. Source/portable/build evidence cannot fill these gates. |
| T41 | Coop-Catch-up-Teleport | ARCHITEKTONISCH_AUSGESCHLOSSEN | No native implementation claim for the deliberately excluded/out-of-scope subsystem; verify unchanged vanilla boundary in current native integrity gates. |

Die gezielten Neubewertungen betreffen insbesondere Nearest/Recovery, getrennte Default0-Wandbewegung bei unbekanntem Support, Luftkontext, statischen Hop-Checkpoint und rein lesende Waffenphasenbeobachtung. Aktuelle/gewünschte Waffe allein bleibt kein Animationsabschluss; früheste Policy-Opportunity bleibt ungemessen. Kein fehlender Pflicht-Callsite wurde in diesem Quellreview gefunden. Native Wirksamkeit und Freigabe werden ausschließlich durch die gesonderten festen Gates belegt.
