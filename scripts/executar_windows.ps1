<#
.SYNOPSIS
    Executa testes e gera relatorios individuais, sem sobrescrever execucoes.
.DESCRIPTION
    Windows PowerShell 5.1. Modos smoke, completo e ragas podem consumir API.
    unit e relatorios sao locais. consolidar e um alias de relatorios.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("smoke", "unit", "completo", "relatorios", "consolidar", "ragas")]
    [string]$Modo,
    [ValidateRange(1, 2147483647)]
    [int]$Exec
)
$ErrorActionPreference = "Stop"
$Raiz = Split-Path -Parent $PSScriptRoot
$py = Join-Path $Raiz ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $py)) { $py = "python" }
$codigoSaida = 0
$saidaAnterior = $env:RESULTADOS_JSONL
$encodingAnterior = $env:PYTHONIOENCODING
Push-Location -LiteralPath $Raiz
try {
    $env:PYTHONIOENCODING = "utf-8"
    & $py -c "import robot, requests, dotenv, docx, PIL"
    if ($LASTEXITCODE -ne 0) { throw "Dependencias ausentes. Instale requirements.txt." }

    switch ($Modo) {
        "unit" {
            & $py -m pytest tests/unit -q
            $codigoSaida = $LASTEXITCODE
        }
        "smoke" {
            $temporario = Join-Path $Raiz ("results\local\smoke-" + [guid]::NewGuid().ToString("N"))
            & $py -m robot --include smoke --outputdir $temporario tests/api.robot
            $codigoSaida = $LASTEXITCODE
            Write-Host "Evidencias do smoke: $temporario"
        }
        "completo" {
            & $py -c "from libraries.dify_client import DifyClient; c=DifyClient(); assert c.api_key and not c.api_key.startswith('app-xxx'), 'Configure DIFY_API_KEY no .env'"
            if ($LASTEXITCODE -ne 0) { throw "Configuracao do ambiente incompleta." }
            if (-not $PSBoundParameters.ContainsKey("Exec")) {
                $numeros = @(Get-ChildItem -LiteralPath (Join-Path $Raiz "results") -Directory |
                    Where-Object { $_.Name -match '^exec\d+$' } |
                    ForEach-Object { [int]($_.Name.Substring(4)) })
                $Exec = 1
                if ($numeros.Count -gt 0) { $Exec = [int](($numeros | Measure-Object -Maximum).Maximum) + 1 }
            }
            $saidaDir = Join-Path $Raiz "results\exec$Exec"
            if (Test-Path -LiteralPath $saidaDir) { throw "Diretorio ja existe: $saidaDir. Nada foi executado." }
            & $py -m pytest tests/unit -q
            if ($LASTEXITCODE -ne 0) { throw "Testes unitarios falharam." }

            # Sem -Force: a reserva tambem falha se outro processo criar a pasta.
            New-Item -ItemType Directory -Path $saidaDir -ErrorAction Stop | Out-Null
            $env:RESULTADOS_JSONL = Join-Path $saidaDir "respostas.jsonl"
            Write-Host "Execucao ${Exec}: chamadas ao Dify/Gemini."
            & $py -m robot --include smoke --outputdir (Join-Path $saidaDir "smoke") tests/api.robot
            if ($LASTEXITCODE -ne 0) { throw "Smoke falhou. Evidencias preservadas em $saidaDir\smoke." }

            & $py -m robot --exclude smoke --outputdir $saidaDir tests/
            $codigoRobot = $LASTEXITCODE
            if (-not (Test-Path -LiteralPath (Join-Path $saidaDir "output.xml"))) {
                throw "Robot nao produziu output.xml. Codigo: $codigoRobot."
            }
            # Mesmo com assertions FAIL, produzir o relatorio e preservar o codigo Robot.
            & $py scripts/consolidar.py $Exec
            $codigoRelatorio = $LASTEXITCODE
            $codigoSaida = $codigoRobot
            if ($codigoRelatorio -ne 0) { $codigoSaida = $codigoRelatorio }
            Write-Host "Execucao $Exec concluida. Robot=$codigoRobot; Word=$codigoRelatorio."
            Write-Host "Evidencias: $saidaDir"
        }
        { $_ -in @("relatorios", "consolidar") } {
            if ($PSBoundParameters.ContainsKey("Exec")) {
                & $py scripts/consolidar.py $Exec
            } else {
                & $py scripts/consolidar.py
            }
            $codigoSaida = $LASTEXITCODE
        }
        "ragas" {
            if (-not $PSBoundParameters.ContainsKey("Exec")) { throw "Informe -Exec para avaliar uma execucao." }
            $entrada = Join-Path $Raiz "results\exec$Exec\respostas.jsonl"
            $metricas = Join-Path $Raiz "results\exec$Exec\metricas_ragas.csv"
            if (-not (Test-Path -LiteralPath $entrada)) { throw "Respostas nao encontradas: $entrada" }
            if (Test-Path -LiteralPath $metricas) { throw "Metricas ja existem: $metricas" }
            & $py scripts/avaliar_ragas.py --resultados $entrada --saida $metricas
            $codigoSaida = $LASTEXITCODE
        }
    }
}
catch {
    Write-Host ("FALHA: " + $_.Exception.Message) -ForegroundColor Red
    $codigoSaida = 1
}
finally {
    $env:RESULTADOS_JSONL = $saidaAnterior
    $env:PYTHONIOENCODING = $encodingAnterior
    Pop-Location
}
exit $codigoSaida
