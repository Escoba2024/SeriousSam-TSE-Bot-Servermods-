#!/usr/bin/env bash
# clone_reference.sh - holt die Referenz-Repos für den Pfad-D-PoC.
# Aufruf:  ./clone_reference.sh [zielordner]   (Standard: ./reference)
set -euo pipefail

DEST="${1:-reference}"
mkdir -p "$DEST"
cd "$DEST"

echo "== SE1-ModSDK (Build-Basis für den 1.07-Bot-Client; --recursive wegen Engine107-Libs) =="
git clone --recursive https://github.com/DreamyCecil/SE1-ModSDK.git

echo "== Croteam Serious Engine v1.10 (nur Lese-Referenz; Commit b408e88a getestet) =="
git clone --depth 1 https://github.com/Croteam-official/Serious-Engine.git

echo "== CecilBotMod (nur KI-Referenz) =="
git clone --depth 1 https://github.com/DreamyCecil/CecilBotMod.git

echo "Fertig. Patch anwenden im 1.10-Klon:"
echo "  cd Serious-Engine && git apply /pfad/zu/0001-gamemp-botdriver-poc.patch"
echo "(Für den echten Bot-Client aber SE1-ModSDK 'Sources/Game' patchen - siehe RUNBOOK.md)"
