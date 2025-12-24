@echo off
chcp 65001 > nul
title TWCU VPN Server
echo Запуск TWCU VPN Server...
python vpn_server.py
pause