@echo off
REM Build Pathfinder for itch.io (browser). Upload build\web.zip as HTML game.
setlocal
cd /d "%~dp0"

echo Installing/upgrading pygbag...
python -m pip install --user --upgrade pygbag

if exist build rmdir /s /q build

echo Building web export...
python -m pygbag --title Pathfinder --package pathfinder --build --archive .

if exist build\web.zip (
    echo.
    echo Success! Upload this file to itch.io:
    echo   %cd%\build\web.zip
    echo.
    echo itch.io settings: Kind of project = HTML, Embed in page, Viewport = 900 x 700
) else (
    echo Build failed - check errors above.
    exit /b 1
)
