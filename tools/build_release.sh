#!/usr/bin/env bash
# Script para empaquetar UAMotorsCADAlert como un ejecutable único para Windows (Single-File)

cd "$(dirname "$0")/.."

echo "Compilando UAMOTORS CAD ALERT para Windows x64 (Single File)..."

dotnet publish src/UAMotorsCADAlert/UAMotorsCADAlert.csproj \
    -c Release \
    -r win-x64 \
    --self-contained true \
    -p:PublishSingleFile=true \
    -p:IncludeNativeLibrariesForSelfExtract=true \
    -p:PublishTrimmed=false \
    -o publish_output

echo "======================================"
echo "Compilación exitosa."
echo "Puedes encontrar tu ejecutable listo para subir a GitHub Releases en:"
echo "publish_output/UAMotorsCADAlert.exe"
echo "======================================"
