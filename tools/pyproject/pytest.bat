@echo off
setlocal

REM Setup the build environment
set VENV=.\_build\tests\venv
echo Building: %VENV%
if exist "%VENV%" (
    rd /s /q "%VENV%"
)

.\_build\target-deps\python\python.exe -m venv "%VENV%"
if %errorlevel% neq 0 ( exit /b %errorlevel% )

call "%VENV%\Scripts\activate.bat"
if %errorlevel% neq 0 ( exit /b %errorlevel% )

REM Install wheel packages
for %%f in ("_build\packages\*.whl") do (
    python.exe -m pip install "%%f"
    if %errorlevel% neq 0 ( exit /b %errorlevel% )
)

REM copy the test dependencies into the env
set TEST_ROOT=%1
echo Copy test deps from: %TEST_ROOT%
for /f "delims=" %%i in ('python.exe -c "import site; print(site.getsitepackages()[-1])"') do set SITE_PACKAGES=%%i
echo Copy test deps to: %SITE_PACKAGES%
if not exist "%SITE_PACKAGES%\usdex\test" (
    mkdir "%SITE_PACKAGES%\usdex\test"
)
xcopy /s /e /y /q "%TEST_ROOT%\python\usdex\test" "%SITE_PACKAGES%\usdex\test"
if not exist "%SITE_PACKAGES%\omni\asset_validator" (
    mkdir "%SITE_PACKAGES%\omni\asset_validator"
)
xcopy /s /e /y /q "%TEST_ROOT%\python\omni\asset_validator" "%SITE_PACKAGES%\omni\asset_validator"

REM Run the tests
python.exe -m unittest discover -v -s source\core\tests\unittest
if %errorlevel% neq 0 ( exit /b %errorlevel% )

endlocal
