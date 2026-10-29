"""Consolida os resultados das execuções do Robot (results/execN/output.xml) por caso de teste.

Saída: tabela em Markdown no terminal e results/consolidado.md, com o status de cada caso em cada
execução, a taxa de aprovação por categoria e as estatísticas de latência/retentativas das respostas.

Uso: python scripts/consolidar.py [1 2 3]
"""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SIMBOLO = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️"}


def ler_execucao(n):
    raiz = ET.parse(RAIZ / f"results/exec{n}/output.xml").getroot()
    status = {}
    for suite in raiz.find("suite").findall("suite"):
        for teste in suite.findall("test"):
            status[teste.get("name")] = (suite.get("name"), teste.find("status").get("status"))
    respostas = [
        json.loads(linha)
        for linha in (RAIZ / f"results/exec{n}/respostas.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    return status, respostas


def main():
    execucoes = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    dados = {n: ler_execucao(n) for n in execucoes}
    nomes = list(dados[execucoes[0]][0])

    linhas = ["## Resultado por caso", "", "| Suíte | Teste | " + " | ".join(f"Exec {n}" for n in execucoes) + " |",
              "|---|---|" + "---|" * len(execucoes)]
    for nome in nomes:
        suite = dados[execucoes[0]][0][nome][0]
        celulas = [SIMBOLO[dados[n][0].get(nome, ("", "SKIP"))[1]] for n in execucoes]
        linhas.append(f"| {suite} | {nome} | " + " | ".join(celulas) + " |")

    linhas += ["", "## Aprovação por suíte", "", "| Suíte | " + " | ".join(f"Exec {n}" for n in execucoes) + " |",
               "|---|" + "---|" * len(execucoes)]
    for suite in dict.fromkeys(s for s, _ in dados[execucoes[0]][0].values()):
        celulas = []
        for n in execucoes:
            st = [v for s, v in dados[n][0].values() if s == suite]
            celulas.append(f"{st.count('PASS')}/{len(st)}")
        linhas.append(f"| {suite} | " + " | ".join(celulas) + " |")
    totais = [f"{[v for _, v in dados[n][0].values()].count('PASS')}/{len(dados[n][0])}" for n in execucoes]
    linhas.append("| **Total** | " + " | ".join(f"**{t}**" for t in totais) + " |")

    linhas += ["", "## Chamadas ao SUT", "", "| Execução | Chamadas | Latência média (s) | Latência máx. (s) | Com retentativa |",
               "|---|---|---|---|---|"]
    for n in execucoes:
        lat = [r["latencia_s"] for r in dados[n][1]]
        ret = sum(r.get("tentativas", 1) > 1 for r in dados[n][1])
        linhas.append(f"| {n} | {len(lat)} | {sum(lat) / len(lat):.1f} | {max(lat):.1f} | {ret} |")

    texto = "\n".join(linhas) + "\n"
    (RAIZ / "results/consolidado.md").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
