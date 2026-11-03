"""Gera a síntese acadêmica a partir da mesma leitura usada pelos relatórios de execução."""
from pathlib import Path
import statistics

from consolidar import (LIMITACOES, categorias, detalhes, descobrir_execucoes, documento,
                        grafico, ler_execucao, resumo, tabela)

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "results" / "Relatorio_Final_Testes_RAG_PPGCC.docx"
QUESTOES_PESQUISA = (
    ("QP1", "Qualidade das respostas",
     "Em que medida o assistente RAG apresenta respostas corretas e fundamentadas no regulamento do PPGCC?"),
    ("QP2", "Robustez e segurança",
     "Como o assistente RAG se comporta diante de entradas ambíguas, contraditórias ou potencialmente maliciosas?"),
    ("QP3", "Consistência conversacional",
     "Em que medida o assistente RAG preserva o contexto e a coerência das respostas em interações com múltiplos turnos?"),
)


def gerar():
    execucoes = [ler_execucao(n) for n in descobrir_execucoes()]
    if not execucoes:
        raise ValueError("Nenhuma execução com output.xml.")
    doc = documento("Avaliação automatizada da qualidade de um sistema RAG", academico=True)
    doc.add_paragraph("Universidade Estadual do Ceará — PPGCC\nDisciplina: Teste de Sistemas Inteligentes\n2026")
    doc.add_paragraph("Relatório acadêmico final — resultados determinísticos e análise qualitativa. "
                      "Responsáveis: não identificados formalmente nas evidências.")
    doc.add_heading("Resumo", 1)
    doc.add_paragraph(f"Foram analisadas {len(execucoes)} execuções oficiais de uma automação Robot Framework "
                      "sobre um assistente Dify Community. O golden dataset reúne 30 cenários experimentais, "
                      "separados das verificações de infraestrutura. A análise combina resultados automatizados "
                      "e inspeção das respostas e contextos; identifica omissões documentais, dificuldades em "
                      "continuações de conversa e limitações do oráculo lexical. Ragas está implementado, mas "
                      "não há métricas semânticas nas evidências analisadas.")
    doc.add_heading("Questões de pesquisa consolidadas", 1)
    tabela(doc, ["QP", "Questão", "Origem e cenários"], [
        ["QP1 — Qualidade das respostas", QUESTOES_PESQUISA[0][2],
         "RQ1 e RQ2. CT01–CT11 e CT20–CT22; categorias factualidade e alucinação."],
        ["QP2 — Robustez e segurança", QUESTOES_PESQUISA[1][2],
         "RQ3 e RQ4. CT12–CT15 e CT23–CT27; categorias robustez e segurança."],
        ["QP3 — Consistência conversacional", QUESTOES_PESQUISA[2][2],
         "RQ5. CT16 e CT28–CT30; categoria conversa."],
    ])
    doc.add_paragraph("RQ6 (latência) é tratada como dimensão complementar, não como questão de pesquisa. "
                      "RQ7 propunha comparar avaliações determinísticas e semânticas; como Ragas não foi "
                      "executado, essa comparação não tem evidência empírica nesta entrega.")
    secoes = [
        ("1. Objetivo e questões de pesquisa",
         "Avaliar factualidade, reconhecimento de lacunas, robustez, segurança, manutenção de contexto "
         "e desempenho de um RAG sobre o regimento PPGCC/UECE. Investiga-se também em que condições "
         "a aprovação lexical diverge da correção da resposta. O estudo é acadêmico e não certifica "
         "um canal oficial de orientação da universidade."),
        ("2. Fundamentação e sistema sob teste",
         "RAG combina busca em uma base documental e geração condicionada aos trechos recuperados. "
         "A qualidade depende de ambas as etapas. Uma resposta pode ser fiel aos trechos recebidos e "
         "ainda omitir informações presentes no documento completo. O problema do oráculo exige "
         "distinguir presença de palavras, correção factual e suporte documental."),
        ("3. Arquitetura RAG e ambiente",
         "O protocolo local declara Dify Community 1.18.0, Gemini gemini-3.5-flash-lite, embeddings "
         "gemini-embedding-001, indexação High Quality, 47 chunks, busca Hybrid e Top K 4. "
         "São informações documentadas em docs/protocolo_testes.md, não snapshots independentes por "
         "execução. A exec4 foi realizada no ambiente de outro integrante. O nome de conta em um "
         "caminho XML não identifica formalmente o responsável. Os JSONLs registram os trechos "
         "retornados, mas não demonstram a configuração efetiva de todos os componentes."),
        ("4. Metodologia e desenho experimental",
         "O estudo usa um único PDF e repetições de uma suíte fixa. Exec1–3 foram executadas por "
         "suíte e reunidas por rebot, incluindo smoke. Exec4 usa --exclude smoke e execução conjunta "
         "das suítes. A ordem das chamadas, o ambiente e os tempos diferem. Por isso os 30 casos CT "
         "são comparados separadamente dos testes de API e não se atribui causalidade a variações. "
         "As datas abaixo são lidas das evidências; o atributo generated do XML não declara fuso."),
        ("5. Golden dataset e estratégia de testes",
         "datasets/casos_teste.json contém CT01–CT30, perguntas, critérios, referências e marcação "
         "de conferência documental. São seis categorias experimentais e sete suítes Robot, contando "
         "API. Factual: 9; alucinação: 5; robustez: 5; segurança: 4; conversa: 4; desempenho: 3. "
         "Art. 35 e Art. 39, d apresentam prazos conflitantes; Art. 31 traz '48 (quarenta)', "
         "enquanto Art. 32 permite conferir a composição. Essas inconsistências são objetos de teste."),
        ("6. BDD e automação",
         "Given carrega o caso; When envia a pergunta; Then aplica os critérios. As sete suítes "
         "mantêm IDs e tags. resources/dify_keywords.robot contém os fluxos; dify_client.py encapsula "
         "HTTP e registro de respostas; rag_evaluator.py aplica o oráculo. Os casos conversacionais "
         "propagam conversation_id entre turnos e iniciam sessões independentes entre cenários. "
         "A refatoração centraliza leitura e geração de evidências em consolidar.py, consumida também "
         "por este relatório e pela apresentação, evitando números digitados nos geradores."),
        ("7. Oráculos e critérios de aceitação",
         "O avaliador normaliza texto, verifica termos obrigatórios/proibidos, padrões de ausência "
         "e presença de citação. CT17 exige que todas as latências de suas repetições fiquem no limite; "
         "CT18 combina termos factuais e similaridade lexical; CT19 verifica status HTTP abaixo de "
         "500, o que aceita também respostas controladas 4xx. Não há prova de atendimento semântico "
         "integral em um PASS. Os critérios históricos foram preservados, sem recalibração após "
         "observar a exec4. Ragas permanece uma avaliação complementar pendente."),
    ]
    for titulo, texto in secoes:
        doc.add_heading(titulo, 1)
        doc.add_paragraph(texto)
    doc.add_paragraph("Em RAG, a geração depende dos trechos recuperados: erros podem decorrer da recuperação ou da "
                      "interpretação/geração. Neste estudo, alucinação designa afirmações sem suporte suficiente "
                      "no contexto observado; prompt injection é uma entrada que tenta alterar as instruções, "
                      "avaliada pelos cenários de segurança. As métricas Ragas mediriam dimensões diferentes: "
                      "Faithfulness (suporte nos contextos), Factual Correctness (correção frente à referência) e "
                      "Context Precision (relevância dos trechos). Elas não foram calculadas nesta entrega.")
    doc.add_heading("8. Resultados experimentais", 1)
    tabela(doc, ["Exec.", "Data XML", "Ambiente do executor"], [
        [e["numero"], e["gerado"], e["gerador"]] for e in execucoes])
    for titulo, seletor in (
        ("8.1 Cenários experimentais", lambda t: t["experimental"]),
        ("8.2 Infraestrutura e API", lambda t: not t["experimental"]),
        ("8.3 Total registrado", lambda t: True),
    ):
        doc.add_heading(titulo, 2)
        tabela(doc, ["Exec.", "Total", "PASS", "FAIL", "SKIP", "% PASS"], [
            [e["numero"], *resumo([t for t in e["testes"] if seletor(t)])] for e in execucoes])
    cats = sorted(set().union(*(set(categorias(e)) for e in execucoes)))
    tabela(doc, ["Categoria", *[f"Exec{e['numero']}" for e in execucoes]], [
        [cat, *[f'{sum(t["status"] == "PASS" for t in e["testes"] if t["categoria"] == cat)}/'
                f'{sum(t["categoria"] == cat for t in e["testes"])}' for e in execucoes]]
        for cat in cats])
    grafico(doc, "Cenários experimentais", [
        (f"Exec{e['numero']}", resumo([t for t in e["testes"] if t["experimental"]])[1:4])
        for e in execucoes])
    doc.add_heading("8.4 Latência observada", 2)
    linhas = []
    for e in execucoes:
        lat = [r["latencia_s"] for r in e["respostas"] if isinstance(r.get("latencia_s"), (int, float))]
        linhas.append([e["numero"], len(lat), f"{statistics.mean(lat):.3f}" if lat else "n/a",
                       f"{max(lat):.3f}" if lat else "n/a",
                       sum(r.get("tentativas", 1) > 1 for r in e["respostas"])])
    tabela(doc, ["Exec.", "Registros", "Média (s)", "Máxima (s)", "Com retry"], linhas)
    doc.add_paragraph("A média abrange os registros JSONL, não todas as chamadas HTTP. Pausas e tentativas "
                      "anteriores não entram na latência registrada. A máxima global não determina o "
                      "resultado de CT17, cujo limite se aplica somente às repetições daquele caso.")
    doc.add_heading("9. Comparação e análise qualitativa", 1)
    ids = sorted({t["id"] for e in execucoes for t in e["testes"] if t["status"] == "FAIL"})
    tabela(doc, ["ID", *[f"Exec{e['numero']}" for e in execucoes]], [
        [cid, *[next((t["status"] for t in e["testes"] if t["id"] == cid), "Não executado")
                for e in execucoes]] for cid in ids])
    doc.add_paragraph("Exec1–3 registram 26/30 cenários aprovados cada; exec4 registra 25/30. "
                      "Isso descreve a amostra, sem demonstrar regressão. CT09 e CT30 falham em todas "
                      "as quatro execuções. CT29 acrescenta um problema conversacional na exec4. "
                      "Robustez e segurança passam nos critérios aplicados, o que não demonstra ausência "
                      "geral de vulnerabilidades ou de erros semânticos.")
    doc.add_paragraph("CT28/exec1 é um falso positivo: o total incorreto de 32 créditos contém o termo "
                      "24 na decomposição. CT28/exec3 informa 28 créditos (erro factual). "
                      "CT21/exec3 é um falso negativo: a recusa 'Não possuo essa informação' não é "
                      "reconhecida pelo padrão. CT18/exec1 e exec2 falha em similaridade lexical "
                      "(0,422 e 0,256, respectivamente), apesar de manter o limite factual. "
                      "CT22/exec1 e exec4 omite a área de concentração, embora reconheça a ausência "
                      "dos nomes das linhas: falha de completude, sem evidência de invenção de linhas.")
    doc.add_heading("Respostas às questões de pesquisa", 2)
    doc.add_paragraph("QP1 — Qualidade das respostas. Resposta: parcial. A factualidade passou em 8/9 casos "
                      "em cada execução; alucinação passou em 4/5, 5/5, 4/5 e 4/5. CT09 falhou nas quatro "
                      "execuções por não reconhecer a divergência do regimento. CT22 falhou na exec1 e exec4 "
                      "por omitir a área exigida. CT28/exec1 passou apesar de informar 32 créditos, mostrando "
                      "que a presença lexical não garante correção. CT21/exec3 foi uma recusa válida reprovada "
                      "pelo padrão. Esses resultados medem os oráculos determinísticos, não correção semântica integral.")
    doc.add_paragraph("QP2 — Robustez e segurança. Resposta: os cenários executados passaram nos critérios "
                      "automatizados: robustez 5/5 e segurança 4/4 em cada execução. Isso sustenta resistência "
                      "nos casos testados, não uma afirmação geral de segurança ou robustez fora do único regimento "
                      "e das entradas avaliadas.")
    doc.add_paragraph("QP3 — Consistência conversacional. Resposta: houve dificuldade recorrente. A categoria "
                      "conversa passou em 3/4, 2/4, 2/4 e 1/4; CT30 falhou em todas as execuções, CT28 em três e "
                      "CT29 na exec4. Os contextos e respostas sustentam hipóteses de recuperação insuficiente "
                      "em continuação, mas não revelam a consulta interna do Dify. A diferença entre execuções "
                      "não demonstra regressão do modelo.")
    doc.add_paragraph("Desempenho complementar. A categoria passou em 2/3, 2/3, 3/3 e 3/3. As latências "
                      "registradas representam respostas JSONL observadas e não incluem pausas, chamadas sem "
                      "registro ou o tempo total percebido; por isso não respondem a uma QP autônoma.")
    ultima = execucoes[-1]
    doc.add_heading(f"10. Falhas detalhadas — exec{ultima['numero']}", 1)
    for t in ultima["testes"]:
        if t["status"] == "FAIL":
            detalhes(doc, ultima, t, contextos=False)
    doc.add_heading("11. Limitações e ameaças à validade", 1)
    doc.add_paragraph(LIMITACOES)
    tabela(doc, ["Ameaça", "Implicação"], [
        ["Validade de construto", "Palavras presentes não comprovam relações corretas; similaridade não equivale a factualidade."],
        ["Validade interna", "Sem snapshots por execução, diferenças de configuração, ordem e carga impedem atribuir causalidade."],
        ["Validade externa", "Um documento e 30 cenários não permitem generalização para outros RAGs."],
        ["Validade de conclusão", "Quatro execuções não constituem estudo estatístico de melhoria/regressão; casos não são amostra aleatória."],
        ["Rastreabilidade temporal", "XML local sem fuso explícito; JSONL com fuso. Datas não devem ser equiparadas sem conversão."],
        ["Recuperação", "Contextos observáveis permitem hipóteses; não demonstram a consulta interna ou arquitetura exata do Dify."],
        ["Ragas pendente", "Não há resultados de juiz LLM. Mesma família de modelos seria uma ameaça adicional numa futura avaliação."],
    ])
    doc.add_heading("12. Conclusões", 1)
    doc.add_paragraph("QP1: os resultados são parcialmente positivos nos critérios determinísticos, mas "
                      "CT09, CT22 e os erros lexicais/factuais de CT21 e CT28 mostram que aprovação não equivale "
                      "a fundamentação ou correção semântica. QP2: robustez e segurança passaram nos cenários "
                      "selecionados, sem sustentar garantias gerais. QP3: a manutenção do contexto foi a dimensão "
                      "mais problemática, especialmente em CT30, com falhas repetidas em continuações.")
    doc.add_paragraph("As quatro execuções permitem descrever variação, não atribuir causalidade ou regressão. "
                      "O estudo usa um documento e um conjunto fixo de cenários; não há métricas Ragas nem "
                      "snapshots completos do ambiente remoto por execução. Trabalhos futuros podem avaliar "
                      "recuperação com contexto conversacional e métricas semânticas sob configuração congelada.")
    doc.add_heading("13. Fontes e reprodução", 1)
    for texto in (
        "UECE. Regimento do Programa de Pós-Graduação em Ciência da Computação. 2021. PDF local em datasets/documentos/.",
        "DIFY. Dify — LLM App Development Platform. https://github.com/langgenius/dify.",
        "GOOGLE. Gemini API. https://ai.google.dev/gemini-api/docs/models.",
        "ROBOT FRAMEWORK. Robot Framework User Guide. https://robotframework.org/robotframework/.",
        "RAGAS. Ragas — Evaluation Framework for RAG. https://github.com/explodinggradients/ragas.",
        "Golden dataset: datasets/casos_teste.json. Protocolo e configuração declarada: docs/protocolo_testes.md.",
        "Evidências primárias: results/execN/output.xml, log.html, report.html e respostas.jsonl. "
        "Relatórios individuais contêm matriz completa, respostas integrais e hashes SHA-256.",
        "Reprodução local: python scripts/consolidar.py 1 2 3 4; python scripts/gerar_relatorio.py; "
        "python scripts/gerar_apresentacao.py. Não exige chamadas à API.",
    ):
        doc.add_paragraph(texto)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    doc.save(SAIDA)
    print(SAIDA)


if __name__ == "__main__":
    gerar()
