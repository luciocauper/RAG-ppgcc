"""Extrai evidências das falhas experimentais dos arquivos respostas.jsonl.

Uso: python scripts/investigar_falhas.py
Saída: docs/analise_falhas.md
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CASOS_FALHA = ["CT09", "CT22", "CT28", "CT30", "CT18", "CT21"]

# Mapeia cada execução para seu arquivo
EXECS = {1: "results/exec1/respostas.jsonl", 2: "results/exec2/respostas.jsonl", 3: "results/exec3/respostas.jsonl"}


def carregar_respostas(exec_n):
    """Retorna dict {caso_id: [lista de respostas]} para uma execução."""
    caminho = RAIZ / EXECS[exec_n]
    respostas = {}
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        r = json.loads(linha)
        cid = r.get("caso_id", "")
        respostas.setdefault(cid, []).append(r)
    return respostas


def extrair_info(r):
    """Extrai informação concisa de uma resposta."""
    return {
        "resposta": r.get("resposta", "")[:500],
        "contextos_count": len(r.get("contextos", [])),
        "contextos_preview": [c[:200] for c in r.get("contextos", [])],
        "latencia_s": r.get("latencia_s", 0),
        "tentativas": r.get("tentativas", 1),
        "rodada": r.get("rodada", 1),
    }


def main():
    dados = {n: carregar_respostas(n) for n in (1, 2, 3)}

    # Dataset para referência
    dataset = json.loads((RAIZ / "datasets/casos_teste.json").read_text(encoding="utf-8"))
    casos = {c["id"]: c for c in dataset["casos"]}

    linhas = ["# Análise das falhas experimentais\n",
              "> Extraído automaticamente de `results/exec1..3/respostas.jsonl`.\n"]

    for caso_id in CASOS_FALHA:
        caso = casos.get(caso_id, {})
        linhas.append(f"\n---\n\n## {caso_id} — {caso.get('categoria', '?')}\n")
        linhas.append(f"**Pergunta:** {caso.get('pergunta', 'N/A')}\n")
        linhas.append(f"**Comportamento esperado:** {caso.get('comportamento_esperado', 'N/A')}\n")
        if caso.get("resposta_referencia"):
            linhas.append(f"**Resposta de referência:** {caso['resposta_referencia']}\n")
        if caso.get("termos_obrigatorios"):
            linhas.append(f"**Termos obrigatórios:** {caso['termos_obrigatorios']}\n")
        if caso.get("deve_reconhecer_ausencia"):
            linhas.append("**Deve reconhecer ausência:** sim\n")
        if caso.get("termos_proibidos"):
            linhas.append(f"**Termos proibidos:** {caso['termos_proibidos']}\n")

        for exec_n in (1, 2, 3):
            resps = dados[exec_n].get(caso_id, [])
            linhas.append(f"\n### Execução {exec_n}\n")
            if not resps:
                linhas.append("Sem respostas registradas.\n")
                continue
            for i, r in enumerate(resps):
                info = extrair_info(r)
                linhas.append(f"\n**Rodada {info['rodada']}** (latência {info['latencia_s']}s, "
                              f"tentativas {info['tentativas']}, {info['contextos_count']} trechos):\n")
                linhas.append(f"> {info['resposta']}\n")
                if info["contextos_preview"]:
                    for j, ctx in enumerate(info["contextos_preview"][:3]):
                        linhas.append(f"  - Trecho {j+1}: `{ctx}`\n")

    # CT18 tem múltiplas rodadas (consistência)
    linhas.append("\n---\n\n## CT18 — Detalhe da consistência\n")
    for exec_n in (1, 2, 3):
        resps = dados[exec_n].get("CT18", [])
        linhas.append(f"\n### Execução {exec_n} — {len(resps)} respostas\n")
        for r in resps:
            linhas.append(f"  - Rodada {r.get('rodada',1)}: \"{r.get('resposta','')[:200]}\" (lat. {r.get('latencia_s',0)}s)\n")

    saida = RAIZ / "docs/analise_falhas.md"
    saida.write_text("\n".join(linhas), encoding="utf-8")
    print(f"Análise salva em {saida}")


if __name__ == "__main__":
    main()
