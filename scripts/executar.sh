#!/bin/bash
# Executa a suíte completa (ou suítes escolhidas) como uma execução numerada do experimento.
# Cada suíte roda em processo próprio (o host tem pouca memória livre) e, ao final, os resultados
# são unidos com rebot em results/execN/. As respostas do SUT vão para results/execN/respostas.jsonl.
#
# Uso: scripts/executar.sh N [suite ...]      ex.: scripts/executar.sh 2
#      scripts/executar.sh N --merge           só une as suítes já executadas
set -u
cd "$(dirname "$0")/.."
N=$1; shift
SAIDA="results/exec$N"
PY=.venv/Scripts/python
[ -x "$PY" ] || PY=.venv/bin/python
ORDEM="api factualidade alucinacao robustez seguranca conversa desempenho"
export RESULTADOS_JSONL="$SAIDA/respostas.jsonl" PYTHONIOENCODING=utf-8
mkdir -p "$SAIDA/parciais"

if [ "${1:-}" != "--merge" ]; then
  for s in ${@:-$ORDEM}; do
    "$PY" -m robot --name "$s" -d "$SAIDA/parciais" -o "$s.xml" -l NONE -r NONE "tests/$s.robot" \
      | grep -E "\| (PASS|FAIL|SKIP) \|" | grep -v "::"
  done
fi

PARCIAIS=$(for s in $ORDEM; do [ -f "$SAIDA/parciais/$s.xml" ] && echo "$SAIDA/parciais/$s.xml"; done)
"$PY" -m robot.rebot --name "Assistente PPGCC - Execucao $N" -d "$SAIDA" -o output.xml $PARCIAIS > /dev/null
echo "Relatório: $SAIDA/report.html"
