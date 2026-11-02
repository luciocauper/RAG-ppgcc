<#
.SYNOPSIS
    Prepara o ambiente Python do projeto RAG-PPGCC no Windows.
.DESCRIPTION
    Verifica Python, cria/ativa o venv, instala dependências, verifica pacotes
    e orienta a configuração do .env. Idempotente: pode ser executado repetidamente.
.NOTES
    Não instala softwares de sistema nem altera configurações globais.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$Raiz = Split-Path -Parent $PSScriptRoot

function Escrever-Cabecalho {
    Write-Host ""
    Write-Host "===== RAG-PPGCC — Preparacao do ambiente =====" -ForegroundColor Cyan
    Write-Host ""
}

function Escrever-OK    { param($msg) Write-Host "  [OK]    $msg" -ForegroundColor Green }
function Escrever-Aviso  { param($msg) Write-Host "  [AVISO]  $msg" -ForegroundColor Yellow }
function Escrever-Erro   { param($msg) Write-Host "  [ERRO]   $msg" -ForegroundColor Red }
function Escrever-Info   { param($msg) Write-Host "  [INFO]   $msg" -ForegroundColor Gray }

# --- 1. Verificar Python ---
Escrever-Cabecalho
Write-Host "1. Verificando Python..." -ForegroundColor White
try {
    $pyVersion = & python --version 2>&1
    if ($LASTEXITCODE -ne 0) { throw "python nao encontrado" }
    Escrever-OK "Python instalado: $pyVersion"
    $versaoNum = [version]($pyVersion -replace "Python ", "")
    if ($versaoNum.Major -lt 3 -or ($versaoNum.Major -eq 3 -and $versaoNum.Minor -lt 11)) {
        Escrever-Erro "Python 3.11+ necessario (atual: $pyVersion)"
        exit 1
    }
} catch {
    Escrever-Erro "Python nao encontrado no PATH. Instale Python 3.11+ de https://python.org"
    exit 1
}

# --- 2. Ambiente virtual ---
Write-Host ""
Write-Host "2. Ambiente virtual (.venv)..." -ForegroundColor White
$venvPython = Join-Path $Raiz ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Escrever-Info "Criando .venv..."
    & python -m venv "$Raiz\.venv" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Escrever-Erro "Falha ao criar .venv"
        exit 1
    }
    Escrever-OK ".venv criado"
} else {
    Escrever-OK ".venv ja existe"
}

# Usar o python do venv daqui em diante
$py = $venvPython
& $py -m pip install --upgrade pip 2>&1 | Out-Null

# --- 3. Instalar dependencias ---
Write-Host ""
Write-Host "3. Instalando dependencias..." -ForegroundColor White
$reqPath = Join-Path $Raiz "requirements.txt"
& $py -m pip install -r "$reqPath" --quiet 2>&1 | ForEach-Object {
    if ($_ -match "error|ERROR|Error") { Escrever-Erro $_ }
}
# Verificar pacotes essenciais
$pacotes = @("robot", "requests", "dotenv", "pptx", "docx", "pytest")
$todosOk = $true
foreach ($p in $pacotes) {
    $mod = if ($p -eq "dotenv") { "dotenv" } elseif ($p -eq "pptx") { "pptx" } elseif ($p -eq "docx") { "docx" } else { $p }
    $check = & $py -c "import $mod; print('ok')" 2>&1
    if ($check -match "ok") {
        Escrever-OK "Pacote $p"
    } else {
        Escrever-Erro "Pacote $p nao disponivel"
        $todosOk = $false
    }
}
if (-not $todosOk) {
    Escrever-Aviso "Alguns pacotes nao instalaram. Tente: & $py -m pip install -r requirements.txt"
}

# --- 4. Verificar .env ---
Write-Host ""
Write-Host "4. Configuracao (.env)..." -ForegroundColor White
$envPath = Join-Path $Raiz ".env"
$envExample = Join-Path $Raiz ".env.example"
if (-not (Test-Path $envPath)) {
    if (Test-Path $envExample) {
        Copy-Item $envExample $envPath
        Escrever-Aviso ".env copiado de .env.example. Edite e preencha as chaves."
    } else {
        Escrever-Erro ".env.example nao encontrado"
        exit 1
    }
} else {
    Escrever-OK ".env existe"
}

# Verificar chaves criticas
$envContent = Get-Content $envPath -Raw
$chavesObrigatorias = @("DIFY_API_KEY", "DIFY_API_URL")
$chavesOpcionais = @("RAGAS_LLM_API_KEY")
foreach ($chave in $chavesObrigatorias) {
    if ($envContent -match "${chave}=(.+)") {
        $valor = $Matches[1].Trim()
        if ($valor -match "xxx|sua-chave|app-xxxx") {
            Escrever-Aviso "$chave ainda tem placeholder — preencha com a chave real do Dify"
        } else {
            Escrever-OK "$chave configurada"
        }
    } else {
        Escrever-Aviso "$chave ausente no .env"
    }
}
foreach ($chave in $chavesOpcionais) {
    if ($envContent -match "${chave}=(.+)") {
        $valor = $Matches[1].Trim()
        if ($valor -match "sua-chave|xxx") {
            Escrever-Aviso "$chave tem placeholder — necessaria apenas para Ragas"
        } else {
            Escrever-OK "$chave configurada"
        }
    } else {
        Escrever-Info "$chave ausente (necessaria apenas para metricas Ragas)"
    }
}

# --- 5. Resumo ---
Write-Host ""
Write-Host "===== Resumo =====" -ForegroundColor Cyan
Write-Host "  Para ativar o venv manualmente:  .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  Para executar testes:             .\scripts\executar_windows.ps1 -Modo smoke" -ForegroundColor White
Write-Host "  Guia completo:                    docs\GUIA_EXECUCAO_WINDOWS.md" -ForegroundColor White
Write-Host ""

if ($todosOk) {
    Escrever-OK "Ambiente preparado com sucesso."
    exit 0
} else {
    Escrever-Aviso "Ambiente parcialmente preparado — revise os avisos acima."
    exit 0
}
