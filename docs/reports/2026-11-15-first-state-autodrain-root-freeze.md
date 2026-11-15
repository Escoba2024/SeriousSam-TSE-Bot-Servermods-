# A1: neuer eingefrorener Methodenbeobachter, Native noch offen

Root57Tests4,221sPASS nachIntegration94bc43b..09aaabc, einschließlich vier
reproduzierter Gegenfälle zur abschließenden Deadline-/2s-Prüfung.
Root5Tests0,093sPASS für exakt beide Cgroupbackends aus e8b6089;
Root8Timestampprüfungen und frühere unabhängige Implementierungsprüfung gelten
nur für den exakten6fd1825b→d6c76f6f-Transform. Keine altenNativeFAILs umgewertet.

DeaktivierterAutodrainParent518aea47 besitzt154Runtime-/75Methodenpins.
Im Root-Timestampzwischenfork60216e88 waren beide Transactionquellen richtig
und Runtimepins aktuell; ein zusätzlicher method_api.manifest_sha256-Verweis
blieb jedoch alt. Das ist ein Vorbereitungsmangel, kein Nativebeleg: niegestartet,
Originalartefakt erhalten. Der folgende deaktivierteCgroupfork
 e0546c37e3de632dc7f0ba720d70b43223b1166bd50d51e2ad8e76b02da9f5e5
korrigiert diese Referenz; beide tatsächlich angewendeten Cgroupquellen
rekonstruieren ihre exakten Parents vollständig. Alle alten Belege behalten Grenzen.

Rootfreeze /srv/tse-a1-first-state-autodrain-root-frozen-20261115:
Manifestf7de423422c967fbfda01225e5c292a86796e30dca7ec98d7411340a2526f5a0,
Runner2451ecbd8454b17df85e482c9a1ab385a3de2905bd9b8bafc44ca4b99b9f8766,
Nestedf81c85f4602b0853dc6ccb75ce093bee82e1af94de7f43f295cb5096b82304ba,
WorkerCDF0f39b48c2ffde860efad38428c79298d7e18f347012bb82a310418907f4e2.
162Runtime-/75Methodenpins,100übrigeDateienbytegleich. Ganze Quelleninversen
für Runnergate+zweiNamespaces/neuenWorkergate/Observergate; alte Worker- und
Input-CLIs deaktiviert. NeuesgepaartesControl/Trace notwendig, keineÜbertragung.
10saktiv/85sinner/90sadmission/15sTTL/100msCaptureService/alteQueue64 bleiben.

Unabhängige Prüfung nur der Root-Paketanwendung/Freeze/Pins ist angefordert;
Autor darf daraus keine unabhängige Prüfung seiner eigenen Implementierung
ableiten. Vor beiden einzelnenFenstern Vollsicherung/DriveRücklesen und
Sourceveröffentlichung. Keine automatische Paarsequenz oder Wiederholung.
Kein Erstzustands-/18ABI-/Schadens-/A-Gesamtpass aus diesem Quellstand.
