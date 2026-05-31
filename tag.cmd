REM git tag -a v0.0.3 -m "Version 0.0.3 stable"
REM git push origin v0.0.3

@echo off
:: Check if a version number was provided
if "%~1"=="" (
    echo Error: Please provide a version number.
    echo Usage: version ^<version-number^>
    echo Example: version 0.0.3
    exit /b 1
)

:: Set the variable
set VERSION=%~1

:: Execute the Git commands
git tag -a v%VERSION% -m "Version %VERSION% stable"
git push origin v%VERSION%
REM
REM
REM alternative
REM git config --global alias.set-version "!f() { git tag -a \"v$1\" -m \"Version $1 stable\" && git push origin \"v$1\"; }; f"
REM git set-version 0.0.3