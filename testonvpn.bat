@echo off
title Quick VPN Connect
cls

echo Quick VPN Connection
echo ====================
echo.
echo Options:
echo 1. Connect to TWCU VPN (rasdial)
echo 2. Connect with saved credentials
echo 3. Disconnect all VPN
echo 4. Show IP address
echo.
set /p opt="Choose [1-4]: "

if "%opt%"=="1" goto QUICK_CONNECT
if "%opt%"=="2" goto SAVED_CONNECT
if "%opt%"=="3" goto QUICK_DISCONNECT
if "%opt%"=="4" goto SHOW_IP
exit

:QUICK_CONNECT
set /p user=Username: 
set /p pass=Password: 
rasdial "TWCU-VPN" "%user%" "%pass%"
goto END

:SAVED_CONNECT
REM Use saved credentials (not secure!)
rasdial "TWCU-VPN" "student123" "password123"
goto END

:QUICK_DISCONNECT
rasdial /disconnect
echo All VPN connections disconnected
goto END

:SHOW_IP
ipconfig | find "IPv4"
echo Public IP: 
powershell -Command "(Invoke-WebRequest ifconfig.me).Content"

:END
timeout /t 5