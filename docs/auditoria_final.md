# Auditoria técnica final — RAG-PPGCC

> Auditoria realizada após a refatoração BDD, a criação dos scripts Windows e a geração do
> relatório Word. Documenta o estado final do projeto e os itens verificados.

---

## 1. Robot Framework — 34 testes

### Classificação dos 34 testes

| Tipo | Quantidade | Suítes | Descrição |
|---|---|---|---|
| Cenários experimentais | 30 | factualidade, alucinacao, robustez, seguranca, conversa, desempenho | CT01–CT30, golden dataset |
| Smoke / infraestrutura | 4 | api | Disponibilidade, resposta, contextos, chave inválida |
| **Total Robot** | **34** | 7 suítes | |

### Testes unitários Python

| Tipo | Quantidade | Local | Descrição |
|---|---|---|---|
| Unitários (pytest) | 49 | tests/unit/ | Normalização, oráculos, latência, consistência, erros HTTP |

### Verificação BDD

- ✅ Todas as 7 suítes usam Given/When/Then nativo do Robot Framework
- ✅ Keywords BDD em `resources/dify_keywords.robot` encapsulam o fluxo
- ✅ Testes descrevem comportamento, não detalhes técnicos
- ✅ Casos conversacionais usam FOR com conversation_id mantido por test variable
- ✅ Tags `smoke`, categoria, criticidade e CT ID presentes
- ✅ `--dryrun`: 34/34 pass, 0 fail

### Smoke test

- ✅ `tests/api.robot` com tag `smoke` (4 testes de infraestrutura)
- ✅ `scripts/smoke_test.py` mantido como diagnóstico manual
- ✅ Sem duplicação: o Robot automatiza, o Python imprime para inspeção
- ✅ `executar_windows.ps1 -Modo smoke` executa apenas os testes com tag `smoke`

---

## 2. Golden dataset

- ✅ 30 casos (CT01–CT30) preservados em `datasets/casos_teste.json`
- ✅ Todos com `"verificado": true` (conferidos no PDF em 29/10/2026)
- ✅ Oráculos por termos obrigatórios: limitação documentada (presença ≠ correção)
- ✅ Casos de ausência (`deve_reconhecer_ausencia`) e proibidos (`termos_proibidos`)
- ✅ Contradições do regimento exploradas (CT09, CT23)
- ✅ Falsos negativos do oráculo registrados (CT21 exec3, CT28 exec1)

---

## 3. Análise das falhas (confirmação dos resultados)

### Tabela consolidada

| ID | Categoria | Exec1 | Exec2 | Exec3 | Aprovações | Reprovações | Causa |
|---|---|---|---|---|---|---|---|
| CT09 | Factual | FAIL | FAIL | FAIL | 0 | 3 | Recuperação: chunk do Art. 39 não recuperado |
| CT22 | Alucinação | FAIL | PASS | PASS | 2 | 1 | Geração: não citou área de concentração |
| CT28 | Conversa | PASS | FAIL | FAIL | 1 | 2 | Recuperação + alucinação (exec3: "28 créditos") |
| CT30 | Conversa | FAIL | FAIL | FAIL | 0 | 3 | Recuperação: busca só pela última mensagem |
| CT18 | Desempenho | FAIL | FAIL | PASS | 1 | 2 | Oráculo: similaridade lexical ruidosa |
| CT21 | Alucinação | PASS | PASS | FAIL | 2 | 1 | Oráculo: falso negativo (frase não coberta) |

### Confirmação dos totais

- Execução 1: 30/34 (88,2%) ✅
- Execução 2: 30/34 (88,2%) ✅
- Execução 3: 30/34 (88,2%) ✅

Verificado diretamente em `results/exec1..3/output.xml` via `scripts/consolidar.py`.

---

## 4. Bibliotecas Python

- ✅ `dify_client.py`: type hints, retry de erros transitórios, registro em JSONL
- ✅ `rag_evaluator.py`: type hints, normalização, padrões de ausência, validação
- ✅ 49 testes unitários cobrindo funções determinísticas
- ✅ Sem credenciais expostas no código

---

## 5. Scripts Windows

- ✅ `scripts/setup_windows.ps1`: cria venv, instala deps, verifica .env (idempotente)
- ✅ `scripts/executar_windows.ps1`: 5 modos (smoke, unit, completo, consolidar, ragas)
- ✅ Novas execuções não sobrescrevem `exec1..3`
- ✅ Códigos de saída apropriados
- ✅ Diferencia indisponibilidade de ambiente de reprovação funcional

---

## 6. Relatório Word

- ✅ `relatório/Relatorio_Final_Testes_RAG_PPGCC.docx` gerado com python-docx
- ✅ A4, margens ABNT (3cm/2cm), Arial 12pt, espaçamento 1,5, justificado
- ✅ 16 seções numeradas + resumo + sumário (campo atualizável)
- ✅ 7 tabelas (configuração, distribuição, ferramentas, resultados, falhas, ameaças)
- ✅ Paginação no rodapé
- ✅ Verificado: 134 parágrafos, estrutura completa

---

## 7. Apresentação PowerPoint

- ✅ `apresentação/Apresentacao_Tecnica_RAG_PPGCC.pptx`: 12 slides, 16:9
- ✅ Gráficos com dados reais (distribuição de casos, resultados por suíte)
- ✅ Notas do apresentador em todos os slides
- ✅ Consistente com o relatório Word (mesmos números: 30/34, 88,2%)

---

## 8. Documentação

- ✅ `README.md`: visão geral, arquitetura, pré-requisitos, execução, limitações
- ✅ `docs/GUIA_EXECUCAO_WINDOWS.md`: passo a passo completo para Windows
- ✅ `docs/relatorio.md`: versão Markdown do relatório (fonte auxiliar)
- ✅ `docs/protocolo_testes.md`: configuração do experimento (versões preenchidas)
- ✅ `docs/auditoria_tecnica.md`: auditoria da primeira refatoração
- ✅ `docs/auditoria_final.md`: este documento
- ✅ `docs/checklist_entrega.md`: checklist de aceitação
- ✅ `instrucoes.md`: instruções detalhadas (atualizado)
- ✅ `docs/analise_falhas.md`: evidências extraídas automaticamente

---

## 9. Resultados das execuções oficiais

- ✅ `results/exec1..3` preservados (não modificados)
- ✅ `results/consolidado.md` regenerado e consistente
- ✅ Evidências completas: output.xml, respostas.jsonl, report.html, log.html

---

## 10. Pendências

| Item | Status | Ação necessária |
|---|---|---|
| Métricas Ragas | Não executadas | `.\scripts\executar_windows.ps1 -Modo ragas -Exec 1` (requer cota Gemini) |
| Execução real dos 30 cenários | Não executada nesta auditoria | `.\scripts\executar_windows.ps1 -Modo completo` (requer Dify) |
| Demonstração ao vivo | Pendente | Configurar Dify na máquina da apresentação |
| Ensaio da apresentação | Pendente | Cronometrar 15 minutos |
