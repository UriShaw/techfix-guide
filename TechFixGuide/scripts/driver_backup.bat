@echo off
title Driver Backup — TechFix Guide
color 0A
echo ============================================
echo    Driver Backup v1.0 — TechFix Guide
echo ============================================
echo.
set BACKUP_DIR=%USERPROFILE%\Desktop\DriverBackup_%DATE:~-4%%DATE:~3,2%%DATE:~0,2%
mkdir "%BACKUP_DIR%" >nul 2>&1
echo Backup destination: %BACKUP_DIR%
echo.
echo Dang sao luu tat ca driver...
pnputil /export-driver * "%BACKUP_DIR%" >nul 2>&1
echo [OK] Driver da duoc sao luu vao: %BACKUP_DIR%
echo.
echo Tao danh sach driver...
driverquery /fo csv > "%BACKUP_DIR%\driver_list.csv" 2>nul
echo [OK] Danh sach driver: driver_list.csv
echo.
echo ============================================
echo  Sao luu hoan tat!
echo  Folder: %BACKUP_DIR%
echo ============================================
pause
