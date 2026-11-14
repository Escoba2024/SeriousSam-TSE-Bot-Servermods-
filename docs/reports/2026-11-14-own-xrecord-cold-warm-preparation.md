# Own167 Cold/Warm: deaktivierter Methodenfork vorbereitet

Root022 war geschlossen/restauriert, bevor diese Offlineumsetzung begann.
Kein TSE/Wine/Frida, Displaystart, Xlib-CDLL oder Nativeinput wurde durch den
Implementierer ausgeführt. Die begrenzten OwnChild-Regressionen starten nur
eigene Python-Fakekinder. Keine Paketinstallation oder zusätzlichen Dienste.

Neue Dateien:

- `tools/xrecord_cold_warm_method.py`: sechs feste Recordranges, enger
  QueryExtension-/GEVersion-Decoder und vollständiger Raw-Replay/Auditor.
- `tools/prepare_xrecord_cold_warm_method.py`: reproduzierender deaktivierter
  Fork des qualifizierten Coreparents, schmaler Diff für Controller/Native/
  Worker, gleiche OwnChild-/Coreparserdateien, keine Mutation des Parents.
- `tools/test_xrecord_cold_warm_method.py`: Header-/Wire-/Fremdclient-/Zähler-/
  Query-/Cleanup-/Paketfälle und tatsächlicher generierter Driver als Fake-C.

Der Driver hat genau zwei feste+12-Aufrufe auf derselben Verbindung, ohne
vorherige Driver-Versionsabfrage/Warmup. Die ursprüngliche Fensterinitialisierung
ist AST-identisch. Öffentliche Counter werden unmittelbar vor/nach dem C-Aufruf
erfasst, danach normaler XSync und tatsächliche QueryPointer-Belege. Nach
abweichendem Coldcounter oder sonstigem Fehler endet der Controller mit Cleanup;
keine Folgeprobe/zusätzliche Eingabe wird daraus erzeugt. Neues PASS-Label nur
für diesen Methodenbeleg, keine A1-/Retail-/XI2-Abnahme.

Der Auditor verlangt die vollständig decodierte Cold5/Warm1-Folge, echte
Discoveryantworten, dynamische Majors, synchron passende Metadatenreplies,
Pointer400→412→424 und exakt dieselbe durch eigenes Fenster/Querysequenzen
gebundene Driververbindung. Jede archivierte abgeleitete Row wird noch einmal
aus ihren Wirebytes decodiert und typisiert verglichen; alle Rawrecords bleiben
geprüft. Fehlende/zusätzliche Queries oder FakeInputs, günstige Fremdclients,
Counterspan allein und nachträglich angenommene Sequenznummern bestehen nicht.

OwnChild/IPC/Freshdisplay/PID/Socket/Recordbudget/normaler Cleanup bleiben
unverändert.15s/1024Records/2MiB/16KiB, Arm/Stop3s, Driverop2s,
Controller30s+Cleanup5s je Kind,8GiB Disk; alle drei Ausführungsgates False.
libXext ist zusätzlich zu X11/Xtst explizit per SHA gepinnt, da dessen XGE-Pfad
Gegenstand der Methode ist. Keine neue A1-Source/Guard-/ACK-/Inputänderung.

## Tatsächliche Primärlayouts

Die lokal nicht installierten Xproto.h/geproto.h wurden aus dem offiziellen
Xorgproto2024.1-Archiv`372225fd…` begrenzt im Speicher gelesen und privat0600
gesichert. QueryExtensionReply hat present an8, major an9, first_event/error
an10/11; GEVersionReply Version16bit an8/10. Keine private Displaystruktur.

Privat `/srv/tse-xrecord-cold-warm-evidence-20261114/Xproto.h`,
SHA`ae2c275f8b7bf4705ef993b50a34ce7418fbbc4789bcb841237116b7c0271c82`;
`geproto.h`,SHA`b831b2d821249670d8ed60a05f9f0dd85caa2c2ef101dbb6989bca5ea7ad02f1`.

## Reale Offline-RED/GREEN-Dateien

Alle folgenden Dateien liegen tatsächlich mit0600 unter
`/srv/tse-xrecord-cold-warm-evidence-20261114/`:

| Datei | tatsächliches Ergebnis | SHA256 |
|---|---|---|
|`red-wire-builder.log`|6RED, Auditor/Builder noch fehlend|`e122fa3b62783921661a08dbdc73b67f6b2e6a6623e22b5c133dff451171b07a`|
|`first-wire-check.log`|5Wirefälle GREEN|`660ba695d106f98a263b9f663d657cfc3a42bc2e537868e727b85b2c78fdf6ad`|
|`red-extra-query.log`|Zusätzliche Driverquery wurde zunächst nicht verworfen: RED|`2cfc86c8a1cc0c40e085ea813ab889ae84b1c523eeb109e3866a36c885c22879`|
|`red-driver-builder.log`|2RED für noch fehlenden Fork/Driver|`a001a034497ad6d7512d59be038e51104886a69ff05568e404499ee9c282f2c7`|
|`first-green-candidate.log`|2ERROR durch fehlendes Leerzeichen im generierten Python-Ausdruck; vor jeglicher Ausführung durch ast.parse erkannt|`f276e3c21b74d27c1c90070546ad87f866ebd25acfe4b972c4c1b14c94a37967`|
|`green-wire-driver-builder.log`|7neueFälle PASS|`3f61423dc0c81cd809fa645bd2e3db9643252f672a17050ce0d2a75e13e3b8dc`|
|`red-xext-pin.log`|fehlender expliziter Xext-Pin RED|`188f4c6d5a9e9a14ba0a8d6d751a0a4631faac0fef28a96200994fe83f80dcdf`|
|`green-final-regressions.log`|7neue+39bestehende=46PASS,0Skips,2,273s|`8a0115806dbab4022b7cbc3b07e1a145a4d6866940ceee80d1e2404758b5cd26`|

Negativfixtures werden nach Mutation neu serialisiert; fehlende/falsche/extra
Requests scheitern daher an tatsächlicher Parser-/Requestbindung, nicht bloß
an einem falschen Callbackindex. Bestehende39Fälle betreffen unveränderten
Coreparser/OwnChild sowie die ursprünglichen Native-/Worker-Fake-C-Modelle;
sie sind keine native Abnahme des neuen Sechsrangekontexts.

Reproduktion aus Repository-`tools/`:

```sh
python3 -B -m unittest test_xrecord_cold_warm_method test_xrecord_core_method test_xrecord_core_process test_xrecord_core_native test_xrecord_core_worker -v
python3 -B prepare_xrecord_cold_warm_method.py --destination /NEUER/PRIVATER/PFAD
```

## Deaktiviertes Paket und nächster Schritt

`/srv/tse-own-xrecord-cold-warm-disabled-20261114`;
ManifestSHA`dbc5ee1f5bbc6b542db89f8cddcdb51a65cd7186322848b4f3fff3142fbdb60f`.
8Dateipins und3Bibliothekspins frisch geprüft. Vollständiger Parentmanifest-
und Quelldateiabgleich erneut unverändert; OwnChild und Coreparser bytegleich.
Reviewdiff `method-fork.diff`,SHA
`ba1e7a7abfc9c981e72a26cb9f0482b0d18aeb79590f5d200c578f46a066b433`.
Private Quittung `/srv/tse-xrecord-cold-warm-evidence-20261114/offline-handoff.json`,
SHA`0c052518c878d2d804c08985cbc58689fcbb5fcb3068fbb235775ee1e5b1a8ae`.

Root prüft/friert separat ein und führt genau eine eigene Methodenqualifikation
unter dem bestehenden Auftrag durch, mit frischer Display-/Lock-/Ressourcen-
Prüfung und Sicherung. Erst nach tatsächlichem Methoden-PASS wird der bereits
geplante A1-Kandidat XTestQueryExtension außerhalb des Inputhotpaths vor
Recorderarm vorbereitet. Der jetzige Fix setzt dies nicht um; `b-a>4` bleibt
unverändert. Historische A1-FAILs, Wirehypothese und Betriebsstand bleiben ehrlich
getrennt. Keine Behauptung unbeaufsichtigter Weiterarbeit.

## Rootreview: enge Query-/Counterkonsistenz nachgetragen

Der Auditor akzeptierte zunächst ein vollständig antwortendes Querypaar trotz
Querysequenz vor dem Call beziehungsweise im nächsten Abschnitt. Ebenso wurden
Callbackpaare vor Cold-Fake/nach Warm-Fake und widersprechende Invocation-/Counter-
Metadaten nicht verworfen. Dies ist ein offline belegter Auditorfehler; kein
bereits beobachteter falscher nativer Methoden-PASS.

Drei neue Testmethoden mit zehn Subfällen reproduzieren diese Annahmen am realen
Auditor; nach Mutation bleiben Rawindices/-zeiten neu serialisiert. Jetzt müssen
`native_invoked` exakt True und die streng ganzzahligen Counterkopien exakt gleich
`sequence_interval` sein. Die Querysequenz liegt ab `after` und vor folgendem
`before`; ihr Rawrequest folgt dem letzten Emissionsrequest, ihre Rawreply liegt
danach und vor dem ersten folgenden Emissionsrequest beziehungsweise EndOfData.
Die feste Fixture enthält nun dieselben tatsächlichen Invocation-/Counterfelder
wie der unveränderte Driver. Keine neue Zeitabfrage oder Runtimeänderung.

Neue tatsächliche0600-Dateien unter demselben privaten Evidenzverzeichnis:

| Datei | Ergebnis | SHA256 |
|---|---|---|
|`red-query-interval-consistency.log`|erster Aufruf: Test-Syntaxfehler vor Testausführung, separat erhalten|`9d16ba62895361264140c52ddc157834b3d91eefec29423c17e4e9ac21002f59`|
|`red-query-interval-consistency-corrected-test.log`|danach echter RED:3Testmethoden,10nicht verworfene Mutationen|`4565c19d30a26e4120bca17f0902e081b34b7c3df4d026720d7267ac5b8be537`|
|`green-query-interval-focused.log`|10neue+39bestehende=49PASS,0Skips,2,264s|`4a8b600aa4dfb000b9fc3ca1628222461b7331754c4c0bc989916303e5b26b7f`|

Neues deaktiviertes Paket:
`/srv/tse-own-xrecord-cold-warm-ordered-disabled-20261114`, ManifestSHA
`cfdbeb92568e7b79c55ad418d62793ab6ff17b396d89805465d305501a071e27`.
8Datei-/3Bibliothekspins frisch geprüft. Gegen voriges Paket ändern sich exakt
`xrecord_cold_warm_method.py` und dessen Test; alle anderen Dateien einschließlich
Driver/Controller/OwnChild/Core sind bytegleich. Der Parentdiff bleibt ebenfalls
bytegleich (`ba1e7a7abfc9c981e72a26cb9f0482b0d18aeb79590f5d200c578f46a066b433`).
Altes Paket unverändert. Quittung
`/srv/tse-xrecord-cold-warm-evidence-20261114/query-order-offline-handoff.json`,
SHA`08472788fd670ebda356f3235c139df0d9d81af9317574c38e04c51e0674855d`.
Alle Ausführungsgates False. Rootreview/-freeze und genau eine Methodenqualifikation
stehen weiterhin aus; A1-Guard≤4 und dessen historische FAILs bleiben unverändert.
