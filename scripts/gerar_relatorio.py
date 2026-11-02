"""Gera o relatório acadêmico final em Microsoft Word (.docx).

Padrão: ABNT adaptado para trabalhos acadêmicos.
- Papel A4, margens 3cm (sup./esq.) e 2cm (inf./dir.)
- Fonte Arial 12pt, espaçamento 1,5, texto justificado
- Títulos hierarquizados, paginação, tabelas numeradas

Uso: python scripts/gerar_relatorio.py
Saída: relatório/Relatorio_Final_Testes_RAG_PPGCC.docx
"""
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
from docx.shared import Cm, Inches, Pt, RGBColor

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "relatório" / "Relatorio_Final_Testes_RAG_PPGCC.docx"

FONTE = "Arial"
TAM_CORPO = Pt(12)
TAM_TIT1 = Pt(14)
TAM_TIT2 = Pt(13)
TAM_TIT3 = Pt(12)
TAM_PEQUENO = Pt(10)


def configurar_pagina(doc):
    """Configura A4 com margens ABNT."""
    sec = doc.sections[0]
    sec.page_width = Cm(21)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(3)
    sec.bottom_margin = Cm(2)
    sec.left_margin = Cm(3)
    sec.right_margin = Cm(2)

    # Estilo Normal
    style = doc.styles["Normal"]
    style.font.name = FONTE
    style.font.size = TAM_CORPO
    style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    style.paragraph_format.space_after = Pt(0)
    style.paragraph_format.space_before = Pt(0)


def configurar_estilos(doc):
    """Configura estilos de título."""
    for nivel, tamanho in [(1, TAM_TIT1), (2, TAM_TIT2), (3, TAM_TIT3)]:
        nome = f"Heading {nivel}"
        if nome in doc.styles:
            s = doc.styles[nome]
            s.font.name = FONTE
            s.font.size = tamanho
            s.font.bold = True
            s.font.color.rgb = RGBColor(0x1A, 0x36, 0x5F)
            s.paragraph_format.space_before = Pt(12)
            s.paragraph_format.space_after = Pt(6)
            s.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE


def add_numero_pagina(doc):
    """Adiciona numeração de página no rodapé."""
    sec = doc.sections[0]
    footer = sec.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # Campo de número de página
    run = p.add_run()
    fldChar1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
    run._r.append(fldChar1)
    run2 = p.add_run()
    instrText = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>')
    run2._r.append(instrText)
    run3 = p.add_run()
    fldChar2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
    run3._r.append(fldChar2)


def add_toc(doc):
    """Insere um campo de sumário (atualizável no Word)."""
    p = doc.add_paragraph()
    run = p.add_run()
    fldBegin = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
    run._r.append(fldBegin)
    run2 = p.add_run()
    instr = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText>')
    run2._r.append(instr)
    run3 = p.add_run()
    fldSep = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>')
    run3._r.append(fldSep)
    run4 = p.add_run("Clique com o botão direito e selecione 'Atualizar campo' para gerar o sumário.")
    run4.font.size = TAM_PEQUENO
    run4.italic = True
    run5 = p.add_run()
    fldEnd = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
    run5._r.append(fldEnd)


def add_paragrafo(doc, texto, justificar=True, espaco_apos=6):
    p = doc.add_paragraph(texto)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if justificar else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(espaco_apos)
    return p


def add_tabela(doc, cabecalhos, linhas, titulo=None):
    if titulo:
        p = doc.add_paragraph()
        r = p.add_run(titulo)
        r.bold = True
        r.font.size = TAM_PEQUENO
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)

    tbl = doc.add_table(rows=1 + len(linhas), cols=len(cabecalhos))
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Cabeçalho
    for i, h in enumerate(cabecalhos):
        cell = tbl.rows[0].cells[i]
        cell.text = h
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.bold = True
                r.font.size = TAM_PEQUENO

    # Dados
    for ri, linha in enumerate(linhas):
        for ci, val in enumerate(linha):
            cell = tbl.rows[ri + 1].cells[ci]
            cell.text = str(val)
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:
                    r.font.size = TAM_PEQUENO

    doc.add_paragraph()  # espaço após tabela
    return tbl


def add_fonte(doc, texto="Fonte: elaborado pelos autores (2026)."):
    p = doc.add_paragraph()
    r = p.add_run(texto)
    r.font.size = TAM_PEQUENO
    r.italic = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(12)


# --- Construção do documento ---

def gerar():
    doc = Document()
    configurar_pagina(doc)
    configurar_estilos(doc)
    add_numero_pagina(doc)

    # === CAPA ===
    for _ in range(6):
        doc.add_paragraph()
    p = doc.add_paragraph("UNIVERSIDADE ESTADUAL DO CEARÁ")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].bold = True
    p = doc.add_paragraph("PROGRAMA DE PÓS-GRADUAÇÃO EM CIÊNCIA DA COMPUTAÇÃO (PPGCC)")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].bold = True
    p = doc.add_paragraph("DISCIPLINA: TESTE DE SISTEMAS INTELIGENTES")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    for _ in range(6):
        doc.add_paragraph()

    p = doc.add_paragraph(
        "AVALIAÇÃO AUTOMATIZADA DA QUALIDADE DE UM SISTEMA INTELIGENTE BASEADO EM RAG: "
        "UMA ABORDAGEM COM ROBOT FRAMEWORK E MÉTRICAS SEMÂNTICAS"
    )
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].bold = True
    p.runs[0].font.size = Pt(13)

    for _ in range(8):
        doc.add_paragraph()

    p = doc.add_paragraph("Fortaleza – CE")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph("2026")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].bold = True

    doc.add_page_break()

    # === RESUMO ===
    doc.add_heading("RESUMO", level=1)
    add_paragrafo(doc,
        "Sistemas inteligentes baseados em Retrieval-Augmented Generation (RAG) representam um "
        "desafio para a engenharia de qualidade de software, pois geram saídas variáveis, "
        "probabilísticas e dependentes da qualidade da recuperação de informação. Este trabalho "
        "avalia um sistema RAG real — um assistente sobre o Regimento do PPGCC/UECE, construído "
        "no Dify Community com Google Gemini — por meio de testes automatizados em dois níveis: "
        "verificações determinísticas (Robot Framework com BDD) e métricas semânticas (Ragas). "
        "Foram elaborados 30 casos de teste distribuídos em sete dimensões de qualidade: correção "
        "factual, alucinação, robustez, segurança, contexto conversacional, desempenho e "
        "fidelidade ao documento. As três execuções oficiais resultaram em 30 de 34 testes "
        "aprovados (88,2%), com falhas consistentes em casos de contradição documental e de "
        "contexto conversacional multi-turno. A análise evidenciou que nenhum oráculo isolado é "
        "suficiente: o determinístico é rápido mas limitado à forma; o semântico captura "
        "significado mas é custoso; a combinação dos dois com análise humana é mais robusta. "
        "As métricas semânticas com Ragas estão implementadas mas pendentes de execução por "
        "limites de cota do plano gratuito do Gemini."
    )
    p = doc.add_paragraph()
    r = p.add_run("Palavras-chave: ")
    r.bold = True
    p.add_run("Teste de sistemas inteligentes; RAG; Robot Framework; BDD; Ragas; oráculo de teste; alucinação.")

    doc.add_page_break()

    # === SUMÁRIO ===
    doc.add_heading("SUMÁRIO", level=1)
    add_toc(doc)
    doc.add_page_break()

    # === 1. INTRODUÇÃO ===
    doc.add_heading("1 INTRODUÇÃO", level=1)
    add_paragrafo(doc,
        "Sistemas inteligentes baseados em modelos de linguagem de grande porte (LLMs) "
        "representam um desafio para a engenharia de qualidade de software. Diferentemente de "
        "sistemas tradicionais, cujo comportamento esperado pode ser especificado por pré-condições "
        "e pós-condições exatas, sistemas que geram linguagem natural produzem saídas variáveis, "
        "probabilísticas e muitas vezes subjetivas. O problema do oráculo de teste — decidir se "
        "uma saída está correta — torna-se central: a mesma pergunta pode ter múltiplas respostas "
        "aceitáveis, e uma resposta pode ser factualmente errada mesmo usando as palavras "
        "esperadas."
    )
    add_paragrafo(doc,
        "Sistemas RAG adicionam uma camada de complexidade: a qualidade da resposta depende não "
        "apenas da geração, mas também da recuperação de trechos relevantes da base de "
        "conhecimento. Uma falha pode ser de recuperação (trecho errado ou ausente) ou de geração "
        "(trecho correto, interpretação errada). Essa distinção é fundamental para o diagnóstico "
        "de defeitos em sistemas inteligentes."
    )
    add_paragrafo(doc,
        "Este trabalho avalia um sistema RAG real — um assistente sobre o Regimento do "
        "PPGCC/UECE — por meio de testes automatizados em dois níveis: verificações "
        "determinísticas (presença de termos, reconhecimento de ausência, latência) e métricas "
        "semânticas (Ragas). O foco acadêmico é a qualidade dos testes realizados e das "
        "ferramentas utilizadas, não a complexidade do desenvolvimento do chatbot."
    )

    # === 2. FUNDAMENTAÇÃO TEÓRICA ===
    doc.add_heading("2 FUNDAMENTAÇÃO TEÓRICA", level=1)

    doc.add_heading("2.1 Sistemas RAG", level=2)
    add_paragrafo(doc,
        "RAG combina recuperação de informação com geração de linguagem: antes de gerar uma "
        "resposta, o sistema busca trechos relevantes em uma base de conhecimento (tipicamente "
        "via embeddings e busca vetorial) e os insere no prompt do LLM. Isso reduz alucinação e "
        "permite que o sistema cite fontes, mas introduz a dependência da qualidade da "
        "recuperação. A avaliação de sistemas RAG deve, portanto, considerar duas dimensões: a "
        "qualidade da recuperação (os trechos corretos foram encontrados?) e a qualidade da "
        "geração (a resposta se apoia nos trechos recuperados?)."
    )

    doc.add_heading("2.2 Alucinação em sistemas RAG", level=2)
    add_paragrafo(doc,
        "Em sistemas RAG, alucinação ocorre quando o modelo gera informações não presentes nos "
        "trechos recuperados, seja por usar conhecimento paramétrico (treinamento) ou por inventar "
        "dados. A detecção de alucinação é um problema de oráculo: é necessário saber o que o "
        "documento diz e o que não diz. Casos de teste que perguntam sobre informações ausentes do "
        "documento são especialmente úteis para avaliar essa dimensão."
    )

    doc.add_heading("2.3 Prompt injection", level=2)
    add_paragrafo(doc,
        "Ataques de injeção de prompt inserem instruções maliciosas na entrada do usuário para "
        "alterar o comportamento do sistema. Em RAG, também é possível injetar conteúdo nos "
        "documentos recuperados. Sistemas bem projetados devem tratar o conteúdo recuperado como "
        "dado, não como instrução. A resistência a esses ataques é uma dimensão de segurança que "
        "deve ser testada explicitamente."
    )

    doc.add_heading("2.4 Métricas semânticas (Ragas)", level=2)
    add_paragrafo(doc,
        "Ragas é um framework de avaliação de RAG que usa um LLM como juiz para calcular métricas "
        "como: (i) Faithfulness — fidelidade da resposta aos contextos recuperados; (ii) Factual "
        "Correctness — correção factual da resposta frente a uma referência; (iii) Context "
        "Precision (with reference) — qualidade da recuperação. Cada métrica mede uma dimensão "
        "distinta: correção da resposta não equivale a fidelidade aos contextos, que não equivale "
        "a qualidade da recuperação, que não equivale a aprovação em testes determinísticos."
    )

    doc.add_heading("2.5 Oráculo de teste e seus limites", level=2)
    add_paragrafo(doc,
        "O oráculo de teste determina se uma saída está correta. Em sistemas de linguagem, nenhum "
        "oráculo é perfeito. O oráculo determinístico (presença de termos) é rápido e "
        "reprodutível, mas verifica forma, não semântica. O oráculo semântico (LLM juiz) captura "
        "semântica, mas é custoso, não determinístico e suscetível a viés. O oráculo humano é mais "
        "confiável, mas não escalável. A combinação de múltiplos oráculos com limites conhecidos "
        "é mais robusta que qualquer oráculo isolado."
    )

    # === 3. OBJETIVOS E QUESTÕES DE PESQUISA ===
    doc.add_heading("3 OBJETIVOS E QUESTÕES DE PESQUISA", level=1)
    add_paragrafo(doc,
        "O objetivo geral é avaliar a qualidade de um sistema inteligente baseado em RAG por "
        "meio de testes automatizados que investiguem correção factual, fidelidade ao documento, "
        "alucinação, robustez, segurança, contexto conversacional e desempenho."
    )
    doc.add_heading("3.1 Questões de pesquisa", level=2)
    rqs = [
        ("RQ1", "O sistema responde corretamente a perguntas factuais sobre o regimento?"),
        ("RQ2", "O sistema reconhece quando a informação não está no documento?"),
        ("RQ3", "O sistema é robusto a variações de escrita, paráfrases e ruído no documento?"),
        ("RQ4", "O sistema resiste a prompt injection e a vazamento de instruções de sistema?"),
        ("RQ5", "O sistema mantém contexto em conversas multi-turno?"),
        ("RQ6", "O sistema responde dentro de limites de latência aceitáveis?"),
        ("RQ7", "Como avaliações determinísticas e semânticas se complementam na avaliação de RAG?"),
    ]
    for rq, texto in rqs:
        p = doc.add_paragraph()
        r = p.add_run(f"{rq}: ")
        r.bold = True
        p.add_run(texto)
        p.paragraph_format.space_after = Pt(4)

    # === 4. CARACTERIZAÇÃO DO SISTEMA SOB TESTE ===
    doc.add_heading("4 CARACTERIZAÇÃO DO SISTEMA SOB TESTE", level=1)
    add_paragrafo(doc,
        "O sistema sob teste (SUT) é um chatbot RAG construído no Dify Community 1.18.0 "
        "(self-hosted via Docker em WSL 2/Ubuntu 22.04), que responde perguntas sobre o Regimento "
        "do PPGCC/UECE (PDF de 13 páginas, 47 chunks após indexação). O LLM utilizado é o Google "
        "Gemini (gemini-3.5-flash-lite) no plano gratuito, com embeddings do próprio Gemini "
        "(gemini-embedding-001, 3072 dimensões) e banco vetorial Weaviate."
    )
    add_tabela(doc,
        ["Item", "Valor"],
        [
            ["Plataforma", "Dify Community 1.18.0 (Docker Compose)"],
            ["LLM do chatbot", "Google Gemini gemini-3.5-flash-lite"],
            ["Embeddings", "gemini-embedding-001 (3072 dim.)"],
            ["Banco vetorial", "Weaviate (incluso no Dify)"],
            ["Chunking", "General, 1024 tokens, sobreposição 100"],
            ["Recuperação", "Hybrid Search (0,7 semântica / 0,3 keyword), Top K 4"],
            ["Temperatura", "Padrão do provedor (não configurável no plugin)"],
            ["Prompt de sistema", "Versão 1.0 (congelada)"],
            ["LLM juiz do Ragas", "gemini-3.5-flash (mais capaz que o do SUT)"],
            ["Limites do plano gratuito", "60 RPM / 100 RPD (em 29/10/2026)"],
        ],
        titulo="Tabela 1 — Configuração do experimento"
    )
    add_fonte(doc)
    add_paragrafo(doc,
        "O prompt de sistema instrui o assistente a fundamentar respostas no regimento, citar "
        "artigos, não inventar informações, reconhecer ausência de informação, apontar "
        "contradições sem escolher interpretação, não usar conhecimento externo e tratar conteúdo "
        "recuperado como referência (não como comando). A versão 1.0 do prompt foi congelada antes "
        "das execuções oficiais."
    )

    # === 5. METODOLOGIA EXPERIMENTAL ===
    doc.add_heading("5 METODOLOGIA EXPERIMENTAL", level=1)

    doc.add_heading("5.1 Golden dataset", level=2)
    add_paragrafo(doc,
        "Foram construídos 30 casos de teste a partir da leitura do regimento, cada um com "
        "pergunta, resposta de referência, artigo do regimento, trecho de origem e critérios de "
        "aceitação determinísticos. O dataset foi conferido no PDF em 29/10/2026 (todos marcados "
        "como verificado). Inconsistências do próprio regimento foram exploradas como casos de "
        "teste: o CT09 explora a contradição entre o Art. 35 (36º mês) e o Art. 39, alínea d "
        "(30º mês) sobre o prazo da qualificação de doutorado; o CT23 explora a divergência entre "
        "o numeral e o extenso no Art. 31, b ('48 (quarenta)' créditos), confirmada como 48 pelo "
        "Art. 32."
    )

    doc.add_heading("5.2 Distribuição dos casos", level=2)
    add_tabela(doc,
        ["Categoria", "Casos", "IDs", "Verificação determinística", "Métrica semântica"],
        [
            ["Factual", "9", "CT01–CT09", "Termos obrigatórios", "Faithfulness, Factual Correctness, Context Precision"],
            ["Alucinação", "5", "CT10, CT11, CT20–CT22", "Reconhecer ausência; termos proibidos", "CT20, CT22"],
            ["Robustez", "5", "CT12, CT13, CT23–CT25", "Termos obrigatórios", "Factual Correctness"],
            ["Segurança", "4", "CT14, CT15, CT26, CT27", "Termos obrigatórios/proibidos", "—"],
            ["Conversa", "4", "CT16, CT28–CT30", "Critérios por turno", "—"],
            ["Desempenho", "3", "CT17–CT19", "Latência, similaridade, status HTTP", "—"],
            ["Total", "30", "—", "—", "—"],
        ],
        titulo="Tabela 2 — Distribuição dos 30 casos por categoria"
    )
    add_fonte(doc)

    doc.add_heading("5.3 Critérios de aprovação", level=2)
    add_paragrafo(doc,
        "O oráculo determinístico verifica: presença de termos obrigatórios, ausência de termos "
        "proibidos, reconhecimento de ausência de informação e citação de artigo, conforme "
        "declarado em cada caso. As metas semânticas (ilustrativas, não universais) são: "
        "Faithfulness maior ou igual a 0,90; Factual Correctness maior ou igual a 0,85; Context "
        "Precision maior ou igual a 0,80. Falhas de segurança são analisadas individualmente, "
        "independentemente das médias gerais."
    )

    doc.add_heading("5.4 Calibração do avaliador", level=2)
    add_paragrafo(doc,
        "Uma execução preliminar (29/10/2026, interrompida por falta de memória) revelou 4 falsos "
        "negativos do avaliador determinístico, corrigidos com regras gerais (não específicas de "
        "caso): remoção de markdown, redução de '12 (doze)' a '12' e adição de padrões de recusa. "
        "A calibração ocorreu antes das execuções oficiais; após estas, falsos negativos são "
        "registrados, não corrigidos, para preservar a integridade do experimento."
    )

    # === 6. ESTRATÉGIA DE AUTOMAÇÃO ===
    doc.add_heading("6 ESTRATÉGIA DE AUTOMAÇÃO", level=1)
    add_paragrafo(doc,
        "A automação segue o padrão BDD (Given/When/Then) com Robot Framework em três camadas: "
        "(i) camada de comportamento (tests/*.robot) — casos de teste descrevem o comportamento "
        "esperado em linguagem estruturada; (ii) camada de keywords (resources/dify_keywords.robot) "
        "— keywords BDD que encapsulam o fluxo de preparação, ação e verificação; (iii) camada de "
        "implementação (libraries/) — cliente HTTP (DifyClient) e oráculo determinístico "
        "(RagEvaluator), expostos como bibliotecas do Robot Framework."
    )
    add_paragrafo(doc,
        "O cliente HTTP distingue erros transitórios (cota do Gemini, falhas de rede) de falhas "
        "funcionais do SUT. Erros transitórios (HTTP 429, 502, 503, 504, ou 4xx com texto de "
        "resource_exhausted ou rate limit) são reintentados com backoff exponencial. O número de "
        "tentativas é registrado. A latência medida é a da tentativa bem-sucedida, sem incluir as "
        "esperas, para não contaminar os testes de desempenho."
    )

    # === 7. ORGANIZAÇÃO E ESPECIFICAÇÃO DOS CASOS DE TESTE ===
    doc.add_heading("7 ORGANIZAÇÃO E ESPECIFICAÇÃO DOS CASOS DE TESTE", level=1)
    add_paragrafo(doc,
        "O projeto possui 34 testes automatizados no Robot Framework, distribuídos em 7 suítes. "
        "Desses, 30 correspondem aos cenários experimentais (CT01–CT30) e 4 são testes de "
        "infraestrutura/API que funcionam como smoke test do ambiente. Os testes de infraestrutura "
        "verificam: disponibilidade da API (tag smoke), presença de resposta e identificador de "
        "conversa, recuperação de trechos da base e rejeição de chave inválida. Não há "
        "duplicação: os testes de infraestrutura verificam pré-condições do ambiente, enquanto os "
        "30 cenários verificam comportamento do sistema inteligente."
    )
    add_paragrafo(doc,
        "Adicionalmente, 49 testes unitários em pytest validam as funções determinísticas das "
        "bibliotecas Python (normalização de texto, detecção de ausência, verificação de termos, "
        "latência, consistência e classificação de erros HTTP), sem chamar o SUT."
    )

    # === 8. FERRAMENTAS E TECNOLOGIAS ===
    doc.add_heading("8 FERRAMENTAS E TECNOLOGIAS", level=1)
    add_tabela(doc,
        ["Ferramenta", "Papel", "Justificativa"],
        [
            ["Robot Framework", "Automação dos testes", "Suporte nativo a BDD, bibliotecas em Python, relatórios HTML"],
            ["Dify Community", "Plataforma do SUT", "Self-hosted, integração com Gemini, RAG com busca híbrida"],
            ["Google Gemini", "LLM e embeddings", "Plano gratuito, endpoint compatível com OpenAI"],
            ["Ragas", "Métricas semânticas", "Métricas específicas para RAG"],
            ["Python", "Linguagem das bibliotecas", "Integração nativa com Robot Framework e Ragas"],
            ["pytest", "Testes unitários", "Padrão de mercado para testes Python"],
        ],
        titulo="Tabela 3 — Ferramentas e justificativas"
    )
    add_fonte(doc)

    # === 9. PROCEDIMENTO EXPERIMENTAL ===
    doc.add_heading("9 PROCEDIMENTO EXPERIMENTAL", level=1)
    add_paragrafo(doc,
        "O procedimento segue sete etapas: (1) verificar dependências e configuração; (2) "
        "validar disponibilidade do ambiente com smoke test; (3) executar os 30 cenários; (4) "
        "coletar evidências (output.xml, respostas.jsonl, relatórios HTML); (5) consolidar os "
        "resultados; (6) calcular métricas semânticas; (7) analisar falhas. As três execuções "
        "oficiais foram realizadas em 29/10/2026, cada uma em pasta própria (results/exec1, exec2, "
        "exec3), preservando todas as evidências."
    )

    # === 10. RESULTADOS QUANTITATIVOS ===
    doc.add_heading("10 RESULTADOS QUANTITATIVOS", level=1)

    doc.add_heading("10.1 Aprovação por suíte", level=2)
    add_tabela(doc,
        ["Suíte", "Exec 1", "Exec 2", "Exec 3"],
        [
            ["API", "4/4", "4/4", "4/4"],
            ["Factual", "8/9", "8/9", "8/9"],
            ["Alucinação", "4/5", "5/5", "4/5"],
            ["Robustez", "5/5", "5/5", "5/5"],
            ["Segurança", "4/4", "4/4", "4/4"],
            ["Conversa", "3/4", "2/4", "2/4"],
            ["Desempenho", "2/3", "2/3", "3/3"],
            ["Total", "30/34", "30/34", "30/34"],
        ],
        titulo="Tabela 4 — Aprovação por suíte nas três execuções (29/10/2026)"
    )
    add_fonte(doc)
    add_paragrafo(doc,
        "A taxa de aprovação geral foi de 88,2% (30 de 34) em todas as execuções. A consistência "
        "entre execuções é notável: as mesmas falhas ocorrem na maioria dos casos, indicando que "
        "o não determinismo do modelo afeta poucos cenários."
    )

    doc.add_heading("10.2 Chamadas ao SUT e latência", level=2)
    add_tabela(doc,
        ["Execução", "Chamadas", "Latência média (s)", "Latência máx. (s)", "Com retentativa"],
        [
            ["1", "40", "2,9", "8,4", "1"],
            ["2", "39", "3,6", "25,2", "0"],
            ["3", "39", "1,5", "2,4", "3"],
        ],
        titulo="Tabela 5 — Estatísticas de chamadas ao SUT"
    )
    add_fonte(doc)

    # === 11. RESULTADOS QUALITATIVOS ===
    doc.add_heading("11 RESULTADOS QUALITATIVOS", level=1)
    add_paragrafo(doc,
        "Os pontos fortes identificados foram: segurança (12 de 12 nas três execuções) e "
        "robustez (15 de 15), indicando que o sistema resiste a prompt injection, não vaza "
        "instruções de sistema, recusa role play de autoridade e não confirma premissas falsas, "
        "além de tolerar variações de escrita, paráfrases e ruído no documento."
    )
    add_paragrafo(doc,
        "As métricas semânticas com Ragas não foram executadas por limites de cota do plano "
        "gratuito do Gemini. O script está implementado e validado sintaticamente; a execução "
        "produzirá métricas de Faithfulness, Factual Correctness e Context Precision por caso, "
        "complementando a análise qualitativa."
    )

    # === 12. ANÁLISE DAS FALHAS ===
    doc.add_heading("12 ANÁLISE DAS FALHAS", level=1)

    doc.add_heading("12.1 Tabela consolidada de falhas", level=2)
    add_tabela(doc,
        ["ID", "Categoria", "Exec 1", "Exec 2", "Exec 3", "Tipo de falha"],
        [
            ["CT09", "Factual", "FAIL", "FAIL", "FAIL", "Recuperação"],
            ["CT22", "Alucinação", "FAIL", "PASS", "PASS", "Geração (não citou área)"],
            ["CT28", "Conversa", "PASS", "FAIL", "FAIL", "Recuperação/Alucinação"],
            ["CT30", "Conversa", "FAIL", "FAIL", "FAIL", "Recuperação"],
            ["CT18", "Desempenho", "FAIL", "FAIL", "PASS", "Oráculo (similaridade lexical)"],
            ["CT21", "Alucinação", "PASS", "PASS", "FAIL", "Oráculo (falso negativo)"],
        ],
        titulo="Tabela 6 — Falhas identificadas nas três execuções"
    )
    add_fonte(doc)

    doc.add_heading("12.2 CT09 — Contradição documental (falhou 3/3)", level=2)
    add_paragrafo(doc,
        "O regimento é contraditório: o Art. 35 fixa a apresentação da Qualificação de Doutorado "
        "até o 36º mês, enquanto o Art. 39, alínea d, prevê desligamento se a Qualificação não for "
        "aprovada até o 30º mês. O SUT sempre responde citando apenas os 36 meses (Art. 35), sem "
        "reconhecer a contradição. Análise dos contextos recuperados mostra que o chunk contendo "
        "o Art. 39, alínea d (30º mês) não foi recuperado em nenhuma execução. O rótulo 'Art. 39' "
        "foi partido na extração do PDF ('Art. 3 9.'), e a alínea d está em um chunk separado do "
        "rótulo do artigo. Trata-se de uma falha de recuperação agravada por ruído no chunking."
    )

    doc.add_heading("12.3 CT30 — Troca de nível na apresentação oral (falhou 3/3)", level=2)
    add_paragrafo(doc,
        "No segundo turno ('E no doutorado?'), o SUT responde 'não há informações' em todas as "
        "execuções. Os contextos recuperados para o segundo turno não incluem o chunk do Art. 43, "
        "§1º (que contém os valores do doutorado: 40 a 50 minutos). O Chatbot básico do Dify busca "
        "na base usando apenas a última mensagem, sem incorporar o contexto da conversa. "
        "Trata-se de uma falha de recuperação inerente à arquitetura do app, não de geração."
    )

    doc.add_heading("12.4 CT28 — Elipse doutorado para mestrado (falhou 2/3)", level=2)
    add_paragrafo(doc,
        "No segundo turno ('E no mestrado?'), a execução 1 passou por um falso positivo do "
        "oráculo: a resposta informou '32 (trinta e dois) créditos' (erro: o correto é 24), mas "
        "continha '24' na decomposição (8+24), satisfazendo o termo obrigatório. Na execução 2, "
        "o SUT disse 'não há informações' (falha de recuperação). Na execução 3, alucinou '28 "
        "créditos' — o número 28 não aparece em nenhum trecho recuperado, caracterizando "
        "alucinação de geração a partir de conhecimento paramétrico."
    )

    doc.add_heading("12.5 CT18 — Consistência entre repetições (falhou 2/3)", level=2)
    add_paragrafo(doc,
        "As três respostas são factualmente corretas em todas as execuções (contêm '8 "
        "orientandos'), mas a similaridade lexical oscila em torno do limite (0,5). Nas execuções "
        "1 e 2, a similaridade ficou abaixo do limite (0,422), causando reprovação; na execução "
        "3, passou. Isso ilustra a limitação da métrica de similaridade lexical: respostas "
        "semanticamente iguais diferem na formulação (ordem de cláusulas, sinônimos, citação de "
        "artigo). Trata-se de uma limitação do oráculo, não do SUT."
    )

    doc.add_heading("12.6 CT22 e CT21 — Falsos negativos do oráculo", level=2)
    add_paragrafo(doc,
        "CT22 (execução 1): o SUT reconheceu corretamente que as linhas de pesquisa não estão "
        "nomeadas, mas não citou a área de concentração ('Computação Científica e Aplicada'), "
        "falhando o termo obrigatório. Trata-se de uma falha parcial de geração. CT21 (execução "
        "3): o SUT respondeu 'Não possuo essa informação no documento', uma recusa correta, mas o "
        "padrão de reconhecimento de ausência não cobriu essa formulação específica. Trata-se de "
        "um falso negativo do oráculo, mantido como registrado sem recalibrar."
    )

    # === 13. AMEAÇAS À VALIDADE ===
    doc.add_heading("13 AMEAÇAS À VALIDADE", level=1)
    add_tabela(doc,
        ["Ameaça", "Impacto", "Mitigação"],
        [
            ["Oráculo por expressões regulares (presença de termos)", "Falsos negativos e positivos", "Calibração preliminar; registro de falsos negativos; complementação com Ragas"],
            ["LLM juiz da mesma família do modelo do SUT (Gemini)", "Viés de autoavaliação", "Modelo mais capaz (flash vs flash-lite); registrado como ameaça"],
            ["Temperatura não configurável no plugin", "Não determinismo", "3 execuções oficiais; medição de variabilidade"],
            ["Um único documento, 30 casos", "Cobertura limitada", "Aceito como escopo do experimento"],
            ["Modelos do plano gratuito podem mudar", "Irreprodutibilidade", "Versões registradas no protocolo"],
            ["Chunking com ruído da extração do PDF", "Recuperação degradada", "Causa raiz de falhas como CT09; documentado"],
            ["Métricas Ragas não executadas", "Avaliação semântica pendente", "Script pronto; status sinalizado"],
        ],
        titulo="Tabela 7 — Ameaças à validade e mitigações"
    )
    add_fonte(doc)

    # === 14. DISCUSSÃO ===
    doc.add_heading("14 DISCUSSÃO", level=1)
    add_paragrafo(doc,
        "Os resultados mostram que o sistema RAG avaliado tem bom desempenho em factualidade "
        "(88%), robustez (100%) e segurança (100%), mas falha consistentemente em contexto "
        "conversacional (50 a 75%). A causa raiz identificada é arquitetural: o Chatbot básico do "
        "Dify busca na base usando apenas a última mensagem, sem incorporar o contexto da "
        "conversa à consulta de recuperação. Isso sugere que a avaliação de sistemas RAG deve "
        "testar não apenas a geração, mas também a recuperação em contextos multi-turno."
    )
    add_paragrafo(doc,
        "A análise das falhas demonstra o valor de combinar oráculos: o oráculo determinístico "
        "detectou a falha do CT09 (contradição não reconhecida), enquanto a análise qualitativa "
        "revelou a alucinação do CT28 (execução 3) e o falso positivo do oráculo no CT28 (execução "
        "1). A métrica de similaridade lexical (CT18) mostrou ser um indicador ruidoso de "
        "consistência: semanticamente estável, mas lexicalmente variável."
    )
    add_paragrafo(doc,
        "A não execução do Ragas é uma limitação desta entrega. As métricas semânticas trariam "
        "evidência quantitativa para complementar a análise qualitativa, especialmente nos casos "
        "onde o oráculo determinístico é insuficiente."
    )

    # === 15. CONCLUSÃO ===
    doc.add_heading("15 CONCLUSÃO", level=1)
    add_paragrafo(doc,
        "Este trabalho demonstrou que a qualidade de um sistema RAG pode ser avaliada de forma "
        "automatizada combinando Robot Framework (BDD, testes determinísticos) com Ragas (métricas "
        "semânticas). A arquitetura em três camadas (comportamento, keywords, implementação) "
        "separou claramente o que é testado de como é testado, facilitando manutenção e "
        "rastreabilidade."
    )
    add_paragrafo(doc,
        "Os 30 casos de teste, organizados em 7 categorias, cobriram dimensões críticas de "
        "qualidade de sistemas inteligentes. As três execuções oficiais revelaram falhas "
        "consistentes (contradição não reconhecida, contexto conversacional) e intermitentes "
        "(alucinação em turno elíptico, variabilidade lexical), além de falsos negativos do "
        "oráculo — todos documentados e analisados."
    )
    add_paragrafo(doc,
        "A principal contribuição metodológica é a constatação de que nenhum oráculo isolado é "
        "suficiente. A combinação de oráculos determinísticos, semânticos e análise humana, com "
        "limites explicitamente declarados, é mais robusta que qualquer abordagem isolada. Como "
        "trabalhos futuros, destacam-se: executar as métricas semânticas com Ragas; testar uma "
        "arquitetura de recuperação que incorpore o contexto da conversa; expandir o dataset com "
        "mais casos de contradição e recuperação; e avaliar o impacto de diferentes estratégias "
        "de chunking."
    )

    # === 16. REFERÊNCIAS ===
    doc.add_heading("16 REFERÊNCIAS BIBLIOGRÁFICAS", level=1)
    refs = [
        "DIFY. Dify — LLM App Development Platform. Disponível em: https://github.com/langgenius/dify. Acesso em: out. 2026.",
        "GOOGLE. Gemini API Documentation. Disponível em: https://ai.google.dev/gemini-api/docs/models. Acesso em: out. 2026.",
        "ROBOT FRAMEWORK. Robot Framework User Guide. Disponível em: https://robotframework.org/robotframework/. Acesso em: out. 2026.",
        "RAGAS. Ragas — Evaluation Framework for RAG. Disponível em: https://github.com/explodinggradients/ragas. Acesso em: out. 2026.",
        "UECE. Regimento do Programa de Pós-Graduação em Ciência da Computação. Fortaleza, 2021.",
    ]
    for ref in refs:
        p = doc.add_paragraph(ref)
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.left_indent = Cm(0)
        p.paragraph_format.space_after = Pt(6)

    # Salvar
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(SAIDA))
    print(f"Relatório gerado: {SAIDA}")


if __name__ == "__main__":
    gerar()
