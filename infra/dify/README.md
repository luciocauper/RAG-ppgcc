# Dify Community (self-hosted) — sistema sob teste

Repositório oficial: https://github.com/langgenius/dify
Guia seguido: https://docs.dify.ai/en/self-host/deploy/quick-start/docker-compose

**Versão usada no experimento: Dify `1.18.0`** (release de 23/10/2026), rodando localmente.
**Modelos: remotos, via API do Google Gemini no plano gratuito** (LLM e embeddings).

## Arquitetura do ambiente

```
Windows 11 ──localhost:80──▶ WSL 2 / Ubuntu 22.04 (systemd)
                               └─ Docker Engine nativo (docker.io 27.5) + Compose v5.6.1
                                  └─ projeto compose "docker" em ~/dify/docker
                                     └─ 15 serviços do Dify (api, worker, web, nginx, weaviate, ...)
                                            │
                                            └──HTTPS──▶ API do Gemini (LLM + embeddings)
```

Decisões e motivos:

- **Código e dados no sistema de arquivos Linux** (`~/dify`), como recomenda o guia oficial para Windows.
- **Docker nativo do Ubuntu, não o Docker Desktop.** O Ubuntu já tinha um Docker Engine próprio.
  O plugin `docker compose` dele era um link para o Docker Desktop, que some quando o Desktop
  entra em modo ocioso. Por isso foi instalado o binário oficial do Compose v5.6.1 em
  `/usr/local/lib/docker/cli-plugins/` (o link antigo ficou como `docker-compose.desktop-link.bak`).
- **Keep-alive do WSL:** o WSL desliga a distribuição quando nenhum processo do Windows está ligado
  a ela, o que derruba o Dify. O script `scripts/subir_ambiente.ps1` mantém um `sleep infinity` oculto.
- **Modelos remotos gratuitos (Gemini) em vez de Ollama local.** A primeira versão usava
  `qwen2.5:7b` no Ollama com GPU (RTX 3050 6 GB), mas o modelo não cabia inteiro na VRAM e deixava
  a máquina pesada. Considerou-se a OpenAI (paga); optou-se pelo plano gratuito do Gemini.
  Consequências: limites de requisições por minuto e por dia (o cliente espera e tenta de novo; ver
  `DIFY_INTERVALO_S` no `.env`) e, segundo os termos do plano gratuito do Google, o conteúdo enviado
  pode ser usado para melhorar os produtos — aceitável aqui, pois o regimento é público.
  O Ollama foi desinstalado (Windows e container) e os modelos apagados; a configuração antiga
  ficou só como referência em `~/dify/docker/docker-compose.override.yaml.ollama-desativado`.

## Subir o ambiente (dia a dia)

```powershell
.\scripts\subir_ambiente.ps1
```

Status / logs:

```powershell
wsl -d Ubuntu -- bash -c "cd ~/dify/docker && docker compose ps"
wsl -d Ubuntu -- bash -c "cd ~/dify/docker && docker compose logs --tail 50 api"
```

## Reproduzir a instalação do zero (dentro do Ubuntu, como root)

```bash
cd ~ && git clone --depth 1 --branch 1.18.0 https://github.com/langgenius/dify.git
cd dify/docker && cp .env.example .env
TOKEN=$(openssl rand -base64 32)
sed -i "s|^DIFY_AGENT_LOCAL_SANDBOX_AUTH_TOKEN=.*|DIFY_AGENT_LOCAL_SANDBOX_AUTH_TOKEN=${TOKEN}|" .env

# Só se o Docker do Ubuntu não tiver o plugin compose:
curl -fsSL -o /usr/local/lib/docker/cli-plugins/docker-compose \
  https://github.com/docker/compose/releases/download/v5.6.1/docker-compose-linux-x86_64
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

docker compose up -d
```

## Configuração no painel do Dify

1. **Conta de administrador:** http://localhost/install, depois login em http://localhost.
2. **Chave do Gemini (gratuita):** em https://aistudio.google.com/apikey, *Create API key*.
   Não ativar faturamento no projeto, para que ele permaneça no plano gratuito.
   Os limites do plano gratuito por modelo aparecem em https://aistudio.google.com/rate-limit —
   anotá-los em `docs/protocolo_testes.md` e ajustar `DIFY_INTERVALO_S` no `.env`.
3. **Modelos:** *Settings > Model Provider* → instalar o plugin **Gemini** e informar a API key.
   Em *System Model Settings*:
   - *System Reasoning Model*: `gemini-3.5-flash-lite`
   - *Embedding Model*: `gemini-embedding-001`

   Modelos conferidos em https://ai.google.dev/gemini-api/docs/models em 29/10/2026 (a família 2.5
   não está mais disponível para projetos novos). Se o plugin não listar algum deles, usar o
   equivalente mais próximo e registrar o nome exato no protocolo.
4. **Base de conhecimento:** *Knowledge > Create Knowledge* → enviar
   `datasets/documentos/Regimento_PPGCC-UECE2021.pdf`. Indexação *High Quality* (usa o modelo de
   embeddings). Registrar em `docs/protocolo_testes.md`: chunking (modo, tamanho, sobreposição),
   recuperação (vetorial / full-text / híbrida), Top K, score threshold e rerank. Conferir na
   pré-visualização se os artigos (ex.: Art. 35 e Art. 39) aparecem legíveis.
5. **Aplicação:** *Studio > Create App > Chatbot*:
   - *Instructions*: prompt de `docs/prompt_sistema.md` (versão congelada).
   - *Context*: a base do regimento.
   - *Features*: habilitar **Citations and Attributions** (sem isso a API não devolve
     `retriever_resources` e o Ragas fica sem contexto).
   - Modelo `gemini-3.5-flash-lite`, temperatura 0 → *Publish*.
6. **API:** no app, *API Access > API Key > Create* e copiar a chave para o `.env` da raiz:
   ```
   DIFY_API_URL=http://localhost/v1
   DIFY_API_KEY=app-...
   ```
   Validar: `python scripts/smoke_test.py`

## Parar

```powershell
wsl -d Ubuntu -- bash -c "cd ~/dify/docker && docker compose down"   # dados ficam em volumes/
```
