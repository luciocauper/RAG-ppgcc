<#
.SYNOPSIS
    Executa os testes do projeto RAG-PPGCC no Windows.
.DESCRIPTION
    Interface centralizada de execucao por modo:
      smoke        - Apenas o smoke test da API (tag smoke)
      unit         - Testes unitarios Python (pytest)
      completo     - Unit + smoke + todas as suites + consolidacao
      consolidar   - Consolida resultados das execucoes oficiais 1-3
      ragas        - Metricas semanticas (requer cota do Gemini)
.PARAMETER Modo
    Modo de execucao (obrigatorio).
.PARAMETER Exec
    Numero da execucao para o modo 'completo' (default: proximo disponivel).
.EXAMPLE
    .\scripts\executar_windows.ps1 -Modo smoke
    .\scripts\executar_windows.ps1 -Modo unit
    .\scripts\executar_windows.ps1 -Modo completo
    .\scripts\executar_windows.ps1 -Modo consolidar
    .\scripts\executar_windows.ps1 -Modo ragas -Exec 1
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("smoke", "unit", "completo", "consolidar", "ragas")]
    [string]$Modo,

    [int]$Exec
)

$ErrorActionPreference = "Stop"
$Raiz = Split-Path -Parent $PSScriptRoot
$py = Join-Path $Raiz ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

function Escrever-Titulo { param($msg) Write-Host "`n===== $msg =====" -ForegroundColor Cyan }
function Escrever-OK     { param($msg) Write-Host "  [OK]    $msg" -ForegroundColor Green }
function Escrever-Falha  { param($msg) Write-Host "  [FALHA] $msg" -ForegroundColor Red }
function Escrever-Info   { param($msg) Write-Host "  [INFO]  $msg" -ForegroundColor Gray }

$codigoSaida = 0

switch ($Modo) {

    "smoke" {
        Escrever-Titulo "SMOKE TEST (API do Dify)"
        Escrever-Info "Verifica disponibilidade da API e chave."
        Escrever-Info "Requer Dify rodando e DIFY_API_KEY configurada."
        & $py -m robot --include smoke --outputdir "$Raiz\results\smoke_temp" "$Raiz\tests\api.robot" 2>&1 | ForEach-Object { Write-Host $_ }
        if ($LASTEXITCODE -eq 0) {
            Escrever-OK "Smoke test passou. Ambiente disponivel."
        } else {
            Escrever-Falha "Smoke test falhou. Verifique se o Dify esta rodando e se a chave e valida."
            $codigoSaida = 1
        }
        Remove-Item -Recurse -Force "$Raiz\results\smoke_temp" -ErrorAction SilentlyContinue
    }

    "unit" {
        Escrever-Titulo "TESTES UNITARIOS (pytest)"
        & $py -m pytest "$Raiz\tests\unit" -v --tb=short 2>&1 | ForEach-Object { Write-Host $_ }
        if ($LASTEXITCODE -eq 0) {
            Escrever-OK "Todos os testes unitarios passaram."
        } else {
            Escrever-Falha "Testes unitarios falharam."
            $codigoSaida = 1
        }
    }

    "completo" {
        Escrever-Titulo "EXECUCAO COMPLETA"

        # Determinar numero da execucao
        if (-not $Exec) {
            $exes = @(Get-ChildItem "$Raiz\results" -Directory | Where-Object { $_.Name -match "^exec\d+$" } | ForEach-Object { [int]($_.Name -replace "exec", "") })
            $Exec = if ($exes.Count -gt 0) { ($exes | Measure-Object -Maximum).Maximum + 1 } else { 1 }
        }
        $saidaDir = "$Raiz\results\exec$Exec"
        Escrever-Info "Diretorio de saida: results\exec$Exec"
        Escrever-Info "ATENCAO: Esta execucao chama a API do Dify (consome cota do Gemini)."
        Escrever-Info "         Pressione Ctrl+C para cancelar se necessario."

        # 1. Testes unitarios
        Escrever-Titulo "1. Testes unitarios"
        & $py -m pytest "$Raiz\tests\unit" -q --tb=short 2>&1 | ForEach-Object { Write-Host $_ }
        if ($LASTEXITCODE -ne 0) { Escrever-Falha "Testes unitarios falharam."; $codigoSaida = 1; break }

        # 2. Smoke test
        Escrever-Titulo "2. Smoke test"
        & $py -m robot --include smoke --outputdir "$Raiz\results\smoke_check" "$Raiz\tests\api.robot" 2>&1 | ForEach-Object { Write-Host $_ }
        if ($LASTEXITCODE -ne 0) {
            Escrever-Falha "Smoke falhou. Ambiente indisponivel — abortando suites dependentes do Dify."
            Remove-Item -Recurse -Force "$Raiz\results\smoke_check" -ErrorAction SilentlyContinue
            $codigoSaida = 1
            break
        }
        Escrever-OK "Ambiente disponivel."
        Remove-Item -Recurse -Force "$Raiz\results\smoke_check" -ErrorAction SilentlyContinue

        # 3. Suites completas
        Escrever-Titulo "3. Suites completas (34 testes)"
        New-Item -ItemType Directory -Path "$saidaDir\parciais" -Force | Out-Null
        $env:RESULTADOS_JSONL = "$saidaDir\respostas.jsonl"
        $env:PYTHONIOENCODING = "utf-8"
        $suites = @("api", "factualidade", "alucinacao", "robustez", "seguranca", "conversa", "desempenho")
        foreach ($suite in $suites) {
            Escrever-Info "Executando: $suite"
            & $py -m robot --name $suite --outputdir "$saidaDir\parciais" --output "$suite.xml" --log NONE --report NONE "$Raiz\tests\$suite.robot" 2>&1 | ForEach-Object { Write-Host $_ }
        }

        # 4. Unir resultados com rebot
        Escrever-Titulo "4. Unindo resultados (rebot)"
        $parciais = (Get-ChildItem "$saidaDir\parciais\*.xml" | ForEach-Object { $_.FullName }) -join " "
        & $py -m robot.rebot --name "Execucao $Exec" --outputdir "$saidaDir" --output output.xml $parciais 2>&1 | Out-Null
        Escrever-OK "Relatorios gerados em: results\exec$Exec\"

        # 5. Consolidar
        Escrever-Titulo "5. Consolidacao"
        $exesConsolidar = @(Get-ChildItem "$Raiz\results" -Directory | Where-Object { $_.Name -match "^exec\d+$" } | ForEach-Object { $_.Name -replace "exec", "" })
        $exesConsolidar = $exesConsolidar | ForEach-Object { [int]$_ } | Sort-Object
        $exesArg = $exesConsolidar -join " "
        & $py "$Raiz\scripts\consolidar.py" $exesArg 2>&1 | ForEach-Object { Write-Host $_ }
        Escrever-OK "Consolidado em: results\consolidado.md"

        Escrever-Titulo "RESUMO"
        Escrever-OK "Execucao $Exec concluida. Veja: results\exec$Exec\report.html"
        Write-Host "  Evidencias: results\exec$Exec\output.xml, respostas.jsonl" -ForegroundColor White
        Write-Host "  Consolidado: results\consolidado.md" -ForegroundColor White
    }

    "consolidar" {
        Escrever-Titulo "CONSOLIDACAO DE RESULTADOS"
        $exes = @(Get-ChildItem "$Raiz\results" -Directory | Where-Object { $_.Name -match "^exec\d+$" } | ForEach-Object { $_.Name -replace "exec", "" })
        if ($exes.Count -eq 0) {
            Escrever-Falha "Nenhuma execucao encontrada em results\"
            $codigoSaida = 1
            break
        }
        $exesArg = ($exes | ForEach-Object { [int]$_ } | Sort-Object) -join " "
        Escrever-Info "Execucoes: $exesArg"
        & $py "$Raiz\scripts\consolidar.py" $exesArg 2>&1 | ForEach-Object { Write-Host $_ }
        Escrever-OK "Consolidado em: results\consolidado.md"
    }

    "ragas" {
        Escrever-Titulo "METRICAS SEMANTICAS (Ragas)"
        if (-not $Exec) {
            Escrever-Info "Uso: -Exec N (ex.: -Exec 1 para results\exec1)"
            Escrever-Falha "Especifique a execucao com -Exec N"
            $codigoSaida = 1
            break
        }
        $jsonl = "$Raiz\results\exec$Exec\respostas.jsonl"
        $csvSaida = "$Raiz\results\exec$Exec\metricas_ragas.csv"
        if (-not (Test-Path $jsonl)) {
            Escrever-Falha "Arquivo nao encontrado: $jsonl"
            $codigoSaida = 1
            break
        }
        Escrever-Info "Entrada: results\exec$Exec\respostas.jsonl"
        Escrever-Info "Saida:   results\exec$Exec\metricas_ragas.csv"
        Escrever-Info "ATENCAO: Esta execucao chama o Gemini como juiz (consome cota)."
        & $py "$Raiz\scripts\avaliar_ragas.py" --resultados $jsonl --saida $csvSaida 2>&1 | ForEach-Object { Write-Host $_ }
        if ($LASTEXITCODE -eq 0) {
            Escrever-OK "Metricas salvas em: results\exec$Exec\metricas_ragas.csv"
        } else {
            Escrever-Falha "Falha ao calcular metricas. Verifique a cota do Gemini e RAGAS_LLM_API_KEY."
            $codigoSaida = 1
        }
    }
}

Write-Host ""
if ($codigoSaida -eq 0) {
    Escrever-OK "Concluido com sucesso."
} else {
    Escrever-Falha "Concluido com erros."
}
exit $codigoSaida
