# Pause-Reader: exakte Prüfung nach PE32-Relokation

Ein isolierter 007-Start wurde beim Bootstrap mit `IsPaused instructions differ`
abgebrochen. Damals wurden weder Mappingbasis noch gelesene Bytes erfasst. Seine
konkrete Ursache bleibt deshalb unbekannt; eine Relokation ist für diesen
Einzelfall nicht nachgewiesen.

Ein davon unabhängiger, reproduzierbarer Readerfehler ist belegt: Die bisherige
Signatur erwartete den absoluten Operanden `0x602cd6b8` auch bei einer anderen
Ladeadresse. Das Original `Engine.dll` mit SHA256
`b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f`
ist PE32, bevorzugte Basis `0x600c0000`, ImageSize `0x22e000`. Seine
Base-Relocation-Directory bei RVA `0x216000`, Größe `0x159f0`, enthält
`IMAGE_REL_BASED_HIGHLOW` (Typ 3) exakt bei RVA `0xdab65`. Das ist der vier Byte
lange absolute Operand des A1-Befehls in IsPaused ab RVA `0xdab60`.

Header, Sektionen, vollständige Relokationsblöcke und originale Signaturbytes
wurden unabhängig direkt aus der hashgeprüften Datei gelesen. Innerhalb der
vier geprüften Instruktionsbereiche gibt es ausschließlich diesen Eintrag;
TogglePause, Rnd und ResetRND sind in ihren geprüften Bereichen relokationsfrei.

Der Reader berechnet den erwarteten Operanden jetzt exakt als
`0x602cd6b8 + tatsächliche_Basis - 0x600c0000`. Alle übrigen Bytes bleiben exakt,
es gibt keine Maskierung. Die Basis muss eine ganze, mindestens `0x10000`
große, auf 4096 Byte ausgerichtete Adresse sein; das vollständige Image muss in
den 32-Bit-Adressraum passen. Bestehende Hash-, Inode-, Prozess-, Session- und
Dateiidentitätsprüfungen bleiben erhalten. Bei einer Instruktionsabweichung
enthält die Fehlermeldung Basis, RVA, erwartete und beobachtete Bytes. Diese
Diagnose enthält keine Spielernamen oder Spielerzustände.

RED: Nach reinem Extrahieren der bisherigen unveränderten Signaturprüfung
bestanden bevorzugte Adressen weiterhin; vier gültige verschobene Mappings
scheiterten reproduzierbar mit `IsPaused instructions differ`.
GREEN: Sieben fokussierte portable Tests bestehen. Enthalten sind bevorzugte
Basis, positive/negative Verschiebung, zulässige untere/obere Grenzen, ungültige
Basen ohne Speicherleseversuch, falscher unveränderter Operand bei Verschiebung,
jede einzelne verfälschte Signaturposition, kurze Bytes und Diagnoseinhalt.

```sh
python3 tools/test_probe_retail_pause.py
objdump -p /path/to/original/Engine.dll
objdump -d -M intel --start-address=0x6019ab60 --stop-address=0x6019ab75 /path/to/original/Engine.dll
```

Keine Runtime wurde gestartet, gelesen oder verändert. Der frühere Fehlstart
bleibt fehlgeschlagen. Die portable Regression beweist die Korrektur des
statischen Relokationsfehlers, keine native Start- oder Gameplay-Abnahme.
