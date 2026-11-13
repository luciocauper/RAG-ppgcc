"""Fatos de auditoria derivados exclusivamente das evidências locais (sem chamadas à API).

Consumido pelo relatório revisado e pela apresentação revisada para que ambos usem os mesmos
números. Nada aqui altera arquivos de results/execN.
"""
import csv
from collections import Counter
import json
import math
from pathlib import Path
import re
import statistics

import consolidar
from consolidar import descobrir_execucoes, ler_execucao, resumo

METRICAS = ("faithfulness", "factual_correctness", "llm_context_precision_with_reference")
ROTULO_METRICA = {
    "faithfulness": "Faithfulness",
    "factual_correctness": "Factual Correctness",
    "llm_context_precision_with_reference": "LLM Context Precision With Reference",
}
CATEGORIAS = ("factual", "alucinacao", "robustez", "seguranca", "conversa", "desempenho")
ROTULO_CATEGORIA = {
    "factual": "Factualidade", "alucinacao": "Alucinação", "robustez": "Robustez",
    "seguranca": "Segurança", "conversa": "Conversa", "desempenho": "Desempenho",
}
QUESTOES = (
    ("QP1", "Qualidade das respostas",
     "Em que medida o chatbot fornece respostas factualmente adequadas e evita alucinações?",
     ("factual", "alucinacao")),
    ("QP2", "Robustez e segurança",
     "Como o chatbot responde a variações de entrada, situações adversariais e tentativas de manipulação?",
     ("robustez", "seguranca")),
    ("QP3", "Contexto conversacional",
     "Em que medida o chatbot preserva e utiliza o contexto em interações com múltiplos turnos?",
     ("conversa",)),
)
# Procedência documentada de cada execução (protocolo, metadata.json e estrutura das pastas).
PROCEDENCIA = {
    1: "Suítes executadas uma a uma e unidas com rebot (pouca memória no host); inclui smoke.",
    2: "scripts/executar.sh 2; suítes unidas com rebot; inclui smoke.",
    3: "scripts/executar.sh 3; suítes unidas com rebot; inclui smoke.",
    4: "robot --exclude smoke em ambiente de outro integrante; ordem diferente das suítes.",
    5: "Padrão de scripts/executar_windows.ps1 -Modo completo: smoke Robot em exec5/smoke e "
       "suíte sem smoke; sem metadata.json nem relatório individual.",
    6: "scripts/executar.py, ciclo completo: smoke (smoke_test.py), pytest, Robot sem smoke, "
       "Ragas e relatórios; metadata.json registra cada etapa.",
}


def carregar():
    return [ler_execucao(n) for n in descobrir_execucoes()]


def _finito(valor):
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    return numero if math.isfinite(numero) else None


def ragas_execucao(pasta):
    """Resumo Ragas de uma execução, distinguindo avaliação formal, piloto e ausência.

    Valores ausentes ou com erro nunca são convertidos em zero.
    """
    pasta = Path(pasta)
    status_path = pasta / "ragas" / "status_avaliacao.json"
    csv_formal = pasta / "ragas" / "metricas_ragas.csv"
    csv_piloto = pasta / "ragas" / "metricas_piloto.csv"
    vazio = {m: {"validos": 0, "valores": [], "media": None, "falhas": 0, "ausentes": 0} for m in METRICAS}
    if status_path.exists() and csv_formal.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        with csv_formal.open(encoding="utf-8-sig", newline="") as arquivo:
            linhas = list(csv.DictReader(arquivo))
        por_metrica = {m: dict(v, valores=[], casos=[]) for m, v in vazio.items()}
        for linha in linhas:
            dados = por_metrica[linha["metrica"]]
            valor = _finito(linha.get("valor"))
            if linha["status"] == "calculada" and valor is not None:
                dados["valores"].append(valor)
                dados["casos"].append(linha["caso_id"])
            elif linha["status"] == "ausente":
                dados["ausentes"] += 1
            elif linha["status"].startswith("erro_"):
                dados["falhas"] += 1
        for dados in por_metrica.values():
            dados["validos"] = len(dados["valores"])
            dados["media"] = statistics.mean(dados["valores"]) if dados["valores"] else None
        modelos_reportados = Counter(
            m.group(1) for linha in linhas
            if (m := re.search(r"model: ([\w.\-]+)", linha.get("mensagem", ""))))
        limites = Counter(
            m.group(1) for linha in linhas
            if (m := re.search(r"limit: (\d+)", linha.get("mensagem", ""))))
        return {
            "tipo": "formal",
            "estado": status.get("estado"),
            "modelo": status.get("modelo_configurado"),
            "versao": status.get("versao_ragas"),
            "rpm": status.get("rpm_configurado"),
            "amostras": status.get("amostras_elegiveis", 0),
            "casos": status.get("casos_elegiveis", []),
            "excluidas": status.get("amostras_excluidas", {}),
            "planejadas": status.get("avaliacoes_planejadas", 0),
            "validas": sum(d["validos"] for d in por_metrica.values()),
            "falhas": sum(d["falhas"] for d in por_metrica.values()),
            "ausentes": sum(d["ausentes"] for d in por_metrica.values()),
            "erros": Counter(linha["status"] for linha in linhas if linha["status"].startswith("erro_")),
            "retomada": status.get("retomada"),
            "inicio": status.get("inicio_em"),
            "fim": status.get("concluido_em"),
            "modelos_reportados": dict(modelos_reportados),
            "limites_reportados": dict(limites),
            "por_metrica": por_metrica,
        }
    if csv_piloto.exists():
        with csv_piloto.open(encoding="utf-8-sig", newline="") as arquivo:
            linhas = list(csv.DictReader(arquivo))
        colunas = {"faithfulness": "faithfulness",
                   "factual_correctness": "factual_correctness(mode=f1)",
                   "llm_context_precision_with_reference": "llm_context_precision_with_reference"}
        por_metrica = {m: dict(v, valores=[], casos=[]) for m, v in vazio.items()}
        for linha in linhas:
            for metrica, coluna in colunas.items():
                valor = _finito(linha.get(coluna))
                if valor is None:
                    por_metrica[metrica]["ausentes"] += 1
                else:
                    por_metrica[metrica]["valores"].append(valor)
                    por_metrica[metrica]["casos"].append(linha["caso_id"])
        for dados in por_metrica.values():
            dados["validos"] = len(dados["valores"])
            dados["media"] = statistics.mean(dados["valores"]) if dados["valores"] else None
        return {
            "tipo": "piloto", "estado": "piloto exploratório", "modelo": "não registrado",
            "versao": "não registrada", "rpm": None, "amostras": len(linhas),
            "casos": [linha["caso_id"] for linha in linhas], "excluidas": {},
            "planejadas": len(linhas) * len(METRICAS),
            "validas": sum(d["validos"] for d in por_metrica.values()), "falhas": 0,
            "ausentes": sum(d["ausentes"] for d in por_metrica.values()), "erros": Counter(),
            "retomada": None, "inicio": None, "fim": None, "modelos_reportados": {},
            "limites_reportados": {}, "por_metrica": por_metrica,
        }
    return {"tipo": "nao_avaliada", "estado": "não avaliada", "amostras": 0, "planejadas": 0,
            "validas": 0, "falhas": 0, "ausentes": 0, "erros": Counter(), "por_metrica": vazio,
            "casos": [], "excluidas": {}, "modelo": None, "versao": None, "rpm": None,
            "modelos_reportados": {}, "limites_reportados": {}}


def linha_historica(e):
    exp = [t for t in e["testes"] if t["experimental"]]
    aux = [t for t in e["testes"] if not t["experimental"]]
    lat = [r["latencia_s"] for r in e["respostas"] if isinstance(r.get("latencia_s"), (int, float))]
    r_exp, r_aux = resumo(exp), resumo(aux)
    return {
        "numero": e["numero"],
        "data": e["gerado"][:10],
        "gerador": e["gerador"],
        "exp_total": r_exp[0], "exp_pass": r_exp[1], "exp_fail": r_exp[2], "exp_skip": r_exp[3],
        "exp_taxa": 100 * r_exp[1] / r_exp[0] if r_exp[0] else None,
        "aux_total": r_aux[0], "aux_pass": r_aux[1],
        "registros": len(e["respostas"]),
        "lat_media": statistics.mean(lat) if lat else None,
        "lat_mediana": statistics.median(lat) if lat else None,
        "lat_max": max(lat) if lat else None,
        "retentativas": sum(r.get("tentativas", 1) > 1 for r in e["respostas"]),
        "contextos": Counter(len(r.get("contextos", [])) for r in e["respostas"]),
        "falhas": [t["id"] for t in e["testes"] if t["experimental"] and t["status"] == "FAIL"],
        "ragas": ragas_execucao(e["pasta"]),
        "procedencia": PROCEDENCIA.get(e["numero"], "Sem procedência documentada."),
        "artefatos": artefatos(e["pasta"]),
    }


def artefatos(pasta):
    pasta = Path(pasta)
    itens = {
        "output.xml": (pasta / "output.xml").exists(),
        "log/report.html": (pasta / "log.html").exists() and (pasta / "report.html").exists(),
        "respostas.jsonl": (pasta / "respostas.jsonl").exists(),
        "XMLs parciais": (pasta / "parciais").is_dir(),
        "smoke": (pasta / "smoke").is_dir(),
        "pytest": (pasta / "unit").is_dir(),
        "metadata.json": (pasta / "metadata.json").exists(),
        "Ragas": (pasta / "ragas").is_dir(),
        "Word individual": any(pasta.glob("Relatorio_Execucao_*.docx")),
    }
    return itens


def por_categoria(e, categoria):
    ts = [t for t in e["testes"] if t["categoria"] == categoria]
    return sum(t["status"] == "PASS" for t in ts), len(ts)


def status_caso(e, caso):
    return next((t["status"] for t in e["testes"] if t["id"] == caso), "—")


def falhas_caso(es, caso):
    return [e["numero"] for e in es if status_caso(e, caso) == "FAIL"]


def agregado_qp(es, categorias):
    aprovados = sum(por_categoria(e, c)[0] for e in es for c in categorias)
    total = sum(por_categoria(e, c)[1] for e in es for c in categorias)
    return aprovados, total


def casos_da_categoria(e, categorias):
    return sorted({t["id"] for t in e["testes"] if t["categoria"] in categorias})


def _registros(e, caso):
    return [r for r in e["respostas"] if r.get("caso_id") == caso]


def _contem(contextos, trecho):
    return any(trecho in c for c in contextos)


def _numero_creditos(resposta):
    m = re.search(r"(\d+)\s*\([a-zà-ú ]+\)\**\s*cr[ée]ditos", resposta.lower())
    return int(m.group(1)) if m else None


def analise_recorrentes(es):
    """Evidência observável dos casos CT09, CT28 e CT30 em cada execução."""
    saida = {"CT09": [], "CT28": [], "CT30": []}
    for e in es:
        r09 = _registros(e, "CT09")
        if r09:
            ctx = r09[0].get("contextos", [])
            resp = r09[0].get("resposta", "")
            saida["CT09"].append({
                "exec": e["numero"], "status": status_caso(e, "CT09"),
                "ctx_art35": _contem(ctx, "36º"), "ctx_art39d": _contem(ctx, "30º"),
                "resp_36": "36" in resp, "resp_30": bool(re.search(r"\b30\b|trig[ée]simo\)", resp)),
                "n_ctx": len(ctx), "resposta": resp,
            })
        r28 = _registros(e, "CT28")
        if len(r28) >= 2:
            t1, t2 = r28[0], r28[1]
            numero = _numero_creditos(t2.get("resposta", ""))
            if status_caso(e, "CT28") == "PASS":
                classe = "Falso positivo (total incorreto aceito)" if numero not in (None, 24) else "Aprovado"
            elif numero not in (None, 24):
                classe = "Erro factual sem suporte nos trechos"
            else:
                classe = "Declara ausência da informação"
            saida["CT28"].append({
                "exec": e["numero"], "status": status_caso(e, "CT28"),
                "t1_ctx_24": _contem(t1.get("contextos", []), "24 (vinte e quatro) cr"),
                "t2_ctx_24": _contem(t2.get("contextos", []), "24 (vinte e quatro) cr"),
                "t2_numero": numero, "classe": classe, "turnos_registrados": len(r28),
                "mesma_conversa": len({r.get("conversation_id") for r in r28}) == 1,
                "resposta_t2": t2.get("resposta", ""),
            })
        r30 = _registros(e, "CT30")
        if len(r30) >= 2:
            t1, t2 = r30[0], r30[1]
            saida["CT30"].append({
                "exec": e["numero"], "status": status_caso(e, "CT30"),
                "t1_ctx_doutorado": any(re.search(r"50 \(cinquenta\)\s+minutos", c)
                                        for c in t1.get("contextos", [])),
                "t2_ctx_minutos": _contem(t2.get("contextos", []), "minutos"),
                "mesma_conversa": t1.get("conversation_id") == t2.get("conversation_id"),
                "resposta_t2": t2.get("resposta", ""),
            })
    return saida


def oraculo_casos_limite(es):
    """Casos em que aprovação automatizada e correção factual divergem ou exigem leitura humana."""
    itens = []
    for e in es:
        for t in e["testes"]:
            cid, st = t["id"], t["status"]
            if cid == "CT28" and st == "PASS":
                resp = " ".join(r.get("resposta", "") for r in _registros(e, cid))
                if "32 (trinta e dois)" in resp:
                    itens.append((cid, e["numero"], st, "Falso positivo",
                                  "Total de 32 créditos aceito porque o termo 24 aparece na decomposição."))
            if cid == "CT21" and st == "FAIL":
                itens.append((cid, e["numero"], st, "Falso negativo",
                              "Recusa adequada ('não possuo essa informação') fora dos padrões de ausência."))
            if cid == "CT18" and st == "FAIL" and "Similaridade" in t["mensagem"]:
                valor = re.search(r"(\d\.\d+)", t["mensagem"])
                itens.append((cid, e["numero"], st, "Limitação do critério lexical",
                              f"Similaridade {valor.group(1).replace('.', ',') if valor else '?'} < 0,5, com o limite de 8 "
                              "orientandos mantido nas repetições."))
            if cid == "CT22" and st == "FAIL":
                itens.append((cid, e["numero"], st, "Omissão (critério correto)",
                              "Reconhece que as linhas não são nomeadas, mas omite a área de concentração exigida."))
    return itens


def fmt_pct(valor, casas=1):
    return "—" if valor is None else f"{valor:.{casas}f}".replace(".", ",") + "%"


def fmt_num(valor, casas=2):
    return "—" if valor is None else f"{valor:.{casas}f}".replace(".", ",")


def faixas(numeros):
    numeros = sorted(numeros)
    grupos = []
    for n in numeros:
        if grupos and n == grupos[-1][-1] + 1:
            grupos[-1].append(n)
        else:
            grupos.append([n])
    partes = [f"exec{g[0]}" if len(g) == 1 else f"exec{g[0]}–{g[-1]}" for g in grupos]
    if not partes:
        return "nenhuma execução"
    return partes[0] if len(partes) == 1 else ", ".join(partes[:-1]) + " e " + partes[-1]


__all__ = [n for n in dir() if not n.startswith("_")] + ["consolidar"]
