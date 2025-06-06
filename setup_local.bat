@echo off
echo ========================================
echo    CONFIGURACAO AMBIENTE LOCAL XAMPP
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado
    echo Instale o Python 3.8+ antes de continuar
    pause
    exit /b 1
)

echo Executando script de configuracao...
echo.

python setup_local.py

echo.
echo Pressione qualquer tecla para continuar...
pause >nul 