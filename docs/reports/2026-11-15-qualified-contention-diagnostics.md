# Qualifizierte Zielkonkurrenz sichtbar machen

Neue passive Quelldiagnose, noch kein DLL-Build oder Laufzeittest. Der aktuelle
Live-Stand bleibt erhalten; A4 ist offen. Anlass ist die geschlossene027-Beobachtung:
ein höher bewertetes Waffenziel wurde gewählt, während ein näherer lokaler Bot
möglicherweise das günstigere Ziel verfolgte. Die damaligen Logs enthalten
keinen vollständigen qualifizierten Anspruch; eine Ursache ist damit nicht belegt.

Die vorhandenen Candidate-/Selection-Zeilen geben jetzt die tatsächliche
Präferenzprüfung und deren bereits qualifizierten ersten lokalen Besitzer aus.
Eine optionale skalare Quittung entsteht ausschließlich am bisherigen positiven
Return der Besitzerprüfung. Sie enthält lokale Nummer, Mapserial, Entity-/Life-/
Item-/Zielkennung, Kosten und die unverwechselbar benannten gemeinsamen bzw.
besitzereigenen Zeitwerte. Keine Zeiger verlassen den Aufruf; keine zusätzliche
Suche, Uhrabfrage, Strahlprüfung, Zufallszahl oder native Objektabfrage entsteht.
Die Gewinnerzeile kopiert genau die Quittung des tatsächlich gewählten Kandidaten.

Ungeprüft oder nicht qualifiziert bedeutet UNKNOWN: `owner_valid=0`,
`owner_local=-1`, zurückgesetzte Werte. Ein Budgetfallback meldet ausdrücklich
`preference_evaluated=0`; er behauptet keine fehlenden Mitbewerber. Die bisherige
Reihenfolge bleibt erhalten, einschließlich erstem qualifizierten Besitzer,
kontestiertem Einzelwaffenfallback, acht Versuchen und gemeinsamen Strahlreserven.
Kosten ohne Itemconnector und höhengewichteter Auswahlscore bleiben getrennt.
Neue Doublewerte verwenden17signifikante Stellen zur eindeutigen Rücklesbarkeit.

Nachweise am echten portablen Bridge-Quellkörper:

- Baseline:3667Prüfungen,2reale fehlende Logvertragsbelege schlugen fehl.
- Nach Änderung:3733Prüfungen,0Fehler, einschließlich26negativer Besitzerfälle,
  veralteter Quittungen, Gewinnerwechsel, Budgetfallback und Diagnose0/1-Vergleich
  von Ziel, Strahlen, Lookups, Uhrabfragen, RNG, Deadline und Restbudget.
- Drei ergänzende Source-/Formatprüfungen bestanden. Der vollständige Header
  invertiert exakt zu Build027 SHA256
  `5530062bdac71b3649a5db0f7af4a4e90daafc60a343bbddf8b2189a878565a0`.
  Driver bleibt bytegleich. Acht bewusste Guard-/Quittungs-/Doppelblockmutationen
  werden zurückgewiesen; keine breite Normalisierung von Gameplaycode.
- Konservative vollständige Zeilen inklusive NUL:Candidate1742B,
  Selection1898B, beide unter dem vorhandenen2048B-Puffer. Tatsächliches printf
  mit extremen Zahlen:1729B/1875B; bestehende Zeilenzahl/Cadence/Candidatecap bleiben.

Eine zusätzliche Sourceprüfung rief zunächst irrtümlich nur `inverse` statt
`verify` für einen angehängten Doppelblock auf. Diese Testassertion wurde
korrigiert; der ursprüngliche FAIL ist privat erhalten. Die Produktionsquelle
wurde dafür nicht geändert. Rootreviewquittung und vollständige Logs liegen
privat; dies ist Root-Selbstreview, noch keine unabhängige Branchschlussprüfung.

Keine neue FinalAction-Zeile, keine belegte physische Bewegung, kein Nachweis
eines Alternativpickups oder einer reparierten52s-Lebensphase. CPU-/Loggingkosten
sind noch nicht nativ qualifiziert. Erst ein neuer eindeutig gepinnter Kandidat
und begründete Runtimeprüfung können weitere Aussagen liefern.

## Separater Build028 und unabhängiger Quellreview

15MSVC-Übersetzungseinheiten und Linker exit0. Sourcecommit
`d96ef33a4c809fa7da13e83de9fc949383ab3c81`,
DLL SHA256 `bdaffd114fd8c1d2b3a54d3af4dafeedaf9a730b6a9ffd92d99887375b5fe8d7`,
448000B; Manifest `cdb3e806d07ae6f12a8e66a4ff9ae29c9ba044bb9eb2aeddd78724701df21b57`.
Alle47Source-/28Overlay-/Manifest-/DLLpins geprüft. Ausschließlich Header
gegenüber027 geändert; kein Native-/Ressourcen-/A4-PASS. Separater unabhängiger
Quellreview PASS_SCOPE ohne offeneBefunde, privateQuittung SHA256
`a8dce9cdc103aa23e79820656dad3794e6ec3144ffec317ac6cd47157bda4b49`.
Tests wurden im Review nicht erneut gestartet.
