# Sobe o ambiente do SUT (Dify 1.18.0, modelos remotos do Gemini) no Docker nativo do Ubuntu/WSL.
# Uso (PowerShell, na raiz do repositório): .\scripts\subir_ambiente.ps1

# O WSL desliga a distribuição quando não há processo do Windows ligado a ela, derrubando o Dify.
# Um "sleep infinity" oculto mantém o Ubuntu ativo enquanto o Windows estiver ligado.
$keepAlive = Get-CimInstance Win32_Process -Filter "Name='wsl.exe'" |
    Where-Object { $_.CommandLine -like '*Ubuntu*sleep infinity*' }
if (-not $keepAlive) {
    Start-Process -WindowStyle Hidden -FilePath wsl.exe -ArgumentList '-d', 'Ubuntu', '--', 'sleep', 'infinity'
    Write-Host "Keep-alive do WSL iniciado."
}

wsl -d Ubuntu -- bash -c "cd ~/dify/docker && docker compose up -d && docker compose ps --format 'table {{.Service}}\t{{.Status}}'"

Write-Host "`nAguardando a API do Dify..."
for ($i = 0; $i -lt 40; $i++) {
    try {
        Invoke-RestMethod -Uri 'http://localhost/console/api/setup' -TimeoutSec 3 | Out-Null
        Write-Host "Dify disponível em http://localhost"
        exit 0
    } catch { Start-Sleep -Seconds 5 }
}
Write-Warning "A API do Dify não respondeu em 200 s. Veja: wsl -d Ubuntu -- bash -c 'cd ~/dify/docker && docker compose logs --tail 50 api'"
