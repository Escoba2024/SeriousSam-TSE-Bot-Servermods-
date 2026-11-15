# Frida IA32: Interpreterverfügbarkeit getrennt von Retailqualifikation

15.11.2026, eigener regulärer Terminalzugang; RDC bleibt unbenutzt.
Auf dem bereits vorhandenen eigenen ELF32-IA32-Testprogramm wurden mit der
gepinnten lokalen Frida-Python-Version 17.26.2 zwei minimale RPC-Skripte
explizit als `qjs` beziehungsweise `v8` geladen. `Script.runtime` meldete
`QJS` beziehungsweise `V8`, Architektur `ia32`, Pointergröße 4.
Beide Skripte wurden entladen, Sessions getrennt; derselbe eigene Kindprozess
beendete seine 400 unveränderten Rückgabewertprüfungen regulär mit Exit 0.
Keine Hooks, Retaildateien, Wine- oder Gameprozesse waren beteiligt.

Private Quelle/Quittung:
`/srv/tse-frida-runtime-availability-20261115/{check.py,receipt.json}`.
Dies belegt ausschließlich verfügbare Interpreter im eigenen Linux-ELF32-Fall.
Es belegt keine Wine-/Retailverträglichkeit, ABI, CPU-Ursache oder Verbesserung.
Der aktuelle A1-Backendaufruf verwendet weiterhin `create_script(self.source)`;
diese Verfügbarkeitsprüfung ändert keine bestehende Runtime oder Freigabe.
Jede Verwendung eines anderen Interpreters braucht eine eigene begründete
prospektive Prüfung mit unveränderten Guards und frischem Kontrollfall.
