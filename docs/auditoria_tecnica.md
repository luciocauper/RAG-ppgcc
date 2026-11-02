# Auditoria técnica do projeto RAG-PPGCC

> Auditoria realizada antes das refatorações. Cada item registra o problema, a gravidade
> (alta / média / baixa), a justificativa e a correção aplicada.

---

## 1. Organização arquitetural

| # | Problema | Gravidade | Justificativa | Decisão / correção |
|---|---|---|---|---|
| 1.1 | Os testes Robot usam `Test Template` com nomes de casos compactos, sem estrutura BDD | Média | O enunciado do trabalho pede escrita orientada ao comportamento (Given/When/Then). A estrutura por template é limpa e idiomática, mas esconde a separação pré-condição → ação → verificação. | Refatoração para BDD com keywords `Given`/`When`/`Then` nativas do Robot Framework, mantendo o template apenas onde o ganho de legibilidade não compensa a verbosidade (ver §4). |
| 1.2 | `saidas-gpt.md` (planejamento inicial com o ChatGPT) está na raiz do repositório | Baixa | É um documento histórico, não um artefato de execução. Mistura arquivos de natureza diferente na raiz. | Mantido na raiz por valor documental (registra a origem do trabalho); citado no relatório como material suplementar. |
| 1.3 | `docs/prompt_sistema.txt` e `docs/prompt_sistema.md` duplicam o mesmo conteúdo | Baixa | O `.txt` é o que vai para o Dify; o `.md` é a versão legível com regras de uso. A duplicação é intencional e documentada. | Mantido. O `.md` já explica que o `.txt` é a fonte canônica. |

## 2. Robot Framework

| # | Problema | Gravidade | Justificativa | Decisão / correção |
|---|---|---|---|---|
| 2.1 | Suites factuais/alucinação/robustez/segurança usam template sem BDD | Média | Ver item 1.1. | Refatorado para testes explícitos com Given/When/Then. |
| 2.2 | Suite `api.robot` faz o papel de smoke test, mas nenhum caso tem a tag `smoke` | Baixa | Não é possível selecionar só o smoke com `--include smoke`. | Adicionada tag `smoke` ao primeiro caso da suíte API. |
| 2.3 | `scripts/smoke_test.py` sobrepõe parcialmente `tests/api.robot` | Baixa | Ambos verificam disponibilidade e enviam uma pergunta. | Decisão documentada: `smoke_test.py` é ferramenta de diagnóstico manual (imprime resposta e contextos para inspeção); `api.robot` é o smoke automatizado dentro da suíte. Papéis distintos, sem redundância real. |
| 2.4 | `desempenho.robot` não usa BDD | Média | Os três casos têm lógica explícita, mas sem Given/When/Then. | Refatorado com keywords BDD. |
| 2.5 | `conversa.robot` usa template conversacional sem BDD | Média | Mesmo motivo dos demais. | Refatorado com Given/When/Then por turno. |
| 2.6 | Nomes dos casos de teste não seguem um padrão consistente | Baixa | Alguns têm acentos ("Contradicao"), outros não. Espaçamento entre CT e número é irregular. | Padronizado: `CT01 Nota mínima para aprovação`. |
| 2.7 | `Suite Setup` em todas as suites exceto `api.robot` chama `Verificar Disponibilidade Da API` | Baixa | Correto: falha cedo se a API estiver indisponível. `api.robot` não usa porque o primeiro caso já testa disponibilidade. | Mantido. |
| 2.8 | Tags de criticidade ausentes em casos individuais | Baixa | Apenas `seguranca.robot` usa `critico`. Casos de contradição (CT09, CT23) não têm tag específica além de `contradicao`. | Mantido `contradicao` em CT09 e CT23; adicionado `critico` apenas em segurança, onde o impacto de falso negativo é maior. |

## 3. Golden dataset (`datasets/casos_teste.json`)

| # | Problema | Gravidade | Justificativa | Decisão / correção |
|---|---|---|---|---|
| 3.1 | Oráculos por `termos_obrigatorios` podem aprovar respostas semanticamente incorretas | Média | Uma resposta que menciona "7,0" pode estar errada (ex.: "7,0 não é suficiente"). O oráculo determinístico só verifica presença. | Documentado no relatório e na documentação do avaliador como limitação conhecida. A avaliação semântica (Ragas) complementa; casos inconclusivos são registrados. Não endurecido artificialmente. |
| 3.2 | CT29 tem lista muito longa de alternativas para "1 externo" | Baixa | A lista cobre muitas formas de expressar "um membro externo". É completa, não rígida. | Mantido. |
| 3.3 | Todos os 30 casos têm `"verificado": true` | — | Conferência no PDF foi concluída em 29/10/2026. | Verificado; nenhuma correção necessária. |
| 3.4 | CT20 tem `deve_reconhecer_ausencia: true` e `termos_obrigatorios: ["colegiado"]` simultaneamente | Baixa | Espera-se que o SUT diga que não há número fixo e mencione o Colegiado. Os dois critérios são complementares, não contraditórios. | Mantido. |

## 4. Bibliotecas Python

| # | Problema | Gravidade | Justificativa | Decisão / correção |
|---|---|---|---|---|
| 4.1 | `dify_client.py`: `_erro_transitorio` trata erros 4xx com texto de quota como transitórios | Baixa | O Dify repassa erros do Gemini como HTTP 400 com texto de `resource_exhausted`. A heurística é necessária e documentada. | Mantido; documentado no docstring. |
| 4.2 | `dify_client.py`: sem type hints | Baixa | Funções pequenas e legíveis; type hints ajudariam em funções públicas. | Adicionados type hints nas assinaturas públicas (`verificar_disponibilidade`, `enviar_pergunta`, `obter_status`). |
| 4.3 | `rag_evaluator.py`: `normalizar` remove parênteses com extenso (ex.: "12 (doze)") | Baixa | Comportamento intencional para tolerância de redação do regimento. | Mantido; documentado. |
| 4.4 | `rag_evaluator.py`: `Validar Caso` levanta `SkipExecution` quando não há critérios | Baixa | Correto para o Robot Framework: marca como SKIP, não como PASS. | Mantido. |
| 4.5 | Sem testes unitários para as funções Python | Média | `normalizar`, `reconhece_ausencia`, `_termos_ausentes`, `_termos_presentes` são lógicas determinísticas que merecem cobertura. | Criados testes unitários com `pytest` em `tests/unit/`. |

## 5. Scripts

| # | Problema | Gravidade | Justificativa | Decisão / correção |
|---|---|---|---|---|
| 5.1 | `avaliar_ragas.py` nunca foi executado de verdade | Média | Pode haver incompatibilidades com a versão do Ragas instalada. | Validada a sintaxe com `python -m py_compile`. Execução real depende de cota do Gemini e não foi realizada neste ambiente. Documentado como pendência. |
| 5.2 | `consolidar.py` lê `output.xml` e `respostas.jsonl` de cada execução | Baixa | Funciona corretamente para as 3 execuções oficiais. | Mantido. |
| 5.3 | `executar.sh` é Bash; o ambiente é Windows | Baixa | Projetado para Git Bash/WSL, que está disponível no ambiente documentado. | Mantido; documentado no README. |
| 5.4 | `subir_ambiente.ps1` assume Dify em `~/dify/docker` no Ubuntu/WSL | Baixa | Caminho documentado no `infra/dify/README.md`. | Mantido. |

## 6. Configuração e segurança

| # | Problema | Gravidade | Justificativa | Decisão / correção |
|---|---|---|---|---|
| 6.1 | `.env` não é versionado (está no `.gitignore`) | — | Correto: protege chaves de API. | Verificado. |
| 6.2 | `.env.example` usa placeholder `app-xxx` e `sua-chave-do-ai-studio` | — | Correto: não expõe credenciais reais. | Verificado. |
| 6.3 | `respostas.jsonl` contém `usage` com custos | Baixa | Informação de uso da API, não credenciais. Sem risco. | Mantido. |
| 6.4 | Nenhuma chave de API aparece no código ou na documentação | — | Verificado em todos os arquivos lidos. | Verificado. |

## 7. Resultados e reprodutibilidade

| # | Problema | Gravidade | Justificativa | Decisão / correção |
|---|---|---|---|---|
| 7.1 | `results/exec1..3` são versionados (dados do experimento) | — | Correto: são as evidências oficiais. O `.gitignore` ignora apenas `results/*.jsonl` temporários. | Verificado. |
| 7.2 | `results/*.jsonl` no `.gitignore` poderia excluir `execN/respostas.jsonl` | Média | O padrão `results/*.jsonl` só ignora arquivos diretamente em `results/`, não em subpastas. `results/exec1/respostas.jsonl` é versionado. | Verificado: o padrão não afeta subpastas. |
| 7.3 | Novas execuções devem usar pastas próprias | — | Documentado em `instrucoes.md` §8 e no protocolo. | Mantido. |

## 8. Documentação

| # | Problema | Gravidade | Justificativa | Decisão / correção |
|---|---|---|---|---|
| 8.1 | `docs/relatorio.md` é apenas um esqueleto com comentários HTML | Alta | Entrega obrigatória em 04/11/2026. | Finalizado com todas as seções do enunciado. |
| 8.2 | `README.md` não lista pré-requisitos de versão nem limitações | Média | Outro estudante pode não saber qual Python instalar. | Atualizado com pré-requisitos e limitações. |
| 8.3 | `instrucoes.md` duplica parte do conteúdo do README | Baixa | `instrucoes.md` é o documento detalhado; o README é o resumo de execução. A sobreposição é intencional (níveis de detalhe diferentes). | Reduzida duplicação; README aponta para `instrucoes.md` para detalhes. |
| 8.4 | Sem apresentação PowerPoint | Alta | Entrega obrigatória em 16/11/2026. | Criada em `apresentacao/Apresentacao_Tecnica_RAG_PPGCC.pptx`. |

---

## Resumo das correções aplicadas

- **Robot Framework:** refatoração BDD (Given/When/Then) em todas as 7 suítes; tag `smoke` no caso
  de disponibilidade da API; padronização de nomes de casos.
- **Bibliotecas Python:** type hints nas funções públicas; criação de testes unitários.
- **Documentação:** relatório finalizado; README atualizado; auditoria e checklist criados.
- **Apresentação:** PowerPoint e roteiro gerados.
- **Sem alteração:** golden dataset (verificado e correto), resultados oficiais (preservados),
  prompt de sistema (congelado), scripts de infraestrutura.
