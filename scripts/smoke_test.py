"""Prova de conceito: envia uma pergunta ao chatbot do Dify e imprime resposta, latência e trechos.

Uso: python scripts/smoke_test.py "Qual é a nota mínima para aprovação em uma disciplina?"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "libraries"))
from dify_client import DifyClient  # noqa: E402


def main():
    pergunta = sys.argv[1] if len(sys.argv) > 1 else "Qual é a nota mínima para aprovação em uma disciplina?"
    cliente = DifyClient()
    cliente.verificar_disponibilidade()
    r = cliente.enviar_pergunta(pergunta, caso_id="SMOKE")
    print(f"Resposta ({r['latencia_s']} s):\n{r['resposta']}\n")
    print(f"Trechos recuperados: {len(r['contextos'])}")
    for fonte, contexto in zip(r["fontes"], r["contextos"]):
        print(f"- [{fonte['documento']} | score {fonte['score']}] {contexto[:150]!r}")
    if not r["contextos"]:
        print("AVISO: nenhum trecho retornado. Habilite 'Citations and Attributions' no app do Dify.")


if __name__ == "__main__":
    main()
