@echo off
rem Packs the raw scan output of the extension into data\raw_extension.zip
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -Command "if (Test-Path data\raw_extension.zip) { Remove-Item data\raw_extension.zip }; Compress-Archive -Path data\raw_phaseD, data\raw_phaseE -DestinationPath data\raw_extension.zip; Write-Host packed"
