# A1: Metadatenvorbereitung vor Recorderarm, deaktivierter Fork

Reine Offlineimplementierung im eigenen Worktree
`/srv/tse-a1-xtest-preparation-20261114`, Branch
`codex/20261114-a1-xtest-preparation`, ab Root`84dfc42`.
Root allein integriert/friert/startet. Keine Runtime-/Live-/Display-/Xlib-
Ausführung oder Builds durch diesen Autor.

## Nachgewiesener Anlass und Abgrenzung

Der geschlossene A1-Lauf20:50:26 scheiterte korrekt am ersten tatsächlichen
Emissionsintervall26→31, fünf Requests statt höchstens4. Das spätere eigene
Own167-Methodenergebnis ist tatsächlich
`PASS_METHOD_COLD_WARM_LIBRARY_REQUESTS_ONLY`, SHA
`45adbbad603ab49fde34e3b20f51c8b38ba62a0cb403937a27d15458ccd7a7d2`:
Cold14→19 mit XInput-/XTEST-/GE-Discovery, GEVersion und einem Relative12;
Warm21→22 nur Relative12, Pointer400→412→424. Datei:
`/srv/tse-cecil-rollout-evidence-20261114/own-xrecord-cold-warm-root-20261114/method-result.json`.
Dies ist ein eigener Bibliotheksmethodenbeleg, keine TSE-/ACK-/Gainabnahme.

Vorhandene öffentliche ABI-/Ressourcen-Metadatenqualifikation81c402ed… bleibt
separat und mit denselben Fingerprints erhalten. Die bereits analysierten
[Xtst1.2.3-Primärquellen](https://xorg.freedesktop.org/releases/individual/lib/libXtst-1.2.3.tar.bz2)
und ELF-Pins/Kette stehen im Bericht
`2026-11-14-a1-five-request-static-audit.md`. Der neue Helfer verwendet die
öffentliche XTestQueryExtension-Signatur, die auch der unveränderte qualifizierte
Core-Nativeadapter verwendet. Kein Zugriff auf private Displaystrukturen.

## Genau geändertes Verhalten

`prepare_xtest_transport` verwendet ausschließlich bestehende
`transport.t`/`transport.x`/`transport.d`. Vanilla154, identischer ungebundener
Proxy und vorhandene Displayguards sind Voraussetzung. Öffentliche Metadaten-
Query ohne Eingabe, Return1/Version2.2/gültige Event-/Error-Bases, danach
XSync derselben Verbindung mit discard0/Return1. Erst anschließend darf der
bisherige Recorderarm stattfinden und danach der Emissionsobserver binden.
Die erfolgreiche Metadatenquittung wird Bestandteil der Armreceipt. Fehler
bleiben sticky, verhindern Arm/neue Inputphasen und erhalten die Ausnahme.

Keine neue Verbindung, keine Eingabe, kein FakeInput-Warmup, kein Retry.
Insbesondere bleibt `b-a>4` FAIL. Emissionsproxy, Attemptjournal, sicherer
finally-Keyup, Counter/Clockreads im Hotpath, CP/ACK/Gain/EPS, Inputscope,
alle Fristen und Host-/Normalclose-/Restoregates unverändert. Neuer Inputfehler
oder fortbestehender Gainfehler muss im nächsten diagnostischen Lauf weiterhin
FAIL bleiben. Der zusätzliche Testfixture-Mock in `test_a1_passive_xrecord.py`
stellt sicher, dass der alte StartOfData-Fehlerfall weiterhin genau dieses Gate
erreicht und nicht bereits am neuen Prephelper scheitert.

## Reale RED/GREEN-Belege

Alle Dateien tatsächlich0600 unter
`/srv/tse-a1-xtest-preparation-evidence-20261114/`:

| Datei | Ergebnis | SHA256 |
|---|---|---|
|`red-prearm-metadata.log`|6Testmethoden,10FAIL+1ERROR: fehlender Helper/Builder und noch fehlende Prearm-Guards, vor Implementierung|`5806d59126c5255be2734ac62a2aa0863e9acfd2c4a6212af82f58c3edaffc5b`|
|`green-prearm-first.log`|7neue+43bestehende=50PASS,0Skips,4,477s|`71b1c6f2dacf59132fff09bca1143a6232834aa2c3c0e60bfb070d2ae298dacb`|

Fake-C-Tests rufen den tatsächlichen Adapter auf: dieselbe Handlebindung,
Query→Sync→Arm mit Observer bis nach Arm None, ungültige Version/Return/Sync,
falsche Rolle/Display/Observer und primäre Nativeausnahme. Kein CDLL-/Display-
Aufruf in Tests. Pakettests vergleichen alle anderen Recorder-/Proxyfunktionen,
Methodenfingerprints und Coredateien, CP/RD/Transport/Transaktion/Host/Auditor
sowie alle Sourcepins; veränderte Methodenbelege verhindern Kopieren.
Bestehende ReleaseSafe-Regressionsfälle bleiben grün, einschließlich echter
geerbter finally-Keyup-Ausführung bei Metadatenreject und exakt4/5-Grenze.

Reproduktion ab Repository-`tools/`:

```sh
python3 -B -m unittest test_a1_xtest_preparation test_a1_passive_attempt_journal test_a1_passive_xrecord test_a1_passive_xrecord_worker test_a1_passive_xrecord_evidence test_prepare_a1_passive_xrecord -v
python3 -B prepare_a1_xtest_preparation.py --destination /NEUER/PRIVATER/PFAD
```

## Deaktiviertes Paket, Pins und nächster Schritt

Parent unverändert:
`/srv/tse-a1-passive-attempt-release-safe-disabled-20261114`, Manifest
`f1cbd265f9b5ade97b8ec27748370b523f877524a6302118bf74fad3e8b18b18`.
Neues Paket `/srv/tse-a1-xtest-preparation-disabled-20261114`, Manifest
`677a213d1a44c1cc3140ba6c5b3922f8411b6161c9716f9fbc1b0ad0c3804871`.
77Runtime-/73Diagnostik-/14Collectorpins frisch geprüft. Alle fünf Gates False,
Dateien0600, neue eigene Namespaces/CollectorPRIVATE. Nach ausschließlich
Namespace-/PRIVATE-Rücknahme sind Runner und Collector bytegleich zum Parent.
Vier Coredateien und Metadatenfingerprints identisch. Alte Pakete unverändert.

| Verteilbare Quelle | SHA256 |
|---|---|
|`a1_passive_xrecord.py`|`f93e192c2eedf6f0d467cf9cf659be79dbfe3d588ae223eb8d6aea4586119c95`|
|`test_a1_passive_xrecord.py`|`c98db1d0719c9dfc3844d284f7a1619a23eebe8027bfffeaf75b17339e928d07`|
|`test_a1_xtest_preparation.py`|`d66ffffb3dcc671b3cdd0b197163e703b234ab82492090435e018f6a31435f16`|
|`prepare_a1_xtest_preparation.py`|`fd0156725d9fbaadf469286666386d9023bb16e7cfda62d41c480346e3f0485b`|

Vollständiger Adapter-/Runner-/Collector-Diff im Paket:
`xtest-preparation-source.diff`,SHA
`183a49e84a0041949318a67bff8f46d39817d5089eebfd814033fa76e7fff7a8`.
Private Offlinequittung
`/srv/tse-a1-xtest-preparation-evidence-20261114/offline-verification.json`,SHA
`dbc2afc9de388c01022a9e163d83d33ac9fb9b1a11bb1527725c30abd5981cb6`.

Nächster Schritt Rootreview und separater eingefrorener, gesicherter einzelner
OriginalNoFire-Diagnostiklauf. Die tatsächliche A1-Wirkung der Vorbereitung ist
noch nicht nativ beobachtet; kein A1-PASS, keine neue vollständige Retail-
Qualifikation und keine Rolloutempfehlung aus diesen Offlinefällen.
