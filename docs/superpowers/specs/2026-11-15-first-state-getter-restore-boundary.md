# FirstState Getterrestore an der Runtimegrenze

Rootauftrag: geschlossener Trace054021 bleibt FAIL. Erfolgreiche Headerarmierung ist keine Methoden-/A1-Abnahme. Kein Native durch den Autor.

Die bisherige Getterprobe detacht sich korrekt selbst, prüft aber sofort innerhalb desselben JS-Callbacks die vollen Originalbytes. Frida dokumentiert automatisches Commit ausstehender Änderungen beim Verlassen der JS-Runtime beziehungsweise `send`/RPC-Rückkehr. Der qualifizierte A3-Pfad prüft das Restore erst später. Daher muss der synchrone Inside-Getter-Check an eine passende spätere Grenze, ohne die Prüfung zu streichen.

Rootruling: bestehendes `lifetime()` unverändert; zusätzlich derselbe volle Gettercheck vor jeder `emit`-Row, sofern TLS gebunden ist, und beim Drain auch nach Hoststop. Im Getter selbst kein Emit, explizites Flush, NativeFunction, Speicherwrite oder Guardersatz. Stop bleibt admission-only, Finishstop nur callbackidle. Schema, Counterlogik, Limits, TTL/Identity und alle18/38/11/G bleiben unverändert.

Tatsächlicher alter Observer in bestehender VM: `detach` stellt zunächst nur pending, Originalbytes werden erst am äußersten Callback-/RPC-Austritt committed. Alter Inside-Getter-Check muss RED liefern. Nach Fix: voller I1/I2-Pfad bei korrektem Commit; Drift beziehungsweise ausbleibendes Commit vor erster Row/Drain muss sticky FAIL liefern, ebenso nonmain/stopped drain/aktive admitted leave. Ein Stop innerhalb der Getter-Detachphase darf kein Inflight-Detach oder erfolgreiches voreiliges Restore behaupten. Keine Folgecallback ist erforderlich, um einen Restorefehler über Drain festzustellen.

Nur neue öffentliche Transform-/Builder-/Testdateien. Neuer deaktivierter Fork vom Manifest87d4c55a; alte Eltern, NativeFAIL und Pakete bleiben unangetastet. Ganze Body-/compiledJS-Inverse, Gbytegleich und vollständige151/72 erwartete Werte sichern jede Ableitung. Root aktiviert separat, überprüft und führt gegebenenfalls einen eigenen Fall aus.
