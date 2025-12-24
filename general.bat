@echo off
chcp 65001 >nul
title TWCU VPN Manager
cls

:START
echo.
echo ========================================
echo          TWCU VPN MANAGER
echo ========================================
echo.
echo 1. Connect to VPN
echo 2. Disconnect VPN
echo 3. Check Connection
echo 4. Network Info
echo 5. Exit
echo.
set /p choice="Choose [1-5]: "

if "%choice%"=="1" goto CONNECT
if "%choice%"=="2" goto DISCONNECT
if "%choice%"=="3" goto CHECK
if "%choice%"=="4" goto NETINFO
if "%choice%"=="5" exit
goto START

:CONNECT
cls
echo Connecting to TWCU VPN...
echo.
REM Check if VPN interface exists
netsh interface show interface | find "TWCU" >nul
if errorlevel 1 (
    echo VPN adapter not found!
    echo Please create VPN connection first:
    echo 1. Press Win + R -> type ncpa.cpl
    echo 2. Create new connection
    echo 3. Use TWCU VPN credentials
    pause
    goto START
)

echo Enter credentials:
set /p vpn_user="Username: "
set /p vpn_pass="Password: "

echo.
echo Connecting...
timeout /t 2 >nul

REM Try to connect using rasdial
rasdial "TWCU-VPN" "%vpn_user%" "%vpn_pass%"

if errorlevel 1 (
    echo Connection failed!
    echo Possible reasons:
    echo - Wrong username/password
    echo - Network issues
    echo - VPN server unavailable
    echo.
    echo Trying alternative method...
    powershell -Command "rasphone.exe -d 'TWCU-VPN'"
)

echo.
ipconfig | find "IPv4"
echo.
pause
goto START

:DISCONNECT
cls
echo Disconnecting from VPN...
echo.
rasdial "TWCU-VPN" /disconnect
if errorlevel 1 (
    echo No active VPN connection found
) else (
    echo Successfully disconnected!
)
pause
goto START

:CHECK
cls
echo Checking VPN status...
echo.
rasdial | find "Connected"
if errorlevel 1 (
    echo Status: DISCONNECTED
) else (
    echo Status: CONNECTED
)
echo.
echo Network interfaces:
netsh interface show interface | findstr "Connected"
pause
goto START

:NETINFO
cls
echo Network Information:
echo ====================
echo.
echo IPv4 Addresses:
ipconfig | findstr "IPv4"
echo.
echo Public IP:
powershell -Command "(Invoke-WebRequest -Uri 'https://api.ipify.org' -UseBasicParsing).Content"
echo.
echo Default Gateway:
ipconfig | findstr "Default Gateway"
pause
goto START