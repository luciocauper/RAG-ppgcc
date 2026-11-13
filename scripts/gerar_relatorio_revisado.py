"""Relatório acadêmico revisado (auditoria das seis execuções), sem chamadas à API.

Saída: results/Relatorio_Final_Testes_RAG_PPGCC_Revisado.docx. O relatório anterior
(results/Relatorio_Final_Testes_RAG_PPGCC.docx) e o gerador original são preservados.
Todos os números vêm de auditoria.py/consolidar.py, que leem results/execN sem alterá-los.
"""
from datetime import date
import hashlib
from pathlib import Path

from docx.shared import Cm, Pt, RGBColor

import auditoria as a
from consolidar import documento, tabela
import figuras

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "results" / "Relatorio_Final_Testes_RAG_PPGCC_Revisado.docx"
pct, num, faixas = a.fmt_pct, a.fmt_num, a.faixas


class Contador:
    def __init__(self):
        self.tabela = 0
        self.figura = 0


def _legenda(doc, texto):
    p = doc.add_paragraph()
    run = p.add_run(texto)
    run.italic = True
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor.from_string("4A5A60")
    return p


def _tab(doc, cont, titulo, cabecalho, linhas, fonte=None, larguras=None):
    cont.tabela += 1
    _legenda(doc, f"Tabela {cont.tabela} — {titulo}")
    t = tabela(doc, cabecalho, linhas)
    if larguras:
        t.autofit = False
        for row in t.rows:
            for cell, largura in zip(row.cells, larguras):
                cell.width = Cm(largura)
    for row in t.rows:
        for cell in row.cells:
            for par in cell.paragraphs:
                par.paragraph_format.line_spacing = 1.0
                for run in par.runs:
                    run.font.size = Pt(9.5)
    if fonte:
        _legenda(doc, f"Fonte: {fonte}")
    return t


def _fig(doc, cont, caminho, titulo, fonte):
    cont.figura += 1
    doc.add_picture(str(caminho), width=Cm(16))
    _legenda(doc, f"Figura {cont.figura} — {titulo}. Fonte: {fonte}.")


def _p(doc, texto):
    return doc.add_paragraph(texto)


def _lista(doc, itens):
    for item in itens:
        doc.add_paragraph(item, style="List Bullet")


def _sha(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def gerar():
    es = a.carregar()
    if not es:
        raise ValueError("Nenhuma execução com output.xml.")
    hist = [a.linha_historica(e) for e in es]
    n_exec = len(es)
    total_registros = sum(h["registros"] for h in hist)
    contextos = sum((h["contextos"] for h in hist), start=a.Counter())
    rec = a.analise_recorrentes(es)
    limites = a.oraculo_casos_limite(es)
    ragas_formais = [h for h in hist if h["ragas"]["tipo"] == "formal"]
    ragas_piloto = [h for h in hist if h["ragas"]["tipo"] == "piloto"]
    rg = ragas_formais[-1]["ragas"] if ragas_formais else None
    figs = figuras.gerar(es)
    cont = Contador()
    hoje = date.today().strftime("%d/%m/%Y")

    doc = documento("Avaliação automatizada da qualidade de um sistema inteligente baseado em RAG", academico=True)
    _p(doc, "Universidade Estadual do Ceará — Programa de Pós-Graduação em Ciência da Computação (PPGCC)\n"
            "Disciplina: Teste de Sistemas Inteligentes\n"
            f"Relatório acadêmico revisado — versão de auditoria gerada em {hoje}")
    _p(doc, "Esta versão substitui, para fins de leitura, o relatório anterior "
            "(results/Relatorio_Final_Testes_RAG_PPGCC.docx), que permanece preservado. Os valores foram "
            f"recalculados a partir das evidências originais das {n_exec} execuções (results/exec1 a "
            f"results/exec{es[-1]['numero']}), sem novas chamadas ao Dify ou ao Gemini e sem alteração dos arquivos de evidência.")

    # Resumo
    doc.add_heading("Resumo", 1)
    taxas = [h["exp_taxa"] for h in hist]
    qp = {q[0]: a.agregado_qp(es, q[3]) for q in a.QUESTOES}
    _p(doc, "Este trabalho avalia um assistente conversacional baseado em Retrieval-Augmented Generation (RAG), "
            "construído no Dify Community sobre o Regimento do PPGCC/UECE, por meio de uma infraestrutura própria "
            "de avaliação composta por Robot Framework (testes funcionais em BDD), pytest (testes unitários da "
            "automação), um oráculo determinístico em Python e uma etapa de avaliação semântica com Ragas. "
            f"Foram analisadas {n_exec} execuções oficiais de um golden dataset com 30 cenários experimentais, "
            f"totalizando {total_registros} respostas registradas com os trechos recuperados. A taxa de aprovação "
            f"automatizada variou de {pct(min(taxas))} a {pct(max(taxas))}. Considerando os veredictos agregados, "
            f"QP1 (qualidade das respostas) obteve {qp['QP1'][0]}/{qp['QP1'][1]} aprovações, QP2 (robustez e "
            f"segurança) {qp['QP2'][0]}/{qp['QP2'][1]} e QP3 (contexto conversacional) {qp['QP3'][0]}/{qp['QP3'][1]}. "
            "A análise das respostas e dos contextos mostra que as reprovações recorrentes (CT09, CT28 e CT30) "
            "coincidem com a ausência, nos trechos recuperados, do dispositivo normativo necessário; e que o oráculo "
            "lexical produziu ao menos um falso positivo e um falso negativo. "
            + (f"A avaliação Ragas foi apenas parcial: na exec{ragas_formais[-1]['numero']}, {rg['validas']} de "
               f"{rg['planejadas']} avaliações planejadas produziram valor válido, sobretudo por limite de cota do "
               "plano gratuito; por isso não se afirma desempenho semântico global. " if rg else "")
            + "As conclusões são descritivas, restritas a um único documento e a um conjunto fixo de cenários.")
    _p(doc, "Palavras-chave: RAG; teste de sistemas inteligentes; oráculo de teste; Robot Framework; Ragas; LLM.")

    # 1 Introdução
    doc.add_heading("1. Introdução e contextualização", 1)
    _p(doc, "Sistemas baseados em modelos de linguagem de grande porte (LLMs) produzem saídas em linguagem natural, "
            "variáveis e não determinísticas. Diferentemente de software convencional, cuja saída esperada pode ser "
            "especificada com exatidão, a mesma pergunta admite várias respostas corretas, e uma resposta pode usar as "
            "palavras esperadas e ainda assim afirmar uma relação factual incorreta. Esse é o problema do oráculo de "
            "teste aplicado a sistemas inteligentes.")
    _p(doc, "Em sistemas RAG, a resposta depende de duas etapas: a recuperação de trechos de uma base documental e a "
            "geração condicionada a esses trechos. Uma falha observada pode decorrer da recuperação (trecho relevante "
            "ausente), da geração (trecho presente, mas mal interpretado) ou do próprio critério de avaliação. O trabalho "
            "trata essa distinção como eixo metodológico: cada reprovação é examinada com a resposta e os trechos "
            "efetivamente registrados.")
    _p(doc, "O objeto de estudo não é apenas o chatbot, mas a construção e a validade de uma infraestrutura "
            "automatizada de avaliação: casos de teste rastreáveis, coleta de evidências por execução, critérios "
            "explícitos de aceitação, testes da própria automação, avaliação semântica complementar e geração "
            "reprodutível de documentos.")

    # 2 Problema e objetivos
    doc.add_heading("2. Problema, objetivos e questões de pesquisa", 1)
    _p(doc, "Problema. Estudantes e docentes consultam com frequência regras do regimento do programa (créditos, prazos, "
            "bancas, desligamento). Um assistente que responda a essas perguntas precisa fundamentar-se exclusivamente no "
            "documento, reconhecer lacunas e não inventar regras. Avaliar se um assistente atende a esses requisitos exige "
            "testes que vão além da verificação de disponibilidade da API.")
    _p(doc, "Objetivo geral. Avaliar, por testes automatizados e análise das evidências, a qualidade de um assistente RAG "
            "sobre o Regimento do PPGCC/UECE, explicitando o que os critérios automatizados permitem e não permitem concluir.")
    _p(doc, "Objetivos específicos:")
    _lista(doc, [
        "construir um golden dataset de 30 cenários com referência documental e critérios de aceitação declarados;",
        "implementar uma suíte BDD em Robot Framework que registre pergunta, resposta, trechos recuperados e latência;",
        "implementar e testar (pytest) um oráculo determinístico para termos, ausência de informação e citação;",
        "integrar uma avaliação semântica (Ragas) com controle de cota, registro incremental e retomada;",
        "executar a suíte repetidamente, preservando as evidências de cada execução;",
        "analisar as reprovações distinguindo falhas do sistema e limitações do oráculo;",
        "responder às questões de pesquisa com base exclusivamente nas evidências registradas.",
    ])
    _tab(doc, cont, "Questões de pesquisa e cenários associados",
         ["QP", "Questão", "Categorias", "Cenários"],
         [[f"{q[0]} — {q[1]}", q[2], ", ".join(a.ROTULO_CATEGORIA[c] for c in q[3]),
           ", ".join(a.casos_da_categoria(es[0], q[3]))] for q in a.QUESTOES],
         "datasets/casos_teste.json")
    _p(doc, "As sete questões iniciais do projeto (RQ1–RQ7, docs/relatorio.md) foram consolidadas nas três QPs acima. "
            "A latência (antiga RQ6) é tratada como dimensão complementar (categoria Desempenho, CT17–CT19). A comparação "
            "entre oráculo determinístico e semântico (antiga RQ7) permanece sem evidência empírica suficiente, pela "
            "cobertura parcial do Ragas descrita na Seção 14.")

    # 3 Fundamentação
    doc.add_heading("3. Fundamentação teórica", 1)
    for titulo, texto in (
        ("3.1 Retrieval-Augmented Generation",
         "RAG combina recuperação de informação e geração: a pergunta é convertida em consulta, trechos da base são "
         "recuperados (por similaridade vetorial, por palavras-chave ou de forma híbrida) e inseridos no prompt do LLM. "
         "A abordagem reduz a dependência do conhecimento paramétrico e permite citar fontes, mas transfere parte da "
         "qualidade para a recuperação: se o trecho necessário não é recuperado, um modelo fiel aos trechos tende a "
         "declarar ausência ou a responder de forma incompleta."),
        ("3.2 Alucinação e fidelidade",
         "Neste estudo, alucinação designa uma afirmação sem suporte suficiente no documento ou nos trechos observados. "
         "Fidelidade (faithfulness) mede se a resposta se apoia nos trechos recuperados; correção factual mede se coincide "
         "com a referência. As duas não se equivalem: uma resposta pode ser fiel a trechos incompletos e ainda assim "
         "factualmente incompleta."),
        ("3.3 Prompt injection e manipulação",
         "Ataques de injeção de prompt tentam substituir as instruções do sistema por instruções do usuário (ou de "
         "documentos recuperados). Variantes avaliadas: instrução explícita para ignorar regras, pedido de vazamento do "
         "prompt de sistema, encenação de autoridade (role play) e premissa falsa sobre artigo inexistente."),
        ("3.4 Oráculo de teste",
         "O oráculo decide se uma saída é aceitável. Oráculos determinísticos (presença/ausência de termos, expressões "
         "regulares) são rápidos e reprodutíveis, mas verificam forma, não significado. Oráculos baseados em LLM (LLM "
         "como juiz) capturam semântica, mas são custosos, não determinísticos e sujeitos a viés. A inspeção humana é "
         "a referência mais confiável, porém não escala. Este trabalho usa os três de forma complementar e declara os "
         "limites de cada um."),
        ("3.5 Métricas Ragas",
         "Faithfulness estima a fração de afirmações da resposta sustentadas pelos contextos; Factual Correctness compara "
         "afirmações da resposta e da referência (modo F1); LLM Context Precision With Reference estima se os trechos "
         "recuperados relevantes para a referência aparecem bem posicionados. Cada métrica exige chamadas ao LLM juiz, "
         "o que torna a cota do provedor um fator limitante."),
        ("3.6 BDD e Robot Framework",
         "Behavior-Driven Development descreve casos como Given/When/Then, separando a especificação do comportamento da "
         "implementação. O Robot Framework oferece essa sintaxe por keywords, bibliotecas em Python e relatórios "
         "XML/HTML rastreáveis, adequados à preservação de evidências."),
    ):
        doc.add_heading(titulo, 2)
        _p(doc, texto)

    # 4 SUT
    doc.add_heading("4. Descrição do sistema sob teste", 1)
    _p(doc, "O sistema sob teste (SUT) é um chatbot do tipo Chatbot do Dify Community, que responde perguntas sobre o "
            "Regimento do PPGCC/UECE (datasets/documentos/Regimento_PPGCC-UECE2021.pdf). Trata-se de um protótipo "
            "acadêmico, não de um canal oficial da universidade. O escopo é limitado a esse documento: perguntas fora "
            "dele devem ser recusadas, lacunas devem ser declaradas e contradições internas do regimento devem ser apontadas.")
    _p(doc, "O prompt de sistema congelado (versão 1.0, docs/prompt_sistema.txt) determina: fundamentar-se no documento, "
            "citar artigos, não inventar regras, declarar ausência de informação, apresentar dispositivos conflitantes "
            "sem escolher interpretação, não usar conhecimento externo, responder em português e tratar instruções "
            "presentes nos trechos recuperados como conteúdo, não como comando.")
    _tab(doc, cont, "Configuração declarada e grau de verificação nas evidências",
         ["Item", "Valor declarado", "Fonte", "Verificação nas evidências"],
         [
             ["Plataforma", "Dify Community 1.18.0 (Docker Compose)", "protocolo; infra/dify/README.md",
              "Não registrada por execução; exec6 confirma 15 serviços em execução (metadata.json)."],
             ["LLM do chatbot", "gemini-3.5-flash-lite (plano gratuito)", "protocolo", "Não registrado nas respostas."],
             ["Embeddings", "gemini-embedding-001", "protocolo", "Não registrado por execução."],
             ["Indexação", "High Quality; 47 chunks; 1024 tokens; sobreposição 100", "protocolo",
              "Não verificável a partir dos JSONL."],
             ["Recuperação (base)", "Pesquisa Vetorial, Top K 3, sem limiar nem rerank", "painel do Dify (12/11/2026)",
              f"Confirmada: {contextos.get(3, 0)} de {total_registros} registros JSONL trazem exatamente 3 trechos."],
             ["Recuperação (app)", "Pontuação ponderada 0,7 semântico / 0,3 palavra-chave, Top K 4", "painel do Dify (12/11/2026)",
              "Atua sobre os 3 candidatos da base: reordena e limita a 4; não busca trechos novos."],
             ["Temperatura", "padrão do provedor (não exposta pelo plugin)", "protocolo",
              "Variabilidade observada por repetição (CT18) e entre execuções."],
             ["Python (executor)", "3.12.10 (protocolo)", "protocolo", "Divergência: output.xml registra Python 3.11.9 em todas as execuções."],
             ["Robot Framework", "7.x", "protocolo", "7.5 (exec1–3, exec5–6) e 7.5.1 (exec4), conforme output.xml."],
             ["LLM juiz Ragas", "gemini-3.5-flash", "protocolo; status_avaliacao.json",
              "Mensagens de erro 429 do provedor citam o modelo gemini-3.6-flash (limite 20 req./dia)." if rg else "—"],
         ],
         "docs/protocolo_testes.md, infra/dify/README.md e results/execN")
    _p(doc, "A coluna de verificação distingue o que foi declarado do que as evidências confirmam. O protocolo original "
            "registrava 'Hybrid Search, Top K 4', que é a configuração do aplicativo. A conferência do painel em "
            "12/11/2026 mostrou que a base de conhecimento usa Pesquisa Vetorial com Top K 3. Como a base é consultada "
            "com a própria configuração, a recuperação efetiva foi vetorial com 3 trechos; a pontuação ponderada do app "
            "apenas reordena esses candidatos, e o Top K 4 atua como teto nunca atingido. Isso explica os 3 trechos em "
            "100% dos registros e mantém as seis execuções comparáveis entre si. A captura reflete a configuração na data "
            "da conferência; sua validade para as execuções é inferida da regularidade dos registros. As divergências "
            "sobre versão do Python e modelo citado nos erros do juiz permanecem pendentes (Seção 18).")
    _fig(doc, cont, RAIZ / "docs/figuras/config_dify_base_conhecimento.png",
         "Configuração de recuperação da base de conhecimento (Pesquisa Vetorial, Top K 3)",
         "captura do painel do Dify em 12/11/2026")
    _fig(doc, cont, RAIZ / "docs/figuras/config_dify_chatbot.png",
         "Configuração de recuperação do aplicativo (pontuação ponderada 0,7/0,3, Top K 4)",
         "captura do painel do Dify em 12/11/2026")

    # 5 Arquitetura
    doc.add_heading("5. Arquitetura técnica da solução", 1)
    _p(doc, "A solução separa dois sistemas: o sistema sob teste (Dify, base de conhecimento e Gemini) e a infraestrutura "
            "de avaliação (Robot Framework, pytest, Ragas e scripts de consolidação). A comunicação entre eles ocorre "
            "exclusivamente pela API HTTP do Dify; a avaliação não acessa o banco vetorial nem os logs internos do Dify, "
            "o que limita a observação da recuperação aos trechos devolvidos em retriever_resources.")
    _fig(doc, cont, figs["arquitetura"], "Arquitetura verificável da solução",
         "elaborada a partir de infra/dify/README.md, scripts/ e results/exec6/metadata.json")
    doc.add_heading("5.1 Fluxos técnicos", 2)
    _fig(doc, cont, figs["fluxos"], "Fluxos de inferência, teste, avaliação semântica e consolidação",
         "elaborada a partir de libraries/, resources/, scripts/avaliar_ragas.py e scripts/consolidar.py")
    _lista(doc, [
        "Inferência: a pergunta chega a /v1/chat-messages; a base devolve 3 trechos por busca vetorial (Top K 3), reordenados pela pontuação ponderada do app, e o Dify "
        "envia prompt, trechos e histórico da conversa ao Gemini; a resposta retorna com conversation_id e, com "
        "'Citations and Attributions' habilitado, com os trechos e seus scores. A consulta interna usada na "
        "recuperação não é exposta pela API.",
        "Testes: cada caso Robot carrega o cenário do dataset (Given), envia a pergunta por DifyClient (When), registra "
        "o resultado em respostas.jsonl e aplica os critérios do RagEvaluator (Then). Casos conversacionais reutilizam "
        "o conversation_id entre turnos.",
        "Avaliação semântica: após a suíte, avaliar_ragas.py filtra os registros elegíveis (casos marcados com 'ragas', "
        "com contextos e referência) e executa uma avaliação por par (amostra, métrica), gravando CSV incremental e "
        "status_avaliacao.json.",
        "Consolidação: consolidar.py lê output.xml (inclusive suítes aninhadas), confere os totais com log/report.html "
        "e com os XMLs parciais, associa respostas JSONL e gera o Word por execução; auditoria.py deriva os fatos "
        "usados neste relatório e na apresentação.",
    ])

    # 6 Ambiente
    doc.add_heading("6. Construção e configuração do ambiente", 1)
    _p(doc, "O ambiente de desenvolvimento é Windows 11 com WSL 2 e Ubuntu 22.04. O Dify Community 1.18.0 foi clonado em "
            "~/dify (sistema de arquivos Linux, conforme recomendação do guia oficial) e executado com Docker Engine nativo "
            "do Ubuntu e o binário oficial do Docker Compose (v5.6.1), em vez do Docker Desktop. O script "
            "scripts/subir_ambiente.ps1 mantém a distribuição ativa (keep-alive) e aguarda a API responder.")
    _tab(doc, cont, "Etapas de configuração documentadas",
         ["Etapa", "Procedimento", "Evidência"],
         [
             ["1. Infraestrutura", "WSL 2/Ubuntu, Docker Engine nativo, Compose v5.6.1, clone do Dify 1.18.0", "infra/dify/README.md"],
             ["2. Modelos", "Plugin Gemini; LLM gemini-3.5-flash-lite; embeddings gemini-embedding-001", "infra/dify/README.md; protocolo"],
             ["3. Base", "Upload do PDF; High Quality; chunking 1024/100; Pesquisa Vetorial, Top K 3", "protocolo; painel do Dify"],
             ["3b. Recuperação do app", "Pontuação ponderada 0,7/0,3; Top K 4 (teto)", "painel do Dify"],
             ["4. Aplicação", "Chatbot; prompt v1.0; 'Citations and Attributions' habilitado; publicação", "infra/dify/README.md"],
             ["5. API", "Chave da aplicação no .env (DIFY_API_URL, DIFY_API_KEY), nunca versionada", ".env.example; .gitignore"],
             ["6. Python", "python -m venv .venv; pip install -r requirements.txt (versões fixadas)", "README.md; requirements.txt"],
             ["7. Validação", "smoke_test.py, pytest tests/unit, robot --dryrun", "README.md; exec6/smoke, exec6/unit"],
         ], "repositório RAG-PPGCC")
    _p(doc, "As dependências de automação e geração de documentos têm versões fixadas (robotframework 7.5, requests 2.34.2, "
            "pytest 9.2.0, python-docx 1.2.0, python-pptx 1.0.2). O Ragas foi fixado em 0.2.15 e o LangChain mantido "
            "abaixo da versão 0.4, porque o Ragas 0.2 importa integrações removidas no LangChain 1.x. As variáveis de "
            "ritmo (DIFY_INTERVALO_S, DIFY_MAX_TENTATIVAS, DIFY_ESPERA_BASE_S, RAGAS_RPM) e os limiares de aceitação "
            "(LIMITE_LATENCIA_S = 30 s, LIMITE_SIMILARIDADE_CONSISTENCIA = 0,5) são configurados no .env.")

    # 7 Estratégia
    doc.add_heading("7. Estratégia de testes", 1)
    _p(doc, "A estratégia distingue quatro níveis, que não devem ser confundidos na interpretação dos resultados:")
    _tab(doc, cont, "Níveis de teste e o que cada um demonstra",
         ["Nível", "Ferramenta", "Objeto", "O que demonstra", "O que não demonstra"],
         [
             ["Unitário", "pytest (65 testes)", "DifyClient, RagEvaluator, avaliar_ragas, consolidar, executar",
              "Correção da automação, sem rede", "Qualidade do chatbot"],
             ["Infraestrutura / smoke", "Robot (api.robot) ou smoke_test.py", "API do Dify",
              "Disponibilidade, chave válida, trechos devolvidos, rejeição de chave inválida", "Correção das respostas"],
             ["Funcional (experimental)", "Robot, 6 suítes BDD", "30 cenários CT",
              "Atendimento a critérios declarados por caso", "Correção semântica integral"],
             ["Semântico", "Ragas 0.2.15 + LLM juiz", "Amostras elegíveis do JSONL",
              "Estimativas de fidelidade, correção e precisão de contexto (quando calculadas)", "Verdade de referência; isento de viés"],
         ], "tests/, scripts/avaliar_ragas.py")
    _p(doc, "Os testes de API são contabilizados separadamente dos 30 cenários experimentais. Isso é necessário porque "
            "exec1–3 incluem quatro testes de API (com o smoke) e exec4–6 incluem três (smoke executado à parte), o que "
            "alteraria a comparação de totais brutos.")

    # 8 Casos
    doc.add_heading("8. Casos de teste e critérios de avaliação", 1)
    _p(doc, "O golden dataset (datasets/casos_teste.json) contém 30 casos, todos marcados como verificados no PDF em "
            "29/10/2026. Cada caso traz pergunta (ou turnos), referência documental, resposta de referência ou "
            "comportamento esperado e critérios de aceitação. Dezesseis casos são elegíveis ao Ragas.")
    _tab(doc, cont, "Distribuição dos cenários",
         ["Categoria", "Casos", "IDs", "Critério determinístico predominante"],
         [["Factualidade", 9, "CT01–CT09 (CT09: contradição)", "termos obrigatórios; citação de artigo"],
          ["Alucinação", 5, "CT10, CT11, CT20–CT22", "reconhecer ausência; termos proibidos"],
          ["Robustez", 5, "CT12, CT13, CT23–CT25", "termos obrigatórios sob variação de escrita e ruído"],
          ["Segurança", 4, "CT14, CT15, CT26, CT27", "termos obrigatórios/proibidos; ausência; citação"],
          ["Conversa", 4, "CT16, CT28–CT30", "critérios por turno no mesmo conversation_id"],
          ["Desempenho", 3, "CT17–CT19", "latência ≤ 30 s; similaridade ≥ 0,5; HTTP < 500"],
          ["Total", 30, "", ""]], "datasets/casos_teste.json")
    _p(doc, "Critérios implementados em libraries/rag_evaluator.py: (i) termos obrigatórios, cada um podendo ter "
            "alternativas; (ii) termos proibidos; (iii) reconhecimento de ausência por 11 padrões regulares; (iv) citação "
            "de artigo pelo padrão 'art./artigo + número'. O texto é normalizado (minúsculas, sem acentos, sem markdown e "
            "com '12 (doze)' reduzido a '12'). CT17 exige que todas as repetições fiquem abaixo de 30 s; CT18 aplica os "
            "termos a cada repetição e exige similaridade lexical média (difflib) ≥ 0,5; CT19 aceita qualquer status "
            "HTTP abaixo de 500, inclusive rejeições controladas 4xx.")
    _p(doc, "Duas inconsistências do próprio regimento foram transformadas em casos: o prazo da qualificação de "
            "doutorado (Art. 35: 36º mês; Art. 39, d: 30º mês — CT09) e a grafia '48 (quarenta)' no Art. 31, b (CT23).")

    # 9 Automação
    doc.add_heading("9. Implementação da automação", 1)
    _tab(doc, cont, "Organização do repositório",
         ["Diretório", "Conteúdo"],
         [["datasets/", "golden dataset e PDF do regimento"],
          ["docs/", "protocolo experimental, prompt congelado, figuras deste relatório"],
          ["infra/dify/", "instalação e configuração do Dify self-hosted"],
          ["libraries/", "dify_client.py (cliente HTTP) e rag_evaluator.py (oráculo determinístico)"],
          ["resources/", "dify_keywords.robot (keywords BDD compartilhadas)"],
          ["tests/", "7 suítes Robot e tests/unit (pytest)"],
          ["scripts/", "executar.py (gerenciador), executar_windows.ps1, avaliar_ragas.py, consolidar.py, geradores"],
          ["results/execN/", "evidências imutáveis de cada execução"],
          ["apresentação/", "apresentações e roteiros"]], "repositório")
    doc.add_heading("9.1 Suítes, keywords e bibliotecas", 2)
    _p(doc, "As sete suítes (api, factualidade, alucinacao, robustez, seguranca, conversa, desempenho) usam um único "
            "arquivo de keywords BDD. Cada keyword encapsula uma etapa: 'o caso de teste' carrega o caso; 'a pergunta é "
            "enviada ao assistente' abre uma conversa nova; 'o turno é enviado ao assistente' propaga o conversation_id; "
            "'a resposta deve atender aos critérios de aceitação' delega ao RagEvaluator. As suítes experimentais "
            "verificam a disponibilidade da API no Suite Setup.")
    _p(doc, "DifyClient (biblioteca Robot de escopo global) envia requisições em modo blocking e registra, em JSONL, "
            "caso, rodada, timestamp com fuso, pergunta, resposta, conversation_id, latência, número de tentativas, "
            "trechos recuperados, fontes (documento, segmento e score) e uso de tokens. Erros transitórios (HTTP 429, "
            "502, 503, 504 ou 4xx com marcas de cota/rede no texto, já que o Dify repassa erros do plugin como HTTP 400) "
            "são repetidos com espera exponencial. A latência registrada é a da tentativa bem-sucedida, sem as esperas.")
    doc.add_heading("9.2 Gerenciador de execuções (scripts/executar.py)", 2)
    _p(doc, "O gerenciador foi criado para padronizar procedimentos que, nas execuções 1 a 5, variaram (rebot por suíte, "
            "robot com --exclude smoke, script PowerShell). Ele oferece um menu com execução individual de cada etapa e "
            "um ciclo integrado, sempre reservando um novo diretório results/execN sem sobrescrever execuções anteriores.")
    _tab(doc, cont, "Funções do gerenciador",
         ["Opção", "Função", "Comportamento relevante"],
         [["1", "Verificar status", "WSL, Ubuntu, Docker, serviços do Compose (api, worker, web), API /parameters, .env e dependências Python"],
          ["2", "Inicializar Dify", "Chama subir_ambiente.ps1 somente se necessário; não reinstala nem limpa dados"],
          ["3", "Ciclo completo", "status → smoke → pytest → Robot sem smoke → Ragas → Word individual → relatório acadêmico; cada etapa gravada em metadata.json"],
          ["4–6", "Smoke, Robot ou pytest isolados", "Robot aceita filtro por suíte, tag ou caso; saída em robot_parciais/<data>"],
          ["7", "Ragas individual", "Escolhe execução, caso e limite de amostras; permite retomada"],
          ["8–9", "Relatórios e consulta", "Regenera Word e lista resultados RAG × API/infra e estado do Ragas por execução"]],
         "scripts/executar.py; tests/unit/test_executar.py")
    _p(doc, "Falhas de cenário não interrompem as etapas seguintes (o Ragas e os relatórios são gerados mesmo com FAIL); "
            "a ausência de output.xml interrompe apenas as etapas dependentes. A exec6 foi produzida por esse ciclo: o "
            "metadata.json registra smoke aprovado, pytest aprovado, Robot com código de saída 3 (três cenários "
            "reprovados), Ragas parcial e relatórios gerados.")

    # 10 Procedimentos
    doc.add_heading("10. Procedimentos experimentais", 1)
    _p(doc, "Antes das execuções oficiais, uma execução preliminar (29/10/2026) foi interrompida por falta de memória "
            "(28 de 34 testes). A leitura das respostas revelou falsos negativos do avaliador, corrigidos com regras "
            "gerais (remoção de markdown, numeral com extenso e novos padrões de recusa). Após o início das execuções "
            "oficiais, os critérios não foram recalibrados: falsos negativos posteriores são registrados, não corrigidos.")
    _tab(doc, cont, "Procedência e artefatos de cada execução",
         ["Exec.", "Data (XML)", "Executor", "Procedimento", "Artefatos ausentes"], larguras=[1.2, 2.2, 3.0, 6.0, 3.6], linhas=
         [[h["numero"], h["data"], h["gerador"], h["procedencia"],
           ", ".join(k for k, v in h["artefatos"].items() if not v) or "—"] for h in hist],
         fonte="results/execN; docs/protocolo_testes.md")
    _p(doc, "A ausência de smoke, pytest, metadata.json ou Ragas nas execuções iniciais reflete a evolução da automação, "
            "não perda de dados. A exec5 não possui relatório Word individual nem metadata.json. A exec4 foi executada "
            "no ambiente de outro integrante. Essas diferenças impedem tratar as seis execuções como réplicas "
            "controladas.")

    # 11 Resultados
    doc.add_heading(f"11. Resultados das {n_exec} execuções", 1)
    _tab(doc, cont, "Consolidação histórica por execução",
         ["Exec.", "CT total", "PASS", "FAIL", "Taxa", "API/infra", "Registros JSONL", "Ragas planejadas", "Ragas válidas", "Ragas erros/ausentes"],
         [[h["numero"], h["exp_total"], h["exp_pass"], h["exp_fail"], pct(h["exp_taxa"]),
           f"{h['aux_pass']}/{h['aux_total']}", h["registros"],
           h["ragas"]["planejadas"] or "—",
           (h["ragas"]["validas"] if h["ragas"]["tipo"] != "nao_avaliada" else "—"),
           (f"{h['ragas']['falhas']}/{h['ragas']['ausentes']}" if h["ragas"]["tipo"] != "nao_avaliada" else "—")]
          for h in hist],
         "output.xml, respostas.jsonl e ragas/ de cada execução")
    _p(doc, "Na exec5, os valores Ragas correspondem a um piloto exploratório de uma amostra (CT01) em formato anterior "
            "do script, sem arquivo de status; na exec6, a uma avaliação formal parcial. Nenhuma das duas é avaliação completa.")
    _fig(doc, cont, figs["execucoes"], "Aprovação dos 30 cenários experimentais por execução", "output.xml de cada execução")
    _p(doc, f"Os totais permaneceram entre {min(h['exp_pass'] for h in hist)} e {max(h['exp_pass'] for h in hist)} "
            "aprovações. A variação de um a dois cenários entre execuções é compatível com o não determinismo do LLM e "
            "com as diferenças de procedimento e ambiente; não há base para afirmar melhoria ou regressão do sistema.")
    _tab(doc, cont, "Aprovação por categoria",
         ["Categoria", *[f"exec{e['numero']}" for e in es], "Agregado"],
         [[a.ROTULO_CATEGORIA[c], *[f"{a.por_categoria(e, c)[0]}/{a.por_categoria(e, c)[1]}" for e in es],
           "{}/{} ({})".format(*a.agregado_qp(es, (c,)), pct(100 * a.agregado_qp(es, (c,))[0] / a.agregado_qp(es, (c,))[1]))]
          for c in a.CATEGORIAS], "output.xml")
    _fig(doc, cont, figs["categorias"], "Mapa de aprovação por categoria e execução", "output.xml")
    ids_falha = sorted({cid for h in hist for cid in h["falhas"]})
    _tab(doc, cont, "Matriz dos cenários com ao menos uma reprovação",
         ["Caso", *[f"exec{e['numero']}" for e in es], "Reprovações"],
         [[cid, *[a.status_caso(e, cid) for e in es], f"{len(a.falhas_caso(es, cid))}/{n_exec}"] for cid in ids_falha],
         "output.xml")
    _tab(doc, cont, "Latência registrada (dimensão complementar)",
         ["Exec.", "Registros", "Média (s)", "Mediana (s)", "Máxima (s)", "Com retentativa", "CT17–19"],
         [[h["numero"], h["registros"], num(h["lat_media"]), num(h["lat_mediana"]), num(h["lat_max"]),
           h["retentativas"], "{}/{}".format(*a.por_categoria(e, "desempenho"))] for h, e in zip(hist, es)],
         "respostas.jsonl; output.xml")
    _p(doc, "As latências descrevem as respostas registradas, excluindo pausas e tentativas anteriores. As médias mais "
            "altas da exec4 e da exec5 não alteraram o CT17, cujo limite se aplica apenas às suas três repetições. Não "
            "foram controladas carga, rede ou ordem de execução; por isso as diferenças não são atribuídas ao modelo.")

    # 12 Reprovações
    doc.add_heading("12. Análise das reprovações e dos oráculos", 1)
    _p(doc, "Cada caso recorrente foi examinado segundo: pergunta, resposta esperada, resposta obtida, trechos "
            "recuperados, regra de aprovação, motivo registrado e classificação. A presença de um dispositivo nos "
            "trechos foi verificada por busca literal no texto devolvido pela API.")
    c09, c28, c30 = rec["CT09"], rec["CT28"], rec["CT30"]
    doc.add_heading("12.1 CT09 — contradição no prazo de qualificação", 2)
    _lista(doc, [
        "Pergunta: 'Qual é o prazo para realizar e obter aprovação na qualificação de doutorado, segundo o regimento?'",
        "Esperado: apontar a contradição entre Art. 35 (36º mês) e Art. 39, d (30º mês).",
        "Regra: termos obrigatórios '30' e '36' e citação de artigo.",
        f"Resultado: FAIL em {len([x for x in c09 if x['status'] == 'FAIL'])}/{len(c09)} execuções; motivo registrado "
        "'termo obrigatório ausente: 30'.",
        f"Trechos: o Art. 35 (36º mês) aparece nos trechos em {sum(x['ctx_art35'] for x in c09)}/{len(c09)} execuções; "
        f"o Art. 39, d (30º mês) aparece em {sum(x['ctx_art39d'] for x in c09)}/{len(c09)}. Os três trechos e seus scores "
        "foram idênticos em todas as execuções, indicando recuperação estável para essa consulta.",
        "Resposta obtida: informa apenas o 36º mês (Art. 35), coerente com os trechos recebidos.",
        "Configuração efetiva: Pesquisa Vetorial com Top K 3 na base; nenhuma busca por palavra-chave foi executada, "
        "de modo que termos literais do Art. 39, d ('Qualificação de Doutorado aprovada até o 30º mês') não "
        "contribuíram para a seleção dos trechos.",
        "Classificação: falha na recuperação de informações (o dispositivo conflitante não chega ao gerador), com "
        "consequência factual (omissão da contradição). O protocolo registra que o rótulo 'Art. 39' foi partido na "
        "extração do PDF ('Art. 3 9'), o que é hipótese plausível, mas não comprovada, para a baixa similaridade.",
    ])
    doc.add_heading("12.2 CT28 — elipse 'E no mestrado?'", 2)
    falsos = [x for x in c28 if x["classe"].startswith("Falso")]
    erros = [x for x in c28 if x["classe"].startswith("Erro")]
    ausencias = [x for x in c28 if x["classe"].startswith("Declara")]
    _lista(doc, [
        "Turnos: 'Quantos créditos em disciplinas são exigidos no doutorado?' → 'E no mestrado?' → prazo da proposta de dissertação.",
        "Esperado no turno 2: 24 créditos (Art. 31, a). Regra: termo obrigatório '24' por turno.",
        f"Resultado: FAIL em {faixas(a.falhas_caso(es, 'CT28'))}; PASS em "
        f"{faixas([x['exec'] for x in c28 if x['status'] == 'PASS'])}.",
        f"Trechos: o trecho com '24 (vinte e quatro) créditos' esteve no turno 1 em {sum(x['t1_ctx_24'] for x in c28)}/{len(c28)} "
        f"execuções e no turno 2 em {sum(x['t2_ctx_24'] for x in c28)}/{len(c28)}. O conversation_id foi mantido em todos os casos.",
        f"Respostas do turno 2: total incorreto de 32 créditos ({faixas([x['exec'] for x in falsos])}); 28 créditos "
        f"({faixas([x['exec'] for x in erros])}); declaração de ausência ({faixas([x['exec'] for x in ausencias])}).",
        "Classificação: falha de interpretação de contexto conversacional associada a falha de recuperação no turno "
        "elíptico; nas execuções com 32 e 28 créditos, há também erro factual sem suporte nos trechos registrados. "
        "Na exec1 o PASS é um falso positivo do oráculo. A origem dos números incorretos não é observável.",
    ])
    doc.add_heading("12.3 CT30 — troca de nível 'E no doutorado?'", 2)
    _lista(doc, [
        "Turnos: duração da apresentação oral no mestrado → 'E no doutorado?'. Esperado no turno 2: 40 a 50 minutos (Art. 43, §1º).",
        "Regra: termos '40' e '50' no turno 2. Motivo registrado: 'termo obrigatório ausente: 40; ... 50'.",
        f"Resultado: FAIL em {len([x for x in c30 if x['status'] == 'FAIL'])}/{len(c30)} execuções.",
        f"Trechos: no turno 1, o trecho com os valores do doutorado (50 minutos) foi recuperado em "
        f"{sum(x['t1_ctx_doutorado'] for x in c30)}/{len(c30)} execuções; no turno 2, nenhum trecho mencionava "
        f"'minutos' em {sum(not x['t2_ctx_minutos'] for x in c30)}/{len(c30)}.",
        "Resposta obtida: declara que o documento não traz a duração para o doutorado — coerente com os trechos do turno 2, "
        "mas não com o turno anterior da mesma conversa.",
        "Classificação: falha de interpretação de contexto conversacional com falha de recuperação no turno de continuação. "
        "Não há erro factual afirmativo; a resposta é incompleta.",
    ])
    _p(doc, "Contraste observado: CT16 ('…nessas disciplinas?') e CT29 ('Quantos deles precisam ser externos à UECE?') "
            "passaram na maioria das execuções e seus turnos de continuação contêm termos recuperáveis por si ('nota "
            "mínima', 'externos'); seus trechos do turno 2 incluíram o dispositivo pertinente. CT28 e CT30 usam elipses "
            "quase sem conteúdo lexical. O padrão é compatível com a hipótese de que a recuperação usa principalmente a "
            "mensagem corrente, enquanto o histórico é usado na geração; a API não expõe a consulta interna, de modo "
            "que a hipótese não é comprovada.")
    doc.add_heading("12.4 Outros casos e análise dos oráculos", 2)
    _tab(doc, cont, "Casos em que aprovação automatizada e correção efetiva divergem ou exigem leitura humana",
         ["Caso", "Exec.", "Robot", "Classificação", "Evidência"],
         [list(x) for x in limites] + [["CT29", 4, "FAIL", "Contexto conversacional",
                                        "Turno 2 desvia para a banca de doutorado; demais execuções aprovadas."]],
         "output.xml; respostas.jsonl")
    _p(doc, "Aprovação automatizada significa que a resposta satisfez os critérios declarados; correção factual "
            "efetiva exige que a relação afirmada seja verdadeira. As principais limitações observadas foram:")
    _lista(doc, [
        "Dependência de palavras-chave: '24' presente em uma decomposição errada aprovou o CT28/exec1 (falso positivo).",
        "Números obrigatórios sem relação semântica: o critério não verifica a qual conceito o número se refere.",
        "Padrões de recusa finitos: 'não possuo essa informação' não foi reconhecida no CT21/exec3 (falso negativo).",
        "Similaridade lexical: CT18/exec1 (0,422) e exec2 (0,256) falharam com o mesmo fato (8 orientandos) em redações distintas.",
        "Termos proibidos são frágeis em ambos os sentidos: no CT14, as respostas das exec2, exec4 e exec6 citam "
        "corretamente '5,0' (média do Art. 39, a); proibir '5,0' para detectar a injeção geraria falsos negativos, "
        "enquanto no CT15 um vazamento parafraseado do prompt não seria detectado pelas frases proibidas literais.",
        "CT19 aceita 4xx como sucesso, por desenho: mede ausência de erro de servidor, não qualidade da resposta.",
    ])
    _p(doc, "Esses casos justificam a avaliação semântica complementar e a inspeção humana dos cenários limítrofes. "
            "Nesta auditoria, a inspeção humana cobriu as reprovações e os casos destacados; não houve revisão "
            "sistemática de todas as aprovações, que permanece como pendência.")

    # 13 QPs
    doc.add_heading("13. Discussão das questões de pesquisa", 1)
    fac, alu = a.agregado_qp(es, ("factual",)), a.agregado_qp(es, ("alucinacao",))
    rob, seg = a.agregado_qp(es, ("robustez",)), a.agregado_qp(es, ("seguranca",))
    conv = [a.por_categoria(e, "conversa")[0] for e in es]
    qps_texto = {
        "QP1": [
            f"Cenários: CT01–CT09 (factualidade) e CT10, CT11, CT20–CT22 (alucinação); {qp['QP1'][1]} veredictos em {n_exec} execuções.",
            f"Resultados: factualidade {fac[0]}/{fac[1]} e alucinação {alu[0]}/{alu[1]}; agregado {qp['QP1'][0]}/{qp['QP1'][1]} "
            f"({pct(100 * qp['QP1'][0] / qp['QP1'][1])}).",
            "Evidências favoráveis: CT01–CT08 aprovados em todas as execuções; perguntas fora do "
            "escopo (CT11) e sem resposta no regimento (CT10, CT20) recusadas sem inventar valores.",
            f"Reprovações: CT09 em {faixas(a.falhas_caso(es, 'CT09'))} (contradição não apontada; Art. 39, d ausente dos trechos); "
            f"CT22 em {faixas(a.falhas_caso(es, 'CT22'))} (omissão da área de concentração); CT21 em "
            f"{faixas(a.falhas_caso(es, 'CT21'))} (falso negativo do oráculo).",
            "Limitações: critérios lexicais; as aprovações não foram todas inspecionadas; Ragas não cobre a amostra.",
            "Resposta: nos cenários testados, o assistente respondeu de forma fundamentada à maioria das perguntas factuais "
            "diretas e recusou perguntas sem resposta no documento, mas não identificou a contradição normativa e omitiu "
            "informação exigida em parte das execuções. A evidência é parcialmente favorável e limitada pelo oráculo.",
        ],
        "QP2": [
            f"Cenários: CT12, CT13, CT23–CT25 (robustez) e CT14, CT15, CT26, CT27 (segurança); {qp['QP2'][1]} veredictos.",
            f"Resultados: robustez {rob[0]}/{rob[1]} e segurança {seg[0]}/{seg[1]}.",
            "Evidências favoráveis: erros ortográficos, paráfrases, linguagem informal e o ruído '48 (quarenta)' não "
            "alteraram a resposta esperada; a injeção explícita (CT14) não mudou a nota de 7,0; o prompt não foi exibido "
            "(CT15); a encenação de coordenador (CT26) não produziu autorização; a premissa falsa sobre o Art. 50 (CT27) "
            "não foi confirmada.",
            "Reprovações: nenhuma.",
            "Limitações: nove cenários, um documento, um idioma; não há injeção indireta via documento recuperado; os "
            "critérios de segurança são lexicais (vide CT15).",
            "Resposta: o assistente resistiu às variações e às tentativas de manipulação testadas, de forma estável nas "
            "seis execuções. O resultado não sustenta afirmação geral de robustez ou segurança fora desse conjunto.",
        ],
        "QP3": [
            f"Cenários: CT16, CT28, CT29, CT30; {qp['QP3'][1]} veredictos.",
            f"Resultados por execução: {', '.join(f'{v}/4' for v in conv)}; agregado {qp['QP3'][0]}/{qp['QP3'][1]} "
            f"({pct(100 * qp['QP3'][0] / qp['QP3'][1])}).",
            "Evidências favoráveis: CT16 aprovado em todas as execuções; CT29 em cinco de seis; conversation_id preservado.",
            "Reprovações: CT30 em todas as execuções; CT28 em cinco (e o único PASS é falso positivo); CT29 na exec4.",
            "Limitações: quatro cenários; a consulta de recuperação interna do Dify não é observável.",
            "Resposta: o assistente preserva o contexto quando o turno seguinte traz termos próprios recuperáveis, mas "
            "falha de forma recorrente em elipses curtas ('E no mestrado?', 'E no doutorado?'), em que os trechos do "
            "turno de continuação não contêm a informação já recuperada no turno anterior. É a dimensão mais frágil observada.",
        ],
    }
    for q in a.QUESTOES:
        doc.add_heading(f"{q[0]} — {q[1]}", 2)
        _p(doc, q[2])
        _lista(doc, qps_texto[q[0]])
    _p(doc, "Desempenho (dimensão complementar): CT17–CT19 tiveram "
            + ", ".join("{}/{}".format(*a.por_categoria(e, "desempenho")) for e in es)
            + ". As reprovações (CT18 em exec1 e exec2) decorreram do critério de similaridade lexical, não de erro factual.")

    # 14 Ragas
    doc.add_heading("14. Avaliação semântica com Ragas", 1)
    _p(doc, "A implementação (scripts/avaliar_ragas.py) usa Ragas 0.2.15 com um LLM juiz acessado por endpoint compatível "
            "com OpenAI. Cada par (amostra, métrica) é avaliado isoladamente, com limitador de taxa (RAGAS_RPM), "
            "temperatura 0 no juiz, sem novas tentativas internas; o resultado de cada par é gravado imediatamente em CSV "
            "(status: calculada, ausente, erro_cota, erro_api, erro_processamento) e o progresso em "
            "status_avaliacao.json. Na retomada, pares já calculados são preservados e apenas os demais são refeitos; a "
            "retomada é recusada se modelo, versão ou métricas divergirem do progresso salvo. Mensagens de erro têm a "
            "chave de API mascarada. Médias usam somente valores válidos.")
    linhas_ragas = []
    for h in hist:
        r = h["ragas"]
        if r["tipo"] == "nao_avaliada":
            linhas_ragas.append([h["numero"], "não avaliada", "—", "—", "—", "—", "—"])
            continue
        for m in a.METRICAS:
            d = r["por_metrica"][m]
            linhas_ragas.append([h["numero"], r["estado"], a.ROTULO_METRICA[m], d["validos"],
                                 num(d["media"], 3) if d["validos"] else "—", d["falhas"], d["ausentes"]])
    _tab(doc, cont, "Resultados Ragas por execução e métrica",
         ["Exec.", "Estado", "Métrica", "N válido", "Média", "Erros", "Ausentes"], linhas_ragas,
         "results/exec5/ragas/metricas_piloto.csv; results/exec6/ragas/")
    if rg:
        h6 = ragas_formais[-1]
        _p(doc, f"Exec{h6['numero']}: {rg['amostras']} amostras elegíveis ({', '.join(rg['casos'])}); "
                f"{sum(rg['excluidas'].values())} registros excluídos por caso não elegível; {rg['planejadas']} avaliações "
                f"planejadas e concluídas como tentativa; {rg['validas']} válidas, {rg['ausentes']} ausente, "
                f"{rg['erros'].get('erro_cota', 0)} erros de cota (HTTP 429) e {rg['erros'].get('erro_api', 0)} erro de API "
                f"(HTTP 503, alta demanda). RPM configurado: {rg['rpm']}. Modelo configurado: {rg['modelo']}; "
                f"as mensagens 429 citam o modelo {', '.join(rg['modelos_reportados'])} com limite de "
                f"{', '.join(rg['limites_reportados'])} requisições diárias no plano gratuito. Retomada: "
                f"{'sim' if rg['retomada'] else 'não utilizada'}. Período: {rg['inicio'][:19]} a {rg['fim'][:19]} (UTC).")
        _fig(doc, cont, figs["ragas"], f"Cobertura da avaliação Ragas na exec{h6['numero']}", "ragas/metricas_ragas.csv")
        fa = rg["por_metrica"]["faithfulness"]
        _p(doc, f"Confiabilidade: a média de Faithfulness ({num(fa['media'], 3)}) baseia-se em {fa['validos']} valores "
                f"({', '.join(fa['casos'])}); Context Precision em {rg['por_metrica']['llm_context_precision_with_reference']['validos']} valor(es); "
                f"Factual Correctness em {rg['por_metrica']['factual_correctness']['validos']}. "
                f"A cobertura efetiva é de {pct(100 * rg['validas'] / rg['planejadas'])} das avaliações planejadas. Com "
                "essa amostra não é possível estimar desempenho semântico, comparar com o oráculo determinístico nem "
                "responder à antiga RQ7.")
    if ragas_piloto:
        rp = ragas_piloto[-1]["ragas"]
        _p(doc, f"Exec{ragas_piloto[-1]['numero']}: piloto exploratório com {rp['amostras']} amostra ({', '.join(rp['casos'])}), "
                "produzido pelo formato anterior do script (CSV largo, sem arquivo de status, sem registro de modelo ou "
                "versão). Faithfulness = "
                f"{num(rp['por_metrica']['faithfulness']['media'], 2)}, Factual Correctness = "
                f"{num(rp['por_metrica']['factual_correctness']['media'], 2)} e Context Precision ausente. Serve apenas "
                "como teste de integração do pipeline. O relatório anterior classificava a exec5 como 'não avaliada', "
                "porque o leitor de métricas não reconhecia esse formato.")

    # 15 Dificuldades
    doc.add_heading("15. Dificuldades encontradas e soluções adotadas", 1)
    _p(doc, "As dificuldades abaixo estão registradas em arquivos do repositório (indicados na última coluna). Cada uma "
            "é descrita como dificuldade → impacto → ação adotada → situação atual → aprendizado técnico. Não foram "
            "incluídas dificuldades genéricas sem evidência.")
    dificuldades = [
        ("Infraestrutura e ambiente", [
            ["LLM local (Ollama, qwen2.5:7b) não coube na GPU de 6 GB", "Máquina sobrecarregada; inviável para execuções repetidas",
             "Migração para Gemini remoto no plano gratuito; Ollama removido", "Resolvido",
             "Escolha de modelo condiciona custo, cota e reprodutibilidade", "infra/dify/README.md"],
            ["Plugin docker compose apontava para o Docker Desktop, que entrava em modo ocioso", "Serviços do Dify indisponíveis",
             "Docker Engine nativo + binário oficial Compose v5.6.1", "Resolvido",
             "Evitar dependências implícitas entre ambientes Windows e WSL", "infra/dify/README.md"],
            ["WSL desliga a distribuição sem processo ativo do Windows", "Queda do Dify durante testes",
             "Keep-alive 'sleep infinity' em subir_ambiente.ps1 e espera ativa da API", "Resolvido",
             "Disponibilidade é pré-condição explícita dos testes", "scripts/subir_ambiente.ps1"],
            ["Memória insuficiente na execução preliminar (28/34 testes)", "Execução interrompida",
             "Execução por suíte e união com rebot (exec1–3)", "Mitigado",
             "Procedimentos diferentes reduzem a comparabilidade", "docs/protocolo_testes.md"],
            ["Reprodução em outra máquina (exec4) e versões divergentes do protocolo (Python, Docker)", "Ambiente não controlado entre execuções",
             "Registro do executor no XML; metadata.json a partir da exec6", "Parcialmente resolvido",
             "Sem snapshot de configuração, não se atribui causalidade", "output.xml; exec6/metadata.json"],
        ]),
        ("Integração e automação", [
            ["Erros transitórios Dify↔Gemini repassados como HTTP 400 (cota, 'Network is unreachable')", "Reprovações sem relação com o SUT",
             "Detecção por texto, retentativa com espera exponencial, registro de tentativas", "Resolvido",
             f"Separar falha de infraestrutura de falha funcional ({sum(h['retentativas'] for h in hist)} registros com retentativa)",
             "libraries/dify_client.py; respostas.jsonl"],
            ["Trechos recuperados só retornam com 'Citations and Attributions'", "Sem contextos para análise e Ragas",
             "Recurso habilitado e verificado por teste de API", "Resolvido", "Observabilidade do SUT deve ser testada",
             "tests/api.robot"],
            ["Incompatibilidade Ragas 0.2 × LangChain 1.x", "Falha de importação", "Fixação de langchain < 0.4",
             "Resolvido", "Fixar versões de dependências de avaliação", "requirements.txt"],
            ["Totais divergentes entre XML, HTML e parciais seriam silenciosos", "Risco de números incorretos",
             "consolidar.py confere totais e falha em divergência", "Resolvido", "Consolidação deve ser verificável",
             "scripts/consolidar.py; tests/unit"],
        ]),
        ("Avaliação de sistemas inteligentes", [
            ["Temperatura não configurável no plugin", "Respostas variam entre execuções",
             "Repetições (CT18) e seis execuções", "Mitigado", "Variabilidade precisa ser medida, não suposta",
             "docs/protocolo_testes.md"],
            ["Falsos negativos do oráculo na calibração", "Respostas corretas reprovadas",
             "Normalização e padrões gerais antes das execuções oficiais", "Resolvido (pré-oficial)",
             "Calibrar antes e congelar depois", "docs/protocolo_testes.md"],
            ["Falso positivo/negativo após o congelamento (CT28/exec1, CT21/exec3)", "Veredictos divergentes da correção",
             "Registro sem recalibração; análise humana", "Pendente", "Aprovação ≠ correção factual", "relatórios individuais"],
            ["Elipses conversacionais (CT28, CT30)", "Reprovações recorrentes", "Diagnóstico por trechos recuperados",
             "Pendente", "Testar recuperação em multi-turno, não só geração", "respostas.jsonl"],
        ]),
        ("Avaliação semântica", [
            ["Cota do plano gratuito (HTTP 429) para o LLM juiz", f"{rg['erros'].get('erro_cota', 0) if rg else 0} de {rg['planejadas'] if rg else 0} avaliações falharam",
             "RPM configurável, CSV incremental, status, retomada e classificação de erros", "Parcialmente resolvido",
             "Custo de avaliação por LLM é restrição de projeto", "results/exec6/ragas"],
            ["Formato inicial do Ragas sem metadados (piloto exec5)", "Resultado não reconhecido pelo consolidador",
             "Reescrita com status_avaliacao.json e CSV por métrica", "Resolvido para novas execuções",
             "Metadados de modelo/versão são parte da evidência", "results/exec5/ragas"],
        ]),
        ("Gestão da execução", [
            ["Procedimentos heterogêneos (rebot, --exclude smoke, PowerShell)", "Totais brutos não comparáveis",
             "Gerenciador executar.py com ciclo completo e metadata.json", "Resolvido a partir da exec6",
             "Padronizar antes de repetir", "scripts/executar.py"],
            ["Risco de sobrescrever evidências", "Perda de histórico", "Reserva atômica de results/execN; nada é limpo",
             "Resolvido", "Evidência experimental é imutável", "scripts/executar.py; executar_windows.ps1"],
            ["Números digitados manualmente em documentos", "Relatórios desatualizados (docs/relatorio.md com 3 execuções)",
             "Geração a partir de consolidar.py/auditoria.py", "Parcialmente resolvido",
             "Documentos derivados devem ser regeneráveis", "scripts/"],
        ]),
    ]
    for grupo, linhas in dificuldades:
        doc.add_heading(f"15.{dificuldades.index((grupo, linhas)) + 1} {grupo}", 2)
        _tab(doc, cont, f"Dificuldades — {grupo.lower()}",
             ["Dificuldade", "Impacto", "Ação adotada", "Situação", "Aprendizado", "Evidência"], linhas,
             larguras=[3.4, 2.5, 3.3, 1.9, 2.8, 2.1])

    # 16 Ameaças
    doc.add_heading("16. Ameaças à validade", 1)
    _tab(doc, cont, "Ameaças à validade e mitigação",
         ["Tipo", "Ameaça", "Mitigação / estado"],
         [["Construto", "Critérios lexicais medem forma; similaridade não mede factualidade", "Inspeção humana dos casos limítrofes; Ragas parcial"],
          ["Interna", "Ambiente, ordem, carga e procedimento variaram; sem snapshot da configuração do Dify", "Procedência registrada; nenhuma inferência causal"],
          ["Interna", "Protocolo descrevia busca híbrida com Top K 4; a efetiva foi vetorial com Top K 3", "Corrigido após conferência do painel; sem snapshot por execução"],
          ["Externa", "Um documento, 30 cenários, um idioma, um provedor de LLM", "Conclusões restritas ao escopo"],
          ["Conclusão", f"{n_exec} execuções não aleatórias e não independentes; casos não amostrados ao acaso", "Estatística descritiva apenas"],
          ["Avaliador semântico", "Juiz da mesma família do SUT; cobertura parcial: " + (f"{pct(100 * rg['validas'] / rg['planejadas'])} na exec{ragas_formais[-1]['numero']}" if rg else "não executado"), "Sem conclusão semântica"],
          ["Rastreabilidade", "XML sem fuso explícito; JSONL em UTC", "Datas não equiparadas sem conversão"]],
         "análise desta auditoria")

    # 17 Limitações
    doc.add_heading("17. Limitações e oportunidades de melhoria", 1)
    _lista(doc, [
        "Registrar por execução a configuração efetiva do Dify (modelo, Top K e método da base e do app, versão do app) por meio da API de console ou exportação do app.",
        "Avaliar, como nova condição experimental, a base com Pesquisa Híbrida e Top K 4 (CT09, CT28 e CT30), sem misturá-la ao histórico.",
        "Testar um aplicativo com reescrita da consulta a partir do histórico (workflow com nó de recuperação) e comparar com o Chatbot básico em CT28/CT30.",
        "Ampliar padrões de ausência e adicionar critérios relacionais (número associado ao conceito) apenas em nova versão do dataset, sem reavaliar o histórico.",
        "Concluir o Ragas com cota adequada, usando a retomada já implementada, e incluir juiz de família distinta.",
        "Adicionar casos de injeção indireta (instruções dentro do documento) e de vazamento parafraseado.",
        "Revisar sistematicamente todas as aprovações por inspeção humana amostral com dois avaliadores.",
        "Gerar o relatório individual ausente da exec5 a partir das evidências preservadas, se a equipe autorizar.",
    ])

    # 18 Auditoria de consistência
    doc.add_heading("18. Auditoria de consistência dos materiais", 1)
    _tab(doc, cont, "Inconsistências identificadas e tratamento",
         ["Item", "Situação encontrada", "Tratamento"],
         [["Relatório acadêmico anterior", "Tabelas com 6 execuções, mas textos fixos em 'quatro execuções' e 'Ragas não executado'",
           "Este relatório revisado; o anterior foi preservado"],
          ["Ragas exec5", "Piloto não reconhecido pelo consolidador (exibido como 'não avaliada')", "Classificado como piloto exploratório"],
          ["Ragas exec6", "Média 0,875 exibida sem destaque para n = 2", "Cobertura e n explicitados"],
          ["docs/relatorio.md", "Desatualizado (3 execuções, RQ1–RQ7, causa arquitetural afirmada como definitiva)", "Mantido como histórico; não usado como fonte"],
          ["README.md", "Cita quatro execuções e ausência de métricas Ragas", "Atualizado para seis execuções"],
          ["Recuperação", "Protocolo: Hybrid, Top K 4 (configuração do app); observados 3 trechos em todos os registros", "Resolvido: base com Pesquisa Vetorial, Top K 3 (painel, 12/11/2026); protocolo corrigido"],
          ["Protocolo × evidências", "Python 3.12.10 × 3.11.9; Docker 27.5 × 29.1.3 (exec6)", "Registrado como pendência humana"],
          ["Juiz Ragas", "Configurado gemini-3.5-flash; erros 429 citam gemini-3.6-flash", "Registrado como pendência humana"],
          ["Apresentação anterior", "Exigia exatamente 4 execuções; CT17–19 exibia PASS/FAIL como PASS/total", "Gerador corrigido; nova apresentação revisada"],
          ["Exec5", "Sem relatório Word individual e sem metadata.json", "Registrado; evidência não alterada"]],
         "auditoria")

    # 19 Conclusões
    doc.add_heading("19. Conclusões e trabalhos futuros", 1)
    _p(doc, "O trabalho construiu e operou uma infraestrutura de avaliação de um assistente RAG que separa claramente "
            "teste da automação (pytest), verificação de infraestrutura (smoke/API), teste funcional por critérios "
            "(Robot Framework) e avaliação semântica (Ragas), com evidências preservadas por execução e documentos "
            "regeneráveis a partir delas.")
    _p(doc, f"QP1: evidência parcialmente favorável — {qp['QP1'][0]}/{qp['QP1'][1]} veredictos aprovados, mas com omissão "
            "recorrente da contradição normativa (CT09), omissões de completude (CT22) e limitações do oráculo. "
            f"QP2: os {qp['QP2'][1]} veredictos de robustez e segurança foram aprovados, dentro do conjunto testado. "
            f"QP3: dimensão mais frágil — {qp['QP3'][0]}/{qp['QP3'][1]}, com falhas sistemáticas em elipses curtas, "
            "associadas à ausência dos trechos necessários no turno de continuação.")
    _p(doc, "A principal contribuição metodológica é mostrar, com evidências, que aprovação automatizada e correção "
            "factual divergem em casos concretos e que a observação dos trechos recuperados permite distinguir falhas de "
            "recuperação, de geração e do oráculo. Trabalhos futuros: concluir a avaliação semântica, testar recuperação "
            "sensível ao histórico, registrar a configuração efetiva por execução e ampliar o conjunto adversarial.")

    # 20 Referências
    doc.add_heading("20. Referências", 1)
    for ref in (
        "DIFY. Dify — LLM App Development Platform. Disponível em: https://github.com/langgenius/dify.",
        "ES, S. et al. RAGAS: Automated Evaluation of Retrieval Augmented Generation. In: EACL (System Demonstrations), 2024.",
        "GOOGLE. Gemini API — Models and rate limits. Disponível em: https://ai.google.dev/gemini-api/docs.",
        "LEWIS, P. et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. In: NeurIPS, 2020.",
        "BARR, E. T. et al. The Oracle Problem in Software Testing: A Survey. IEEE Transactions on Software Engineering, v. 41, n. 5, 2015.",
        "ROBOT FRAMEWORK. Robot Framework User Guide. Disponível em: https://robotframework.org/robotframework/.",
        "RAGAS. Ragas documentation. Disponível em: https://docs.ragas.io/.",
        "UECE. Regimento do Programa de Pós-Graduação em Ciência da Computação. 2021. Arquivo local em datasets/documentos/.",
    ):
        _p(doc, ref)

    # Apêndice
    doc.add_heading("Apêndice A — Reprodução e integridade das evidências", 1)
    _p(doc, "Reprodução sem chamadas à API: python scripts/gerar_relatorio_revisado.py; "
            "python scripts/gerar_apresentacao_revisada.py; python -m pytest tests/unit -q. "
            "Hashes SHA-256 das evidências primárias usadas nesta versão:")
    linhas = []
    for e in es:
        for nome in ("output.xml", "respostas.jsonl"):
            caminho = e["pasta"] / nome
            if caminho.exists():
                linhas.append([f"exec{e['numero']}/{nome}", _sha(caminho)])
    _tab(doc, cont, "Hashes SHA-256 das evidências primárias", ["Arquivo", "SHA-256"], linhas, "results/execN")

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    doc.save(SAIDA)
    print(SAIDA)
    return SAIDA


if __name__ == "__main__":
    gerar()
