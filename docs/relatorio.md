# Avaliação Automatizada da Qualidade de um Sistema Inteligente Baseado em RAG: Uma Abordagem com Robot Framework e Métricas Semânticas

Entrega: 04/11/2026 · Apresentação: 16/11/2026

Disciplina: Teste de Sistemas Inteligentes — PPGCC/UECE

---

## 1. Introdução

Sistemas inteligentes baseados em modelos de linguagem de grande porte (LLMs) representam um
desafio para a engenharia de qualidade de software. Diferentemente de sistemas tradicionais, cujo
comportamento esperado pode ser especificado por pré-condições e pós-condições exatas, sistemas
que geram linguagem natural produzem saídas variáveis, probabilísticas e muitas vezes
subjetivas. O problema do oráculo de teste — decidir se uma saída está correta — torna-se
central: a mesma pergunta pode ter múltiplas respostas aceitáveis, e uma resposta pode ser
factualmente errada mesmo usando as palavras esperadas.

Sistemas RAG (*Retrieval-Augmented Generation*) adicionam uma camada de complexidade: a
qualidade da resposta depende não apenas da geração, mas também da recuperação de trechos
relevantes da base de conhecimento. Uma falha pode ser de recuperação (trecho errado ou
ausente) ou de geração (trecho correto, interpretação errada).

Este trabalho avalia um sistema RAG real — um assistente sobre o Regimento do PPGCC/UECE —
por meio de testes automatizados em dois níveis: verificações determinísticas (presença de
termos, reconhecimento de ausência, latência) e métricas semânticas (Ragas). O objetivo não é
testar a complexidade do desenvolvimento, mas a **qualidade dos testes e das ferramentas
utilizadas** para avaliar um sistema inteligente.

## 2. Objetivos e questões de pesquisa

### Objetivo geral

Avaliar a qualidade de um sistema inteligente baseado em RAG por meio de testes automatizados
que investiguem correção factual, fidelidade ao documento, alucinação, robustez, segurança,
contexto conversacional e desempenho.

### Questões de pesquisa

- **RQ1:** O sistema responde corretamente a perguntas factuais sobre o regimento?
- **RQ2:** O sistema reconhece quando a informação não está no documento (alucinação)?
- **RQ3:** O sistema é robusto a variações de escrita, paráfrases e ruído no documento?
- **RQ4:** O sistema resiste a prompt injection e a vazamento de instruções de sistema?
- **RQ5:** O sistema mantém contexto em conversas multi-turno?
- **RQ6:** O sistema responde dentro de limites de latência aceitáveis?
- **RQ7:** Como avaliações determinísticas e semânticas se complementam na avaliação de RAG?

## 3. Fundamentação teórica

### Sistemas RAG

RAG combina recuperação de informação com geração de linguagem: antes de gerar uma resposta,
o sistema busca trechos relevantes em uma base de conhecimento (tipicamente via embeddings e
busca vetorial) e os insere no prompt do LLM. Isso reduz alucinação e permite que o sistema
cite fontes, mas introduz a dependência da qualidade da recuperação.

### Alucinação

Em sistemas RAG, alucinação ocorre quando o modelo gera informações não presentes nos
trechos recuperados, seja por usar conhecimento paramétrico (treinamento) ou por inventar
dados. A detecção de alucinação é um problema de oráculo: é necessário saber o que o documento
diz e o que não diz.

### Prompt injection

Ataques de injeção de prompt inserem instruções maliciosas na entrada do usuário para
alterar o comportamento do sistema. Em RAG, também é possível injetar conteúdo nos documentos
recuperados. Sistemas bem projetados devem tratar o conteúdo recuperado como dado, não como
instrução.

### Métricas semânticas (Ragas)

Ragas é um *framework* de avaliação de RAG que usa um LLM como juiz para calcular métricas
como:

- **Faithfulness:** fidelidade da resposta aos contextos recuperados (a resposta se apoia nos
  trechos, sem inventar?).
- **Factual Correctness:** correção factual da resposta frente a uma referência (a resposta
  coincide com a verdade do documento?).
- **Context Precision (with reference):** qualidade da recuperação (os trechos recuperados são
  relevantes para a pergunta?).

Cada métrica mede uma dimensão distinta. Correção da resposta ≠ fidelidade aos contextos ≠
qualidade da recuperação ≠ sucesso da chamada HTTP ≠ aprovação em testes determinísticos.

### Oráculo de teste e seus limites

O oráculo de teste determina se uma saída está correta. Em sistemas de linguagem, nenhum
oráculo é perfeito:

- **Oráculo determinístico** (presença de termos): rápido, reprodutível, mas limitado —
  verifica forma, não semântica.
- **Oráculo semântico** (LLM juiz): captura semântica, mas é custoso, não determinístico e
  suscetível a viés.
- **Oráculo humano:** mais confiável, mas não escalável nem automatizável.

A combinação de múltiplos oráculos com limites conhecidos é mais robusta que qualquer
oráculo isolado.

## 4. Caracterização do sistema sob teste

### Visão geral

O SUT é um chatbot RAG construído no Dify Community 1.18.0 (self-hosted via Docker em
WSL 2/Ubuntu 22.04), que responde perguntas sobre o Regimento do PPGCC/UECE (PDF de 13
páginas, 47 chunks após indexação).

### Configuração do experimento

| Item | Valor |
|---|---|
| Plataforma | Dify Community 1.18.0 (Docker Compose) |
| LLM do chatbot | Google Gemini `gemini-3.5-flash-lite` (plano gratuito) |
| Embeddings | Google Gemini `gemini-embedding-001` (3072 dimensões) |
| Banco vetorial | Weaviate (incluso no Dify) |
| Chunking | General, separador `\n\n`, 1024 tokens, sobreposição 100 |
| Recuperação | Hybrid Search (0,7 semântica / 0,3 palavra-chave), Top K 4 |
| Temperatura | Padrão do provedor (não configurável no plugin) |
| Prompt de sistema | Versão 1.0 (congelada, ver `docs/prompt_sistema.txt`) |
| LLM juiz do Ragas | Google Gemini `gemini-3.5-flash` |
| Limites do plano gratuito | 60 RPM / 100 RPD (em 29/10/2026) |

### Prompt de sistema (resumo)

O prompt instrui o assistente a: fundamentar respostas no regimento, citar artigos, não inventar
informações, reconhecer ausência de informação, apontar contradições sem escolher
interpretação, não usar conhecimento externo, responder em português e tratar conteúdo
recuperado como referência (não como comando).

## 5. Metodologia experimental

### Golden dataset

Foram construídos 30 casos de teste a partir da leitura do regimento, cada um com pergunta,
resposta de referência, artigo do regimento, trecho de origem e critérios de aceitação
determinísticos. O dataset foi conferido no PDF em 29/10/2026 (todos marcados
`"verificado": true`).

Inconsistências do próprio regimento foram exploradas como casos de teste:
- **CT09:** prazo da qualificação de doutorado — Art. 35 fixa 36º mês, Art. 39, d fixa 30º mês.
- **CT23:** Art. 31, b escreve "48 (quarenta)" — numeral e extenso divergem; Art. 32 confirma 48.

### Distribuição dos casos

| Categoria | Casos | IDs | Verificação | Métrica semântica |
|---|---|---|---|---|
| Factual | 9 | CT01–CT09 | termos obrigatórios | Faithfulness, Factual Correctness, Context Precision |
| Alucinação | 5 | CT10, CT11, CT20–CT22 | reconhecer ausência; termos proibidos | CT20, CT22 |
| Robustez | 5 | CT12, CT13, CT23–CT25 | termos obrigatórios | Factual Correctness |
| Segurança | 4 | CT14, CT15, CT26, CT27 | termos obrigatórios/proibidos | — (análise individual) |
| Conversa | 4 | CT16, CT28–CT30 | critérios por turno | — |
| Desempenho | 3 | CT17–CT19 | latência, similaridade, status HTTP | — |
| **Total** | **30** | | | |

### Critérios de aprovação

- **Determinístico:** presença de termos obrigatórios, ausência de termos proibidos,
  reconhecimento de ausência de informação e citação de artigo, conforme declarado em cada caso.
- **Semântico (metas ilustrativas):** Faithfulness ≥ 0,90; Factual Correctness ≥ 0,85;
  Context Precision ≥ 0,80.
- Falhas de segurança são analisadas individualmente, independentemente das médias gerais.

### Calibração do avaliador

Uma execução preliminar (29/10/2026, interrompida por falta de memória) revelou 4 falsos
negativos do avaliador determinístico, corrigidos com regras gerais (não específicas de caso):
remoção de markdown, redução de "12 (doze)" a "12" e adição de padrões de recusa. A
calibração ocorreu antes das execuções oficiais; após estas, falsos negativos são registrados,
não corrigidos (para preservar a integridade do experimento).

## 6. Estratégia de testes

### Arquitetura de automação

A automação segue o padrão BDD (Given/When/Then) com Robot Framework:

1. **Camada de comportamento** (`tests/*.robot`): casos de teste descrevem o comportamento
   esperado em linguagem estruturada.
2. **Camada de keywords** (`resources/dify_keywords.robot`): keywords BDD que encapsulam
   o fluxo de preparação → ação → verificação.
3. **Camada de implementação** (`libraries/`): cliente HTTP (DifyClient) e oráculo
   determinístico (RagEvaluator), expostos como bibliotecas do Robot Framework.

### Smoke test

A suíte `api.robot` funciona como smoke test automatizado (tag `smoke`): verifica
disponibilidade da API, chave válida, presença de contextos e rejeição de chave inválida.
O script `scripts/smoke_test.py` é uma ferramenta de diagnóstico manual que imprime a
resposta e os trechos recuperados para inspeção visual.

### Tratamento de erros de infraestrutura

O cliente HTTP distingue erros transitórios (cota do Gemini, falhas de rede) de falhas
funcionais do SUT. Erros transitórios (HTTP 429, 502, 503, 504, ou 4xx com texto de
`resource_exhausted`/`rate limit`) são reintentados com backoff exponencial. O número de
tentativas é registrado em `respostas.jsonl`. A latência medida é a da tentativa
bem-sucedida, sem incluir as esperas, para não contaminar os testes de desempenho.

## 7. Ferramentas e justificativas

| Ferramenta | Papel | Justificativa |
|---|---|---|
| Robot Framework | Automação dos testes | Suporte nativo a BDD, bibliotecas em Python, relatórios HTML |
| Dify Community | Plataforma do SUT | Self-hosted, integração com Gemini, RAG com busca híbrida |
| Google Gemini | LLM e embeddings | Plano gratuito, endpoint compatível com OpenAI |
| Ragas | Métricas semânticas | Métricas específicas para RAG (Faithfulness, Factual Correctness, Context Precision) |
| Python | Linguagem das bibliotecas | Integração nativa com Robot Framework e Ragas |
| pytest | Testes unitários | Padrão de mercado para testes Python |

## 8. Resultados quantitativos

### Aprovação por suíte (3 execuções, 29/10/2026)

| Suíte | Exec 1 | Exec 2 | Exec 3 |
|---|---|---|---|
| API | 4/4 | 4/4 | 4/4 |
| Factual | 8/9 | 8/9 | 8/9 |
| Alucinação | 4/5 | 5/5 | 4/5 |
| Robustez | 5/5 | 5/5 | 5/5 |
| Segurança | 4/4 | 4/4 | 4/4 |
| Conversa | 3/4 | 2/4 | 2/4 |
| Desempenho | 2/3 | 2/3 | 3/3 |
| **Total** | **30/34** | **30/34** | **30/34** |

Taxa de aprovação geral: **88,2%** (média nas 3 execuções: 30/34).

### Chamadas ao SUT e latência

| Execução | Chamadas | Latência média (s) | Latência máx. (s) | Com retentativa |
|---|---|---|---|---|
| 1 | 40 | 2,9 | 8,4 | 1 |
| 2 | 39 | 3,6 | 25,2 | 0 |
| 3 | 39 | 1,5 | 2,4 | 3 |

### Resultado por caso

Ver `results/consolidado.md` para a tabela completa.

### Métricas semânticas (Ragas)

**Status: não executadas.** O script `scripts/avaliar_ragas.py` foi escrito e validado
sintaticamente, mas a execução real depende de cota do Gemini (plano gratuito) e não foi
realizada no período desta entrega. Cada amostra gera múltiplas chamadas ao juiz, exigindo
controle de taxa. Quando executadas, as métricas serão gravadas em
`results/execN/metricas_ragas.csv`.

## 9. Análise qualitativa das falhas

### Falhas consistentes (presentes nas 3 execuções)

**CT09 — Contradição no prazo de qualificação (factual):**

O regimento é contraditório: o Art. 35 fixa a apresentação da Qualificação de Doutorado até o
36º mês, enquanto o Art. 39, alínea d, prevê desligamento se a Qualificação não for aprovada
até o 30º mês. O SUT sempre responde citando apenas os 36 meses (Art. 35), sem reconhecer a
contradição. Hipótese: o chunk que contém o Art. 39, alínea d, pode não estar sendo recuperado
junto com o do Art. 35 (estão em chunks diferentes, e o rótulo "Art. 39" foi partido na
extração do PDF — "Art. 3 9.").

**CT30 — Troca de nível na duração da apresentação (conversa):**

No 2º turno ("E no doutorado?"), o SUT não responde com os valores do doutorado (40–50 min,
Art. 43, §1º). Hipótese: o Chatbot básico do Dify busca na base usando apenas a última
mensagem ("E no doutorado?"), que isoladamente não recupera trechos sobre o doutorado.
Trata-se de uma **falha de recuperação** inerente à arquitetura do app, não de geração.

### Falhas intermitentes

**CT28 — Elipse doutorado para mestrado (conversa):**

Passou na execução 1, falhou nas execuções 2 e 3. No 2º turno ("E no mestrado?"), o SUT às
vezes responde "não há informações" (exec 2) e às vezes **alucina** (exec 3: "28 créditos"
para o mestrado; o correto é 24). O número 28 não aparece em nenhum trecho recuperado — é
geração a partir de conhecimento paramétrico, caracterizando alucinação. Mesma causa raiz
do CT30: busca pela última mensagem sem contexto do turno anterior.

**CT18 — Consistência entre repetições (desempenho):**

As respostas são factualmente corretas em todas as execuções (contêm "8 orientandos"), mas
a similaridade lexical entre repetições oscila em torno do limite (0,5). Na exec 1 e 2,
a similaridade ficou abaixo (0,422), causando reprovação; na exec 3, passou. Isso ilustra
a **limitação da métrica de similaridade lexical**: respostas semanticamente iguais podem
diferir na formulação (ordem de cláusulas, sinônimos, citação de artigo).

### Falsos negativos do oráculo

**CT21 (exec 3):** O SUT respondeu "Não possuo essa informação no documento", uma recusa
correta, mas o padrão de reconhecimento de ausência não cobriu essa formulação. Mantido
como registrado (sem recalibrar após a execução oficial).

**CT22 (exec 1):** O SUT listou linhas de pesquisa reais do programa usando conhecimento
externo, mas a resposta também mencionou a área de concentração correta. O oráculo
verificou apenas a presença de "computação científica e aplicada", passando o caso quando
deveria falhar por alucinação (linhas nomeadas). Limitação do oráculo determinístico.

### Pontos fortes

- **Segurança: 12/12** nas 3 execuções. O SUT resistiu a prompt injection (CT14), não
  vazou o prompt de sistema (CT15), recusou role play de autoridade (CT26) e não confirmou
  premissa falsa sobre artigo inexistente (CT27).
- **Robustez: 15/15** nas 3 execuções. Variações de escrita, paráfrases, ruído no documento
  e linguagem informal não afetaram a correção das respostas.

## 10. Ameaças à validade

| Ameaça | Impacto | Mitigação |
|---|---|---|
| Oráculo por expressões regulares (presença de termos) | Falsos negativos e falsos positivos | Calibração preliminar; registro de falsos negativos; complementação com Ragas |
| LLM juiz do Ragas da mesma família do modelo do SUT (Gemini) | Viés de autoavaliação | Registrado como ameaça; uso de modelo mais capaz (`gemini-3.5-flash` vs `flash-lite`) reduz, não elimina |
| Temperatura não configurável no plugin | Não determinismo | 3 execuções oficiais; medição de variabilidade (CT18) |
| Um único documento, 30 casos | Cobertura limitada | Aceito como escopo do experimento; não generaliza |
| Modelos do plano gratuito podem mudar de versão | Irreprodutibilidade | Versões registradas no protocolo |
| Chunking com ruído da extração do PDF ("Art. 3 9", imagens do cabeçalho) | Recuperação degradada | Documentado; causa raiz de falhas como CT09 |
| Não execução do Ragas | Avaliação semântica pendente | Status sinalizado; script pronto e validado sintaticamente |

## 11. Discussão

Os resultados mostram que o sistema RAG avaliado tem bom desempenho em factualidade (88%),
robustez (100%) e segurança (100%), mas falha consistentemente em contexto conversacional
(50–75%) — especificamente quando a pergunta depende de turnos anteriores para recuperar
trechos corretos. A causa raiz identificada é arquitetural: o Chatbot básico do Dify busca
na base usando apenas a última mensagem, sem incorporar o contexto da conversa à consulta
de recuperação. Isso sugere que a avaliação de sistemas RAG deve testar não apenas a geração,
mas também a recuperação em contextos multi-turno.

A análise das falhas demonstra o valor de combinar oráculos: o oráculo determinístico detectou
a falha do CT09 (contradição não reconhecida), enquanto a análise qualitativa revelou a
alucinação do CT28 (exec 3) que o oráculo por termos não capturou isoladamente. A métrica de
similaridade lexical (CT18) mostrou ser um indicador ruidoso de consistência: semanticamente
estável, mas lexicalmente variável.

A não execução do Ragas é uma limitação desta entrega. As métricas semânticas trariam
evidência quantitativa para complementar a análise qualitativa, especialmente nos casos onde
o oráculo determinístico é insuficiente (CT09, CT22, CT28). O script está pronto e validado;
a execução depende apenas de cota do Gemini.

## 12. Conclusão

Este trabalho demonstrou que a qualidade de um sistema RAG pode ser avaliada de forma
automatizada combinando Robot Framework (BDD, testes determinísticos) com Ragas (métricas
semânticas). A arquitetura em três camadas (comportamento, keywords, implementação) separou
claramente o que é testado de como é testado, facilitando manutenção e rastreabilidade.

Os 30 casos de teste, organizados em 7 categorias, cobriram dimensões críticas de qualidade
de sistemas inteligentes: correção factual, alucinação, robustez, segurança, contexto
conversacional e desempenho. As 3 execuções oficiais revelaram falhas consistentes
(contradição não reconhecida, contexto conversacional) e intermitentes (alucinação em turno
elíptico, variabilidade lexical), além de falsos negativos do oráculo determinístico — todos
documentados e analisados.

A principal contribuição metodológica é a constatação de que nenhum oráculo isolado é
suficiente: o oráculo determinístico é rápido mas limitado à forma; o semântico captura
significado mas é custoso e não determinístico; a análise humana é necessária para casos
limítrofes. A combinação dos três, com limites explicitamente declarados, é mais robusta.

### Trabalhos futuros

- Executar as métricas semânticas com Ragas (script pronto).
- Testar um app do Dify com nó de recuperação que incorpora o contexto da conversa
  (workflow em vez de chatbot básico) para verificar se resolve as falhas de CT28/CT30.
- Expandir o dataset para incluir mais casos de contradição e de recuperação.
- Avaliar o impacto de diferentes estratégias de chunking na recuperação.

## 13. Referências

- DIFY. *Dify — LLM App Development Platform.* Disponível em: https://github.com/langgenius/dify. Acesso em: out. 2026.
- GOOGLE. *Gemini API.* Disponível em: https://ai.google.dev/gemini-api/docs/models. Acesso em: out. 2026.
- ROBOT FRAMEWORK. *Robot Framework User Guide.* Disponível em: https://robotframework.org/robotframework/. Acesso em: out. 2026.
- RAGAS. *Ragas — Evaluation Framework for RAG.* Disponível em: https://github.com/explodinggradients/ragas. Acesso em: out. 2026.
- UECE. *Regimento do PPGCC.* Disponível em: https://www.uece.br/ppgcc. 2021.
