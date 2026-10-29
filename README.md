# Testes automatizados de um sistema inteligente RAG — Assistente PPGCC/UECE

Trabalho da disciplina de Teste de Sistemas Inteligentes. O sistema sob teste (SUT) é um chatbot RAG
construído no [Dify Community](https://github.com/langgenius/dify) (self-hosted), que responde perguntas
sobre o [Regimento do PPGCC/UECE](https://www.uece.br/ppgcc/wp-content/uploads/sites/51/2019/11/Regimento_PPGCC-UECE2021-.pdf).
A suíte, em Robot Framework, chama a API do Dify, aplica verificações determinísticas e registra as
respostas para avaliação semântica com Ragas.

**Documentação completa (tecnologias, histórico, resultados e passo a passo para replicar):
[instrucoes.md](instrucoes.md).**

```
Robot Framework (tests/*.robot)
   └─ libraries/dify_client.py  ──HTTP──▶  Dify (Docker) ─▶ LLM + base de conhecimento (regimento)
   └─ libraries/rag_evaluator.py  (termos, ausência de informação, latência, consistência)
          │
          ▼
results/respostas.jsonl ──▶ scripts/avaliar_ragas.py ──▶ results/metricas_ragas.csv
```

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `infra/dify/README.md` | Instalação do Dify Community e configuração do app |
| `datasets/documentos/` | PDF do regimento (base de conhecimento) |
| `datasets/casos_teste.json` | Golden dataset: perguntas, referências e critérios |
| `tests/` | Suítes por categoria: api, factualidade, alucinacao, robustez, seguranca, conversa, desempenho |
| `resources/dify_keywords.robot` | Keywords compartilhadas |
| `libraries/` | Cliente da API do Dify e verificações determinísticas |
| `scripts/` | Smoke test e cálculo das métricas Ragas |
| `docs/` | Protocolo, prompt de sistema congelado e relatório |
| `results/` | Saídas das execuções (não versionadas) |

## Como executar

```bash
# 1. Ambiente Python
python -m venv .venv
.venv\Scripts\activate            # Windows (Git Bash: source .venv/Scripts/activate)
pip install -r requirements.txt

# 2. Subir e configurar o Dify: ver infra/dify/README.md
# 3. Configurar credenciais
cp .env.example .env              # preencher DIFY_API_KEY

# 4. Prova de conceito
python scripts/smoke_test.py

# 5. Suíte completa (ou por categoria: --include factual)
robot -d results tests/

# 6. Métricas semânticas
python scripts/avaliar_ragas.py
```

Relatórios do Robot: `results/report.html` e `results/log.html`.

## Estado do dataset

Os casos com `"verificado": false` usam referências sugeridas durante o planejamento e devem ser
conferidos no PDF antes de valer como oráculo. Casos sem critérios definidos são marcados como *SKIP*.
