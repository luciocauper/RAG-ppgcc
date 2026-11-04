"""Avaliação Ragas 0.2.15 incremental, limitada por RPM e retomável."""
import argparse
import csv
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import json
import math
import os
from pathlib import Path
import re
import statistics
import time

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")
METRICAS = (
    "faithfulness",
    "factual_correctness",
    "llm_context_precision_with_reference",
)
CAMPOS_CSV = (
    "caso_id", "rodada", "metrica", "status", "valor", "tipo_erro",
    "mensagem", "modelo_configurado", "versao_ragas", "atualizado_em",
)


def _agora():
    return datetime.now(timezone.utc).isoformat()


def carregar_amostras(caminho_resultados, caminho_casos=None, caso_id=None, limite=None):
    caminho_casos = Path(caminho_casos or RAIZ / "datasets/casos_teste.json")
    dados = json.loads(caminho_casos.read_text(encoding="utf-8"))
    casos = {c["id"]: c for c in dados["casos"]}
    amostras, excluidas = [], {}
    with Path(caminho_resultados).open(encoding="utf-8") as arquivo:
        for linha_num, linha in enumerate(arquivo, 1):
            if not linha.strip():
                continue
            resposta = json.loads(linha)
            cid = resposta.get("caso_id", "")
            caso = casos.get(cid)
            motivo = None
            if caso is None or "ragas" not in caso.get("avaliacao", []):
                motivo = "caso_nao_elegivel"
            elif not isinstance(resposta.get("contextos"), list) or not resposta["contextos"]:
                motivo = "sem_contextos"
            elif not caso.get("resposta_referencia"):
                motivo = "sem_referencia"
            elif caso_id and cid != caso_id:
                continue
            if motivo:
                excluidas[motivo] = excluidas.get(motivo, 0) + 1
                continue
            resposta["_linha"] = linha_num
            amostras.append((resposta, caso))
    if limite is not None:
        if limite < 1:
            raise ValueError("O limite de amostras deve ser positivo.")
        amostras = amostras[:limite]
    return amostras, excluidas


def criar_llm_juiz(rpm=None, modelo=None):
    from langchain_core.rate_limiters import InMemoryRateLimiter
    from langchain_openai import ChatOpenAI
    from ragas.llms import LangchainLLMWrapper

    rpm = int(os.getenv("RAGAS_RPM", "5")) if rpm is None else rpm
    if rpm < 1:
        raise ValueError("RAGAS_RPM deve ser positivo.")
    rate_limiter = InMemoryRateLimiter(
        requests_per_second=rpm / 60,
        check_every_n_seconds=0.1,
        max_bucket_size=1,
    )
    model = modelo or os.getenv("RAGAS_LLM_MODEL", "gemini-3.5-flash")
    return LangchainLLMWrapper(ChatOpenAI(
        model=model,
        base_url=os.getenv("RAGAS_LLM_BASE_URL") or None,
        api_key=os.getenv("RAGAS_LLM_API_KEY") or None,
        temperature=0,
        max_retries=0,
        rate_limiter=rate_limiter,
    )), model


def retry_after_segundos(erro, rpm):
    response = getattr(erro, "response", None)
    headers = getattr(response, "headers", {}) or {}
    milliseconds = headers.get("retry-after-ms")
    if milliseconds:
        try:
            return max(0.0, float(milliseconds) / 1000)
        except ValueError:
            pass
    valor = headers.get("retry-after")
    if valor:
        try:
            return max(0.0, float(valor))
        except ValueError:
            try:
                return max(0.0, (parsedate_to_datetime(valor) - datetime.now(timezone.utc)).total_seconds())
            except (TypeError, ValueError, OverflowError):
                pass
    return 60 / rpm


def classificar_erro(erro):
    response = getattr(erro, "response", None)
    status = getattr(response, "status_code", None)
    texto = str(erro).lower()
    if status == 429 or any(x in texto for x in ("rate limit", "resource_exhausted", "quota exceeded")):
        return "quota"
    if status is not None or any(x in texto for x in ("api connection", "connection error", "timeout")):
        return "api"
    return "processamento"


def mensagem_segura(erro):
    mensagem = str(erro)
    chave = os.getenv("RAGAS_LLM_API_KEY")
    if chave:
        mensagem = mensagem.replace(chave, "<redacted>")
    return re.sub(r"(?i)(api[_ -]?key|authorization)\s*[:=]\s*\S+", r"\1=<redacted>", mensagem)[:1000]


def _carregar_csv(caminho):
    if not caminho.exists():
        return {}
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        return {(r["caso_id"], str(r["rodada"]), r["metrica"]): r for r in csv.DictReader(arquivo)}


def _salvar_progresso(caminho_csv, caminho_status, linhas, status):
    caminho_csv.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho_csv.with_suffix(caminho_csv.suffix + ".tmp")
    with temporario.open("w", encoding="utf-8-sig", newline="") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV)
        writer.writeheader()
        writer.writerows(sorted(linhas.values(), key=lambda r: (r["caso_id"], str(r["rodada"]), r["metrica"])))
    temporario.replace(caminho_csv)
    status["atualizado_em"] = _agora()
    status_temp = caminho_status.with_suffix(caminho_status.suffix + ".tmp")
    status_temp.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    status_temp.replace(caminho_status)


def _resumo_metricas(registros):
    resumo = {}
    for metrica in METRICAS:
        correspondentes = [r for r in registros if r.get("metrica") == metrica]
        validos = [float(r["valor"]) for r in correspondentes
                   if r.get("status") == "calculada" and r.get("valor") not in (None, "")]
        resumo[metrica] = {
            "validos": len(validos),
            "falhas": sum(r.get("status") in ("erro_cota", "erro_api", "erro_processamento")
                          for r in correspondentes),
            "ausentes": sum(r.get("status") == "ausente" for r in correspondentes),
            "media": round(statistics.mean(validos), 6) if validos else None,
        }
    return resumo


def _atualizar_contagens(status, linhas, chaves):
    atuais = [linhas[chave] for chave in chaves if chave in linhas]
    status["avaliacoes_concluidas"] = sum(r.get("status") != "em_andamento" for r in atuais)
    status["falhas"] = sum(r.get("status") in ("erro_cota", "erro_api", "erro_processamento") for r in atuais)
    status["ausentes"] = sum(r.get("status") == "ausente" for r in atuais)
    status["validas"] = sum(r.get("status") == "calculada" and r.get("valor") not in (None, "") for r in atuais)
    status["por_metrica"] = _resumo_metricas(atuais)


def _executar_metrica(amostra, caso, nome_metrica, llm, run_config):
    from ragas import EvaluationDataset, evaluate
    from ragas.dataset_schema import SingleTurnSample
    from ragas.metrics import FactualCorrectness, Faithfulness, LLMContextPrecisionWithReference

    metricas = {
        "faithfulness": Faithfulness,
        "factual_correctness": FactualCorrectness,
        "llm_context_precision_with_reference": LLMContextPrecisionWithReference,
    }
    sample = SingleTurnSample(
        user_input=amostra["pergunta"],
        response=amostra["resposta"],
        retrieved_contexts=amostra["contextos"],
        reference=caso["resposta_referencia"],
    )
    result = evaluate(
        dataset=EvaluationDataset(samples=[sample]),
        metrics=[metricas[nome_metrica]()],
        llm=llm,
        run_config=run_config,
        raise_exceptions=True,
        show_progress=False,
    )
    valor = result.scores[0].get(nome_metrica)
    if valor is None or not math.isfinite(float(valor)):
        return None
    return float(valor)


def avaliar(caminho_resultados, saida, caso_id=None, limite=None, retomar=True,
            rpm=None, evaluate_metric=None, dormir=time.sleep):
    from importlib.metadata import version
    from ragas import RunConfig

    caminho_resultados, saida = Path(caminho_resultados), Path(saida)
    caminho_status = saida.parent / "status_avaliacao.json"
    rpm = int(os.getenv("RAGAS_RPM", "5")) if rpm is None else rpm
    modelo_configurado = os.getenv("RAGAS_LLM_MODEL", "gemini-3.5-flash")
    amostras, excluidas = carregar_amostras(caminho_resultados, caso_id=caso_id, limite=limite)
    try:
        versao_ragas = version("ragas")
    except Exception:
        versao_ragas = "desconhecida"

    if not retomar and (saida.exists() or caminho_status.exists()):
        raise FileExistsError("A avaliação existente será preservada; escolha outro caminho de saída ou retome-a.")
    linhas = _carregar_csv(saida) if retomar else {}
    anterior = {}
    if retomar and caminho_status.exists():
        anterior = json.loads(caminho_status.read_text(encoding="utf-8"))
        if (anterior.get("modelo_configurado") != modelo_configurado
                or anterior.get("versao_ragas") != versao_ragas
                or anterior.get("metricas") != list(METRICAS)):
            raise ValueError("Modelo, versão ou métricas diferem do progresso salvo; use --sem-retomada ou outro caminho.")

    total = len(amostras) * len(METRICAS)
    status = {
        "modelo_configurado": modelo_configurado,
        "versao_ragas": versao_ragas,
        "metricas": list(METRICAS),
        "rpm_configurado": rpm,
        "amostras_elegiveis": len(amostras),
        "casos_elegiveis": sorted({r["caso_id"] for r, _ in amostras}),
        "amostras_excluidas": excluidas,
        "avaliacoes_planejadas": total,
        "retomada": bool(retomar and linhas),
        "inicio_em": anterior.get("inicio_em", _agora()),
        "atualizado_em": _agora(),
        "concluido_em": None,
        "validas": 0,
        "falhas": 0,
        "ausentes": 0,
        "estado": "em_andamento" if total else "sem_amostras_elegiveis",
    }
    _salvar_progresso(saida, caminho_status, linhas, status)
    if not amostras:
        return status

    llm = None
    if evaluate_metric is None:
        try:
            llm, modelo_configurado = criar_llm_juiz(rpm=rpm, modelo=modelo_configurado)
            status["modelo_configurado"] = modelo_configurado
            run_config = RunConfig(
                max_workers=1,
                max_retries=1,
                max_wait=1,
                timeout=300,
                exception_types=(),
            )
            evaluate_metric = lambda resposta, caso, metrica: _executar_metrica(
                resposta, caso, metrica, llm, run_config
            )
        except Exception as erro:
            status["estado"] = "erro_configuracao"
            status["falhas"] = total
            status["erro_configuracao"] = mensagem_segura(erro)
            status["concluido_em"] = _agora()
            _salvar_progresso(saida, caminho_status, linhas, status)
            return status

    avaliacao_num = 0
    chaves_selecionadas = []
    for resposta, caso in amostras:
        rodada = str(resposta.get("rodada", 1))
        for metrica in METRICAS:
            avaliacao_num += 1
            chave = (resposta["caso_id"], rodada, metrica)
            chaves_selecionadas.append(chave)
            existente = linhas.get(chave, {})
            if existente.get("status") == "calculada" and existente.get("valor") not in (None, ""):
                _atualizar_contagens(status, linhas, chaves_selecionadas)
                _salvar_progresso(saida, caminho_status, linhas, status)
                continue
            registro = {
                "caso_id": resposta["caso_id"], "rodada": rodada, "metrica": metrica,
                "status": "em_andamento", "valor": "", "tipo_erro": "", "mensagem": "",
                "modelo_configurado": modelo_configurado, "versao_ragas": versao_ragas,
                "atualizado_em": _agora(),
            }
            espera_cota = None
            try:
                valor = evaluate_metric(resposta, caso, metrica)
                if valor is None or not math.isfinite(float(valor)):
                    registro["status"] = "ausente"
                    status["ausentes"] += 1
                else:
                    registro["status"] = "calculada"
                    registro["valor"] = f"{float(valor):.8f}"
                    status["validas"] += 1
            except Exception as erro:
                registro["tipo_erro"] = classificar_erro(erro)
                registro["mensagem"] = mensagem_segura(erro)
                registro["status"] = "erro_cota" if registro["tipo_erro"] == "quota" else (
                    "erro_api" if registro["tipo_erro"] == "api" else "erro_processamento"
                )
                if registro["tipo_erro"] == "quota":
                    espera_cota = retry_after_segundos(erro, rpm)
                status["falhas"] += 1
            registro["atualizado_em"] = _agora()
            linhas[chave] = registro
            status["estado"] = "em_andamento"
            _atualizar_contagens(status, linhas, chaves_selecionadas)
            _salvar_progresso(saida, caminho_status, linhas, status)
            print(f"Ragas {avaliacao_num}/{total}: {resposta['caso_id']} · {metrica} · {registro['status']}")
            if espera_cota is not None and avaliacao_num < total:
                dormir(espera_cota)

    _atualizar_contagens(status, linhas, chaves_selecionadas)
    status["estado"] = "concluida" if status["validas"] == total else "parcial"
    status["concluido_em"] = _agora()
    _salvar_progresso(saida, caminho_status, linhas, status)
    return status


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resultados", type=Path, default=RAIZ / os.getenv("RESULTADOS_JSONL", "results/respostas.jsonl"))
    parser.add_argument("--saida", type=Path, default=RAIZ / "results/metricas_ragas.csv")
    parser.add_argument("--caso-id")
    parser.add_argument("--limite", type=int)
    parser.add_argument("--rpm", type=int, default=int(os.getenv("RAGAS_RPM", "5")))
    parser.add_argument("--sem-retomada", action="store_true")
    args = parser.parse_args(argv)
    status = avaliar(args.resultados, args.saida, args.caso_id, args.limite,
                     not args.sem_retomada, args.rpm)
    print(f"Ragas: {status['estado']} · válidas={status['validas']} · falhas={status['falhas']} · "
          f"ausentes={status['ausentes']} · status={args.saida.parent / 'status_avaliacao.json'}")
    return 0 if status["estado"] in ("concluida", "sem_amostras_elegiveis") else 2


if __name__ == "__main__":
    raise SystemExit(main())
