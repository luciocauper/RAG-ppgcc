#!/usr/bin/env bash
# Compatibilidade com Git Bash no Windows: delega ao executor PowerShell.
# Uso: bash scripts/executar.sh [N]. Sem N, aloca a proxima execucao.
set -eu
if [ "$#" -gt 1 ]; then
  echo "Use executar_windows.ps1; execucao parcial/merge historico nao e suportada." >&2
  exit 2
fi
SCRIPT="$(cd "$(dirname "$0")" && pwd)/executar_windows.ps1"
if ! command -v powershell.exe >/dev/null; then
  echo "Este atalho requer Windows PowerShell 5.1. Veja README.md." >&2
  exit 2
fi
if [ "$#" -eq 1 ]; then
  exec powershell.exe -NoProfile -File "$SCRIPT" -Modo completo -Exec "$1"
fi
exec powershell.exe -NoProfile -File "$SCRIPT" -Modo completo
