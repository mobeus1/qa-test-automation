@echo off
REM ============================================================
REM TestComplete/TestExecute CLI Wrapper
REM Usage: run-tests.bat <project_suite> <test_items_csv> <access_key> <base_url>
REM ============================================================

setlocal enabledelayedexpansion

set PROJECT_SUITE=%~1
set TEST_ITEMS=%~2
set ACCESS_KEY=%~3
set BASE_URL=%~4
set LOG_DIR=test-results\%date:~-4%%date:~4,2%%date:~7,2%

echo ============================================================
echo QA Test Automation - TestComplete Runner
echo ============================================================
echo Project Suite: %PROJECT_SUITE%
echo Test Items:    %TEST_ITEMS%
echo Base URL:      %BASE_URL%
echo Log Directory: %LOG_DIR%
echo ============================================================

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Try TestExecute first (lighter weight), fall back to TestComplete
set TC_EXE=""
if exist "C:\Program Files (x86)\SmartBear\TestExecute 15\Bin\TestExecute.exe" (
    set TC_EXE="C:\Program Files (x86)\SmartBear\TestExecute 15\Bin\TestExecute.exe"
    echo Using TestExecute
) else if exist "C:\Program Files (x86)\SmartBear\TestComplete 15\Bin\TestComplete.exe" (
    set TC_EXE="C:\Program Files (x86)\SmartBear\TestComplete 15\Bin\TestComplete.exe"
    echo Using TestComplete
) else (
    echo ERROR: Neither TestExecute nor TestComplete found
    exit /b 3
)

echo Running tests...

set EXIT_CODE=0
set ITEMS_LIST=%TEST_ITEMS:,= %
for %%T in (%ITEMS_LIST%) do (
    set ITEM=%%T
    set ITEM_SAFE=!ITEM: =_!
    echo Running Test Item: !ITEM!
    %TC_EXE% "%PROJECT_SUITE%" /run /p:"!ITEM!" /AccessKey:%ACCESS_KEY% /ExportLog:"%LOG_DIR%\results_!ITEM_SAFE!.mht" /exit
    set ITEM_EXIT=!ERRORLEVEL!
    if !ITEM_EXIT! GTR !EXIT_CODE! set EXIT_CODE=!ITEM_EXIT!
)

echo.
echo ============================================================
if %EXIT_CODE% EQU 0 (
    echo RESULT: PASSED - All tests succeeded
) else if %EXIT_CODE% EQU 1 (
    echo RESULT: WARNINGS - Tests completed with warnings
) else if %EXIT_CODE% EQU 2 (
    echo RESULT: FAILED - Tests completed with errors
) else (
    echo RESULT: ERROR - Exit code: %EXIT_CODE%
)
echo ============================================================

exit /b %EXIT_CODE%
