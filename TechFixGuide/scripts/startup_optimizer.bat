@echo off
title Startup Optimizer — TechFix Guide
color 0A
echo ============================================
echo   Startup Optimizer v1.0 — TechFix Guide
echo ============================================
echo.
echo Tat cac chuong trinh khoi dong khong can thiet...
echo.
:: Disable common bloatware startup items via registry
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run" /v "OneDrive" /t REG_BINARY /d 0300000000000000000000000 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run" /v "Spotify" /t REG_BINARY /d 0300000000000000000000000 /f >nul 2>&1

echo [OK] Startup items da duoc toi uu.
echo.
echo Tat Windows Search indexing tam thoi...
sc stop "WSearch" >nul 2>&1
echo [OK] Search indexing tam dung.
echo.
echo Tat Superfetch/SysMain...
sc stop "SysMain" >nul 2>&1
echo [OK] SysMain da dung.
echo.
echo ============================================
echo  Hoan tat! Khoi dong lai de ap dung.
echo ============================================
pause
