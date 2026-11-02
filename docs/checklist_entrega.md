# Checklist de Entrega Final

> Verificação final do projeto RAG-PPGCC após auditoria completa.

---

## 1. Robot Framework

- [x] Todos os testes Robot compilam sem erros (dryrun: 34/34 pass)
- [x] A estrutura BDD está correta (Given/When/Then em todas as 7 suítes)
- [x] Os 30 cenários possuem rastreabilidade (tags CT01–CT30)
- [x] Os 4 testes adicionais (API/infraestrutura) estão documentados
- [x] O smoke test não apresenta duplicidades (tag `smoke` em api.robot; smoke_test.py como diagnóstico)
- [x] Keywords reutilizáveis, sem redundância
- [x] Testes independentes (conversas novas, conversation_id próprio)

## 2. Testes unitários Python

- [x] 49 testes unitários executam corretamente (pytest: 49/49 pass)
- [x] Asserções de qualidade, independentes, com mocks
- [x] Cobertura das funções determinísticas (normalização, oráculos, latência, consistência, erros HTTP)

## 3. Golden dataset e oráculos

- [x] 30 casos revisados contra o PDF (`verificado: true`)
- [x] Oráculos analisados (limitação: presença de termos ≠ correção semântica)
- [x] Falsos negativos do oráculo documentados (CT21 exec3, CT28 exec1)
- [x] Contradições do regimento exploradas (CT09, CT23)

## 4. Análise das falhas

- [x] As três execuções históricas estão preservadas (`results/exec1..3` não modificados)
- [x] Resultados consolidados corretos (30/34 = 88,2% em todas as execuções)
- [x] CT09 investigado (falha de recuperação: chunk do Art. 39 não recuperado)
- [x] CT30 investigado (falha de recuperação: busca só pela última mensagem)
- [x] CT28 investigado (recuperação + alucinação: "28 créditos" na exec3)
- [x] CT18 investigado (limitação do oráculo: similaridade lexical ruidosa)
- [x] Tabela consolidada de falhas gerada (ID, categoria, execuções, tipo, causa)
- [x] Evidências extraídas automaticamente (`docs/analise_falhas.md`)

## 5. Scripts Windows

- [x] `scripts/setup_windows.ps1` implementado (idempotente, verifica Python/venv/deps/.env)
- [x] `scripts/executar_windows.ps1` implementado (5 modos: smoke, unit, completo, consolidar, ragas)
- [x] O ambiente pode ser preparado por procedimento documentado
- [x] Existe um comando centralizado de execução
- [x] Novas evidências não sobrescrevem as antigas (execN auto-incrementado)
- [x] Falhas apresentadas com mensagens claras e códigos de saída adequados

## 6. Guia de execução

- [x] `docs/GUIA_EXECUCAO_WINDOWS.md` criado (passo a passo completo em PowerShell)

## 7. Relatório acadêmico (Word)

- [x] `relatório/Relatorio_Final_Testes_RAG_PPGCC.docx` gerado
- [x] Formato A4, margens ABNT, Arial 12pt, espaçamento 1,5, justificado
- [x] 16 seções numeradas + resumo + palavras-chave + sumário
- [x] 7 tabelas com dados reais
- [x] Paginação no rodapé
- [x] Verificado: 134 parágrafos, estrutura completa

## 8. Apresentação PowerPoint

- [x] `apresentação/Apresentacao_Tecnica_RAG_PPGCC.pptx` (12 slides, 16:9, gráficos)
- [x] Resultados consistentes com o relatório Word (30/34, 88,2%)
- [x] `apresentação/roteiro_apresentacao.md` atualizado

## 9. Segurança

- [x] O projeto não contém credenciais expostas
- [x] `.env` no `.gitignore`
- [x] `.env.example` usa placeholders

## 10. Documentação

- [x] `README.md` funciona como ponto de entrada
- [x] `docs/GUIA_EXECUCAO_WINDOWS.md` concentra instruções de execução local
- [x] `relatório/Relatorio_Final_Testes_RAG_PPGCC.docx` concentra a descrição científica
- [x] `docs/auditoria_final.md` documenta problemas e correções
- [x] `docs/checklist_entrega.md` (este arquivo)
- [x] Sem redundância excessiva entre documentos

## 11. Pendências documentadas

- [ ] Métricas Ragas não executadas (requer cota do Gemini)
- [ ] Execução real dos 30 cenários não realizada nesta auditoria (requer Dify)
- [ ] Demonstração ao vivo (requer Dify na máquina da apresentação)
- [ ] Ensaio da apresentação com cronômetro

---

## Resumo de verificação

| Item | Verificado | Método |
|---|---|---|
| Robot dryrun | 34/34 pass | `python -m robot --dryrun tests\` |
| pytest | 49/49 pass | `python -m pytest tests/unit/ -v` |
| py_compile | sem erros | `python -m py_compile libraries/*.py scripts/*.py` |
| Consolidador | 30/34 correto | `python scripts/consolidar.py 1 2 3` |
| DOCX | 134 parágrafos, 7 tabelas | `python scripts/gerar_relatorio.py` |
| PPTX | 12 slides, 2 gráficos | `python scripts/gerar_apresentacao.py` |
| Setup PS1 | funcional | `.\scripts\setup_windows.ps1` |
| Executar PS1 | 5 modos | `.\scripts\executar_windows.ps1 -Modo unit` |
