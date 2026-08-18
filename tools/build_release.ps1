# Script para empaquetar UAMotorsCADAlert como un ejecutable único para Windows (Single-File)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$ScriptDir\.."

Write-Host "Compilando UAMOTORS CAD ALERT para Windows x64 (Single File)..." -ForegroundColor Cyan

dotnet publish src/UAMotorsCADAlert/UAMotorsCADAlert.csproj `
    -c Release `
    -r win-x64 `
    --self-contained true `
    -p:PublishSingleFile=true `
    -p:IncludeNativeLibrariesForSelfExtract=true `
    -p:PublishTrimmed=false `
    -o publish_output

Write-Host "======================================" -ForegroundColor Green
Write-Host "Compilación exitosa." -ForegroundColor Green
Write-Host "Puedes encontrar tu ejecutable listo para subir a GitHub Releases en:"
Write-Host "publish_output\UAMotorsCADAlert.exe" -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Green
