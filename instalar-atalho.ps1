# Cria o atalho "Parâmetros Mínimos" na Area de Trabalho, apontando para
# "INICIAR SISTEMA.cmd", com o icone assets\parametros-minimos.ico. Sem administrador.
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$appDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$alvo   = Join-Path $appDir 'INICIAR SISTEMA.cmd'
$icone  = Join-Path $appDir 'assets\parametros-minimos.ico'
$destino = [Environment]::GetFolderPath('Desktop')

if (-not (Test-Path $alvo)) { Write-Host "ERRO: nao encontrei $alvo"; exit 1 }

$atalho = Join-Path $destino 'Parâmetros Mínimos.lnk'
$sh = New-Object -ComObject WScript.Shell
$lnk = $sh.CreateShortcut($atalho)
$lnk.TargetPath = $alvo
$lnk.WorkingDirectory = $appDir
$lnk.Description = 'Parâmetros Mínimos / ONASP 2026 - iniciar o sistema com o servidor local'
if (Test-Path $icone) { $lnk.IconLocation = "$icone,0" }
$lnk.Save()

Write-Host ""
if (Test-Path $atalho) {
  Write-Host "  PRONTO. Atalho criado em:" -ForegroundColor Green
  Write-Host "  $atalho"
  if (Test-Path $icone) { Write-Host "  Icone: $icone" }
} else {
  Write-Host "  Nao foi possivel criar o atalho." -ForegroundColor Red
  exit 1
}
Write-Host ""
