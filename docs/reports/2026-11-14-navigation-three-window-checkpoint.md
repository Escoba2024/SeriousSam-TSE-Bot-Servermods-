# Cecil048, Build018 und020: drei geschlossene Red-Station-Fenster

Am14.11.2026 liefen048→018→020 jeweils einmal600 Sekunden auf isoliertem
Red Station/Hard2, mit Original-Dedicated1c41…, acht eigenen Bots und
unverändertem Originalclient. Nur dessen normale Renderkonfiguration war in
allen drei Armen20/20FPS. Navpayload, Botprofilwerte, Seeds und Pauseprotokoll
waren gleich; gleiche lebende Anfangspositionen sind nicht vollständig belegt.
Bei048 bedeutet Profil7 Expert-Rifle/tier5/marksman, bei018/020 DEMON/tier3/
duelist. Das ist ein Vergleich ganzer Kandidaten und keine isolierte
Aim-/Navigationsparameterstudie.

Alle drei Ergebnisse bleiben PASS_LIMITED_A4_OBSERVATION_FUNCTIONAL_REVIEW_REQUIRED.
Je vier normale Closes, danach unabhängiger Rootabgleich von640 Dateien
(Inhalt/uid/gid/mode), vier gesicherten Schlusslogs und Prozess-/Displayenden:
PASS_RESTORE. Keine neuen Sync-/Disconnect-/CRC-/Crash-/InvalidAction-/
Joinfehler in diesen geschlossenen Fenstern. Kein A1-, Reset-, Langzeit-
oder vollständiger A4-Abschluss und keine neue Livepromotion.

| Build | protokollierte Kills | Leben mit Usefulbesitz / beobachtet | echte Inventargewinne | gebundene FIRE-Beobachtungen | links-/rechtszensiert | max. Stillstand s | längster beobachteter lebender Abschnitt ohne Useful s |
|---|---:|---:|---:|---:|---:|---:|---:|
|048|84|76/96|100|570|52/8|3.40|48.20|
|018|168|88/185|121|3708|117/8|2.40|51.44|
|020|159|84/180|112|3468|105/8|2.45|45.74|

Kills sind eigene Nicht-Suizid-Abschüsse im jeweiligen Acht-Bot-Match einschließlich
des passiven Originalbeobachters als möglichem Opfer. Keine direkten048↔018↔020-
Duelle;168 gegenüber159 beweist keine allgemeine Überlegenheit von018 gegenüber020.
Die früheren109:33 stammen aus anderen direkten018-vs-Gen2-Vergleichen und
werden nicht addiert. Alle acht Slots haben in jedem Arm echte Usefulgewinne,
gebundenes FIRE und Bewegung gezeigt. Das beweist keine zuverlässige
Waffenbeschaffung in jedem einzelnen Leben.

Die Lebensdauern unterscheiden sich stark: Median der beobachteten lebenden
Abschnitte04838,54s,01818,45s,02019,70s. Frühe Tode und unvollständig beobachtete
Anfänge begrenzen direkte Versorgungsquoten. Die Stillstandsmetrik ist der
vorhandene1m-Anker mit höchstens0,5s Messlücken; sie prüft weder alle Ausnahmen
des10s-UNERKLÄRT-Vertrags noch größere Bewegungsschleifen. Eine geladene
Navdatei und kurze Stillstandsmaxima sind kein vollständiger Routennachweis.

## Neue konservative Lebensbilanz

Der neue Offlinehelfer nutzt die unveränderten V3-Frame-/Gruppen-/Attempt-/
Epochregeln. Alle Rohgruppen einschließlich des später ausgeschlossenen
Overlap werden geprüft; drei Pause-Smoke-Reads werden getrennt an ihre
Journalereignisse gebunden, ausschließlich Gameplay aus festen tatsächlichen
Botgruppen fließt in die Lebensbilanz ein. Keine SourceTick/20-Umrechnung,
Zeitinterpolation oder günstiger Quellenfallback. Die JSON-Dateihashes binden
die Ausgabe an die tatsächlichen Archive.

Waffenbesitz am linken Rand wird nicht als neuer Erwerb gezählt. Erwerb benötigt
eine strikt spätere native Beobachtung desselben Lebens. Erste tote und letzte
lebende Beobachtung bleiben getrennt; spätere Leichenzeit verlängert keine
Lebensdauer. In018/020 enthalten einzelne geordnete Reads positive Gesundheit
nach einem bereits beobachteten Tod bei noch gleichem Spawnclock:4/2Samples.
Diese werden als mehrdeutig markiert und erweitern weder Lebens-/Pickupzeit noch
Erwerbszahl. Nicht als CRC-Ursache oder echte Wiederbelebung interpretieren;
die Frames sind ausdrücklich keine atomaren Simulationsevents.

Die kanonischen Linkszensierungen52/117/105 weichen von den alten Vollstream-
Zahlen50/108/101 ab: dort las die Overlapgruppe bei2/9/4Leben früher am SpawnTick.
Die alten Resultate/Rohdaten bleiben unverändert. Keine Toleranz wurde gelockert. Ein Peer-MINOR im ausgeschlossenen Smoke-ID-Abgleich (PythonBool/Integeralias) wurde mit zwei reproduzierten REDs und unverändertem typisierten V3-Digestvergleich behoben.
20 neue gezielte Fälle und44 vorhandene V3-/Gruppen-/Firefälle:64/64PASS0,114s.
Ein erster Archivaufruf hatte Ereignishüllen noch nicht ausgepackt, ein zweiter
hatte Pause-Smoke fälschlich als Gameplay übergeben; beide wurden strikt
abgewiesen. Enge Regressionen sichern nun die korrekte Trennung. Zwei
Dateierzeugungsaufrufe im falschen Arbeitsverzeichnis scheiterten vor Änderungen.

## Offene Navigation und konkrete nächste Reproduktion

Alle drei Arme enthalten lange, tödlich endende Leben ohne beobachtete Usefulwaffe.
Beim020-Fall A:2/global3 folgt nach abgebrochenen Waffenzielen ein Healthziel
über denselben Navpunkt. Source-/Nativebelege und tatsächlicher Code stützen
eine mögliche Rückannäherung zwischen Navradius und anschließendem Itemconnector.
Das ist eine eingegrenzte Hypothese; ein SDK107-Reproducer am unveränderten
BotSupplyNative muss sie vor jeder Korrektur bestätigen. Kein Pitchfehler oder
alleiniger Ausfallgrund ist damit bewiesen. Der enge020-Weapon-Terminalwatchdog
ist für diese Healthziele nicht zuständig und wurde hier nicht positiv ausgeübt.

Vollständige10s/0,75m-Episodenqualifikation, gebundene Schleifen-/Recovery-
Erfolgsbilanz und relevante Spezialübergänge bleiben offen. Mehrere interne
Eligibilityzustände werden bei Diagnostics0 nicht aufgezeichnet. Goal.entity
ist die Item-ID; Goal/End/Pickup ohne eigene Generation müssen über den lokalen
Lifecyclekontext gebunden werden. Replan-/Recoverymarker allein sind kein Erfolg.

## Ressourcen und Provenienz

CPUmax048/018/02052,94/58,79/53,98%; verfügbarer RAM mindestens
2646388736/2683879424/2681044992Byte; Disk mindestens
9615716352/9441566720/9268142080Byte. Gameplay-Abstände höchstens
1,224/1,163/1,197s, Startabstände aber46,800/47,774/47,084s:
kein lückenloser pauschaler Hostbudget-PASS. Die zusätzlichen gemeinsamen
Fleet-/Deploymentlocks verhindern Überschneidung mit normalen Projektrollouts.

Nach Garbage-Collection waren die Units nicht mehr per systemctl abrechenbar.
Die tatsächlichen systemd-Abschlusswerte wurden stattdessen aus den
CPU_USAGE_NSEC-Journalfeldern gesichert: Original272,909/302,264/293,278CPU-s;
endgültige Botgruppen zusammen63,000/66,602/63,875CPU-s. Bootstrap-BotA separat.
Ganze Unitlaufzeiten einschließlich Startup/Winehelfern, keine reine Renderzeit
und keine Attribution einzelner Hostspitzen. Kein weiterer Test nur zur
Wiedergewinnung dieser Metadaten.

| Build | Ergebnis-SHA256 |
|---|---|
|048|`9f2553e9c6be1dbb954f149e3ab685651f731e2b40b2745a531a7feacbf20b0b`|
|018|`efa69cc64f5426b2342641d10243f186b5006337a84db96e8c0b56cb0c7adf04`|
|020|`4e5f096529e31f4c13efb44ccc32da71af924a0308df27dcdeaeb2be87ca5d66`|

[Bereinigte gemeinsame Kennzahlen](milestone-a-20261114/navigation-comparison20-closed-summary.json).
Private Rawpfade unter /srv/tse-milestone-a-evidence-20261111/nav20-*;
RootEV/navigation-comparison20-*-root-restore.json und -life-summary.json;
unabhängiger Audit navigation-comparison20-closed-peer-audit.json,
SHAf38a10e4925891960f228faf792e64755133e29b46a334c8a1b2badf2be4ae7a.
Neue Belege benötigenDelta045. Live bleibt nach ausdrücklicher Nutzerantwort:
Dev048,RedGen2,vierPublic018; A offen, B nicht begonnen.
