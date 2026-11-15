# Reiner Messhelfer für übergebene eigene CPU-Domänen

Owner/Claim: a4_diagnosis, eigener WT. Nur neue helper/test/plan/report-Dateien;
keine bestehenden Sources oder Pakete ändern. Root liefert bekannte PID+Startticks
und exakte eigene Cgroup-Unitpfade. Der Helper entdeckt/steuert keine Prozesse,
schreibt keine Logs und startet keinen Loop/Thread oder Frida.

API: `sample(epoch, processes={name:(pid,start_ticks)}, cgroups={name:path},
clock_hz=..., read=..., stat=..., clock=...)`; `delta(before,after)`.
PID-stat zweimal: PID/Startticks müssen vor/nach stimmen; ausschließlich eigene
utime/stime, niemals cutime/cstime. Cgroupverzeichnis dev/inode vor/nach cpu.stat;
eine usage_usec-Zeile. Quellen-/Counterfehler bleiben als UNKNOWN mit Raw/Error
archivierbar, niemals0. Kein Discovery-/Fallbackpfad.

Jedes Sample hat monotone Anfang-/Endgrenzen und epoch. Delta verwendet positive,
getrennte Messintervallgrenzen (after.begin-before.end bis after.end-before.begin)
und liefert pro Domäne Kernäquivalent-RANGE statt vorgetäuschter exakter Zeit.
Überlappung/reverse/nonfinite, Quellenrecreation/Reuse, Counterrückgang und
Epochen-/Hz-Wechsel werden UNKNOWN. Prozess- und Cgroupdomänen bleiben getrennt;
Cgroups können Prozesse/Kinder enthalten, also niemals aufsummieren/HostCPU%claim.

TDD: sechs kleine FakeFS-/Counter-Fälle, inklusive fehlendem Endsample,
PIDreuse, Cgrouprecreation, comm mit') ', fremden Kinderzeiten, kaputten
Counters/Zeiten und noFallback. Keine realen /proc-/Cgroup-/Runtimezugriffe in Tests.
Danach Source-only Quittung/Report und Commit; Rootwrapper integriert separat
identische1s-Beobachtung beider Arme. Keine Guardgrenzenänderung/Hostpass.

Status: COMPLETE_SOURCE_ONLY/HANDOFF. Sechs neue API-Assertions RED;
sechs FakeFS-Tests finalPASS/0.005s. Eigene erste Testfixturefehler separat
behalten/korrigiert. Kein Runtime-/Hostpass; Rootintegration offen.
