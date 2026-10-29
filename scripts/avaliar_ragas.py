"""Calcula as métricas semânticas do Ragas sobre as respostas registradas pela suíte Robot.

Entrada:  results/respostas.jsonl (gerado pelo DifyClient) + datasets/casos_teste.json
Saída:    results/metricas_ragas.csv (por resposta) e resumo com as médias frente aos limites.

Uso: python scripts/avaliar_ragas.py [--resultados results/respostas.jsonl]
"""
import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")

# Metas do planejamento (ilustrativas, ver docs/protocolo_testes.md)
LIMITES = {
    "faithfulness": 0.90,
    "factual_correctness": 0.85,
    "llm_context_precision_with_reference": 0.80,
}


def carregar_amostras(caminho_resultados):
    dados = json.loads((RAIZ / "datasets/casos_teste.json").read_text(encoding="utf-8"))
    casos = {c["id"]: c for c in dados["casos"] if "ragas" in c.get("avaliacao", [])}
    amostras = []
    with open(caminho_resultados, encoding="utf-8") as f:
        for linha in f:
            r = json.loads(linha)
            caso = casos.get(r.get("caso_id"))
            if caso is None or not r["contextos"]:
                continue
            amostras.append((r, caso))
    return amostras


def criar_llm_juiz():
    from langchain_openai import ChatOpenAI
    from ragas.llms import LangchainLLMWrapper

    return LangchainLLMWrapper(
        ChatOpenAI(
            model=os.getenv("RAGAS_LLM_MODEL", "gemini-3.5-flash"),
            base_url=os.getenv("RAGAS_LLM_BASE_URL") or None,
            api_key=os.getenv("RAGAS_LLM_API_KEY") or None,
            temperature=0,
        )
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resultados", default=RAIZ / os.getenv("RESULTADOS_JSONL", "results/respostas.jsonl"))
    parser.add_argument("--saida", default=RAIZ / "results/metricas_ragas.csv")
    args = parser.parse_args()

    from ragas import EvaluationDataset, RunConfig, SingleTurnSample, evaluate
    from ragas.metrics import FactualCorrectness, Faithfulness, LLMContextPrecisionWithReference

    amostras = carregar_amostras(args.resultados)
    if not amostras:
        raise SystemExit("Nenhuma resposta elegível (casos com 'ragas' e com contextos recuperados).")

    dataset = EvaluationDataset(
        samples=[
            SingleTurnSample(
                user_input=r["pergunta"],
                response=r["resposta"],
                retrieved_contexts=r["contextos"],
                reference=caso["resposta_referencia"],
            )
            for r, caso in amostras
        ]
    )
    resultado = evaluate(
        dataset=dataset,
        metrics=[Faithfulness(), FactualCorrectness(), LLMContextPrecisionWithReference()],
        llm=criar_llm_juiz(),
        # Poucas chamadas em paralelo e esperas longas entre tentativas: plano gratuito do Gemini.
        run_config=RunConfig(
            max_workers=int(os.getenv("RAGAS_MAX_WORKERS", "2")),
            max_retries=int(os.getenv("RAGAS_MAX_RETRIES", "10")),
            max_wait=int(os.getenv("RAGAS_MAX_WAIT_S", "120")),
            timeout=300,
        ),
    )

    df = resultado.to_pandas()
    df.insert(0, "caso_id", [r["caso_id"] for r, _ in amostras])
    df.insert(1, "rodada", [r["rodada"] for r, _ in amostras])
    df.to_csv(args.saida, index=False, encoding="utf-8")
    print(f"Métricas por resposta salvas em {args.saida}\n")

    for metrica, limite in LIMITES.items():
        if metrica in df:
            media = df[metrica].mean()
            situacao = "OK" if media >= limite else "ABAIXO"
            print(f"{metrica:40s} média {media:.3f}  (meta {limite:.2f})  {situacao}")


if __name__ == "__main__":
    main()
