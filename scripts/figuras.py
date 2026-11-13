"""Figuras do relatório revisado (Pillow), geradas a partir das evidências locais.

Saída: docs/figuras/*.png. Diagramas descrevem apenas componentes verificáveis no repositório.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import auditoria as a

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "docs" / "figuras"
INK, MUTED, LINE, PAPER = "#172A32", "#5E6D72", "#C9C3B8", "#FFFFFF"
CORAL, TEAL, MUSTARD, BLUE, GREY = "#C8553F", "#2F7F76", "#C99A2E", "#4F7489", "#B9B3A8"
FONTES = Path("C:/Windows/Fonts")


def _fonte(tamanho, negrito=False):
    nome = "arialbd.ttf" if negrito else "arial.ttf"
    caminho = FONTES / nome
    return ImageFont.truetype(str(caminho), tamanho) if caminho.exists() else ImageFont.load_default(size=tamanho)


def _caixa(d, xy, titulo, linhas=(), cor=TEAL, fundo="#F4F1EA"):
    x0, y0, x1, y1 = xy
    d.rounded_rectangle(xy, 14, fill=fundo, outline=cor, width=3)
    d.rectangle((x0, y0 + 10, x0 + 8, y1 - 10), fill=cor)
    d.text((x0 + 22, y0 + 14), titulo, fill=INK, font=_fonte(24, True))
    for i, linha in enumerate(linhas):
        d.text((x0 + 22, y0 + 50 + i * 28), linha, fill=MUTED, font=_fonte(20))


def _seta(d, p0, p1, cor=INK, rotulo=None):
    d.line((p0, p1), fill=cor, width=3)
    (x0, y0), (x1, y1) = p0, p1
    if abs(x1 - x0) >= abs(y1 - y0):
        s = 1 if x1 > x0 else -1
        d.polygon([(x1, y1), (x1 - 14 * s, y1 - 8), (x1 - 14 * s, y1 + 8)], fill=cor)
    else:
        s = 1 if y1 > y0 else -1
        d.polygon([(x1, y1), (x1 - 8, y1 - 14 * s), (x1 + 8, y1 - 14 * s)], fill=cor)
    if rotulo:
        d.text(((x0 + x1) / 2 + 8, (y0 + y1) / 2 - 26), rotulo, fill=MUTED, font=_fonte(18))


def arquitetura(caminho):
    img = Image.new("RGB", (2000, 1180), PAPER)
    d = ImageDraw.Draw(img)
    d.text((40, 24), "Arquitetura verificável: sistema sob teste × infraestrutura de avaliação",
           fill=INK, font=_fonte(34, True))
    # Host
    d.rounded_rectangle((30, 90, 1180, 1150), 18, outline=LINE, width=3)
    d.text((50, 102), "Windows 11 (host)", fill=MUTED, font=_fonte(22, True))
    d.rounded_rectangle((60, 150, 1150, 760), 18, outline=BLUE, width=3)
    d.text((80, 162), "WSL 2 · Ubuntu 22.04 · Docker Engine + Docker Compose", fill=BLUE, font=_fonte(22, True))
    _caixa(d, (100, 210, 560, 400), "Dify Community 1.18.0",
           ["Chatbot (app) + prompt v1.0", "api · worker · web · nginx", "15 serviços (metadata exec6)"], BLUE)
    _caixa(d, (640, 210, 1110, 400), "Base de conhecimento",
           ["Regimento PPGCC/UECE (PDF)", "47 chunks · High Quality", "Pesquisa Vetorial · Top K 3"], BLUE)
    _caixa(d, (100, 480, 1110, 720), "API HTTP do Dify  (/v1/chat-messages, /v1/parameters)",
           ["Resposta em modo blocking: answer, conversation_id, retriever_resources (trechos + score)",
            "Requer 'Citations and Attributions' habilitado para devolver os trechos",
            "Erros do provedor repassados pelo plugin Gemini (ex.: HTTP 400 com 429 no texto)"], BLUE)
    _seta(d, (560, 305), (640, 305))
    _seta(d, (600, 400), (600, 480))
    # Infra de testes
    d.rounded_rectangle((60, 790, 1150, 1130), 18, outline=CORAL, width=3)
    d.text((80, 802), "Infraestrutura de avaliação (Python 3.11 · .venv)", fill=CORAL, font=_fonte(22, True))
    _caixa(d, (100, 850, 400, 1100), "Robot Framework",
           ["7 suítes BDD", "dify_keywords.robot", "DifyClient", "RagEvaluator"], CORAL)
    _caixa(d, (420, 850, 690, 1100), "Pytest", ["65 testes unitários", "sem chamadas", "à API"], MUSTARD)
    _caixa(d, (710, 850, 1110, 1100), "Ragas 0.2.15 (pós-execução)",
           ["avaliar_ragas.py", "LLM juiz via endpoint", "compatível OpenAI", "CSV + status + retomada"], TEAL)
    _seta(d, (250, 850), (250, 720), CORAL, "HTTP")
    # Externo
    _caixa(d, (1260, 210, 1960, 470), "Google Gemini API (plano gratuito)",
           ["LLM do chatbot: gemini-3.5-flash-lite", "Embeddings: gemini-embedding-001",
            "Juiz Ragas: gemini-3.5-flash (configurado)", "Limites de requisição por minuto/dia"], MUSTARD)
    _seta(d, (1110, 300), (1260, 300), INK, "HTTPS")
    # Ragas -> Gemini (juiz), por um corredor vertical entre as colunas.
    d.line(((1110, 1060), (1205, 1060), (1205, 420)), fill=TEAL, width=3)
    _seta(d, (1205, 420), (1260, 420), TEAL)
    d.text((1060, 1066), "juiz", fill=TEAL, font=_fonte(18))
    _caixa(d, (1260, 560, 1960, 860), "Evidências por execução (results/execN)",
           ["output.xml · log.html · report.html (Robot)", "respostas.jsonl (pergunta, resposta,",
            "  contextos, latência, tentativas)", "metadata.json · ragas/ · smoke/ · unit/",
            "Relatório Word individual"], INK)
    d.line(((1150, 830), (1235, 830), (1235, 760)), fill=INK, width=3)
    _seta(d, (1235, 760), (1260, 760), INK)
    d.text((1160, 836), "grava", fill=MUTED, font=_fonte(18))
    _caixa(d, (1260, 920, 1960, 1130), "Consolidação (sem API)",
           ["consolidar.py → Word por execução", "auditoria.py → relatório e apresentação",
            "Leitura cruzada XML × HTML × parciais"], GREY)
    _seta(d, (1610, 860), (1610, 920), INK)
    img.save(caminho)


def fluxos(caminho):
    img = Image.new("RGB", (2000, 1240), PAPER)
    d = ImageDraw.Draw(img)
    d.text((40, 24), "Quatro fluxos separados: inferência, testes, avaliação semântica e consolidação",
           fill=INK, font=_fonte(34, True))
    faixas = [
        ("A. Inferência do chatbot", BLUE, ["Pergunta do usuário", "Dify: embedding +\nbusca vetorial (base)", "3 trechos (Top K 3\nda base; app 0,7/0,3\nreordena, teto 4)",
                                            "Gemini flash-lite:\nprompt + trechos\n+ histórico", "Resposta +\ncitações"]),
        ("B. Testes automatizados", CORAL, ["Given: carrega caso\n(casos_teste.json)", "When: DifyClient\nenvia (retry/backoff)",
                                            "Registro JSONL\n(resposta, contextos,\nlatência)", "Then: RagEvaluator\naplica critérios", "PASS/FAIL em\noutput.xml"]),
        ("C. Avaliação semântica", TEAL, ["respostas.jsonl\nda execução", "Filtra casos com\n'ragas' + contexto\n+ referência",
                                          "1 avaliação por\n(caso, métrica)\nlimitada por RPM", "CSV incremental +\nstatus_avaliacao.json", "Retomada pula\nmétricas calculadas"]),
        ("D. Consolidação e documentos", MUSTARD, ["output.xml +\nHTML + parciais", "consolidar.py\nconfere totais",
                                                   "auditoria.py:\nfatos derivados", "Word individual +\nrelatório revisado", "Apresentação\nrevisada"]),
    ]
    for i, (titulo, cor, etapas) in enumerate(faixas):
        y = 100 + i * 285
        d.text((40, y), titulo, fill=cor, font=_fonte(26, True))
        for j, etapa in enumerate(etapas):
            x = 40 + j * 392
            d.rounded_rectangle((x, y + 44, x + 330, y + 240), 14, fill="#F4F1EA", outline=cor, width=3)
            d.multiline_text((x + 18, y + 62), etapa, fill=INK, font=_fonte(22), spacing=6)
            if j < len(etapas) - 1:
                _seta(d, (x + 330, y + 142), (x + 392, y + 142), cor)
    img.save(caminho)


def execucoes(caminho, es):
    linhas = [a.linha_historica(e) for e in es]
    img = Image.new("RGB", (1800, 820), PAPER)
    d = ImageDraw.Draw(img)
    d.text((40, 24), "Cenários experimentais por execução (30 casos CT; testes de API excluídos)",
           fill=INK, font=_fonte(30, True))
    base, topo, x0 = 700, 120, 140
    escala = (base - topo) / 30
    for v in (0, 10, 20, 30):
        y = base - v * escala
        d.line((x0 - 10, y, 1720, y), fill="#E6E1D8", width=2)
        d.text((x0 - 60, y - 12), str(v), fill=MUTED, font=_fonte(20))
    largura = 170
    for i, h in enumerate(linhas):
        x = x0 + 40 + i * 260
        yp = base - h["exp_pass"] * escala
        d.rectangle((x, yp, x + largura, base), fill=TEAL)
        d.rectangle((x, base - 30 * escala, x + largura, yp), fill=CORAL)
        d.text((x + 40, yp + 12), f"{h['exp_pass']}/30", fill="white", font=_fonte(26, True))
        d.text((x + 50, base - 30 * escala - 34), f"{h['exp_fail']} FAIL", fill=CORAL, font=_fonte(20, True))
        d.text((x + 38, base + 14), f"exec{h['numero']}", fill=INK, font=_fonte(24, True))
        d.text((x + 50, base + 46), f"{h['data'][8:10]}/{h['data'][5:7]}", fill=MUTED, font=_fonte(18))
    d.rectangle((1460, 60, 1484, 84), fill=TEAL)
    d.text((1494, 60), "PASS", fill=INK, font=_fonte(20))
    d.rectangle((1580, 60, 1604, 84), fill=CORAL)
    d.text((1614, 60), "FAIL", fill=INK, font=_fonte(20))
    img.save(caminho)


def categorias(caminho, es):
    img = Image.new("RGB", (1800, 640), PAPER)
    d = ImageDraw.Draw(img)
    d.text((40, 24), "Aprovação por categoria e execução (PASS / total da categoria)", fill=INK, font=_fonte(30, True))
    x0, y0, cw, ch = 300, 110, 240, 76
    for j, e in enumerate(es):
        d.text((x0 + j * cw + 80, y0 - 4), f"exec{e['numero']}", fill=INK, font=_fonte(22, True))
    for i, cat in enumerate(a.CATEGORIAS):
        y = y0 + 40 + i * ch
        d.text((40, y + 22), a.ROTULO_CATEGORIA[cat], fill=INK, font=_fonte(24, True))
        for j, e in enumerate(es):
            p, t = a.por_categoria(e, cat)
            frac = p / t if t else 0
            cor = TEAL if frac == 1 else (MUSTARD if frac >= .75 else CORAL)
            x = x0 + j * cw
            d.rounded_rectangle((x + 10, y + 6, x + cw - 10, y + ch - 6), 10, fill=cor)
            d.text((x + 92, y + 22), f"{p}/{t}", fill="white", font=_fonte(26, True))
    d.text((40, 600), "Verde: 100% · Amarelo: ≥ 75% · Coral: < 75%. Aprovação automatizada não equivale a correção factual.",
           fill=MUTED, font=_fonte(20))
    img.save(caminho)


def ragas(caminho, resumo):
    img = Image.new("RGB", (1800, 620), PAPER)
    d = ImageDraw.Draw(img)
    d.text((40, 24), f"Ragas na exec6: {resumo['validas']} valores válidos em {resumo['planejadas']} avaliações planejadas",
           fill=INK, font=_fonte(30, True))
    por = resumo["por_metrica"]
    total = resumo["amostras"]
    x0, largura = 560, 1160
    for i, m in enumerate(a.METRICAS):
        y = 120 + i * 130
        dados = por[m]
        cota_api = dados["falhas"]
        d.text((40, y + 20), a.ROTULO_METRICA[m], fill=INK, font=_fonte(24, True))
        x = x0
        for qtd, cor, rotulo in ((dados["validos"], TEAL, "válida"), (dados["ausentes"], MUSTARD, "ausente"),
                                 (cota_api, CORAL, "erro")):
            w = largura * qtd / total if total else 0
            if w:
                d.rectangle((x, y + 10, x + w, y + 70), fill=cor)
                if w > 60:
                    d.text((x + 10, y + 26), str(qtd), fill="white", font=_fonte(24, True))
            x += w
        d.text((x0, y + 78), f"{dados['validos']} válidas · {dados['ausentes']} ausentes · {cota_api} erros (cota/API) de {total}",
               fill=MUTED, font=_fonte(18))
    erros = resumo["erros"]
    d.text((40, 540), f"Erros: {erros.get('erro_cota', 0)} por cota (HTTP 429) e {erros.get('erro_api', 0)} de API "
                      "(HTTP 503). Valores ausentes ou com erro não são tratados como zero.",
           fill=MUTED, font=_fonte(20))
    img.save(caminho)


def gerar(es=None):
    es = es or a.carregar()
    DESTINO.mkdir(parents=True, exist_ok=True)
    saidas = {
        "arquitetura": DESTINO / "fig1_arquitetura.png",
        "fluxos": DESTINO / "fig2_fluxos.png",
        "execucoes": DESTINO / "fig3_execucoes.png",
        "categorias": DESTINO / "fig4_categorias.png",
        "ragas": DESTINO / "fig5_ragas_exec6.png",
    }
    arquitetura(saidas["arquitetura"])
    fluxos(saidas["fluxos"])
    execucoes(saidas["execucoes"], es)
    categorias(saidas["categorias"], es)
    formal = [a.ragas_execucao(e["pasta"]) for e in es]
    formal = [r for r in formal if r["tipo"] == "formal"]
    if formal:
        ragas(saidas["ragas"], formal[-1])
    else:
        saidas.pop("ragas")
    return saidas


if __name__ == "__main__":
    for nome, caminho in gerar().items():
        print(nome, caminho)
