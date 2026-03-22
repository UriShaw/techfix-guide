@echo off
title RAM Diagnostic — TechFix Guide
color 0A
echo ============================================
echo    RAM Diagnostic v1.0 — TechFix Guide
echo ============================================
echo.
echo Chay Windows Memory Diagnostic...
echo May se khoi dong lai de kiem tra RAM.
echo.
choice /c YN /m "Ban co muon chay Memory Diagnostic khong? (Y/N)"
if %errorlevel%==1 (
    echo Dang lich kiem tra RAM...
    mdsched.exe
) else (
    echo Da huy.
)
echo.
echo Xem RAM thong tin hien tai:
wmic memorychip get BankLabel,Capacity,MemoryType,Speed,Manufacturer
echo.
pause
