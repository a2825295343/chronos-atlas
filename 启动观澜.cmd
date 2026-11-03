@echo off
setlocal
set "PYTHONUTF8=1"
pushd "%~dp0"
if errorlevel 1 goto workspace_error

echo Starting Guanlan / CHRONOS...
where python >nul 2>&1
if errorlevel 1 goto try_py
python "%~dp0start.py" %*
if errorlevel 1 goto launch_error
goto success

:try_py
where py >nul 2>&1
if errorlevel 1 goto no_python
py -3 "%~dp0start.py" %*
if errorlevel 1 goto launch_error
goto success

:no_python
echo Python 3 was not found. Install Python 3 and enable "Add Python to PATH".
goto launch_error

:workspace_error
echo Cannot open the application folder.
pause
exit /b 1

:launch_error
echo.
echo Guanlan could not start. Please check the error above.
popd
pause
exit /b 1

:success
popd
exit /b 0
