@echo off
rem Double-click to scan the 17 new matched pairs. Keep this window open (6-8 hours).
cd /d "%~dp0"
powershell -NoExit -ExecutionPolicy Bypass -File "%~dp0run_extension_scan.ps1"
