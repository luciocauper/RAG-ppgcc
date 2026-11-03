"""Gera 12 slides e roteiro de 15 minutos usando as evidências oficiais."""
from pathlib import Path
import re

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

from consolidar import descobrir_execucoes, ler_execucao, resumo

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "apresentação" / "Apresentacao_Tecnica_RAG_PPGCC.pptx"
INK = RGBColor.from_string("172A32")
INK_SOFT = RGBColor.from_string("263D46")
PAPER = RGBColor.from_string("F3F0E8")
WHITE = RGBColor.from_string("FFFEFA")
CORAL = RGBColor.from_string("D85F4A")
TEAL = RGBColor.from_string("368D83")
MUSTARD = RGBColor.from_string("D5A43B")
BLUE = RGBColor.from_string("557D91")
LIGHT_CORAL = RGBColor.from_string("F3DFD8")
MUTED = RGBColor.from_string("68767B")
LINE = RGBColor.from_string("D5D0C6")
FONT_DISPLAY = "Aptos Display"
FONT_BODY = "Aptos"


def _rect(slide, x, y, width, height, fill, rounded=False):
      kind = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
      shape = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(width), Inches(height))
      shape.fill.solid()
      shape.fill.fore_color.rgb = fill
      shape.line.fill.background()
      return shape


def texto(slide, conteudo, x, y, largura, altura, tamanho=18, cor=INK,
              fonte=FONT_BODY, negrito=False, alinhamento=PP_ALIGN.LEFT,
              vertical=MSO_ANCHOR.TOP):
      box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(largura), Inches(altura))
      frame = box.text_frame
      frame.clear()
      frame.word_wrap = True
      frame.margin_left = frame.margin_right = Inches(.02)
      frame.margin_top = frame.margin_bottom = Inches(.01)
      frame.vertical_anchor = vertical
      paragraph = frame.paragraphs[0]
      paragraph.text = conteudo
      paragraph.alignment = alinhamento
      paragraph.font.name = fonte
      paragraph.font.size = Pt(tamanho)
      paragraph.font.color.rgb = cor
      paragraph.font.bold = negrito
      paragraph.space_after = Pt(0)
      return box


def _fundo(slide, color):
      slide.background.fill.solid()
      slide.background.fill.fore_color.rgb = color


def _rodape(slide, numero, total, dark=False):
      color = RGBColor.from_string("9CA9A7") if dark else MUTED
      rule = LINE if not dark else INK_SOFT
      _rect(slide, .65, 7.08, 12.0, .012, rule)
      texto(slide, "PPGCC / TESTE DE SISTEMAS INTELIGENTES", .68, 7.16, 5.5, .18,
              8, color, negrito=True)
      texto(slide, f"RAG-PPGCC     {numero:02d} / {total:02d}", 10.1, 7.16, 2.5, .18,
              8, color, alinhamento=PP_ALIGN.RIGHT)


def _slide(prs, kicker, title, lead="", dark=False):
      slide = prs.slides.add_slide(prs.slide_layouts[6])
      _fundo(slide, INK if dark else PAPER)
      _rect(slide, 0, 0, .13, 7.5, CORAL)
      main = WHITE if dark else INK
      secondary = RGBColor.from_string("C0CDCA") if dark else MUTED
      texto(slide, kicker.upper(), .72, .3, 10.8, .22, 9, TEAL if dark else CORAL,
              negrito=True)
      texto(slide, title, .7, .66, 12.0, .55, 27, main, FONT_DISPLAY, True)
      if lead:
            texto(slide, lead, .72, 1.25, 11.9, .48, 13, secondary)
      _rodape(slide, len(prs.slides), 12, dark)
      return slide


def _nota(slide, roteiro, titulo, tempo, fala):
      slide.notes_slide.notes_text_frame.text = f"Tempo previsto: {tempo}\n{fala}"
      numero = sum(item.startswith("## ") for item in roteiro) + 1
      roteiro.extend([f"## {numero}. {titulo} ({tempo})", "", fala, ""])


def _barra_resultado(slide, y, label, values, denominador, color, label_x=.8, bar_x=4.0):
      texto(slide, label, label_x, y-.02, 2.75, .32, 15, INK, negrito=True)
      for i, value in enumerate(values):
            x = bar_x + i * 2.05
            _rect(slide, x, y, 1.34, .25, LINE, rounded=True)
            if value:
                  _rect(slide, x, y, 1.34 * value / denominador, .25, color, rounded=True)
            texto(slide, f"{value}/{denominador}", x, y+.32, 1.34, .25, 11, INK,
                    negrito=True, alinhamento=PP_ALIGN.CENTER)


def gerar():
    es = [ler_execucao(n) for n in descobrir_execucoes()]
    if len(es) != 4:
        raise ValueError(f"Esperadas quatro execuções oficiais; encontradas {len(es)}.")
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    roteiro = ["# Roteiro oral — 15 minutos", "",
               "Duração anotada é estimativa. Ensaio com cronômetro continua necessário.", ""]
    qps = (
        ("QP1", "Qualidade das respostas",
         "Em que medida o assistente RAG apresenta respostas corretas e fundamentadas no regulamento do PPGCC?",
         "CT01–CT11, CT20–CT22 · factualidade + alucinação"),
        ("QP2", "Robustez e segurança",
         "Como o assistente RAG se comporta diante de entradas ambíguas, contraditórias ou potencialmente maliciosas?",
         "CT12–CT15, CT23–CT27 · robustez + segurança"),
        ("QP3", "Consistência conversacional",
         "Em que medida o assistente RAG preserva o contexto e a coerência das respostas em interações com múltiplos turnos?",
         "CT16, CT28–CT30 · conversa"),
    )

    # 1. Capa
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _fundo(s, INK)
    _rect(s, 0, 0, .16, 7.5, CORAL)
    _rect(s, .78, .62, .55, .08, TEAL)
    texto(s, "PPGCC / UECE    ·    TESTE DE SISTEMAS INTELIGENTES", .8, .88, 8.5, .25,
          10, RGBColor.from_string("B9CCC7"), negrito=True)
    texto(s, "Avaliação automatizada\nda qualidade de um sistema RAG", .78, 1.55, 8.3, 2.0,
          36, WHITE, FONT_DISPLAY, True)
    texto(s, "Robot Framework, evidências e análise crítica do oráculo", .82, 3.85, 7.7, .48,
          18, RGBColor.from_string("D1DAD5"))
    _rect(s, 9.55, 1.42, 2.75, 4.55, INK_SOFT, rounded=True)
    texto(s, "30", 9.82, 1.88, 2.15, 1.18, 68, MUSTARD, FONT_DISPLAY, True,
          alinhamento=PP_ALIGN.CENTER)
    texto(s, "CENÁRIOS\nEXPERIMENTAIS", 9.9, 3.05, 2.0, .72, 12, WHITE, negrito=True,
          alinhamento=PP_ALIGN.CENTER)
    _rect(s, 10.1, 4.02, 1.65, .015, RGBColor.from_string("60747A"))
    texto(s, "04", 10.0, 4.28, 1.8, .74, 38, TEAL, FONT_DISPLAY, True,
          alinhamento=PP_ALIGN.CENTER)
    texto(s, "EXECUÇÕES", 10.0, 5.06, 1.8, .28, 11, WHITE, negrito=True,
          alinhamento=PP_ALIGN.CENTER)
    texto(s, "Dify RAG   /   resultados determinísticos   /   Ragas não executado",
          .82, 6.55, 8.4, .3, 11, RGBColor.from_string("B9CCC7"))
    _rodape(s, 1, 12, True)
    _nota(s, roteiro, "Avaliação automatizada da qualidade de um sistema RAG", "0:45",
          "Abra pelo escopo: um assistente RAG sobre o regimento do PPGCC, avaliado com Robot Framework. "
          "Foram conduzidas quatro execuções oficiais de 30 casos cada. O trabalho mede comportamento "
          "observado nos critérios e documentos disponíveis; não certifica o sistema nem apresenta métricas Ragas.")

    # 2. Problema do oráculo
    s = _slide(prs, "Motivação", "Presença de termos não é evidência de verdade",
               "Uma resposta pode conter a palavra esperada e ainda afirmar uma relação factual incorreta.")
    _rect(s, .82, 2.16, 5.15, 3.48, WHITE, rounded=True)
    texto(s, "CT28 / EXEC1", 1.15, 2.5, 3.2, .28, 10, CORAL, negrito=True)
    texto(s, "24", 1.08, 3.0, 2.1, 1.15, 62, TEAL, FONT_DISPLAY, True)
    texto(s, "aparece na decomposição dos créditos", 1.15, 4.25, 4.25, .6, 17, INK)
    texto(s, "PASS", 4.55, 2.95, 1.0, .35, 13, TEAL, negrito=True, alinhamento=PP_ALIGN.RIGHT)
    _rect(s, 6.32, 2.16, 5.95, 3.48, LIGHT_CORAL, rounded=True)
    texto(s, "O TOTAL INFORMADO FOI 32", 6.72, 2.5, 4.9, .3, 10, CORAL, negrito=True)
    texto(s, "Mestrado: total\nincorreto", 6.72, 3.08, 4.9, 1.0, 31, INK, FONT_DISPLAY, True)
    texto(s, "A presença de “24” não prova que o total foi associado corretamente.",
          6.75, 4.6, 4.85, .58, 14, INK)
    _nota(s, roteiro, "Motivação e problema do oráculo", "1:00",
          "O exemplo CT28 da primeira execução mostra a limitação de um critério lexical: a resposta passou "
          "porque mencionava 24 na decomposição, embora informasse total incorreto de 32 créditos. Esse caso "
          "motivou separar resultado automatizado de julgamento factual. Não recalibramos o histórico depois de observar as execuções.")

    # 3. Questões de pesquisa
    s = _slide(prs, "Perguntas de pesquisa", "Três perguntas delimitam a investigação",
               "As sete questões iniciais foram agrupadas; latência fica como dimensão complementar.")
    rows = [2.02, 3.28, 4.54]
    accents = [CORAL, TEAL, MUSTARD]
    for (code, title, question, mapping), y, accent in zip(qps, rows, accents):
        _rect(s, .82, y, .08, 1.02, accent)
        texto(s, code, 1.12, y+.02, .72, .3, 12, accent, negrito=True)
        texto(s, title, 1.92, y, 3.1, .34, 17, INK, FONT_DISPLAY, True)
        texto(s, question, 5.12, y, 7.08, .68, 15, INK)
        texto(s, mapping, 1.93, y+.51, 3.0, .24, 10, MUTED)
    _nota(s, roteiro, "Questões de pesquisa consolidadas", "1:30",
          "QP1: Em que medida o assistente RAG apresenta respostas corretas e fundamentadas no regulamento do PPGCC? "
          "QP2: Como o assistente RAG se comporta diante de entradas ambíguas, contraditórias ou potencialmente maliciosas? "
          "QP3: Em que medida o assistente RAG preserva o contexto e a coerência das respostas em interações com múltiplos turnos? "
          "A latência é complementar. "
          "Como Ragas não foi executado, não há comparação empírica entre oráculos semântico e determinístico.")

    # 4. Sistema sob teste
    s = _slide(prs, "Sistema sob teste", "Recuperação e geração são fontes distintas de erro",
               "O protocolo registra a configuração declarada; não há snapshot remoto completo por execução.")
    nodes = [("01", "PERGUNTA", "Entrada do cenário", CORAL),
             ("02", "RECUPERAÇÃO", "Dify · regimento", TEAL),
             ("03", "GERAÇÃO", "Gemini · resposta", BLUE),
             ("04", "EVIDÊNCIA", "XML + JSONL", MUSTARD)]
    node_x = [.9, 4.0, 7.1, 10.2]
    for (number, label, detail, accent), x in zip(nodes, node_x):
        _rect(s, x, 2.58, 2.12, 1.64, WHITE, rounded=True)
        texto(s, number, x+.2, 2.77, .44, .3, 11, accent, negrito=True)
        texto(s, label, x+.2, 3.15, 1.76, .28, 12, INK, negrito=True)
        texto(s, detail, x+.2, 3.55, 1.78, .32, 12, MUTED)
    for x in (3.22, 6.34, 9.46):
        texto(s, "→", x, 3.07, .54, .38, 21, CORAL, FONT_DISPLAY, True,
              alinhamento=PP_ALIGN.CENTER)
    _rect(s, .92, 4.82, 11.25, .012, LINE)
    texto(s, "Dify Community 1.18.0", .98, 5.14, 2.8, .34, 14, INK, negrito=True)
    texto(s, "Gemini gemini-3.5-flash-lite  ·  embeddings gemini-embedding-001  ·  Hybrid / Top K 4",
          3.78, 5.14, 8.25, .34, 12, MUTED)
    texto(s, "Contextos registrados ajudam a formular hipóteses; não revelam a consulta interna do Dify.",
          .98, 5.84, 11.15, .38, 12, MUTED)
    _nota(s, roteiro, "Sistema sob teste", "1:00",
          "Apresente o fluxo observado: pergunta, trechos recuperados pelo Dify, resposta do Gemini e registros locais. "
          "O protocolo documenta Dify 1.18.0, Gemini flash-lite, embeddings Gemini e busca híbrida Top K quatro. "
          "Esses são valores declarados, não snapshots completos de cada execução. Contextos no JSONL não mostram a consulta interna.")

    # 5. Desenho experimental
    s = _slide(prs, "Método", "30 cenários em seis categorias",
               "Um regimento; critérios determinísticos por caso; quatro execuções com diferenças documentadas.")
    categories = [("Factual", 9, CORAL), ("Alucinação", 5, MUSTARD), ("Robustez", 5, TEAL),
                  ("Segurança", 4, BLUE), ("Conversa", 4, CORAL), ("Desempenho", 3, MUSTARD)]
    for i, (label, count, accent) in enumerate(categories):
        y = 2.02 + i*.57
        texto(s, label, .95, y, 1.72, .3, 13, INK, negrito=True)
        _rect(s, 2.72, y+.04, 5.6, .22, LINE, rounded=True)
        _rect(s, 2.72, y+.04, 5.6*count/9, .22, accent, rounded=True)
        texto(s, str(count), 8.52, y, .48, .3, 13, INK, negrito=True)
    _rect(s, 9.35, 2.02, .02, 3.5, LINE)
    texto(s, "30", 9.72, 2.08, 1.5, .74, 42, INK, FONT_DISPLAY, True)
    texto(s, "casos CT\nseis dimensões", 9.76, 2.92, 2.3, .62, 15, MUTED)
    texto(s, "Exec1–3: incluem smoke nos totais brutos. Exec4: sem smoke.\nComparação de qualidade usa sempre 30 cenários experimentais.",
          9.75, 4.13, 2.55, 1.05, 12, INK)
    _nota(s, roteiro, "Desenho experimental e cobertura", "1:15",
          "A suíte contém 30 casos experimentais: nove factuais, cinco de alucinação, cinco robustos, quatro de segurança, "
          "quatro conversacionais e três de desempenho. Execuções 1 a 3 também têm quatro testes de API, incluindo smoke; "
          "execução 4 tem três. Por isso comparamos sempre os 30 cenários, não totais brutos diferentes.")

    # 6. BDD e oráculos
    s = _slide(prs, "Automação", "BDD rastreia a pergunta até o critério",
               "O veredito automatizado é uma medida da regra de aceitação, não uma certificação semântica.")
    phases = [("G", "Given", "carregar o caso", CORAL),
              ("W", "When", "enviar e registrar", TEAL),
              ("T", "Then", "avaliar critérios", MUSTARD)]
    for i, (letter, label, detail, accent) in enumerate(phases):
        y = 2.05 + i*1.03
        _rect(s, .98, y, .56, .56, accent, rounded=True)
        texto(s, letter, .98, y+.02, .56, .48, 20, WHITE, FONT_DISPLAY, True,
              alinhamento=PP_ALIGN.CENTER, vertical=MSO_ANCHOR.MIDDLE)
        texto(s, label, 1.82, y+.02, 1.18, .27, 15, INK, negrito=True)
        texto(s, detail, 3.05, y+.02, 2.55, .3, 13, MUTED)
        if i < 2:
            _rect(s, 1.25, y+.59, .025, .42, LINE)
    _rect(s, 6.05, 2.05, .02, 3.3, LINE)
    texto(s, "ORÁCULO DETERMINÍSTICO", 6.48, 2.1, 3.2, .28, 10, CORAL, negrito=True)
    texto(s, "Termos · ausência · citação\nLatência · similaridade lexical",
          6.48, 2.6, 5.3, .77, 18, INK, FONT_DISPLAY, True)
    _rect(s, 6.48, 3.75, 5.65, .012, LINE)
    texto(s, "RAGAS / LLM JUIZ", 6.48, 4.02, 3.1, .27, 10, TEAL, negrito=True)
    texto(s, "Implementado; não executado.\nNenhuma métrica semântica reportada.",
          6.48, 4.42, 5.4, .68, 15, MUTED)
    _nota(s, roteiro, "BDD e limites do oráculo", "1:15",
          "As suítes expressam Given, When e Then; keywords compartilhadas chamam o cliente e o avaliador Python. "
          "Os critérios cobrem termos, ausência, citação, latência e similaridade. Um PASS significa que o critério passou; "
          "não demonstra todas as relações factuais. Ragas está implementado, mas não foi executado e não gerou métricas.")

    # 7. QP1
    factual = [sum(t["status"] == "PASS" for t in e["testes"] if t["categoria"] == "factual") for e in es]
    hallucination = [sum(t["status"] == "PASS" for t in e["testes"] if t["categoria"] == "alucinacao") for e in es]
    s = _slide(prs, "QP1 · Qualidade das respostas", "Resultados parciais nos critérios determinísticos",
               qps[0][2])
    for i, e in enumerate(es):
        texto(s, f"EXEC {e['numero']}", 4.0+i*2.05, 2.08, 1.34, .24, 9, MUTED, negrito=True,
              alinhamento=PP_ALIGN.CENTER)
    _barra_resultado(s, 2.63, "Factualidade", factual, 9, CORAL)
    _barra_resultado(s, 3.62, "Alucinação", hallucination, 5, MUSTARD)
    _rect(s, .88, 4.48, 3.67, 1.35, WHITE, rounded=True)
    texto(s, "CT09 · 4/4 FAIL", 1.12, 4.7, 3.16, .26, 12, CORAL, negrito=True)
    texto(s, "A contradição 30/36 meses não foi reconhecida.", 1.12, 5.08, 3.15, .55, 13, INK)
    _rect(s, 4.83, 4.48, 3.67, 1.35, WHITE, rounded=True)
    texto(s, "CT22 · exec1 e exec4", 5.08, 4.7, 3.16, .26, 12, MUSTARD, negrito=True)
    texto(s, "Omissão de completude; não prova invenção de linhas.", 5.08, 5.08, 3.15, .55, 13, INK)
    _rect(s, 8.78, 4.48, 3.67, 1.35, WHITE, rounded=True)
    texto(s, "CT21 · exec3", 9.02, 4.7, 3.16, .26, 12, TEAL, negrito=True)
    texto(s, "Recusa válida reprovada pelo padrão de ausência.", 9.02, 5.08, 3.15, .55, 13, INK)
    texto(s, "TOTAL CT01–CT30   ·   EXEC1  26/30     EXEC2  26/30     EXEC3  26/30     EXEC4  25/30",
          .98, 6.05, 11.25, .34, 12, INK, negrito=True)
    _nota(s, roteiro, "QP1 — Qualidade das respostas", "1:30",
          "A factualidade passou em oito de nove casos em cada execução. Alucinação passou em quatro de cinco, cinco de cinco, "
          "quatro de cinco e quatro de cinco. CT09 falhou em todas; CT22, na primeira e quarta. O quadro não esgota a qualidade: "
          "CT28 da primeira execução passou apesar do total incorreto, e CT21 da terceira rejeitou uma recusa adequada. "
          "Assim, a resposta à QP1 é parcial e limitada pelos oráculos lexicais.")

    # 8. QP2
    robustness = [sum(t["status"] == "PASS" for t in e["testes"] if t["categoria"] == "robustez") for e in es]
    security = [sum(t["status"] == "PASS" for t in e["testes"] if t["categoria"] == "seguranca") for e in es]
    s = _slide(prs, "QP2 · Robustez e segurança", "Os casos selecionados passaram",
               qps[1][2])
    for i, e in enumerate(es):
        texto(s, f"EXEC {e['numero']}", 4.0+i*2.05, 2.34, 1.34, .24, 9, MUTED, negrito=True,
              alinhamento=PP_ALIGN.CENTER)
    _barra_resultado(s, 2.93, "Robustez", robustness, 5, TEAL)
    _barra_resultado(s, 4.05, "Segurança", security, 4, BLUE)
    _rect(s, .9, 5.2, .09, .65, MUSTARD)
    texto(s, "Escopo limitado", 1.18, 5.18, 2.35, .29, 14, INK, negrito=True)
    texto(s, "Passar nestes cenários não prova ausência geral de vulnerabilidades nem cobre entradas fora do conjunto testado.",
          3.48, 5.18, 8.55, .65, 14, MUTED)
    _nota(s, roteiro, "QP2 — Robustez e segurança", "1:00",
          "Robustez teve cinco de cinco aprovações e segurança quatro de quatro em cada execução. Isso sustenta a conclusão "
          "de que os casos selecionados passaram os critérios determinísticos. Não equivale a uma avaliação ampla de segurança, "
          "nem permite afirmar que não existam vulnerabilidades ou comportamento adversarial não coberto.")

    # 9. QP3
    conversation = [sum(t["status"] == "PASS" for t in e["testes"] if t["categoria"] == "conversa") for e in es]
    s = _slide(prs, "QP3 · Consistência conversacional", "O contexto multi-turno foi o ponto fraco",
               qps[2][2])
    texto(s, "CASOS PASS NA CATEGORIA CONVERSA", .98, 2.16, 6.7, .24, 10, CORAL, negrito=True)
    for i, (e, value) in enumerate(zip(es, conversation)):
        x = 1.08 + i*1.72
        texto(s, f"EXEC {e['numero']}", x, 2.56, 1.24, .22, 9, MUTED, negrito=True,
              alinhamento=PP_ALIGN.CENTER)
        _rect(s, x, 2.92, 1.24, 1.18, LINE, rounded=True)
        if value:
            height = 1.18*value/4
            _rect(s, x, 2.92+1.18-height, 1.24, height, CORAL, rounded=True)
        texto(s, f"{value}/4", x, 4.26, 1.24, .28, 12, INK, negrito=True,
              alinhamento=PP_ALIGN.CENTER)
    _rect(s, 8.65, 2.3, .02, 2.7, LINE)
    texto(s, "FALHAS OBSERVADAS", 9.05, 2.32, 2.8, .25, 10, CORAL, negrito=True)
    texto(s, "CT30  ·  falha nas quatro execuções\nCT28  ·  falha nas exec2–4\nCT29  ·  falha na exec4",
          9.05, 2.78, 3.2, 1.2, 14, INK, negrito=True)
    texto(s, "CT28/exec1 passou com resposta factualmente incorreta.",
          .98, 4.2, 7.05, .38, 12, MUSTARD, negrito=True)
    texto(s, "Hipótese: recuperação insuficiente em elipse/anáfora. As evidências não revelam o mecanismo interno do Dify.",
          .98, 5.05, 11.2, .55, 14, MUTED)
    _nota(s, roteiro, "QP3 — Consistência conversacional", "1:30",
          "A categoria passou em três de quatro casos na primeira execução, dois de quatro na segunda e terceira, e um de quatro na quarta. "
          "CT30 falhou em todas; CT28 em execuções posteriores; CT29 na quarta. CT28/exec1 passou com total errado. Contextos observáveis "
          "sustentam hipótese de recuperação insuficiente em perguntas elípticas, mas não provam o caminho interno da busca no Dify.")

    # 10. Desempenho complementar
    s = _slide(prs, "Dimensão complementar · Desempenho", "Latência é descritiva, não uma QP separada",
               "Médias/máximas calculadas sobre respostas JSONL registradas; não incluem pausas nem chamadas sem registro.")
    for i, e in enumerate(es):
        x = .9 + i*3.1
        lat = [r["latencia_s"] for r in e["respostas"] if isinstance(r.get("latencia_s"), (int, float))]
        mean = sum(lat)/len(lat) if lat else 0
        maximum = max(lat) if lat else 0
        passed, total = resumo([t for t in e["testes"] if t["categoria"] == "desempenho"])[1:3]
        _rect(s, x, 2.25, 2.75, 2.48, WHITE, rounded=True)
        texto(s, f"EXEC {e['numero']}", x+.22, 2.52, 1.8, .25, 10, TEAL, negrito=True)
        texto(s, f"{mean:.2f}s", x+.2, 2.98, 2.25, .62, 30, INK, FONT_DISPLAY, True)
        texto(s, f"média  ·  máximo {maximum:.2f}s", x+.23, 3.7, 2.36, .34, 11, MUTED)
        texto(s, f"CT17–19  {passed}/{total}", x+.23, 4.2, 2.35, .32, 12, CORAL, negrito=True)
    texto(s, "Variações entre execuções não demonstram regressão: ambiente, ordem e carga não foram controlados de forma equivalente.",
          .98, 5.42, 11.2, .56, 14, INK, negrito=True)
    _nota(s, roteiro, "Desempenho como dimensão complementar", "1:15",
          "O desempenho teve dois de três, dois de três, três de três e três de três aprovações. As médias JSONL variaram, "
          "e a quarta execução teve uma máxima maior; são estatísticas descritivas das respostas registradas. Pausas e chamadas "
          "sem registro ficam fora. Como ambiente e ordem variaram, não inferimos regressão de modelo.")

    # 11. Limitações
    s = _slide(prs, "Limitações", "O que as evidências não permitem afirmar",
               "A validade depende do escopo de casos, da regra de aceitação e da configuração observável.", dark=True)
    limits = [("ORÁCULO", "Termos presentes não provam relações corretas; CT28/exec1 expõe falso positivo.", CORAL),
              ("RAGAS", "Não executado; nenhuma validação semântica quantitativa nesta entrega.", TEAL),
              ("SISTEMA", "Um regimento e configurações remotas sem snapshot completo por execução.", MUSTARD),
              ("COMPARAÇÃO", "Quatro repetições não isolam efeito de ambiente, ordem ou carga.", BLUE)]
    for i, (label, explanation, accent) in enumerate(limits):
        col, row = i % 2, i // 2
        x, y = .95 + col*6.05, 2.25 + row*1.72
        _rect(s, x, y, .07, 1.18, accent)
        texto(s, label, x+.28, y+.02, 2.8, .24, 10, accent, negrito=True)
        texto(s, explanation, x+.28, y+.38, 4.95, .76, 15, WHITE, FONT_BODY)
    _nota(s, roteiro, "Limitações e validade", "1:30",
          "Quatro limites devem acompanhar a leitura: oráculos lexicais podem aceitar erro e rejeitar recusa válida; Ragas não foi executado; "
          "o experimento usa um documento e não tem snapshot remoto completo; diferenças de totais não isolam causa. São resultados observados "
          "no desenho usado, não estimativas universais do comportamento de sistemas RAG.")

    # 12. Conclusão
    s = _slide(prs, "Conclusão", "Três respostas, sem extrapolar a amostra",
               "A inspeção humana complementa o Robot; nenhuma QP é respondida por um único percentual.")
    conclusions = [("QP1", "Parcial", "Há aprovações consistentes, mas falhas factuais e limites do oráculo impedem afirmar correção geral.", CORAL),
                   ("QP2", "Nos casos testados", "Robustez e segurança passaram nos critérios; isso não garante cobertura ampla.", TEAL),
                   ("QP3", "Dificuldade recorrente", "As falhas de continuação indicam fragilidade observada de contexto multi-turno.", MUSTARD)]
    for i, (code, result, detail, accent) in enumerate(conclusions):
        y = 2.15 + i*1.12
        texto(s, code, .98, y+.04, .8, .24, 11, accent, negrito=True)
        texto(s, result, 1.92, y, 2.65, .35, 16, INK, FONT_DISPLAY, True)
        texto(s, detail, 4.7, y, 7.35, .54, 14, INK)
        if i < 2:
            _rect(s, .98, y+.79, 11.1, .012, LINE)
    texto(s, "Próximo estudo: recuperação com histórico e oráculos semânticos sob configuração congelada. Ragas permanece pendente.",
          .98, 5.83, 11.15, .42, 12, MUTED, negrito=True)
    _nota(s, roteiro, "Conclusões", "1:30",
          "Responda diretamente: QP1, evidência parcialmente favorável mas limitada por erros e oráculos; QP2, os casos de robustez e segurança "
          "passaram sem garantia geral; QP3, conversas multi-turno tiveram dificuldades recorrentes. A contribuição é a rastreabilidade e a análise "
          "crítica dos critérios. O estudo futuro pode testar recuperação contextual e avaliação semântica com ambiente congelado. Ensaie com cronômetro.")

    if len(prs.slides) != 12:
        raise ValueError(f"Esperados 12 slides; gerados {len(prs.slides)}.")
    tempos = [re.match(r"## \d+\. .* \((\d+:\d+)\)", line).group(1)
              for line in roteiro if line.startswith("## ")]
    total_segundos = sum(int(t.split(":")[0])*60 + int(t.split(":")[1]) for t in tempos)
    if total_segundos != 900:
        raise ValueError(f"O roteiro deve prever 15 minutos; recebeu {total_segundos} segundos.")
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    prs.save(SAIDA)
    (SAIDA.parent / "roteiro_apresentacao.md").write_text("\n".join(roteiro), encoding="utf-8")
    print(SAIDA)


if __name__ == "__main__":
    gerar()
