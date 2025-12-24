@echo off
title TWCU VPN Setup Wizard
cls

echo TWCU VPN Setup Wizard
echo =====================
echo.

echo This wizard will help you setup TWCU VPN
echo.

echo Step 1: Creating VPN connection...
set /p "SERVER=vpn.twcu.edu"
set /p "NAME=TWCU-VPN"

powershell -Command "
    Add-VpnConnection -Name '%NAME%' `
    -ServerAddress '%SERVER%' `
    -TunnelType IKEv2 `
    -EncryptionLevel Required `
    -AuthenticationMethod Eap `
    -RememberCredential `
    -Force
"

echo.
echo Step 2: Creating shortcut on desktop...
echo @echo off > "%USERPROFILE%\Desktop\TWCU-VPN.bat"
echo rasdial "TWCU-VPN" %%1 %%2 >> "%USERPROFILE%\Desktop\TWCU-VPN.bat"

echo.
echo Setup completed!
echo.
echo To connect: Run TWCU-VPN.bat on your desktop
echo or use: rasdial "TWCU-VPN" [username] [password]
pause