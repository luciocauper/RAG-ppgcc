# Avaliação Automatizada da Qualidade de um Sistema Inteligente Baseado em RAG

Trabalho da disciplina de **Teste de Sistemas Inteligentes** (PPGCC/UECE). O sistema sob teste
(SUT) é um chatbot RAG construído no [Dify Community](https://github.com/langgenius/dify)
(self-hosted), que responde perguntas sobre o
[Regimento do PPGCC/UECE](datasets/documentos/Regimento_PPGCC-UECE2021.pdf) usando o Google Gemini
como LLM. A suíte, em Robot Framework, chama a API do Dify, aplica verificações determinísticas e
registra as respostas para avaliação semântica com Ragas.

**Documentação completa (tecnologias, histórico, passo a passo para replicar):
[instrucoes.md](instrucoes.md).**

## Arquitetura

```
Robot Framework (tests/*.robot, BDD Given/When/Then)
   └─ resources/dify_keywords.robot       ← keywords compartilhadas (comportamento)
   └─ libraries/dify_client.py            ← cliente HTTP da API do Dify (implementação)
   └─ libraries/rag_evaluator.py          ← verificações determinísticas (oráculo)
          │
          ▼
results/execN/respostas.jsonl ──▶ scripts/avaliar_ragas.py ──▶ results/execN/metricas_ragas.csv
results/execN/output.xml       ──▶ scripts/consolidar.py    ──▶ results/consolidado.md
```

## Estrutura do repositório

| Caminho | Conteúdo |
|---|---|
| `datasets/documentos/` | PDF do regimento (base de conhecimento) |
| `datasets/casos_teste.json` | Golden dataset: 30 casos com perguntas, referências e critérios |
| `tests/*.robot` | 7 suítes BDD: api, factualidade, alucinacao, robustez, seguranca, conversa, desempenho |
| `tests/unit/` | Testes unitários das bibliotecas Python (pytest) |
| `resources/dify_keywords.robot` | Keywords BDD compartilhadas (Given/When/Then) |
| `libraries/` | Cliente da API do Dify e oráculo determinístico |
| `scripts/` | Smoke test, execução numerada, consolidação e métricas Ragas |
| `docs/` | Protocolo, prompt de sistema congelado, relatório e auditoria |
| `infra/dify/README.md` | Instalação do Dify Community e configuração do app |
| `results/exec1..3/` | Execuções oficiais (evidências: output.xml, respostas.jsonl, report.html) |
| `apresentacao/` | PowerPoint técnico e roteiro da apresentação |

## Pré-requisitos

- **Python 3.11+** (testado com 3.12.10)
- **Robot Framework 7.0+** (instalado via `requirements.txt`)
- **Dify Community** self-hosted (Docker) — necessário apenas para executar os testes, não para
  analisar resultados existentes
- **Conta Google** com chave gratuita do Gemini (AI Studio) — para o LLM do chatbot e o juiz do Ragas

## Configuração

```bash
# 1. Ambiente Python
python -m venv .venv
.venv\Scripts\activate            # Windows (Git Bash: source .venv/Scripts/activate)
pip install -r requirements.txt

# 2. Subir e configurar o Dify: ver infra/dify/README.md

# 3. Configurar credenciais
cp .env.example .env              # preencher DIFY_API_KEY e RAGAS_LLM_API_KEY
```

## Execução dos testes

```bash
# Smoke test (diagnóstico manual — imprime resposta e trechos recuperados)
python scripts/smoke_test.py

# Suíte completa (ou por categoria: --include factual)
robot -d results tests/

# Execução numerada do experimento (Git Bash; roda suíte por suíte e une com rebot)
bash scripts/executar.sh 1

# Validação de sintaxe sem chamar a API
python -m robot --dryrun tests/

# Testes unitários das bibliotecas Python
python -m pytest tests/unit/ -v
```

Relatórios do Robot: `results/report.html` e `results/log.html`.

## Execução das métricas semânticas

```bash
# Comparar as execuções oficiais
python scripts/consolidar.py 1 2 3

# Métricas Ragas de uma execução (exige RAGAS_LLM_API_KEY no .env)
python scripts/avaliar_ragas.py --resultados results/exec1/respostas.jsonl --saida results/exec1/metricas_ragas.csv
```

## Localização dos resultados

- **Resultados por caso e por suíte:** `results/consolidado.md`
- **Evidências por execução:** `results/execN/output.xml`, `respostas.jsonl`, `report.html`
- **Relatório técnico:** `docs/relatorio.md`
- **Auditoria técnica:** `docs/auditoria_tecnica.md`
- **Apresentação:** `apresentacao/Apresentacao_Tecnica_RAG_PPGCC.pptx`

## Principais limitações

- O oráculo determinístico verifica **presença de termos**, não correção semântica. Uma resposta
  pode conter os termos esperados e ainda estar incorreta. A avaliação semântica (Ragas) complementa,
  mas não substitui a análise humana.
- O LLM juiz do Ragas é da mesma família do modelo do SUT (Gemini), o que pode introduzir viés de
  autoavaliação.
- O dataset cobre um único documento (regimento) com 30 casos — insuficiente para generalização.
- A temperatura do modelo não é configurável no plugin do Gemini no Dify, gerando não determinismo
  medido pelas 3 execuções.
- As métricas semânticas com Ragas **ainda não foram executadas** (dependem de cota do Gemini).
