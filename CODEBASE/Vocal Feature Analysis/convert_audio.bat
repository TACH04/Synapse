@echo off
REM Audio Conversion Script using FFmpeg
REM Converts audio files to 16kHz mono WAV format

SET INPUT_FILE=%1
SET OUTPUT_FILE=%2

IF "%INPUT_FILE%"=="" (
    echo Usage: convert_audio.bat input_file.m4a [output_file.wav]
    echo.
    echo Example:
    echo   convert_audio.bat test_audio.m4a
    echo   convert_audio.bat test_audio.m4a output.wav
    exit /b 1
)

REM If no output file specified, create one based on input filename
IF "%OUTPUT_FILE%"=="" (
    SET OUTPUT_FILE=%~n1_converted.wav
)

echo Converting: %INPUT_FILE%
echo Output: %OUTPUT_FILE%
echo.

REM Check if ffmpeg is available
where ffmpeg >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: ffmpeg not found in PATH
    echo.
    echo Please install ffmpeg:
    echo 1. Download from: https://ffmpeg.org/download.html
    echo 2. Extract and add to your system PATH
    echo.
    echo Or install using winget:
    echo   winget install ffmpeg
    echo.
    echo Or using chocolatey:
    echo   choco install ffmpeg
    exit /b 1
)

REM Convert audio: 16kHz, mono, PCM WAV
ffmpeg -i "%INPUT_FILE%" -ar 16000 -ac 1 -sample_fmt s16 -y "%OUTPUT_FILE%"

IF %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Conversion complete!
    echo Output saved to: %OUTPUT_FILE%
) ELSE (
    echo.
    echo ✗ Conversion failed!
    exit /b 1
)

