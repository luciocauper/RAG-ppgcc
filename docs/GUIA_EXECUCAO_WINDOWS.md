# Guia de Execução no Windows — RAG-PPGCC

> Passo a passo completo, do PowerShell aos resultados. Comandos em PowerShell (não use Bash aqui).

---

## 1. Pré-requisitos

| Item | O que é | Como verificar |
|---|---|---|
| Python 3.11+ | Linguagem da automação | `python --version` |
| PowerShell 5.1+ | Shell do Windows | `$PSVersionTable.PSVersion` |
| Dify (opcional) | Sistema sob teste | `Invoke-RestMethod http://localhost/v1/parameters` |
| Chave do Gemini (opcional) | Para Ragas | Configurada no `.env` |

**Importante:** testes unitários e dry-run NÃO precisam do Dify nem do Gemini.
Apenas a execução real dos 30 cenários e as métricas Ragas chamam serviços externos.

---

## 2. Preparar o ambiente (uma vez)

```powershell
# Abra o PowerShell na pasta do projeto
cd "C:\Users\Ana Klyssia\Documents\testesSistemaInteligente\RAG-ppgcc"

# Execute o script de setup (cria .venv, instala dependências, verifica .env)
.\scripts\setup_windows.ps1
```

O script faz tudo automaticamente: verifica Python, cria o venv, instala as dependências
e orienta a configuração do `.env`. Pode ser executado repetidamente (idempotente).

Se não tiver o `.env`, ele copia do `.env.example`. Edite e preencha:
- `DIFY_API_KEY` — chave da aplicação no Dify (obrigatória para executar os testes)
- `RAGAS_LLM_API_KEY` — chave do Gemini AI Studio (necessária apenas para Ragas)

---

## 3. Configurar o .env

```powershell
# Se não existir, copie do exemplo
if (-not (Test-Path .env)) { Copy-Item .env.example .env }

# Edite com seu editor preferido
notepad .env
```

Preencha no mínimo:
```
DIFY_API_URL=http://localhost/v1
DIFY_API_KEY=app-sua-chave-real
```

Para Ragas (opcional):
```
RAGAS_LLM_API_KEY=sua-chave-do-ai-studio
```

---

## 4. Verificar o Dify (opcional)

O Dify precisa estar rodando se você for executar os 30 cenários contra o sistema real.

```powershell
# Verificar se a API responde
try {
    Invoke-RestMethod -Uri "http://localhost/v1/parameters" -TimeoutSec 5 -Headers @{"Authorization"="Bearer $env:DIFY_API_KEY"}
    Write-Host "Dify disponível" -ForegroundColor Green
} catch {
    Write-Host "Dify indisponível. Testes unitários e dry-run ainda funcionam." -ForegroundColor Yellow
}
```

Se o Dify não estiver rodando, você ainda pode:
- Executar testes unitários (pytest)
- Fazer o dry-run (validação de sintaxe)
- Consolidar resultados históricos

---

## 5. Execução por modo

### 5.1 Testes unitários (não precisa do Dify)

```powershell
.\scripts\executar_windows.ps1 -Modo unit
```

Resultado esperado: 49 testes aprovados.

### 5.2 Smoke test (precisa do Dify)

```powershell
.\scripts\executar_windows.ps1 -Modo smoke
```

Verifica se a API está acessível, a chave é válida e a recuperação funciona.
Se falhar, o Dify não está disponível ou a chave é inválida.

### 5.3 Execução completa (precisa do Dify)

```powershell
.\scripts\executar_windows.ps1 -Modo completo
```

Executa: testes unitários → smoke → 34 testes Robot → consolidação.
As evidências ficam em `results/execN/` (próximo número disponível).
**Atenção:** chama a API do Dify e consome cota do Gemini.

### 5.4 Consolidar resultados (não precisa do Dify)

```powershell
.\scripts\executar_windows.ps1 -Modo consolidar
```

Gera `results/consolidado.md` com a tabela comparativa de todas as execuções.

### 5.5 Métricas Ragas (precisa do Gemini)

```powershell
.\scripts\executar_windows.ps1 -Modo ragas -Exec 1
```

Calcula Faithfulness, Factual Correctness e Context Precision sobre as respostas
da execução 1. **Atenção:** chama o Gemini como juiz e consome cota.

---

## 6. Validação de sintaxe (não precisa do Dify)

```powershell
# Dry-run do Robot (verifica keywords, imports, estrutura)
python -m robot --dryrun --outputdir $env:TEMP\robot_check tests\

# Compilação de todos os scripts Python
python -m py_compile libraries\dify_client.py libraries\rag_evaluator.py scripts\avaliar_ragas.py scripts\consolidar.py
```

---

## 7. Consultar os resultados

### 7.1 Resultados da execução

```powershell
# Relatório HTML do Robot
Start-Process results\exec1\report.html

# Log detalhado
Start-Process results\exec1\log.html

# Consolidado (Markdown)
Start-Process results\consolidado.md
```

### 7.2 Respostas do sistema (JSONL)

As respostas estão em `results/execN/respostas.jsonl`, uma por linha, com:
- `caso_id`, `pergunta`, `resposta`, `conversation_id`
- `contextos` (trechos recuperados), `fontes` (documentos, scores)
- `latencia_s`, `tentativas`, `timestamp`

### 7.3 Métricas semânticas (quando executadas)

```powershell
# CSV com métricas por caso
Start-Process results\exec1\metricas_ragas.csv
```

---

## 8. Erros frequentes e soluções

| Sintoma | Causa provável | Solução |
|---|---|---|
| `ModuleNotFoundError: No module named 'robot'` | Venv não ativado ou deps não instaladas | `.\scripts\setup_windows.ps1` |
| `DIFY_API_KEY não configurada` | `.env` com placeholder | Editar `.env` com a chave real |
| `API do Dify indisponível: HTTP 000` | Dify não está rodando | `.\scripts\subir_ambiente.ps1` |
| `HTTP 401` | Chave inválida | Gerar nova chave no Dify (Studio > API Access) |
| `RESOURCE_EXHAUSTED` | Cota do Gemini esgotada | Aguardar reset da cota ou reduzir `DIFY_INTERVALO_S` |
| `Network is unreachable` | Rede entre Dify e Gemini | O cliente tenta novamente; aumentar `DIFY_ESPERA_BASE_S` |
| `AssertionError` em teste | Resposta não atende critério | Verificar `results/execN/log.html` para detalhes |
| pytest falha | Mudança no código | `python -m pytest tests/unit/ -v` para detalhes |

---

## 9. Comandos rápidos (referência)

```powershell
# Setup completo
.\scripts\setup_windows.ps1

# Apenas testes unitários
.\scripts\executar_windows.ps1 -Modo unit

# Smoke (verificar ambiente)
.\scripts\executar_windows.ps1 -Modo smoke

# Tudo (com Dify)
.\scripts\executar_windows.ps1 -Modo completo

# Consolidar
.\scripts\executar_windows.ps1 -Modo consolidar

# Ragas (com Gemini)
.\scripts\executar_windows.ps1 -Modo ragas -Exec 1

# Dry-run (sem Dify)
python -m robot --dryrun tests\

# Relatório
Start-Process results\exec1\report.html
```

---

## 10. Preservação das evidências

As execuções oficiais (`results/exec1`, `exec2`, `exec3`) **não devem ser modificadas**.
Novas execuções criam pastas próprias (`exec4`, `exec5`, etc.) automaticamente.
O script `executar_windows.ps1 -Modo completo` sempre usa o próximo número disponível.

```powershell
# Verificar quais execuções existem
Get-ChildItem results -Directory -Filter "exec*"
```
