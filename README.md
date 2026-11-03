de automação e documentos têm versões fixadas; dependências semânticas opcionais
diferente; não interprete diferenças de ambiente como evolução do sistema.
o ambiente. Não altere os limiares para aprovar respostas observadas.
o próximo diretório `execN`, executa smoke e os 33 testes sem smoke, registra
da exec4; para resultados atuais, use os Word e PowerPoint acima.
# RAG-PPGCC

Projeto acadêmico de Teste de Sistemas Inteligentes (PPGCC/UECE) que avalia, por API,
um assistente RAG no Dify sobre o Regimento do PPGCC. A suíte mantém 30 cenários
experimentais em BDD e verificações de infraestrutura separadas.

## Arquitetura

```text
tests/*.robot -> resources/dify_keywords.robot
              -> libraries/dify_client.py + libraries/rag_evaluator.py
output.xml + respostas.jsonl -> scripts/consolidar.py -> Word por execução
                              -> scripts/gerar_relatorio.py -> Word acadêmico
                              -> scripts/gerar_apresentacao.py -> PowerPoint
```

## Tecnologias

Python, Robot Framework, pytest, requests, python-docx, python-pptx e Pillow.
Ragas é um avaliador complementar opcional; não há métricas Ragas nesta entrega.

## Pré-requisitos e ambiente

Python 3.11+ e Windows PowerShell 5.1. Crie o ambiente e instale as dependências:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Configuração do .env

Copie `.env.example` para `.env` e preencha `DIFY_API_URL` e `DIFY_API_KEY`.
`RAGAS_LLM_API_KEY` é necessária apenas para avaliação semântica. Nunca versione
credenciais. O setup local do Dify e as configurações experimentais estão descritos
em [infra/dify/README.md](infra/dify/README.md) e [docs/protocolo_testes.md](docs/protocolo_testes.md).

## Robot Framework

Validações sem acesso externo:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit -q
.\.venv\Scripts\python.exe -m robot --dryrun --outputdir results/local/dryrun tests/
```

Execução real, que consome a API, é opcional:

```powershell
.\scripts\executar_windows.ps1 -Modo completo
```

## Relatórios Word

```powershell
.\.venv\Scripts\python.exe scripts/consolidar.py 1 2 3 4
.\.venv\Scripts\python.exe scripts/gerar_relatorio.py
.\.venv\Scripts\python.exe scripts/gerar_apresentacao.py
```

O relatório acadêmico é `results/Relatorio_Final_Testes_RAG_PPGCC.docx`.
Cada execução tem seu Word individual em `results/execN/`. A apresentação e o roteiro
de 15 minutos ficam em `apresentação/`.

## Evidências

As quatro execuções oficiais estão em `results/exec1` a `results/exec4`, com XML, HTML,
JSONL e documentos Word. Não confunda os testes de API/infraestrutura com os 30 casos
experimentais. Exec1–3 tiveram 26/30 casos experimentais aprovados; exec4, 25/30.

## Estrutura

```text
datasets/       golden dataset e documento de referência
docs/           protocolo experimental e prompt congelado
infra/          notas específicas do ambiente Dify
libraries/      cliente da API e avaliador determinístico
resources/      keywords Robot compartilhadas
results/        evidências, relatórios Word e execuções oficiais
scripts/        execução, avaliação e geração de entregáveis
tests/          suítes Robot e testes unitários Python
apresentação/   PowerPoint e roteiro
```
