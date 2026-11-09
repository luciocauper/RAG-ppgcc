"""Relatórios Word individuais derivados das evidências Robot/JSONL, sem chamadas à API.

Uso: python scripts/consolidar.py [1 2 3 4]
Sem argumentos, descobre execuções que contém output.xml. Não altera evidências.
"""
import argparse
import csv
from collections import Counter
import hashlib
from io import BytesIO
import json
import math
import os
from pathlib import Path
import re
import statistics
import sys
import tempfile
import xml.etree.ElementTree as ET

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
CAMPOS_ORACULO = ("termos_obrigatorios", "termos_proibidos",
                  "deve_reconhecer_ausencia", "deve_citar_artigo")
LIMITACOES = (
    "PASS significa aprovação no critério automatizado, não correção semântica integral. "
    "Termos podem aparecer em contexto incorreto; regex de recusa pode rejeitar uma recusa válida. "
    "Similaridade lexical não mede equivalência factual. CT19 verifica status HTTP e não registra "
    "a resposta completa no JSONL; chamadas negativas, smoke e tentativas malsucedidas também não "
    "formam registros completos nesse arquivo. Latência mede a tentativa final, excluindo pausas "
    "e retentativas; não representa tempo total percebido pelo usuário. Turnos posteriores a uma "
    "assertion reprovada podem não ter sido executados. Não há métricas Ragas produzidas nestas evidências. "
    "O dataset e o código atuais são referências de interpretação; os XMLs preservam as assertions "
    "efetivamente executadas, mas não uma cópia integral do código ou da configuração remota."
)


def descobrir_execucoes():
    return sorted(int(p.parent.name[4:]) for p in (RAIZ / "results").glob("exec*/output.xml")
                  if p.parent.name[4:].isdigit())


def ler_execucao(numero):
    """Lê todos os testes, inclusive suítes aninhadas, e confere totais HTML/XML."""
    pasta = RAIZ / "results" / f"exec{numero}"
    raiz = ET.parse(pasta / "output.xml").getroot()
    casos = {c["id"]: c for c in json.loads(
        (RAIZ / "datasets/casos_teste.json").read_text(encoding="utf-8"))["casos"]}
    testes = []
    for suite in raiz.iter("suite"):
        for t in suite.findall("test"):
            status = t.find("status")
            match = re.match(r"^(CT\d{2})\b", t.get("name", ""))
            cid = match.group(1) if match else ""
            api_id = next((a.text.split("=", 1)[1] for a in t.iter("arg")
                           if (a.text or "").startswith("caso_id=API")), "")
            testes.append(dict(id=cid or api_id or t.get("id"), robot_id=t.get("id"),
                               nome=t.get("name"), categoria=casos.get(cid, {}).get("categoria", "infraestrutura"),
                               experimental=bool(cid), status=status.get("status"),
                               mensagem=status.text or "", objetivo=t.findtext("doc", ""),
                               tags=[x.text for x in t.findall("tag")], xml=t))
    if not testes:
        raise ValueError(f"{pasta}: nenhum teste encontrado")
    ids = [t["id"] for t in testes if t["experimental"]]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{pasta}: IDs experimentais duplicados")
    respostas = []
    avisos = []
    arquivo = pasta / "respostas.jsonl"
    if arquivo.exists():
        for linha, texto in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), 1):
            if texto.strip():
                r = json.loads(texto)
                r["_linha"] = linha
                respostas.append(r)
    else:
        avisos.append("respostas.jsonl ausente: respostas recuperáveis somente das mensagens XML.")
    contagem = Counter(t["status"] for t in testes)
    for nome in ("log.html", "report.html"):
        p = pasta / nome
        if not p.exists():
            avisos.append(f"{nome} ausente.")
            continue
        html = p.read_text(encoding="utf-8")
        m = re.search(r'window.output\["stats"\] = (.+);', html)
        if m:
            totais = json.loads(m.group(1))[0][0]
            if any(totais.get(k, 0) != contagem[s] for k, s in
                   (("pass", "PASS"), ("fail", "FAIL"), ("skip", "SKIP"))):
                raise ValueError(f"{p}: totais divergentes do XML")
        else:
            avisos.append(f"{nome}: estatísticas embutidas não reconhecidas; consultar visualmente.")
    for p in pasta.glob("parciais/*.xml"):
        parcial = ET.parse(p)
        for t in parcial.iter("test"):
            equivalente = next((x for x in testes if x["nome"] == t.get("name")), None)
            if equivalente is None or equivalente["status"] != t.find("status").get("status"):
                raise ValueError(f"{p}: parcial diverge do consolidado")
    return dict(numero=numero, pasta=pasta, testes=testes, respostas=respostas, casos=casos,
                gerador=raiz.get("generator", ""), gerado=raiz.get("generated", ""),
                avisos=avisos)


def resumo(testes):
    c = Counter(t["status"] for t in testes)
    return [len(testes), c["PASS"], c["FAIL"], c["SKIP"],
            f'{100 * c["PASS"] / len(testes):.1f}%' if testes else "n/a"]


def categorias(execucao):
    return sorted({t["categoria"] for t in execucao["testes"]})


def registros(execucao, teste):
    return [r for r in execucao["respostas"] if r.get("caso_id") == teste["id"]]


def diagnostico(execucao, teste):
    """Interpretação condicionada ao conteúdo observado; nunca muda o resultado Robot."""
    rs = registros(execucao, teste)
    cid = teste["id"]
    respostas = "\n".join(r.get("resposta", "") for r in rs).lower()
    if not rs:
        return "Resultado inconclusivo", "Não há resposta JSONL vinculada; consultar mensagem e keywords do XML."
    if cid == "CT09" and teste["status"] == "FAIL":
        return ("Falha factual; recuperação inadequada (hipótese)",
                "A resposta omite o prazo de 30 meses e a divergência com 36 meses. "
                "Os trechos registrados devem ser confrontados com Art. 35 e Art. 39, d. "
                "Ausência do dispositivo relevante sugere cobertura insuficiente da recuperação; "
                "não comprova isoladamente a causa interna do Dify.")
    if cid == "CT22" and "computacao cientifica e aplicada" in teste["mensagem"]:
        return ("Limitação do oráculo; resposta incompleta",
                "A resposta reconhece que os nomes das linhas não estão listados, mas omite a área "
                "de concentração exigida pelo dataset. A reprovação é coerente com esse critério de "
                "completude; não demonstra invenção de linhas. Na exec4 o nome da área aparece nos "
                "contextos, sustentando omissão na geração, e há atribuição imprecisa ao Art. 3º.")
    if cid == "CT21" and "não possuo essa informação" in respostas:
        return ("Falso negativo; limitação do oráculo",
                "A recusa é adequada à ausência da taxa no documento. O padrão de ausência não "
                "abrange 'não possuo essa informação'. Mantém-se FAIL histórico.")
    if cid == "CT18" and "Similaridade" in teste["mensagem"]:
        return ("Limitação do oráculo",
                "O critério lexical falhou embora as respostas registradas mantenham o limite de "
                "8 orientandos. Isso é falha do limiar de similaridade, não evidência suficiente "
                "de inconsistência factual. Possível falso negativo se interpretado como correção semântica.")
    if cid == "CT28" and ("32 (trinta e dois)" in respostas or "28 (vinte e oito)" in respostas):
        return ("Falso positivo; falha factual" if teste["status"] == "PASS" else "Falha factual; alucinação",
                "A resposta atribui ao mestrado um total incorreto de créditos (referência: 24). "
                "Na exec1, 32 foi aceito porque 24 aparece na decomposição errada; na exec3 foram "
                "informados 28. A presença lexical não verifica a relação entre número e conceito. "
                "A origem do número incorreto não pode ser atribuída ao conhecimento paramétrico sem rastreio interno.")
    if cid in ("CT28", "CT29", "CT30") and teste["status"] == "FAIL":
        return ("Problema conversacional; recuperação inadequada (hipótese)",
                "O turno de continuação não entrega o dado esperado. Os registros mantém o mesmo "
                "conversation_id, portanto não indicam perda de sessão pelo cliente. Os contextos "
                "do turno problemático omitem o trecho específico que constava no turno anterior. "
                "CT28 deveria informar 24 créditos; CT29, ao menos 1 membro externo no mestrado; "
                "CT30, 40–50 minutos no doutorado. A resposta de CT29 desvia para doutorado. "
                "A evidência sugere recuperação insuficiente em elipse/anáfora; não comprova o mecanismo interno.")
    return "Resultado inconclusivo", "Exige revisão humana do critério, da resposta e dos contextos abaixo."


def documento(titulo, academico=False):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.top_margin = sec.left_margin = Cm(3 if academico else 2)
    sec.bottom_margin = sec.right_margin = Cm(2)
    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size = "Arial", Pt(12 if academico else 11)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.5 if academico else 1.08
    for n in range(1, 4):
        estilo = doc.styles[f"Heading {n}"]
        estilo.font.name = "Arial"
        estilo.font.color.rgb = RGBColor.from_string("234665")
        estilo.font.size = Pt(17 - n)
    sec.header.paragraphs[0].text = "RAG-PPGCC | Teste de Sistemas Inteligentes"
    rodape = sec.footer.paragraphs[0]
    rodape.alignment = 2
    rodape.add_run("Página ")
    campo = OxmlElement("w:fldSimple")
    campo.set(qn("w:instr"), "PAGE")
    rodape._p.append(campo)
    doc.add_heading(titulo, 0)
    return doc


def tabela(doc, cabecalho, linhas):
    t = doc.add_table(rows=1, cols=len(cabecalho))
    t.style = "Light Shading Accent 1"
    for cell, valor in zip(t.rows[0].cells, cabecalho):
        cell.text = str(valor)
    repeat = OxmlElement("w:tblHeader")
    t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for linha in linhas:
        for cell, valor in zip(t.add_row().cells, linha):
            cell.text = str(valor)
    doc.add_paragraph()
    return t


def grafico(doc, titulo, linhas):
    """Barras com Pillow (já usado pelo PowerPoint), sem artefatos auxiliares em disco."""
    imagem = Image.new("RGB", (1400, 140 + 90 * len(linhas)), "white")
    draw = ImageDraw.Draw(imagem)
    fonte_path = Path("C:/Windows/Fonts/arial.ttf")
    fonte = ImageFont.truetype(str(fonte_path), 27) if fonte_path.exists() else ImageFont.load_default(size=27)
    draw.text((20, 15), titulo, fill="#234665", font=fonte)
    maximo = max((sum(valores) for _, valores in linhas), default=1) or 1
    for i, (nome, valores) in enumerate(linhas):
        y, x = 80 + i * 90, 320
        draw.text((20, y), nome, fill="#333333", font=fonte)
        for valor, cor in zip(valores, ("#347C67", "#B34F50", "#999999")):
            largura = int(valor / maximo * 800)
            if largura:
                draw.rectangle((x, y, x + largura, y + 38), fill=cor)
                x += largura
        draw.text((x + 12, y), "/".join(map(str, valores)), fill="#333333", font=fonte)
    draw.text((20, imagem.height - 45), "Ordem: aprovados / reprovados / ignorados | Fonte: output.xml", fill="#333333", font=fonte)
    stream = BytesIO()
    imagem.save(stream, format="PNG")
    stream.seek(0)
    doc.add_picture(stream, width=Cm(16))


def detalhes(doc, e, t, contextos=True):
    caso = e["casos"].get(t["id"], {})
    doc.add_heading(t["nome"], 2)
    classificacao, analise = diagnostico(e, t)
    for rotulo, valor in (
        ("Resultado Robot", t["status"]), ("Objetivo", t["objetivo"] or caso.get("comportamento_esperado")),
        ("Resposta esperada", caso.get("resposta_referencia") or caso.get("comportamento_esperado")),
        ("Referência documental", caso.get("referencia_regimento")),
        ("Mensagem de falha", t["mensagem"] or "Não há falha automatizada."),
        ("Classificação", classificacao), ("Análise técnica e possível causa", analise),
        ("Evidência Robot", f"output.xml: test[@id='{t['robot_id']}']; log.html#{t['robot_id']}"),
    ):
        doc.add_paragraph(f"{rotulo}: {valor or 'Não documentado.'}")
    criterios = {k: caso[k] for k in CAMPOS_ORACULO if k in caso}
    if caso.get("turnos"):
        criterios["turnos"] = caso["turnos"]
    doc.add_paragraph("Critério do dataset atual: " + json.dumps(criterios, ensure_ascii=False))
    keywords = []
    for kw in t["xml"].iter("kw"):
        if kw.get("name", "").startswith(("Validar ", "Should ")):
            st = kw.find("status")
            keywords.append(f"{kw.get('name')} | argumentos: " +
                            "; ".join(x.text or "" for x in kw.findall("arg")) +
                            f" | {st.get('status') if st is not None else 'n/a'} | " +
                            (st.text or "" if st is not None else ""))
    doc.add_paragraph("Assertions efetivamente registradas no XML:\n" + "\n".join(keywords))
    rs = registros(e, t)
    if not rs:
        doc.add_paragraph("Sem registro JSONL. Mensagens XML disponíveis:")
        for msg in t["xml"].iter("msg"):
            if msg.text and ("Resposta" in msg.text or "HTTP " in msg.text):
                doc.add_paragraph(msg.text)
    for i, r in enumerate(rs, 1):
        doc.add_heading(f"Registro {i} — respostas.jsonl, linha {r['_linha']}", 3)
        doc.add_paragraph("Pergunta: " + r.get("pergunta", "Não registrada"))
        doc.add_paragraph("Resposta completa: " + r.get("resposta", "Não registrada"))
        doc.add_paragraph(f"Conversa: {r.get('conversation_id', 'n/a')} | "
                          f"Data: {r.get('timestamp', 'n/a')} | Latência: {r.get('latencia_s', 'n/a')} s")
        if contextos:
            for j, ctx in enumerate(r.get("contextos", []), 1):
                doc.add_paragraph(f"Contexto recuperado {j}:\n{ctx}")
            doc.add_paragraph("Fontes/segmentos: " + json.dumps(r.get("fontes", []), ensure_ascii=False))
    if caso.get("turnos") and len(rs) < len(caso["turnos"]):
        doc.add_paragraph("Há turnos planejados sem registro de resposta; não foram contados como testes independentes.")


def resumo_ragas(pasta):
    pasta = Path(pasta)
    status_path = pasta / "ragas" / "status_avaliacao.json"
    csv_path = pasta / "ragas" / "metricas_ragas.csv"
    legado = pasta / "metricas_ragas.csv"
    if not csv_path.exists() and legado.exists():
        csv_path = legado
    metricas = ("faithfulness", "factual_correctness", "llm_context_precision_with_reference")
    status = json.loads(status_path.read_text(encoding="utf-8")) if status_path.exists() else {}
    por_metrica = status.get("por_metrica", {})
    if csv_path.exists():
        with csv_path.open(encoding="utf-8-sig", newline="") as arquivo:
            linhas = list(csv.DictReader(arquivo))
        if linhas and "metrica" in linhas[0]:
            for nome in metricas:
                valores = [float(r["valor"]) for r in linhas
                           if r.get("metrica") == nome and r.get("status") == "calculada"
                           and r.get("valor") not in (None, "")]
                por_metrica.setdefault(nome, {
                    "validos": len(valores),
                    "falhas": sum(r.get("metrica") == nome and r.get("status", "").startswith("erro_") for r in linhas),
                    "ausentes": sum(r.get("metrica") == nome and r.get("status") == "ausente" for r in linhas),
                    "media": statistics.mean(valores) if valores else None,
                })
        elif linhas:
            for nome in metricas:
                valores = []
                for linha in linhas:
                    try:
                        valor = float(linha.get(nome, ""))
                        if math.isfinite(valor):
                            valores.append(valor)
                    except (TypeError, ValueError):
                        continue
                por_metrica.setdefault(nome, {"validos": len(valores), "falhas": 0,
                                              "ausentes": len(linhas)-len(valores),
                                              "media": statistics.mean(valores) if valores else None})
    if not status and csv_path.exists():
        status = {"estado": "parcial", "modelo_configurado": "metadados indisponíveis",
                  "versao_ragas": "metadados indisponíveis"}
    return {
        "estado": status.get("estado", "não avaliada"),
        "modelo": status.get("modelo_configurado", "não informado"),
        "versao": status.get("versao_ragas", "não informada"),
        "rpm": status.get("rpm_configurado"),
        "amostras_elegiveis": status.get("amostras_elegiveis", 0),
        "por_metrica": por_metrica,
    }


def adicionar_resultados_ragas(doc, execucoes):
    doc.add_heading("Avaliação semântica Ragas", 2)
    nomes = ("faithfulness", "factual_correctness", "llm_context_precision_with_reference")
    linhas = []
    for e in execucoes:
        resultado = resumo_ragas(e["pasta"])
        for nome in nomes:
            metrica = resultado["por_metrica"].get(nome, {})
            validos = metrica.get("validos", 0)
            media = metrica.get("media")
            estado = "não avaliada" if resultado["estado"] == "não avaliada" else (
                "calculada" if validos and media is not None else resultado["estado"]
            )
            linhas.append([e["numero"], nome, estado, validos,
                           f"{media:.3f}" if media is not None and validos else "—",
                           metrica.get("falhas", 0), metrica.get("ausentes", 0)])
    tabela(doc, ["Exec.", "Métrica", "Estado", "N válido", "Média", "Falhas", "Ausentes"], linhas)
    doc.add_paragraph("Médias calculadas somente sobre valores válidos; falhas e ausências não são convertidas em zero. "
                      "Consulte ragas/status_avaliacao.json em cada execução para modelo, versão, cota e metadados.")


def gerar_relatorio(e):
    n = e["numero"]
    doc = documento(f"Relatório de execução {n:02d}")
    doc.add_heading("1. Identificação da execução", 1)
    datas = [r["timestamp"] for r in e["respostas"] if r.get("timestamp")]
    tabela(doc, ["Item", "Evidência"], [
        ["Projeto / SUT", "RAG-PPGCC / assistente Dify Community sobre o regimento PPGCC/UECE"],
        ["Execução", f"exec{n}"],
        ["Geração do XML (sem fuso explícito)", e["gerado"]],
        ["Datas JSONL (fuso explícito)", f"{min(datas)} a {max(datas)}" if datas else "Não disponíveis"],
        ["Ambiente do executor", e["gerador"]],
        ["Dify / LLM", "Protocolo declara Dify 1.18.0 e gemini-3.5-flash-lite; não há snapshot remoto individual que confirme a configuração desta execução."],
        ["Dataset", "datasets/casos_teste.json — 30 casos; Regimento_PPGCC-UECE2021.pdf"],
        ["Configuração declarada", "docs/protocolo_testes.md: Hybrid, Top K 4, embeddings Gemini; JSONL registra contextos retornados, não a configuração completa."],
        ["Responsáveis", "Não identificados formalmente nas evidências da execução."],
    ])
    doc.add_heading("2. Resumo executivo", 1)
    grupos = [("Todos", e["testes"]), ("Experimentais", [t for t in e["testes"] if t["experimental"]]),
              ("Infraestrutura/API", [t for t in e["testes"] if not t["experimental"]])]
    tabela(doc, ["Escopo", "Total", "PASS", "FAIL", "SKIP", "% PASS"],
           [[nome, *resumo(ts)] for nome, ts in grupos])
    doc.add_paragraph("Infraestrutura aprovada confirma as verificações de API; não mede correção das respostas RAG. "
                      "A taxa usa todos os testes do escopo como denominador, incluindo ignorados.")
    doc.add_heading("3. Resultado por categoria", 1)
    linhas = [(cat, [t for t in e["testes"] if t["categoria"] == cat]) for cat in categorias(e)]
    tabela(doc, ["Categoria", "Total", "PASS", "FAIL", "SKIP", "% PASS"],
           [[cat, *resumo(ts)] for cat, ts in linhas])
    doc.add_heading("4. Relação completa dos testes", 1)
    tabela(doc, ["ID", "Cenário", "Categoria", "Resultado", "Motivo"],
           [[t["id"], t["nome"], t["categoria"], t["status"], t["mensagem"]] for t in e["testes"]])
    doc.add_heading("5. Detalhamento das falhas", 1)
    falhas = [t for t in e["testes"] if t["status"] == "FAIL"]
    if not falhas:
        doc.add_paragraph("Nenhuma reprovação registrada.")
    for t in falhas:
        detalhes(doc, e, t)
    doc.add_heading("6. Indicadores e gráficos", 1)
    grafico(doc, "Distribuição por escopo", [(nome, resumo(ts)[1:4]) for nome, ts in grupos])
    grafico(doc, "Resultados por categoria", [(cat, resumo(ts)[1:4]) for cat, ts in linhas])
    lat = [r["latencia_s"] for r in e["respostas"] if isinstance(r.get("latencia_s"), (int, float))]
    tabela(doc, ["Indicador", "Valor"], [
        ["Registros JSONL (não todas as chamadas HTTP)", len(e["respostas"])],
        ["Latência média / mediana / máxima (s)", " / ".join(f"{x:.3f}" for x in
            (statistics.mean(lat), statistics.median(lat), max(lat))) if lat else "Não disponível"],
        ["Registros com retentativa", sum(r.get("tentativas", 1) > 1 for r in e["respostas"])],
    ])
    doc.add_heading("7. Análise e limitações", 1)
    doc.add_paragraph(LIMITACOES)
    doc.add_paragraph("O protocolo registra execução por suíte nas exec1–3, incluindo smoke; a exec4 excluiu "
                      "smoke e alterou a ordem das suítes. O XML informa ambiente de executor próprio por execução. "
                      "Sem controle equivalente de ambiente, carga, modelo, configuração e ordem, variações não "
                      "demonstram melhoria ou regressão. Contextos são evidência observável, não rastreio interno do Dify.")
    for aviso in e["avisos"]:
        doc.add_paragraph(aviso)
    ragas = resumo_ragas(e["pasta"])
    doc.add_heading("Avaliação semântica Ragas", 2)
    if ragas["estado"] == "não avaliada":
        doc.add_paragraph("Ragas não foi executado para esta execução; nenhuma métrica semântica foi calculada.")
    else:
        tabela(doc, ["Métrica", "Estado", "N válido", "Média", "Falhas", "Ausentes"], [
            [nome, ("calculada" if dados.get("validos") and dados.get("media") is not None else ragas["estado"]),
             dados.get("validos", 0),
             f'{dados["media"]:.3f}' if dados.get("media") is not None and dados.get("validos") else "—",
             dados.get("falhas", 0), dados.get("ausentes", 0)]
            for nome, dados in ragas["por_metrica"].items()])
        doc.add_paragraph(f"Modelo configurado: {ragas['modelo']} · Ragas: {ragas['versao']} · RPM: {ragas['rpm']}.")
    for t in e["testes"]:
        if t["id"] == "CT28" and t["status"] == "PASS" and "32 (trinta e dois)" in "\n".join(
                r.get("resposta", "") for r in registros(e, t)):
            doc.add_heading("Aprovação com erro factual identificado", 2)
            detalhes(doc, e, t)
    doc.add_heading("8. Conclusão da execução", 1)
    experimentais = grupos[1][1]
    r = resumo(experimentais)
    doc.add_paragraph(f"Dos {r[0]} cenários experimentais, {r[1]} foram aprovados e {r[2]} reprovados "
                      f"({r[4]} de aprovação automatizada). Os resultados permanecem como registrados. "
                      "A análise das falhas deve distinguir omissão, erro factual, recuperação e limitações "
                      "lexicais antes de inferir qualidade semântica.")
    doc.add_heading("Apêndice — rastreabilidade e respostas completas", 1)
    tabela(doc, ["Arquivo", "SHA-256"], [
        [p.name, hashlib.sha256(p.read_bytes()).hexdigest()]
        for p in (e["pasta"] / x for x in ("output.xml", "log.html", "report.html", "respostas.jsonl"))
        if p.exists()])
    for t in e["testes"]:
        if t["status"] != "FAIL":
            doc.add_heading(t["nome"], 2)
            caso = e["casos"].get(t["id"], {})
            doc.add_paragraph("Oráculo do dataset atual: " + json.dumps(
                {k: caso[k] for k in (*CAMPOS_ORACULO, "turnos", "comportamento_esperado") if k in caso},
                ensure_ascii=False))
            rs = registros(e, t)
            if not rs:
                doc.add_paragraph("Sem resposta JSONL vinculada; consultar keywords e mensagens no XML.")
            for r in rs:
                doc.add_paragraph(f"Linha {r['_linha']} | Pergunta: {r.get('pergunta', '')}")
                doc.add_paragraph("Resposta completa: " + r.get("resposta", ""))
    saida = e["pasta"] / f"Relatorio_Execucao_{n:02d}.docx"
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(dir=saida.parent, prefix=f".{saida.stem}.",
                                         suffix=".tmp.docx", delete=False) as arquivo:
            temporario = Path(arquivo.name)
        doc.save(temporario)
        try:
            os.replace(temporario, saida)
        except PermissionError as erro:
            alternativo = saida.with_name(f"{saida.stem}_novo.docx")
            indice = 2
            while alternativo.exists():
                alternativo = saida.with_name(f"{saida.stem}_novo_{indice}.docx")
                indice += 1
            try:
                os.replace(temporario, alternativo)
            except PermissionError as erro_alternativo:
                raise PermissionError(
                    f"Não foi possível substituir {saida}; o arquivo pode estar aberto "
                    f"em outro programa ou sem permissão. Feche-o no Word/visualizador "
                    f"e tente novamente. Também não foi possível salvar {alternativo}: "
                    f"{erro_alternativo}"
                ) from erro
            print(f"AVISO: {saida} não pôde ser substituído (arquivo bloqueado ou sem permissão). "
                  f"O original foi preservado; nova versão salva em {alternativo}.", file=sys.stderr)
            return alternativo
        return saida
    except PermissionError as erro:
        raise PermissionError(
            f"Sem permissão para gerar o relatório da execução {n:02d} em {saida.parent}. "
            f"Verifique se a pasta está acessível e tente novamente: {erro}"
        ) from erro
    finally:
        if temporario is not None and temporario.exists():
            temporario.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("execucoes", nargs="*", type=int)
    args = parser.parse_args()
    numeros = args.execucoes or descobrir_execucoes()
    if not numeros or any(n < 1 for n in numeros):
        parser.error("Informe execuções positivas com output.xml disponível.")
    falhas = []
    for n in dict.fromkeys(numeros):
        try:
            e = ler_execucao(n)
            print(gerar_relatorio(e))
        except PermissionError as erro:
            falhas.append(n)
            print(f"ERRO: execução {n:02d}: {erro}", file=sys.stderr)
    if falhas:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
