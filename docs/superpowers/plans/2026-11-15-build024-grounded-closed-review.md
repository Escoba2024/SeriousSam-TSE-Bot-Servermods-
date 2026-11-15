# Build024: vollständige geschlossene GroundReplan-Auswertung

**Ziel:** Alle neun protokollierten Replanfälle des geschlossenen Red600-Laufs
streng auf eigene Rolle/Local/Slot/Entity/Generation und Nativeleben binden;
neuen Stale-anchor-Pfad nur bei tatsächlicher Vorankerbeobachtung behaupten.

**Architektur:** Bestehende Root-V3-Lebensauswertung samt Inputhashes lesen,
kanonische typisierte Nativebeobachtungen und SourceSpawn/State/WPO vollständig
für die neun Fälle auswerten. Originalnavmetadaten sind kataloggepinnt.
SourceTicks werden nicht durch20 in Nativezeit umgerechnet. Gerundete WPO-
Werte liefern nur ganze Druckintervalle und umgebende Beobachtungsfenster.

**Spezifikation:** Rootauftrag nach abgeschlossenem024-Lauf; bestehender
GroundedReplan-Fix und frühere geschlossene Replan-/Recoveryanalysen.

- [x] Geschlossenes Resultat und fertige Rootauswertung/hashgebundene Inputs lesen.
- [x] Gesamtnenner neun Events, SourceSpawn/State/WPO/Ownslot/NativeLife/World/Epoch binden; Ambiguitäten ausdrücklich UNKNOWN.
- [x] Voranker nur bis zur tatsächlichen zeitlichen Aussagekraft der Sourcezeilen bestimmen, keine Preanchorannahme aus Postresetlog.
- [x] Alle Folgezeilen bis Tod/Reset verfolgen: Ziel/Deadline, tatsächliche ursprüngliche strikte Radien, Bewegung, Navsource/Hop/Travel, Itemende, Inventargewinne und begrenzte Kampfbelege getrennt.
- [x] Größte NoUseful-Leben sachlich zuordnen; Diagnostics0-Gründe bleiben UNKNOWN, keine retrospektive Erklärung alter023-Leben.
- [x] Private reproduzierbare Vollquittung und bereinigten Bericht committen; keine Tests oder Runtime.

Abgeschlossen: vollständiger Neuner-Nenner und acht gebundene Leben; Report und private zweistufige Reproduktion gesichert. Root hat beide Quittungen unverändert bytegenau reproduziert. Kein Native-/A4-Freigabebefund.
