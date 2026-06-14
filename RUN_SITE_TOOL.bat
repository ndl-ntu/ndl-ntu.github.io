@echo off
setlocal
cd /d "%~dp0"

where bash >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  bash scripts/ndl_site_tool.sh menu
  goto done
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  echo Bash was not found, but Python is available.
  echo Please install Git for Windows or open this repository in Git Bash, then run:
  echo scripts/ndl_site_tool.sh menu
  goto done
)

echo Bash and Python were not found.
echo Please install Git for Windows and Python 3.

:done
echo.
pause
