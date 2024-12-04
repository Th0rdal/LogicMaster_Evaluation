@echo off
setlocal enabledelayedexpansion

REM Initialize lists for storing results
set success_builds=
set failed_builds=

REM Step 1: Build the Docker image ai_base
echo Starting ai_base build...
docker build -t ai_base -f .\dockerfile_ai_base .
IF %ERRORLEVEL% NEQ 0 (
    REM Error in red
    echo ^[[31mDocker ai_base build failed! Stopping execution.^[[0m
    set failed_builds=!failed_builds!ai_base,
    exit /b 1
) ELSE (
    REM Success in green
    echo ^[[32mai_base build succeeded!^[[0m
    set success_builds=!success_builds!ai_base,
)

REM Step 2: Build the Docker image preprocessing
echo Starting preprocessing build...
docker build -t preprocessing -f .\dockerfile_preprocessing .
IF %ERRORLEVEL% NEQ 0 (
    REM Error in red
    echo ^[[31mpreprocessing build failed!^[[0m
    set failed_builds=!failed_builds!preprocessing,
) ELSE (
    REM Success in green
    echo ^[[32mpreprocessing build succeeded!^[[0m
    set success_builds=!success_builds!preprocessing,
)

REM Step 3: Build the Docker image qlearning
echo Starting qlearning build...
docker build -t qlearning -f .\dockerfile_qlearning .
IF %ERRORLEVEL% NEQ 0 (
    REM Error in red
    echo ^[[31mqlearning build failed!^[[0m
    set failed_builds=!failed_builds!qlearning,
) ELSE (
    REM Success in green
    echo ^[[32mqlearning build succeeded!^[[0m
    set success_builds=!success_builds!qlearning,
)

REM Final Results
echo.
echo --- Build Results ---
echo Success builds: !success_builds!
echo Failed builds: !failed_builds!

endlocal
