#!/usr/bin/env python3
"""
Установщик TWCU VPN
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 6):
        print("Требуется Python 3.6 или выше")
        return False
    return True

def install_dependencies():
    """Установка зависимостей"""
    print("Установка зависимостей...")
    
    dependencies = [
        'cryptography',
        'colorama',
        'psutil'
    ]
    
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✓ {dep} установлен")
        except:
            print(f"✗ Ошибка установки {dep}")
            return False
    
    return True

def create_config_files():
    """Создание конфигурационных файлов"""
    print("\nСоздание конфигурационных файлов...")
    
    configs = {
        'server_config.json': '''{
    "server": {
        "host": "0.0.0.0",
        "port": 5555,
        "max_clients": 100,
        "timeout": 300,
        "log_file": "vpn_server.log"
    },
    "security": {
        "encryption": true,
        "require_auth": true,
        "session_timeout": 3600
    },
    "users": [
        {
            "username": "admin",
            "role": "administrator",
            "permissions": ["full_access"]
        }
    ]
}''',
        
        'client_config.json': '''{
    "connection": {
        "server_host": "127.0.0.1",
        "server_port": 5555,
        "auto_reconnect": true,
        "timeout": 30
    },
    "credentials": {
        "username": "",
        "save_password": false
    },
    "network": {
        "dns_servers": ["8.8.8.8", "1.1.1.1"],
        "mtu": 1500
    }
}'''
    }
    
    for filename, content in configs.items():
        try:
            with open(filename, 'w') as f:
                f.write(content)
            print(f"✓ Создан {filename}")
        except Exception as e:
            print(f"✗ Ошибка создания {filename}: {e}")
    
    return True

def create_windows_bat():
    """Создание bat-файлов для Windows"""
    if platform.system() == 'Windows':
        print("\nСоздание bat-файлов для Windows...")
        
        # Сервер
        server_bat = '''@echo off
chcp 65001 > nul
title TWCU VPN Server
echo Запуск TWCU VPN Server...
python vpn_server.py
pause'''
        
        # Клиент
        client_bat = '''@echo off
chcp 65001 > nul
title TWCU VPN Client
echo Запуск TWCU VPN Client...
python vpn_client.py
pause'''
        
        try:
            with open('start_server.bat', 'w') as f:
                f.write(server_bat)
            print("✓ Создан start_server.bat")
            
            with open('start_client.bat', 'w') as f:
                f.write(client_bat)
            print("✓ Создан start_client.bat")
        except Exception as e:
            print(f"✗ Ошибка создания bat-файлов: {e}")

def create_unix_scripts():
    """Создание скриптов для Unix/Linux"""
    if platform.system() != 'Windows':
        print("\nСоздание скриптов для Unix/Linux...")
        
        scripts = {
            'start_server.sh': '''#!/bin/bash
echo "Запуск TWCU VPN Server..."
python3 vpn_server.py
''',
            
            'start_client.sh': '''#!/bin/bash
echo "Запуск TWCU VPN Client..."
python3 vpn_client.py
'''
        }
        
        for filename, content in scripts.items():
            try:
                with open(filename, 'w') as f:
                    f.write(content)
                os.chmod(filename, 0o755)
                print(f"✓ Создан {filename}")
            except Exception as e:
                print(f"✗ Ошибка создания {filename}: {e}")

def show_instructions():
    """Показать инструкции"""
    print("\n" + "="*50)
    print("ИНСТРУКЦИЯ ПО УСТАНОВКЕ")
    print("="*50)
    print("\n1. Сервер VPN:")
    print("   python vpn_server.py")
    print("   или start_server.bat (Windows)")
    print("   или ./start_server.sh (Linux/Mac)")
    
    print("\n2. Клиент VPN:")
    print("   python vpn_client.py")
    print("   или start_client.bat (Windows)")
    print("   или ./start_client.sh (Linux/Mac)")
    
    print("\n3. Тестовые пользователи:")
    print("   student1 / pass123")
    print("   teacher1 / teacher456")
    print("   admin / admin789")
    
    print("\n4. Порт по умолчанию: 5555")
    print("\n5. Конфигурационные файлы:")
    print("   - server_config.json")
    print("   - client_config.json")
    
    print("\n" + "="*50)
    print("Установка завершена успешно!")
    print("="*50)

def main():
    """Основная функция установки"""
    print("""
╔═══════════════════════════════════════╗
║      УСТАНОВЩИК TWCU VPN             ║
╚═══════════════════════════════════════╝
    """)
    
    # Проверки
    if not check_python_version():
        sys.exit(1)
    
    print("1. Установка зависимостей...")
    if not install_dependencies():
        print("Продолжить без зависимостей? (y/n): ", end='')
        if input().lower() != 'y':
            sys.exit(1)
    
    print("\n2. Создание файлов...")
    create_config_files()
    
    # Создание скриптов запуска
    if platform.system() == 'Windows':
        create_windows_bat()
    else:
        create_unix_scripts()
    
    print("\n3. Завершение установки...")
    show_instructions()

if __name__ == "__main__":
    main()