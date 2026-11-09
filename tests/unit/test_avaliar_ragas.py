"""Testes locais do fluxo Ragas; não importam nem chamam Gemini."""
import csv
import json
from pathlib import Path
import sys
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import avaliar_ragas


def criar_entrada(tmp_path):
    casos = tmp_path / "datasets" / "casos_teste.json"
    casos.parent.mkdir(parents=True, exist_ok=True)
    casos.write_text(json.dumps({"casos": [
        {"id": "CT01", "avaliacao": ["ragas"], "resposta_referencia": "Resposta de referência"},
        {"id": "CT02", "avaliacao": ["ragas"], "resposta_referencia": "Resposta de referência"},
    ]}), encoding="utf-8")
    respostas = tmp_path / "respostas.jsonl"
    linhas = [
        {"caso_id": "CT01", "rodada": 1, "pergunta": "Pergunta?", "resposta": "Resposta.", "contextos": ["Contexto"]},
        {"caso_id": "CT02", "rodada": 1, "pergunta": "Pergunta?", "resposta": "Resposta.", "contextos": []},
        {"caso_id": "CT99", "rodada": 1, "pergunta": "Pergunta?", "resposta": "Resposta.", "contextos": ["Contexto"]},
    ]
    respostas.write_text("".join(json.dumps(x) + "\n" for x in linhas), encoding="utf-8")
    return casos, respostas


def test_carregar_amostras_identifica_nao_elegiveis(tmp_path):
    casos, respostas = criar_entrada(tmp_path)

    amostras, excluidas = avaliar_ragas.carregar_amostras(respostas, casos)

    assert len(amostras) == 1
    assert amostras[0][0]["caso_id"] == "CT01"
    assert excluidas == {"sem_contextos": 1, "caso_nao_elegivel": 1}


def test_avaliacao_parcial_registra_429_e_retoma_metricas_pendentes(tmp_path, monkeypatch):
    casos, respostas = criar_entrada(tmp_path)
    monkeypatch.setattr(avaliar_ragas, "RAIZ", tmp_path)
    saida = tmp_path / "exec5/ragas/metricas_ragas.csv"
    esperas = []
    chamadas = []

    class ErroQuota(Exception):
        response = Mock(status_code=429, headers={"retry-after": "7"})

    def primeira_tentativa(resposta, caso, metrica):
        chamadas.append(metrica)
        if metrica == "factual_correctness":
            raise ErroQuota("HTTP 429 quota exceeded")
        if metrica == "llm_context_precision_with_reference":
            return None
        return 0.9

    parcial = avaliar_ragas.avaliar(
        respostas, saida, evaluate_metric=primeira_tentativa, dormir=esperas.append
    )

    assert parcial["estado"] == "parcial"
    assert parcial["validas"] == 1 and parcial["falhas"] == 1 and parcial["ausentes"] == 1
    assert esperas == [7.0]
    assert parcial["por_metrica"]["faithfulness"]["validos"] == 1
    assert parcial["por_metrica"]["factual_correctness"]["media"] is None
    assert (saida.parent / "status_avaliacao.json").exists()
    with saida.open(encoding="utf-8-sig", newline="") as arquivo:
        registros = list(csv.DictReader(arquivo))
    assert {r["status"] for r in registros} == {"calculada", "erro_cota", "ausente"}
    assert not any(r["valor"] == "0" for r in registros)

    chamadas.clear()
    completa = avaliar_ragas.avaliar(
        respostas, saida,
        evaluate_metric=lambda resposta, caso, metrica: chamadas.append(metrica) or 0.75,
        dormir=esperas.append,
    )

    assert completa["estado"] == "concluida"
    assert completa["validas"] == 3 and completa["falhas"] == 0 and completa["ausentes"] == 0
    assert chamadas == ["factual_correctness", "llm_context_precision_with_reference"]
    assert completa["retomada"] is True


def test_classifica_cota_api_e_processamento():
    quota = Mock(response=Mock(status_code=429))
    api = Mock(response=Mock(status_code=500))
    assert avaliar_ragas.classificar_erro(quota) == "quota"
    assert avaliar_ragas.classificar_erro(api) == "api"
    assert avaliar_ragas.classificar_erro(ValueError("bad sample")) == "processamento"


def test_avaliacao_sem_amostras_elegiveis_nao_fabrica_metricas(tmp_path, monkeypatch):
    _, respostas = criar_entrada(tmp_path)
    monkeypatch.setattr(avaliar_ragas, "RAIZ", tmp_path)
    vazio = tmp_path / "vazio.jsonl"
    vazio.write_text("", encoding="utf-8")

    status = avaliar_ragas.avaliar(vazio, tmp_path / "exec6/ragas/metricas_ragas.csv")

    assert status["estado"] == "sem_amostras_elegiveis"
    assert status["validas"] == 0
    assert status["avaliacoes_planejadas"] == 0
    assert (tmp_path / "exec6/ragas/status_avaliacao.json").exists()
