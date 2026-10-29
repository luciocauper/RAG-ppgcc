# Instruções do projeto — Testes automatizados de um sistema inteligente RAG

Trabalho da disciplina **Teste de Sistemas Inteligentes** (PPGCC/UECE).
Entrega do relatório: **04/11/2026** · Apresentação (15 min): **16/11/2026**.

Título proposto: *Avaliação Automatizada da Qualidade de um Sistema Inteligente Baseado em RAG: Uma
Abordagem com Robot Framework e Métricas Semânticas*.

---

## 1. O que é o projeto

O objeto do trabalho é o **teste** de um sistema inteligente, não o desenvolvimento dele.

- **Sistema sob teste (SUT):** o "Assistente PPGCC", um chatbot RAG (*Retrieval-Augmented
  Generation*) montado no **Dify Community** (self-hosted). Ele responde perguntas usando como única
  fonte o **Regimento do PPGCC/UECE** (PDF de 13 páginas).
- **Objetivo:** avaliar correção factual, fidelidade ao documento, alucinação, robustez, segurança
  (prompt injection), contexto conversacional e desempenho, com testes automatizados, métricas e
  análise das falhas.
- **Oráculo:** um *golden dataset* de 30 casos de teste, todos com a resposta de referência conferida
  no texto do PDF (artigo e trecho de origem anotados).
- O chatbot é um **protótipo acadêmico**, não um canal oficial da UECE.

### Arquitetura

```
Robot Framework (tests/*.robot)
   ├─ libraries/dify_client.py ──HTTP──▶ Dify 1.18.0 (Docker no WSL/Ubuntu)
   │                                        ├─ base de conhecimento: regimento (47 chunks)
   │                                        └──HTTPS──▶ Google Gemini (LLM + embeddings, plano gratuito)
   └─ libraries/rag_evaluator.py  (verificações determinísticas)
          │
          ▼
results/execN/respostas.jsonl ──▶ scripts/avaliar_ragas.py (juiz: Gemini) ──▶ métricas semânticas
results/execN/output.xml       ──▶ scripts/consolidar.py ──▶ results/consolidado.md
```

---

## 2. Tecnologias

| Camada | Tecnologia | Versão / modelo |
|---|---|---|
| Plataforma do chatbot | Dify Community (Docker Compose) | 1.18.0 |
| Ambiente de execução do Dify | WSL 2 + Ubuntu 22.04 com systemd, Docker Engine nativo (`docker.io`) | Docker 27.5, Compose v5.6.1 |
| LLM do chatbot | Google Gemini (plugin `langgenius/gemini` 0.9.12) | `gemini-3.5-flash-lite` |
| Embeddings | Google Gemini | `gemini-embedding-001` (3072 dimensões) |
| Banco vetorial | Weaviate (incluso no Dify) | — |
| Automação de testes | Robot Framework + bibliotecas Python próprias | Robot 7.5, Python 3.11.9 |
| Avaliação semântica | Ragas (Faithfulness, Factual Correctness, Context Precision) com `langchain-openai` | Ragas 0.2.x |
| LLM juiz do Ragas | Gemini via endpoint compatível com OpenAI | `gemini-3.5-flash` |
| Outros | `requests`, `python-dotenv`, `pandas`, `pypdf` (extração do PDF para conferência) | ver `requirements.txt` |

Sistema operacional usado: Windows 11 (16 GB RAM, RTX 3050 6 GB — a GPU acabou não sendo usada).

---

## 3. Estrutura do repositório

| Caminho | Conteúdo |
|---|---|
| `instrucoes.md` | Este documento |
| `README.md` | Visão rápida e comandos principais |
| `saidas-gpt.md` | Planejamento inicial (conversa com o ChatGPT) que originou o trabalho |
| `requirements.txt` | Dependências Python |
| `.env.example` | Modelo de configuração (copiar para `.env`; o `.env` não é versionado) |
| `infra/dify/README.md` | Instalação do Dify e decisões de infraestrutura, em detalhe |
| `datasets/documentos/Regimento_PPGCC-UECE2021.pdf` | Base de conhecimento |
| `datasets/casos_teste.json` | Golden dataset (30 casos) |
| `tests/*.robot` | 7 suítes: `api`, `factualidade`, `alucinacao`, `robustez`, `seguranca`, `conversa`, `desempenho` |
| `resources/dify_keywords.robot` | Keywords compartilhadas |
| `libraries/dify_client.py` | Cliente da API do Dify (registro das respostas, retentativas, pausa entre chamadas) |
| `libraries/rag_evaluator.py` | Verificações: termos obrigatórios/proibidos, reconhecimento de ausência, citação de artigo, latência, consistência |
| `scripts/subir_ambiente.ps1` | Sobe o Dify no WSL e mantém o Ubuntu ativo |
| `scripts/smoke_test.py` | Teste rápido com uma pergunta |
| `scripts/executar.sh` | Roda uma execução numerada (suíte por suíte) e une os relatórios |
| `scripts/consolidar.py` | Tabela comparativa das execuções → `results/consolidado.md` |
| `scripts/avaliar_ragas.py` | Métricas semânticas com Ragas |
| `docs/prompt_sistema.txt` | Prompt de sistema congelado (v1.0) — é este o texto colado no Dify |
| `docs/prompt_sistema.md` | O mesmo prompt, com as regras de uso |
| `docs/protocolo_testes.md` | Protocolo: configuração exata do experimento, critérios, calibração e registro das execuções |
| `docs/relatorio.md` | Esqueleto do relatório |
| `results/exec1..3/` | Execuções oficiais (versionadas): `report.html`, `log.html`, `output.xml`, `respostas.jsonl` (pergunta, resposta, trechos recuperados, latência) |
| `results/consolidado.md` | Comparação das 3 execuções por caso e por suíte |

---

## 4. O golden dataset

30 casos em `datasets/casos_teste.json`, cada um com pergunta, resposta de referência, artigo do
regimento, trecho de origem, comportamento esperado e critérios de aceitação.

| Categoria | Casos | IDs |
|---|---|---|
| Factual | 9 | CT01–CT09 (CT09 = contradição do próprio regimento) |
| Alucinação | 5 | CT10, CT11, CT20–CT22 |
| Robustez | 5 | CT12, CT13, CT23–CT25 |
| Segurança | 4 | CT14, CT15, CT26, CT27 |
| Conversa (vários turnos) | 4 | CT16, CT28–CT30 |
| Desempenho | 3 | CT17–CT19 |

Inconsistências do regimento usadas como casos de teste:

- **CT09:** prazo da qualificação de doutorado — 36º mês (Art. 35 e §4º) × 30º mês (Art. 39, alínea d).
- **CT23:** o Art. 31, b escreve "48 (quarenta)" créditos; o Art. 32 confirma 48.

---

## 5. O que foi realizado (histórico)

1. **Planejamento** a partir de `saidas-gpt.md`: escolha de Dify + RAG, do regimento como base e da
   arquitetura Robot Framework + Ragas.
2. **Esqueleto do repositório** (suítes, bibliotecas, scripts, documentação) validado com `robot --dryrun`.
3. **Conferência do dataset no PDF:** as 8 referências sugeridas pelo ChatGPT estavam corretas; o
   CT13 foi corrigido (o Art. 36 não diz "reprovado"); a contradição do CT09 mostrou-se mais forte do
   que o previsto (envolve também o Art. 35, §4º); foi descoberta a divergência "48 (quarenta)".
   O dataset foi ampliado de 19 para 30 casos.
4. **Instalação do Dify 1.18.0** no WSL/Ubuntu, conforme o guia oficial. Ajustes necessários:
   - o Docker do Ubuntu dependia do plugin Compose do Docker Desktop → instalado o Compose oficial;
   - o WSL desligava o Ubuntu quando ocioso, derrubando o Dify → processo *keep-alive*.
5. **Modelos:** primeiro testado **Ollama local** (`qwen2.5:7b` na GPU, ~27 tokens/s), mas a máquina
   ficou pesada; o Ollama foi desinstalado. Considerada a OpenAI (paga) e escolhido o **Gemini no plano
   gratuito**. O `gemini-3.8-flash` não respondeu nos testes e foi trocado por `gemini-3.5-flash` como juiz.
6. **Configuração do Dify:** plugin Gemini, modelos padrão, base de conhecimento (chunking General,
   1024 tokens, sobreposição 100, *High Quality*), app **Chatbot** básico com o prompt congelado,
   busca híbrida (0,7 semântica / 0,3 palavra-chave, Top K 4) e citações ativadas.
7. **Calibração do avaliador** com uma execução preliminar (interrompida por falta de memória): 4 falsos
   negativos corrigidos com regras gerais (markdown, "12 (doze) meses", frases de recusa), e
   retentativa para erros de rede entre Dify e Gemini. Tudo registrado no protocolo.
8. **Três execuções oficiais** da suíte completa (29/10/2026).

### Resultados das execuções 1–3

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

Principais achados:

- **CT09 falhou nas 3 execuções:** o chatbot nunca reconhece a contradição (só cita os 36 meses).
- **CT30 falhou nas 3 e CT28 em 2:** em perguntas elípticas ("E no mestrado?") o chatbot responde
  "não há informações" ou **alucina** (exec 3: "28 créditos" para o mestrado; o correto é 24).
  Hipótese: o Chatbot básico do Dify busca na base usando só a última mensagem.
- **Segurança 12/12 e robustez 15/15** nas três execuções.
- **CT18:** respostas sempre factualmente corretas, mas a similaridade lexical oscila em torno do
  limite (0,5) — limitação da métrica.
- **CT21 (exec 3):** falso negativo do avaliador ("Não possuo essa informação"), mantido como registrado.
- Latência média 1,5–3,6 s (máx. 25,2 s).

O que ainda falta está detalhado na **seção 9**.

---

## 6. Como replicar em outro computador

### 6.1 Pré-requisitos

- **Windows 10/11** com **WSL 2** e uma distribuição **Ubuntu** (ou um Linux nativo — nesse caso pule
  as partes de WSL).
- No Ubuntu: `git`, `curl`, `openssl` e Docker Engine com o plugin Compose ≥ 2.24.
- **Python 3.11** no Windows (para a automação).
- Mínimo de 4 GB de RAM livres para o Dify (o guia recomenda 8 GB para o Docker).
- Uma conta Google para gerar a chave gratuita do Gemini.

### 6.2 Obter o projeto

```powershell
git clone <url-do-repositorio> pratica-inteligente
cd pratica-inteligente
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### 6.3 Habilitar systemd no Ubuntu (WSL)

O Docker precisa rodar como serviço. Dentro do Ubuntu, `/etc/wsl.conf` deve conter:

```ini
[boot]
systemd=true
```

Depois, no PowerShell: `wsl --shutdown` e abra o Ubuntu de novo.

### 6.4 Docker e Compose no Ubuntu

Se o Ubuntu ainda não tem Docker:

```bash
sudo apt-get update && sudo apt-get install -y docker.io
sudo systemctl enable --now docker
```

Se `docker compose version` falhar (ou apontar para o Docker Desktop), instale o plugin oficial:

```bash
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -fsSL -o /usr/local/lib/docker/cli-plugins/docker-compose \
  https://github.com/docker/compose/releases/download/v5.6.1/docker-compose-linux-x86_64
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
docker compose version
```

### 6.5 Instalar o Dify (dentro do Ubuntu, no sistema de arquivos Linux)

```bash
cd ~
git clone --depth 1 --branch 1.18.0 https://github.com/langgenius/dify.git
cd dify/docker
cp .env.example .env
TOKEN=$(openssl rand -base64 32)
sed -i "s|^DIFY_AGENT_LOCAL_SANDBOX_AUTH_TOKEN=.*|DIFY_AGENT_LOCAL_SANDBOX_AUTH_TOKEN=${TOKEN}|" .env
docker compose up -d
docker compose ps   # 15 serviços Up/healthy; init_permissions "Exited" é normal
```

No Windows, para os próximos usos: `.\scripts\subir_ambiente.ps1` (sobe o Dify e mantém o WSL ativo).
Se o script do projeto ficar em outro usuário/caminho do Ubuntu, ajuste `~/dify/docker` nele.

### 6.6 Chave do Gemini

1. Em https://aistudio.google.com/apikey, *Create API key* (não ative faturamento).
2. Veja os limites do plano gratuito em https://aistudio.google.com/rate-limit.
3. No `.env` do projeto, preencha `RAGAS_LLM_API_KEY` e ajuste `DIFY_INTERVALO_S` ao limite de
   requisições por minuto (nas execuções oficiais foi usado `50`).

### 6.7 Configurar o Dify (navegador)

1. **Conta:** http://localhost/install → criar administrador → login em http://localhost.
2. **Plugin:** *Settings → Model Provider* → instalar **Gemini** e informar a chave.
3. **Modelos padrão** (*System Model Settings*): LLM `gemini-3.5-flash-lite`; Embedding
   `gemini-embedding-001`; Rerank vazio.
4. **Base de conhecimento:** *Knowledge → Create Knowledge → Import from file* →
   `datasets/documentos/Regimento_PPGCC-UECE2021.pdf`:
   - Chunk: **General**, delimitador `\n\n`, máximo **1024** tokens, sobreposição **100**,
     "Replace consecutive spaces" marcado, "Delete URLs/emails" desmarcado;
   - Index Method: **High Quality**. Aguarde o status **Available** (esperado: 47 chunks).
5. **App:** *Studio → Criar do zero → "Mais tipos básicos de aplicativo" → **Chatbot*** (não usar
   "Fluxo de bate-papo"):
   - **Instruções:** conteúdo inteiro de `docs/prompt_sistema.txt`;
   - **Contexto:** + Adicionar → base do regimento; em *Configurações de recuperação*: pesos
     **0,7 semântico / 0,3 palavra-chave**, **Top K 4**, sem rerank, limite de pontuação desligado;
   - **Modelo:** `gemini-3.5-flash-lite`; **Output length 2048**. Grounding, URL context, Code
     execution e Include thoughts ficam desligados e Thinking level em Minimal (padrões do plugin).
     O plugin não oferece temperatura para este modelo;
   - **Recursos:** ativar **Citações e atribuições** (sem isso o Ragas fica sem contexto);
   - **Publicar**.
6. **Chave de API do app:** *Ponto de acesso → Chave de API → Criar* → copiar para `DIFY_API_KEY` no `.env`.

### 6.8 Rodar

```powershell
# Teste rápido
python scripts\smoke_test.py

# Execução completa numerada (Git Bash); resultados em results\execN\
bash scripts/executar.sh 1
bash scripts/executar.sh 1 factualidade conversa   # só algumas suítes
bash scripts/executar.sh 1 --merge                 # só reunir relatórios já gerados

# Comparar execuções
python scripts\consolidar.py 1 2 3

# Métricas semânticas de uma execução
python scripts\avaliar_ragas.py --resultados results\exec1\respostas.jsonl --saida results\exec1\metricas_ragas.csv
```

Relatórios: `results\execN\report.html` e `results\execN\log.html`.

---

## 7. Problemas conhecidos e soluções

| Sintoma | Causa | Solução |
|---|---|---|
| Dify some depois de alguns minutos / `localhost` não responde | WSL desligou o Ubuntu ocioso | `.\scripts\subir_ambiente.ps1` |
| `docker compose` mostra a ajuda do `docker` dentro do Ubuntu | plugin Compose era link para o Docker Desktop | instalar o Compose oficial (seção 6.4) |
| Criar base de conhecimento trava | modelos padrão não definidos | *System Model Settings* (seção 6.7, passo 3) |
| App sem consultar a base | app criado como "Fluxo de bate-papo" sem nó de conhecimento | usar o **Chatbot** básico |
| Teste reprova com `Network is unreachable` ou `RESOURCE_EXHAUSTED` | rede ou cota do Gemini | o cliente já tenta de novo; aumentar `DIFY_INTERVALO_S` / `DIFY_ESPERA_BASE_S` |
| Execução encerrada "por falta de memória" | pouca RAM livre no Windows | fechar programas; usar `scripts/executar.sh`, que roda suíte por suíte |
| `gemini-3.8-flash` não responde | modelo indisponível/lento no plano gratuito | usar `gemini-3.5-flash` como juiz |

---

## 8. Regras do experimento (para manter a comparabilidade)

- Não alterar o prompt (`docs/prompt_sistema.txt`), o chunking, a busca nem os modelos depois das
  execuções oficiais. Qualquer mudança é uma nova configuração e deve ser registrada no protocolo.
- Não recalibrar o avaliador após as execuções oficiais; falsos negativos são anotados na análise.
- Registrar cada execução na tabela de `docs/protocolo_testes.md`.
- Nunca versionar o `.env` (contém as chaves).

---

## 9. Atividades pendentes (continuação do trabalho)

Situação em 29/10/2026: ambiente montado, dataset conferido e **3 execuções oficiais concluídas**
(`results/exec1..3`). Falta a avaliação semântica, a análise das falhas, o relatório e a apresentação.

**Prazos:** relatório em **04/11/2026** · apresentação em **16/11/2026**.

### 9.1 Antes de tudo: o que vem e o que não vem no repositório

- **Vem:** código, dataset, PDF, documentação e os resultados das 3 execuções (`results/exec1..3`).
  Para as atividades 9.3 a 9.6 **não é preciso ter o Dify instalado**: tudo usa os arquivos de `results/`.
- **Não vem:** o `.env` (chaves) e a configuração do Dify (fica no banco de dados local de quem instalou).
  - Para rodar o Ragas basta uma **chave própria do Gemini** no `.env` (`RAGAS_LLM_API_KEY`).
  - Só é preciso reinstalar e configurar o Dify (seção 6) para fazer **novas execuções** ou a
    **demonstração ao vivo**. Um Dify configurado em outra máquina é uma nova instância: novas
    execuções devem ser registradas no protocolo como tal, e não misturadas às execuções 1–3.

### 9.2 Preparar o ambiente Python

- [ ] `python -m venv .venv`, ativar e `pip install -r requirements.txt` (inclui Ragas e `langchain-openai`).
- [ ] `copy .env.example .env` e preencher `RAGAS_LLM_API_KEY` com a chave do Gemini
      (https://aistudio.google.com/apikey).

### 9.3 Métricas semânticas com Ragas (prioridade 1)

O `scripts/avaliar_ragas.py` **ainda não foi executado de verdade** — só foi escrito. Pode exigir
pequenos ajustes de compatibilidade com a versão do Ragas instalada (nomes de classes/colunas).

- [ ] Rodar para cada execução (os casos elegíveis são os marcados com `"ragas"` no dataset e com
      trechos recuperados; cerca de 20 por execução):
      ```powershell
      python scripts\avaliar_ragas.py --resultados results\exec1\respostas.jsonl --saida results\exec1\metricas_ragas.csv
      python scripts\avaliar_ragas.py --resultados results\exec2\respostas.jsonl --saida results\exec2\metricas_ragas.csv
      python scripts\avaliar_ragas.py --resultados results\exec3\respostas.jsonl --saida results\exec3\metricas_ragas.csv
      ```
- [ ] Cada amostra gera várias chamadas ao juiz (`gemini-3.5-flash`). Com a cota gratuita, provavelmente
      será preciso **uma execução por dia** ou reduzir `RAGAS_MAX_WORKERS` para 1. Se a cota acabar no
      meio, rodar de novo só aquela execução.
- [ ] Anotar no protocolo os limites da conta (RPM/RPD) vistos em https://aistudio.google.com/rate-limit.
- [ ] Comparar as médias com as metas do protocolo (Faithfulness ≥ 0,90; Factual Correctness ≥ 0,85;
      Context Precision ≥ 0,80) e registrar uma linha por execução em `docs/protocolo_testes.md`.
- [ ] Olhar os casos com nota baixa: o Ragas e as verificações determinísticas concordam?
      (ex.: CT09 deve ter Factual Correctness baixa; CT18 deve ter nota alta apesar da similaridade lexical baixa).

### 9.4 Análise das falhas (prioridade 2)

Fonte: `results/consolidado.md` e os `respostas.jsonl` (campos `resposta`, `contextos`, `fontes`).

- [ ] **CT28 / CT30 (conversa):** verificar a hipótese de que o Chatbot do Dify busca na base usando só a
      última mensagem. Comparar os `contextos` recuperados no 2º turno ("E no mestrado?", "E no
      doutorado?") com os do 1º turno: se os trechos do Art. 31, a / Art. 43, §1º não aparecem, a falha é
      de **recuperação**; se aparecem e mesmo assim a resposta está errada, é de **geração**.
      O caso da exec 3 do CT28 ("28 créditos") é alucinação: conferir se o número 28 aparece em algum trecho.
- [ ] **CT09 (contradição):** conferir se o trecho do Art. 39 (chunk que começa com "39. O desempenho")
      foi recuperado. Lembrar que o rótulo "Art. 39" ficou partido entre dois chunks (ver protocolo).
- [ ] **CT18:** mostrar que as 3 respostas são factualmente iguais e discutir a limitação da similaridade lexical.
- [ ] **CT21 (exec 3) e CT22 (exec 1):** registrar como falso negativo do avaliador e falha parcial, respectivamente.
- [ ] Montar uma tabela: caso · execuções em que falhou · tipo (recuperação / geração / oráculo) · evidência.

### 9.5 Relatório (`docs/relatorio.md`) — entrega 04/11

As seções já estão criadas com comentários do que entra em cada uma. Material pronto para usar:

- [ ] **Sistema sob teste e metodologia:** seções 1, 2 e 4 deste arquivo + tabela de configuração e
      critérios de `docs/protocolo_testes.md` + `infra/dify/README.md` (decisões de infraestrutura).
- [ ] **Resultados:** tabelas de `results/consolidado.md`, métricas do Ragas (9.3), latências.
- [ ] **Discussão:** análise das falhas (9.4). Pontos fortes: segurança 12/12 e robustez 15/15.
- [ ] **Ameaças à validade** (já identificadas):
      - avaliador por expressões regulares → falsos negativos (calibração preliminar + CT21 exec 3);
      - juiz do Ragas da mesma família do modelo testado (Gemini);
      - temperatura não configurável no plugin → não determinismo (medido pelas 3 execuções);
      - um único documento, 30 casos;
      - modelos do plano gratuito podem mudar de versão; limites de cota;
      - chunking com ruído da extração do PDF ("Art. 3 9", imagens do cabeçalho).
- [ ] **Conclusão e referências** (Dify, Gemini, Ragas, Robot Framework, regimento).

### 9.6 Apresentação — 16/11 (15 minutos)

- [ ] Slides: problema → SUT → metodologia (dataset + avaliação em dois níveis) → resultados → achados → limitações.
- [ ] **Demonstração ao vivo** (exige o Dify configurado na máquina da apresentação, seção 6):
      `python scripts\smoke_test.py` e uma suíte curta, por exemplo
      `bash scripts/executar.sh demo seguranca`. Com `DIFY_INTERVALO_S=50` cada pergunta leva quase
      1 minuto: para a demo, usar um valor menor (ex.: 5) se a cota permitir, ou mostrar o
      `results/exec1/log.html` já gerado como alternativa.
- [ ] Ensaiar com cronômetro.

### 9.7 Ao final

- [ ] Gerar uma nova chave do Gemini e apagar a antiga (a atual foi compartilhada em conversa).
- [ ] Revogar a chave de API do app no Dify, se o ambiente ficar ligado.
