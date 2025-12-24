@echo off
title VPN Auto-Repair Tool
cls

echo VPN Auto-Repair Tool
echo ====================
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Administrator rights required!
    echo Please run as Administrator
    pause
    exit /b 1
)

echo [1] Checking network services...
sc query W32Time | find "RUNNING" >nul
if errorlevel 1 (
    echo Starting Windows Time service...
    net start W32Time
)

echo [2] Flushing DNS cache...
ipconfig /flushdns

echo [3] Resetting network adapters...
netsh winsock reset
netsh int ip reset

echo [4] Checking VPN services...
sc query RasMan | find "RUNNING" >nul
if errorlevel 1 (
    echo Starting Remote Access service...
    net start RasMan
)

echo [5] Testing VPN connectivity...
ping vpn.twcu.edu -n 2 >nul
if errorlevel 1 (
    echo WARNING: Cannot reach VPN server
    echo Check network connection
)

echo.
echo Repair completed!
echo Please restart your computer for changes to take effect
pause