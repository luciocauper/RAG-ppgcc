"""Regressões do módulo de auditoria (sem API): Ragas formal/piloto e formatação."""
import csv
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import auditoria as a


def _csv(caminho, campos, linhas):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)


def test_ragas_formal_nao_converte_erro_em_zero(tmp_path):
    (tmp_path / "ragas").mkdir()
    (tmp_path / "ragas/status_avaliacao.json").write_text(json.dumps({
        "estado": "parcial", "modelo_configurado": "juiz", "versao_ragas": "0.2.15", "rpm_configurado": 2,
        "amostras_elegiveis": 1, "casos_elegiveis": ["CT01"], "avaliacoes_planejadas": 3}), encoding="utf-8")
    campos = ["caso_id", "rodada", "metrica", "status", "valor", "tipo_erro", "mensagem"]
    _csv(tmp_path / "ragas/metricas_ragas.csv", campos, [
        {"caso_id": "CT01", "rodada": 1, "metrica": "faithfulness", "status": "calculada", "valor": "0.5"},
        {"caso_id": "CT01", "rodada": 1, "metrica": "factual_correctness", "status": "erro_cota",
         "mensagem": "Error 429 limit: 20, model: juiz-x"},
        {"caso_id": "CT01", "rodada": 1, "metrica": "llm_context_precision_with_reference", "status": "ausente"},
    ])
    r = a.ragas_execucao(tmp_path)
    assert r["tipo"] == "formal"
    assert (r["validas"], r["falhas"], r["ausentes"], r["planejadas"]) == (1, 1, 1, 3)
    assert r["por_metrica"]["faithfulness"]["media"] == 0.5
    assert r["por_metrica"]["factual_correctness"]["media"] is None
    assert r["modelos_reportados"] == {"juiz-x": 1} and r["limites_reportados"] == {"20": 1}


def test_ragas_piloto_formato_largo(tmp_path):
    _csv(tmp_path / "ragas/metricas_piloto.csv",
         ["caso_id", "faithfulness", "factual_correctness(mode=f1)", "llm_context_precision_with_reference"],
         [{"caso_id": "CT01", "faithfulness": "1.0", "factual_correctness(mode=f1)": "0.5",
           "llm_context_precision_with_reference": ""}])
    r = a.ragas_execucao(tmp_path)
    assert r["tipo"] == "piloto"
    assert (r["planejadas"], r["validas"], r["ausentes"]) == (3, 2, 1)


def test_sem_ragas(tmp_path):
    assert a.ragas_execucao(tmp_path)["tipo"] == "nao_avaliada"


def test_formatacao_e_faixas():
    assert a.fmt_pct(86.666) == "86,7%"
    assert a.fmt_num(None) == "—"
    assert a.faixas([2, 3, 4, 5, 6]) == "exec2–6"
    assert a.faixas([1, 4]) == "exec1 e exec4"
    assert a.faixas([]) == "nenhuma execução"


def test_numero_creditos():
    assert a._numero_creditos("total de **28 (vinte e oito)** créditos") == 28
    assert a._numero_creditos("não há informação") is None
