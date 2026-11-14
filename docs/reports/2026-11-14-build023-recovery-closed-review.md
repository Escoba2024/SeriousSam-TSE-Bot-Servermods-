# Build023: geschlossene Recoveryprüfung

**Recoverywirkung nativ nicht nachgewiesen.** Im gesamten600s-Fenster gibt es
**0 Recoveryvorschläge**. Fünf `not_usable`-Interaktionen verlassen Knoten175
anschließend mit dem vorhandenen NAVpfad. Der konkrete022-Repro anKnoten138
trat hier nicht auf. Weniger beobachtete Stationarität beweist unter diesen
Bedingungen keine kausale Fixverbesserung und erlaubt keine Promotion.

## Fenster und Belegvertrag

Geschlossenes privates Fenster
`nav20-023-root-redstation-20261114-220049`, ResultSHA256
`405974020bd4a533a5036f8d42b1945c324a4cbb4b6d94baa48190a2694c34cb`.
600.118889s; vorhandener Status bleibt begrenzter Beobachtungs-PASS mit
funktionalem Reviewbedarf. Root belegt0neueSync-/Disconnectmeldungen, vier
reguläreCloses und640Datei-/vierClosedlog-Restoreprüfungen. DieserReview
startete wederRuntime nochBuild und ersetzt keine eigenen Dauer-/Syncgates.

Die vollständig geschriebene Root-Lebenssummierung wurde zuerst als gültiges
JSON gelesen. Anschließend wurden alle Eingabehashes und V3-Hüllen,
Versuchsjournal, festeGruppen, PID/Start-/Epoch-/World-/Slot-/Entitybindung und
Lebenssummen unabhängig mit dem bestehenden Validator erneut geprüft:
identisch. ProBotrolle genau einSource-CecilLoad. AlleRecoveryzeilen und
sämtliche fünfInteraktionen wurden berücksichtigt, keine günstige Auswahl.

NativeFrames sind geordnete, zweimal gleich gelesene Speicherbeobachtungen,
keine atomaren Simulationstraces. Sourcepolicytick wird niemals durch20geteilt,
um Gamezeit zu erfinden. Sourcegenerationen binden über tatsächliche WPO-
`native_time`-Zeilen an genau einNativeleben; die vorhandene ganze
±0.0000005-Druckrundungsgrenze und exakten Float/Decimal-Lebensintervalle
wurden unverändert angewandt. Die vollständigen Lebensgrenzen bleiben erhalten.

## Alle fünf Interaktionen

Alle betreffen gewöhnlicheMetadaten anSlot175/stabilerID177: Flags0,
Important544, Lock/Next−1, Links174/111. Root022-Reproquelle138 ist verschieden.
Die Tabelle nennt lokale eigene Botaliases, keine Spieleridentitäten.

| Rolle:Local / Generation | not_usable: Sourcezeile / Tick | Erster Folgestate: Zeile / Tick / neuesGoal | Native ersteSphäre im WPO-Fenster: Anzahl |
|---|---|---|---:|
| A:2 /6 |580 /708 |588 /720 /74 |4 |
| A:1 /35 |7854 /10987 |7863 /11000 /44 |9 |
| B:0 /16 |3114 /3955 |3116 /3960 /57 |3 |
| B:0 /19 |4509 /5851 |4511 /5860 /79 |4 |
| B:1 /22 |5636 /7449 |5638 /7460 /0 |2 |

Jeder ersteFolgestate zeigt `nav_source=175,hop=111,nav_travel=1`, lebenden
Zustand, nichtneutralen finalen Move/Strafe und `floor=1`. Die weiteren
Positionen und Hop-/Anchorwechsel sind mit dem bestehenden gerichteten
Ausgang vereinbar. Sie sind keine beobachtete neueRecoveryphase. Interner
`HasCommittedEdge` wurde nicht direkt nativ gelesen; auch die tatsächliche
Avoiddeadline steht nicht in diesen Interaktionslogs. Quellcodeprovenienz
mit unveränderter10s-Frist ist hiervon getrennt.

Die ursprünglicheAnkunft ist exakt die vorhandeneLogik, nicht `d<=r` und
nicht eine neueToleranz: gültigesr>0 und `Delta²<r²` ODER
`(Delta-gravity*r*.5)²<r²`. Die privaten Nativebelege enthalten sämtliche
Positionen und strikten Sphärenergebnisse in den umgebenden WPO-Intervallen.
Alle fünf enthalten bereits Treffer der erstenSphäre; dafür ist keine aus
Source gerundeteGravityannahme nötig. ZweiteSphären mit lediglich geloggter
Gravity bleiben ausdrücklich diagnostisch.

Nur der B:0/gen16-Zeitbereich ist durch WPO3954/196.457382 bis
3961/196.807404 eng eingerahmt. Die anderen vierFenster sind8.45–13.70s breit.
Daher werden ihre NativeSphärentreffer nicht als exakt dieser Interaktion
zugeordnete atomareAnkunft oder kausaleFixwirkung ausgegeben. Readserials,
Nativezeiten, Originalpositionen, alleSourcezustände und Unsicherheiten stehen
vollständig privat. KeinResetrand, Tod, Zielwechsel oder fehlenderGrenzread
wird durch Interpolation oder optimistischenCut als Erfolg ergänzt.

## Stationarität und offene Funktion

Unverändertes bestehendes Feld `max_stationary_alive_game_seconds` aus den
jeweiligen `active-evidence.json`; beideArme600s/20FPS. Dies ist ausdrücklich
der identisch geerbte **ALLSTREAM**-Auswerter, keine kanonischeSlot-/Life-Messung
und kein kontinuierlicherZeitnenner.022 separat kanonisch gemessene9.849850s
werden hier weder als9.999847s ausgegeben noch mit dem ALLSTREAMset vermischt. Alle `stationary_unknown_gap_count` sind0. Unterschiedliche
Spawns/Leben/Routen erlauben keinen isolierten kausalenVergleich.

| EigenerSlotalias |022 maxSekunden |023 maxSekunden |
|---|---:|---:|
| A:0 |10.000 |2.549 |
| A:1 |2.100 |1.550 |
| A:2 |1.600 |1.500 |
| A:3 |2.100 |1.700 |
| B:0 |2.599 |2.950 |
| B:1 |1.950 |1.950 |
| B:2 |1.850 |2.199 |
| B:3 |1.950 |2.150 |

Die frühere10s-Episode wurde in023 nicht wiederbeobachtet. Gleichzeitig bleiben
Rootbelege für langeLeben ohneUseful offen: Slot7/spawn312.1972961425781, firstAlive312.2472839355469 bis
lastAlive415.9719543457031 (103.72467041015625s beobachteterAliveabschnitt),
Slot4/spawn473.8078308105469 mit76.631317s. Keines dieser beidenLeben enthält
einenRecoveryvorschlag oder eine der fünf not_usable-Interaktionen. Lebensenden
und der konservative alive-after-deadGuard bleiben unverändert. Die unbekannte
Weapon-unavailable-Ursache beiDiagnostics0 wird nicht als gelöst ausgegeben.

Bewegung, erlaubter Safetyvorschlag, echtePositionsänderung, Ankunft, Exit,
Inventargewinn, Schaden und Heilung bleiben getrennteAussagen. KeinHumanlevel-,
Cecil-Paritäts-, A4-, A- oder Promotioneffekt wird aus diesem Review behauptet.

## Private reproduzierbare Quittung

EigenerWorktree `.codex/evidence/recovery023/analyze.py` führt nur geschlossene
Datei-/Navmetadaten- und bestehendeValidatorreads aus; keineSpeicher- oder
Gameplayoperation. `final-receipt.json` enthält sämtliche fünf vollständigen
Fälle, Sourcezeilen, NativeReadserials/-hüllen/-positionen, WPO-Grenzen,
Originalmetadaten, unveränderteVergleichsstatistik und vollständigeHashpins.
Privatpfad `/srv/tse-nav20-build023-retarget-20261114/.codex/evidence/recovery023/`.
QuittungSHA256 `b47dfb7d7e7653fb961387c0ab84c916e3d06f865adb08678a793bc7a872f322`.
AllePrivatdateien0600, Verzeichnis0700; keineRaw-/Retaildateien imRepository.
Alle eigenenAuswertungsjobs sind beendet. Root entscheidet die nächsten
Schritte; nativeRecoveryqualifikation und weitere A4-Funktion bleiben offen.
