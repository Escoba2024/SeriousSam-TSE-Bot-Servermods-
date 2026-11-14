# A4: native Feuerbeobachtung V2

Status: Design und Offline-Nachprüfung; keine Runtime-Freigabe. Eigentümer:
`candidate_audit`; Hauptagent integriert und besitzt alle nativen Ressourcen.

Build020s unveränderter 480-s-Controller endete am 14.11.2026 mit FAIL:
Phase0 `botA:3:fire_action_rows`. Alle übrigen alten Aktivitätsfelder waren
vorhanden. Einmal pro Sekunde protokolliertes `CecilState.fire` war bei diesem
Slot immer null, während der bereits vorhandene Originalserver-Reader elf
lebende Schusswaffensamples mit Ammo, `fire_requested=1` und tatsächlich
gesetztem `CPlayer.last_buttons & 1` aufzeichnete. Source-`shots` stieg ebenfalls.
Dieser Lauf und sein bisheriger Kriteriumsstatus werden nicht umgewertet.

## Unveränderte Grenzen

Keine Botproduktionsänderung, kein weiterer Lauf, keine Frida-Instrumentierung,
keine neue Abtastrate und keine gelockerten Bewegungs-/Pickup-/Stabilitätswerte.
Die neuen Belege bezeichnen eine beobachtete gültige Feueraktion, keinen
nachgewiesenen Einschlag, Schaden oder Kill. Die gesonderte A3-Damageabnahme
bleibt erforderlich. Alle 24 Slotphasen bleiben verpflichtend. Die native
Wirksamkeit des neuen terminalen Build020-Watchdogs bleibt unbewiesen.

## V2-Vertrag

1. Phase und tatsächliche lokale→globale Slotabbildung aus archivierter Registry
   verwenden. Bereits geschnittene Phasenlogs niemals erneut mit ihrem
   ursprünglichen Byteoffset schneiden. Phase, Entity-ID/-Pointer, Weltpointer,
   Spawnclock und kontrollierte Serverprozessidentität bilden den Epochenschlüssel.
   Der ursprüngliche hostgebundene Reader und sein doppelt stabiler Read bleiben
   unverändert. Keine Queryindex-Zuordnung oder Anzeigeidentitäten verwenden.
2. Pro Slot/Phase mindestens ein tatsächlich gelesenes Originalserversample:
   vorhanden, Render3, gesund, passende Registry-Entity/Welt, gültiges Leben,
   `last_buttons & FIRE(1)`, gültige aktuelle Schusswaffe in `0x3df8`, deren
   eigener Besitzbit gesetzt ist, `has_ammo=1` und `fire_requested=1`. Der
   Weapon-Owner-/Worldcheck des geerbten Readers bleibt notwendig. Ein AI-Wunsch,
   `shots` allein oder interpolierte Aktionen sind keine Ersatzbelege.
3. Dasselbe beobachtete Leben an eine eindeutige Source-Entity/Generation und
   tatsächlich vorhandene `CecilWeaponObserve.native_time`-Innenzeugen binden.
   CecilSpawn ist Beobachtungszeit und kann nach dem tatsächlichen serverseitigen
   Spawn liegen; seine Grenzzeile allein reicht daher nicht. Das gesamte mögliche
   Rundungsintervall des Source-printf-Werts (sechs Dezimalstellen, ±0,5 Mikrosekunden)
   muss innerhalb der unveränderten exakten servernativen Grenzen liegen:
   `Decimal.from_float(spawned_tick)` bis zum letzten tatsächlich gesunden Sample
   desselben Lebens. Keine Rundung der Servergrenzen, kein numerisches Epsilon,
   kein Schätzen von Positionen/Aktionen und keine Überbrückung fehlender Leben.
   Randzeugen werden verworfen und gezählt. Gegenläufige Innenzeugen machen die
   Generation ungültig. Mehrere Generationen für ein Serverleben zählen nicht.
4. Innerhalb genau dieser Entity/Generation muss zwischen zwei tatsächlichen
   lebenden `CecilState`-Zeilen der kumulative `shots`-Counter wachsen. Counter
   über Tod, Generation, Phase oder Entity hinweg niemals zusammenrechnen.
   Die nativ beobachtete Feueraktion und der Counterzuwachs müssen im gleichen
   gebundenen Leben vorliegen; keine exakte Schusszahl oder Schusszeit daraus
   rekonstruieren. Counterrückgang macht die Bindung ungültig.
5. Pickup ebenfalls nur als tatsächlicher Useful-Besitzübergang zwischen zwei
   gesunden, stabilen Serversamples derselben Phase/Entity/Welt/Spawnclock
   zählen. Zuerst bereits bewaffnet beobachtete Leben bleiben links zensiert.
   Waffen-/Lebenswechsel, fehlerhafte Registry, Corpse und Duplikate zählen nicht.
6. V2 liefert getrennte beobachtete Counts und Belegreferenzen (Datei/Zeile,
   Tick, Phase/Slot, Entity-/Life-/Generation-Schlüssel), keine nachträgliche
   PASS-Ausgabe für den alten Lauf. In einer künftigen Controllerrevision darf
   V2 genau das fehlerhafte `CecilState.fire`-Samplegate durch diesen strengeren
   vollständigen Vertrag ersetzen; übrige Gates bleiben bytegleich.

## Aufgaben und Nachweise

- [x] Einen konkreten Aliasfall anhand Originalserver-Inventar und Sourcecounter
  identifizieren; Ergebnis dem Hauptagenten melden.
- [x] Alle 24 archivierten Slotphasen gegen den vollständigen V2-Vertrag prüfen;
  bereinigte Counts und Eingabehashes im zugehörigen Bericht ablegen.
- [x] Engen portablen Archivaudit getrennt implementieren. Fokussierte
  Negativtests: falsche Welt/Entity/Life/Epoch, fehlendes FIREbit, falsche oder
  unbesessene Waffe, fehlende Ammo, reiner AI-Wunsch, Counter ohne Nativeaction,
  Nativeaction ohne Sourcezuwachs, Counterreset/Generationwechsel, links zensierter
  Besitz und vollständige printf-Rundungsbereiche. Dreizehn fokussierte Tests grün;
  ein vorher roter Grenzfall belegt die Korrektur. Keine breite Testdiscovery.
- [x] Bereinigten Bericht mit Dateien/SHA256 und Grenzen committen; Rohidentitäten
  und private Retaildaten bleiben außerhalb Git.
- [ ] Hauptagent reviewed eine eigene deaktivierte Controller-V2-Revision samt
  unveränderten restlichen Kriterien. Erst danach entscheidet er über Freeze,
  Preflight und einen gesonderten nativen Lauf. Kein impliziter Runtimeauftrag.

Private Eingaben: `/srv/tse-milestone-a-evidence-20261111/`
`a4-reset020-extended-20261114-092735`; geerbter Controller
`/srv/tse-a4-build020-controller-20261114`; Reader
`/srv/tse-milestone-a-20261111/tools/retail_inventory_readonly.py`.
