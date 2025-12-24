@echo off
setlocal enabledelayedexpansion

chcp 65001 >nul
title Universal VPN Client v2.0
mode con: cols=80 lines=25

:MAIN_MENU
cls
echo.
echo ========================================
echo        UNIVERSAL VPN CLIENT
echo ========================================
echo.
echo [1] Connect to Windows VPN
echo [2] Connect via OpenVPN
echo [3] Network Diagnostics
echo [4] VPN Configuration
echo [5] Speed Test
echo [6] View Logs
echo [7] Exit
echo.
set /p "CHOICE=Select option [1-7]: "

if "!CHOICE!"=="1" goto WINDOWS_VPN
if "!CHOICE!"=="2" goto OPENVPN
if "!CHOICE!"=="3" goto DIAGNOSE
if "!CHOICE!"=="4" goto CONFIG
if "!CHOICE!"=="5" goto SPEEDTEST
if "!CHOICE!"=="6" goto VIEWLOGS
if "!CHOICE!"=="7" exit
goto MAIN_MENU

:WINDOWS_VPN
cls
echo.
echo ========================================
echo        WINDOWS VPN CONNECTION
echo ========================================
echo.

REM List available VPN connections
echo Available VPN connections:
echo --------------------------
rasdial > "%temp%\vpns.txt"
type "%temp%\vpns.txt"
echo.

set /p "VPN_NAME=Enter VPN name (default: TWCU-VPN): "
if "!VPN_NAME!"=="" set VPN_NAME=TWCU-VPN

echo.
set /p "USERNAME=Username: "
set /p "PASSWORD=Password: "

echo.
echo Attempting to connect to !VPN_NAME!...
rasdial "!VPN_NAME!" "!USERNAME!" "!PASSWORD!"

if !errorlevel! equ 0 (
    echo SUCCESS: Connected to !VPN_NAME!
    call :SHOW_CONNECTION_INFO
) else (
    echo ERROR: Connection failed
    echo.
    echo Troubleshooting:
    echo 1. Check username/password
    echo 2. Verify VPN connection exists
    echo 3. Check network connectivity
    echo 4. Contact IT support
)

echo.
pause
goto MAIN_MENU

:OPENVPN
cls
echo.
echo ========================================
echo           OPENVPN CLIENT
echo ========================================
echo.

REM Check if OpenVPN is installed
where openvpn >nul 2>nul
if !errorlevel! neq 0 (
    echo ERROR: OpenVPN is not installed!
    echo.
    echo Download from: https://openvpn.net/community-downloads/
    echo.
    pause
    goto MAIN_MENU
)

echo Available OpenVPN configs (.ovpn files):
echo ---------------------------------------
dir /b *.ovpn 2>nul || echo No .ovpn files found in current directory
echo.

set /p "OVPN_FILE=Enter .ovpn filename: "
if "!OVPN_FILE!"=="" (
    echo No file specified
    pause
    goto MAIN_MENU
)

if not exist "!OVPN_FILE!" (
    echo ERROR: File "!OVPN_FILE!" not found!
    pause
    goto MAIN_MENU
)

echo.
echo Starting OpenVPN connection...
echo Press Ctrl+C to disconnect
echo.
openvpn "!OVPN_FILE!"
pause
goto MAIN_MENU

:DIAGNOSE
cls
echo.
echo ========================================
echo        NETWORK DIAGNOSTICS
echo ========================================
echo.

echo [1] Testing internet connectivity...
ping 8.8.8.8 -n 4 >nul && (
    echo ✓ Internet: AVAILABLE
) || (
    echo ✗ Internet: UNAVAILABLE
)

echo.
echo [2] Testing DNS resolution...
nslookup google.com >nul && (
    echo ✓ DNS: WORKING
) || (
    echo ✗ DNS: FAILED
)

echo.
echo [3] Checking public IP address...
for /f "delims=" %%i in ('powershell -Command "(Invoke-WebRequest -Uri 'https://api.ipify.org' -UseBasicParsing).Content"') do set "PUBLIC_IP=%%i"
echo Public IP: !PUBLIC_IP!

echo.
echo [4] Testing VPN connectivity...
netsh interface show interface | findstr "TWCU" >nul && (
    echo ✓ VPN adapter: DETECTED
) || (
    echo ✗ VPN adapter: NOT FOUND
)

echo.
echo [5] Current network interfaces:
echo ------------------------------
ipconfig | findstr /C:"IPv4" /C:"Adapter"

echo.
pause
goto MAIN_MENU

:CONFIG
cls
echo.
echo ========================================
echo        VPN CONFIGURATION
echo ========================================
echo.

echo [1] Create new VPN connection
echo [2] Delete VPN connection
echo [3] List all VPN connections
echo [4] Import OpenVPN config
echo [5] Back to main menu
echo.
set /p "CONFIG_CHOICE=Select option [1-5]: "

if "!CONFIG_CHOICE!"=="1" goto CREATE_VPN
if "!CONFIG_CHOICE!"=="2" goto DELETE_VPN
if "!CONFIG_CHOICE!"=="3" goto LIST_VPN
if "!CONFIG_CHOICE!"=="4" goto IMPORT_OVPN
if "!CONFIG_CHOICE!"=="5" goto MAIN_MENU
goto CONFIG

:CREATE_VPN
set /p "NEW_VPN_NAME=Enter VPN connection name: "
set /p "VPN_SERVER=Enter VPN server address: "
set /p "VPN_TYPE=Enter VPN type (PPTP/L2TP/SSTP/IKEv2): "

echo Creating VPN connection: !NEW_VPN_NAME!...
powershell -Command "
    Add-VpnConnection -Name '!NEW_VPN_NAME!' `
    -ServerAddress '!VPN_SERVER!' `
    -TunnelType '!VPN_TYPE!' `
    -EncryptionLevel Required `
    -AuthenticationMethod MSChapv2 `
    -RememberCredential `
    -Force
"
echo VPN connection created successfully!
pause
goto CONFIG

:DELETE_VPN
echo Existing VPN connections:
echo -------------------------
rasdial
echo.
set /p "DEL_NAME=Enter VPN name to delete: "
powershell -Command "Remove-VpnConnection -Name '!DEL_NAME!' -Force"
echo VPN connection deleted!
pause
goto CONFIG

:LIST_VPN
rasdial
echo.
pause
goto CONFIG

:IMPORT_OVPN
echo Place .ovpn files in current directory
echo They will appear in OpenVPN menu
pause
goto CONFIG

:SPEEDTEST
cls
echo.
echo ========================================
echo        NETWORK SPEED TEST
echo ========================================
echo.

echo Testing download speed...
echo This may take 20-30 seconds...
echo.

REM Simple speed test using PowerShell
powershell -Command "
    \$testFile = 'https://speedtest.ftp.otenet.gr/files/test100Mb.db'
    \$outputFile = '\$env:TEMP\speedtest.tmp'
    \$webClient = New-Object System.Net.WebClient
    \$startTime = Get-Date
    \$webClient.DownloadFile(\$testFile, \$outputFile)
    \$endTime = Get-Date
    \$fileSize = (Get-Item \$outputFile).Length
    \$timeTaken = (\$endTime - \$startTime).TotalSeconds
    \$speedMbps = (\$fileSize * 8 / \$timeTaken / 1MB)
    Write-Host ('Download Speed: {0:N2} Mbps' -f \$speedMbps)
    Remove-Item \$outputFile -Force
"

echo.
pause
goto MAIN_MENU

:VIEWLOGS
cls
echo.
echo ========================================
echo        VPN CONNECTION LOGS
echo ========================================
echo.

echo Recent connection attempts:
echo --------------------------
rasdial > "%temp%\current_vpn.txt"
type "%temp%\current_vpn.txt"

echo.
echo Event logs (last 5 VPN events):
echo -------------------------------
powershell -Command "Get-WinEvent -FilterHashtable @{LogName='System';ID=20261} -MaxEvents 5 | Format-Table TimeCreated,Message -AutoSize"

echo.
pause
goto MAIN_MENU

:SHOW_CONNECTION_INFO
echo.
echo Connection Information:
echo -----------------------
ipconfig | findstr /C:"IPv4" /C:"Subnet" /C:"Gateway"
echo.
echo Active connections:
netstat -an | findstr ":443" | findstr "ESTABLISHED"
goto :eof