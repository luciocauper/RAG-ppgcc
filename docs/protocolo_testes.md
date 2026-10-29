# Protocolo de testes

## Objetivo

Avaliar a qualidade de um sistema inteligente baseado em RAG (Assistente PPGCC/UECE sobre Dify
Community) por meio de testes automatizados que investiguem correção factual, fidelidade ao
contexto, robustez, segurança, contexto conversacional e desempenho.

O chatbot é um protótipo acadêmico, não um canal oficial da UECE. O oráculo é exclusivamente o
documento `datasets/documentos/Regimento_PPGCC-UECE2021.pdf`.

## Configuração do experimento (preencher antes da primeira execução)

| Item | Valor |
|---|---|
| Dify (tag/release) | 1.18.0 (Docker Compose, WSL 2 / Ubuntu 22.04) |
| Data da instalação | 29/10/2026 |
| Provedor e modelo LLM | Google Gemini, plano gratuito — `gemini-3.5-flash-lite` |
| Temperatura | Padrão do provedor — o plugin `langgenius/gemini` 0.9.12 não expõe temperatura para este modelo (variabilidade medida por repetições e pelo CT18) |
| Demais parâmetros do modelo | Output length: 2048 (salvo no app). Grounding: false · URL context: false · Code execution: false · Include thoughts: false · Thinking level: Minimal · Service tier: standard — padrões do plugin, conferidos em `models/llm/gemini-3.5-flash-lite.yaml` do plugin 0.9.12 (o Dify só grava parâmetros diferentes do padrão) |
| Modelo de embeddings | Gemini — `gemini-embedding-001` |
| Limites do plano gratuito (RPM / RPD), conforme AI Studio na data |60/100 |
| Chunking (modo / tamanho / sobreposição) | General (custom) — separador `\n\n`, máx. 1024 tokens, sobreposição 100; remove espaços extras: sim; remove URLs/e-mails: não |
| Resultado da indexação | High Quality (`gemini-embedding-001`); 47 chunks (235–1022 caracteres, média 813); 16.242 tokens |
| Recuperação (vetorial / full-text / híbrida) | Hybrid Search (configurado no Dify em 29/10/2026 — ver nota abaixo) |
| Top K / score threshold / rerank | 4 / desligado / sem rerank (Gemini não oferece modelo de rerank) |
| Versão do prompt de sistema | 1.0 (`docs/prompt_sistema.md`) |
| LLM juiz do Ragas | Gemini — `gemini-3.5-flash` (modelo diferente e mais capaz que o do SUT, para reduzir viés de autoavaliação; mesma família, o que fica como ameaça à validade) |
| Versões de Python / Robot Framework / Ragas | |

Observações sobre a base de conhecimento:

- A criação inicial salvou Semantic Search com Top K = 3. Foi alterada para Hybrid / Top K = 4 antes
  dos testes porque o CT09 depende de recuperar, juntos, os trechos do Art. 35 e do Art. 39, que
  ficam em chunks diferentes.
- O texto extraído do PDF traz "Art. 3 9." (espaço dentro do número). O chunk 35 termina em
  "Art. 39." e o chunk 36 começa em "39. O desempenho..." — a alínea d (30º mês) fica no chunk 36 sem
  o rótulo completo do artigo. Considerar na análise de falhas de citação do CT09.
- Os chunks incluem referências às imagens do cabeçalho institucional (`![image](/files/...)`), ruído
  sem conteúdo normativo.

## Categorias e critérios

| Categoria | Casos | IDs | Verificação determinística | Métrica semântica |
|---|---|---|---|---|
| Factual | 9 | CT01–CT09 (CT09 = contradição) | termos obrigatórios | Faithfulness, Factual Correctness, Context Precision |
| Alucinação | 5 | CT10, CT11, CT20–CT22 | reconhecer ausência; termos proibidos | CT20, CT22 |
| Robustez | 5 | CT12, CT13, CT23–CT25 (CT23 = ruído no documento) | termos obrigatórios | Factual Correctness |
| Segurança | 4 | CT14, CT15, CT26, CT27 | termos obrigatórios/proibidos | — (análise individual) |
| Conversa | 4 | CT16, CT28–CT30 | critérios por turno | — |
| Desempenho | 3 | CT17–CT19 | latência, similaridade, status HTTP | — |
| **Total** | **30** | | | |

Inconsistências do próprio regimento exploradas: prazo da qualificação de doutorado
(Art. 35 × Art. 39, d → CT09) e "48 (quarenta)" créditos no Art. 31, b (→ CT23).

Metas semânticas (ilustrativas, não universais): Faithfulness ≥ 0,90; Factual Correctness ≥ 0,85;
Context Precision ≥ 0,80. Falhas de segurança são analisadas uma a uma, mesmo com médias satisfatórias.

## Procedimento

1. Conferir cada caso do dataset no PDF e marcar `"verificado": true`.
2. Limpar `results/` e executar a suíte completa: `robot -d results tests/`.
3. Repetir a execução 3 vezes (não determinismo) — cada execução em pasta própria (`-d results/exec1`, ...).
4. Calcular métricas semânticas: `python scripts/avaliar_ragas.py`.
5. Registrar falhas: caso, resposta obtida, causa provável (recuperação × geração × oráculo).

## Calibração do avaliador (antes da execução oficial)

Uma execução preliminar em 29/10/2026 foi interrompida por falta de memória no host (28 de 34 testes
executados). A leitura das respostas mostrou 3 falsos negativos do avaliador determinístico — respostas
corretas reprovadas por detalhes de formatação — corrigidos com regras gerais, não específicas de caso:

| Caso | Resposta do SUT (correta) | Causa do falso negativo | Correção em `rag_evaluator.py` |
|---|---|---|---|
| CT05 | "**não** é permitido o trancamento..." | negrito markdown entre as palavras | `normalizar` remove `* _ \` #` |
| CT06 | "até 12 (doze) meses" | numeral com extenso entre parênteses | `normalizar` reduz "12 (doze)" a "12" |
| CT11 | "Eu não sei [...] não está relacionada ao regimento" | frase de recusa não prevista | padrões "não sei", "não está relacionada", "não posso responder/informar" |
| CT21 | "Não possuo informações sobre o valor da taxa de matrícula..." | frase de recusa não prevista | padrão "não possuo/tenho informações" |

As respostas preliminares, reavaliadas após a calibração, mantiveram reprovados apenas os casos com
falha real do SUT (CT09, CT22, CT28 turno 2, CT30 turno 2). A execução preliminar não entra nos resultados.

Também foi incluída nova tentativa para erros de infraestrutura entre o Dify e o Gemini
(ex.: `[Errno 101] Network is unreachable` no plugin, que reprovou o CT05 sem resposta do modelo).
Esses erros não refletem o comportamento do SUT; o número de tentativas fica registrado em
`respostas.jsonl`. Pausa entre perguntas na execução oficial: `DIFY_INTERVALO_S=50` (limite por minuto
do plano gratuito).

## Registro de execuções

| Execução | Data | Aprovados | Reprovados | Pulados | Observações |
|---|---|---|---|---|---|
| 1 (`results/exec1`) | 29/10/2026 | 30 | 4 | 0 | Suítes executadas uma a uma (pouca memória no host) e unidas com `rebot`. 40 chamadas ao SUT, latência média 2,9 s (máx. 8,4 s), 1 retentativa. Falhas: CT09, CT22, CT30 (turno 2), CT18 (similaridade lexical 0,422 < 0,5; as 3 respostas estavam factualmente corretas). CT28 passou nesta execução, mas falhou na execução preliminar com o mesmo padrão do CT30. |
| 2 (`results/exec2`) | 29/10/2026 | 30 | 4 | 0 | `scripts/executar.sh 2`. 39 chamadas, latência média 3,6 s (máx. 25,2 s), 0 retentativas. Falhas: CT09, CT28 (turno 2: "não há informações" sobre créditos do mestrado), CT30 (turno 2), CT18 (similaridade lexical). |
| 3 (`results/exec3`) | 29/10/2026 | 30 | 4 | 0 | `scripts/executar.sh 3`. 39 chamadas, latência média 1,5 s (máx. 2,4 s), 3 retentativas por erro transitório do provedor. Falhas: CT09, CT28 (turno 2: **alucinação** — "28 créditos" no mestrado; o correto é 24), CT30 (turno 2), CT21 (**falso negativo do avaliador**: "Não possuo essa informação no documento" é uma recusa correta não coberta pelo padrão; mantido como registrado, sem recalibrar após a execução oficial). |

Consolidado por caso: `python scripts/consolidar.py` → `results/consolidado.md`.
