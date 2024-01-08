@echo off
set "script_path=ultimatevocalremovergui\UVR.py"
set "conda_env=base"

:loop
call conda activate %conda_env%
python "%script_path%"
if %errorlevel% neq 1 (
    echo Error: script exited with code %errorlevel%
    echo Please press any key to continue . . .
    pause >nul
    exit /b %errorlevel%
)
goto loop
