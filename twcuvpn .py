#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
УСТАНОВЩИК TWCU VPN
Запуск: python setup_twcuvpn.py
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

class TWCUVPNInstaller:
    def __init__(self):
        self.home_dir = Path.home()
        self.app_dir = self.home_dir / "TWCU_VPN"
        self.config_file = self.app_dir / "config.json"
        
    def print_banner(self):
        """Печать баннера"""
        print("""
╔══════════════════════════════════════════════════════╗
║                TWCU VPN INSTALLER                   ║
║               Версия 2.0 (2024)                     ║
╚══════════════════════════════════════════════════════╝
        """)
    
    def check_python(self):
        """Проверка Python"""
        print("[1/5] 🔍 Проверка Python...")
        
        if sys.version_info < (3, 6):
            print("❌ Требуется Python 3.6 или выше!")
            print("   Скачайте с: https://python.org")
            return False
        
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} обнаружен")
        return True
    
    def install_dependencies(self):
        """Установка зависимостей"""
        print("\n[2/5] 📦 Установка зависимостей...")
        
        dependencies = [
            'requests',
            'colorama',
            'psutil'
        ]
        
        for dep in dependencies:
            try:
                print(f"   Устанавливаю {dep}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep, '--quiet'])
                print(f"   ✅ {dep} установлен")
            except Exception as e:
                print(f"   ⚠️  Не удалось установить {dep}: {e}")
                print("   Продолжаю без него...")
        
        return True
    
    def create_app_directory(self):
        """Создание директории приложения"""
        print("\n[3/5] 📁 Создание структуры приложения...")
        
        try:
            self.app_dir.mkdir(exist_ok=True)
            print(f"✅ Директория создана: {self.app_dir}")
            return True
        except Exception as e:
            print(f"❌ Ошибка создания директории: {e}")
            return False
    
    def create_config(self):
        """Создание конфигурационного файла"""
        print("\n[4/5] ⚙️  Создание конфигурации...")
        
        config = {
            "vpn": {
                "name": "TWCU-VPN",
                "server": "vpn.twcu.edu",
                "default_port": 443,
                "protocol": "IKEv2"
            },
            "credentials": {
                "save_password": False,
                "auto_connect": False
            },
            "network": {
                "dns_servers": ["8.8.8.8", "1.1.1.1"],
                "timeout": 30
            },
            "interface": {
                "language": "ru",
                "theme": "dark"
            }
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print(f"✅ Конфигурация создана: {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ Ошибка создания конфигурации: {e}")
            return False
    
    def create_vpn_scripts(self):
        """Создание скриптов VPN"""
        print("\n[5/5] 🚀 Создание скриптов VPN...")
        
        scripts = {
            "twcuvpn_client.py": self.get_client_code(),
            "twcuvpn_server.py": self.get_server_code(),
            "twcuvpn_quick.py": self.get_quick_code(),
            "start_vpn.bat": self.get_bat_code()
        }
        
        created = 0
        for filename, content in scripts.items():
            try:
                filepath = self.app_dir / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   ✅ Создан {filename}")
                created += 1
            except Exception as e:
                print(f"   ❌ Ошибка создания {filename}: {e}")
        
        # Делаем Python файлы исполняемыми
        for file in self.app_dir.glob("*.py"):
            if platform.system() != 'Windows':
                os.chmod(file, 0o755)
        
        return created > 0
    
    def create_desktop_shortcut(self):
        """Создание ярлыка на рабочем столе"""
        if platform.system() == 'Windows':
            print("\n📋 Создание ярлыков...")
            
            # BAT файл для запуска
            desktop = Path.home() / "Desktop" / "TWCU VPN.bat"
            bat_content = f'''@echo off
chcp 65001
title TWCU VPN
echo Запуск TWCU VPN...
cd /d "{self.app_dir}"
python twcuvpn_client.py
pause'''
            
            try:
                with open(desktop, 'w', encoding='utf-8') as f:
                    f.write(bat_content)
                print(f"✅ Ярлык создан на рабочем столе")
            except:
                print("⚠️  Не удалось создать ярлык")
    
    def get_client_code(self):
        """Код основного клиента"""
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TWCU VPN CLIENT - Основной клиент
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
import getpass
from pathlib import Path
import requests

class TWCUVPNClient:
    def __init__(self):
        self.app_dir = Path.home() / "TWCU_VPN"
        self.config_file = self.app_dir / "config.json"
        self.log_file = self.app_dir / "vpn_log.txt"
        self.load_config()
        
    def load_config(self):
        """Загрузка конфигурации"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except:
            self.config = {
                "vpn": {"name": "TWCU-VPN"},
                "credentials": {},
                "network": {}
            }
    
    def log(self, message):
        """Логирование"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + "\\n")
        
        print(f"📝 {log_message}")
    
    def check_internet(self):
        """Проверка интернета"""
        try:
            response = requests.get("http://1.1.1.1", timeout=5)
            return True
        except:
            return False
    
    def connect(self):
        """Подключение к VPN"""
        self.log("Запуск подключения к VPN")
        
        if not self.check_internet():
            print("❌ НЕТ ИНТЕРНЕТ-ПОДКЛЮЧЕНИЯ")
            return False
        
        print("\\n🔐 ВХОД В TWCU VPN")
        print("="*40)
        
        username = input("Логин: ").strip()
        password = getpass.getpass("Пароль: ")
        
        print(f"\\n🔗 Подключаемся к {self.config['vpn']['name']}...")
        
        # Основная команда подключения
        cmd = f'rasdial "{self.config["vpn"]["name"]}" "{username}" "{password}"'
        
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                encoding='cp866'
            )
            
            if result.returncode == 0:
                self.log(f"Успешное подключение: {username}")
                print("✅ VPN ПОДКЛЮЧЕНО!")
                
                # Показать информацию
                self.show_network_info()
                return True
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                self.log(f"Ошибка подключения: {error_msg}")
                print(f"❌ ОШИБКА: {error_msg}")
                return False
                
        except Exception as e:
            self.log(f"Исключение при подключении: {e}")
            print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
            return False
    
    def disconnect(self):
        """Отключение от VPN"""
        self.log("Отключение от VPN")
        
        cmd = f'rasdial "{self.config["vpn"]["name"]}" /disconnect'
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                encoding='cp866'
            )
            
            if result.returncode == 0:
                print("✅ VPN ОТКЛЮЧЕНО")
                self.log("Успешное отключение")
            else:
                print("ℹ️  VPN не было активно")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.log(f"Ошибка отключения: {e}")
    
    def show_network_info(self):
        """Показать сетевую информацию"""
        print("\\n📊 СЕТЕВАЯ ИНФОРМАЦИЯ")
        print("="*40)
        
        try:
            # Локальные IP
            result = subprocess.run(
                "ipconfig | findstr IPv4",
                shell=True,
                capture_output=True,
                text=True,
                encoding='cp866'
            )
            print("📍 Локальные адреса:")
            if result.stdout:
                for line in result.stdout.strip().split('\\n'):
                    print(f"   {line}")
            
            # Публичный IP
            try:
                public_ip = requests.get('https://api.ipify.org', timeout=5).text
                print(f"\\n🌐 Публичный IP: {public_ip}")
            except:
                print("\\n🌐 Публичный IP: Не определен")
                
        except Exception as e:
            print(f"Ошибка получения информации: {e}")
    
    def status(self):
        """Проверка статуса"""
        self.log("Проверка статуса VPN")
        
        try:
            result = subprocess.run(
                "rasdial",
                shell=True,
                capture_output=True,
                text=True,
                encoding='cp866'
            )
            
            if self.config["vpn"]["name"] in result.stdout:
                print("✅ VPN АКТИВНО")
                self.show_network_info()
            else:
                print("❌ VPN НЕ АКТИВНО")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def menu(self):
        """Основное меню"""
        while True:
            print("\\n" + "="*50)
            print("              TWCU VPN КЛИЕНТ")
            print("="*50)
            print()
            print("1. 📡 Подключиться к VPN")
            print("2. 🔌 Отключиться от VPN")
            print("3. 📊 Проверить статус")
            print("4. 🌐 Проверить интернет")
            print("5. 📝 Показать логи")
            print("6. 🚪 Выход")
            print()
            
            choice = input("Выберите действие [1-6]: ").strip()
            
            if choice == "1":
                self.connect()
            elif choice == "2":
                self.disconnect()
            elif choice == "3":
                self.status()
            elif choice == "4":
                if self.check_internet():
                    print("✅ Интернет доступен")
                else:
                    print("❌ Нет интернета")
            elif choice == "5":
                self.show_logs()
            elif choice == "6":
                print("До свидания!")
                break
            else:
                print("❌ Неверный выбор")
            
            input("\\nНажмите Enter для продолжения...")
    
    def show_logs(self):
        """Показать логи"""
        if self.log_file.exists():
            print("\\n📋 ПОСЛЕДНИЕ ЗАПИСИ ЛОГА:")
            print("="*40)
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-20:]  # Последние 20 строк
                    for line in lines:
                        print(line.strip())
            except Exception as e:
                print(f"Ошибка чтения логов: {e}")
        else:
            print("📋 Лог файл не найден")

def main():
    """Главная функция"""
    print("\\n" + "="*50)
    print("         TWCU VPN CLIENT v2.0")
    print("="*50)
    
    client = TWCUVPNClient()
    
    # Проверка прав администратора
    try:
        test = subprocess.run(["net", "session"], capture_output=True)
        if test.returncode != 0:
            print("\\n⚠️  ВНИМАНИЕ: Требуются права администратора!")
            print("   Запустите от имени администратора для полного функционала")
            input("\\nНажмите Enter для продолжения...")
    except:
        pass
    
    client.menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n\\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"\\n❌ Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")
'''

    def get_server_code(self):
        """Код сервера"""
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TWCU VPN SERVER - Тестовый сервер
(Для учебных целей)
"""

import socket
import threading
import time
import json
from datetime import datetime

class TWCUVPNTestServer:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.clients = {}
        self.running = False
        
    def start(self):
        """Запуск сервера"""
        self.running = True
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        
        print(f"🚀 TWCU VPN Test Server запущен на {self.host}:{self.port}")
        print("   (Это учебный сервер для тестирования)")
        print("   Нажмите Ctrl+C для остановки\\n")
        
        try:
            while self.running:
                try:
                    client_socket, address = self.server.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except:
                    continue
        except KeyboardInterrupt:
            print("\\n⏹️  Остановка сервера...")
        finally:
            self.stop()
    
    def handle_client(self, client_socket, address):
        """Обработка клиента"""
        client_id = f"{address[0]}:{address[1]}"
        self.clients[client_id] = {
            'socket': client_socket,
            'address': address,
            'connected': datetime.now().strftime("%H:%M:%S")
        }
        
        print(f"🔗 Новое подключение: {client_id}")
        
        try:
            # Отправляем приветственное сообщение
            welcome = {
                'status': 'connected',
                'server': 'TWCU-VPN-Test',
                'timestamp': time.time(),
                'message': 'Добро пожаловать в TWCU VPN Test Server'
            }
            client_socket.send(json.dumps(welcome).encode())
            
            # Имитация работы VPN
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                        
                    # Простая обработка
                    response = {
                        'status': 'ok',
                        'data': 'Эхо: ' + data.decode('utf-8', errors='ignore'),
                        'timestamp': time.time()
                    }
                    client_socket.send(json.dumps(response).encode())
                    
                except:
                    break
                    
        except Exception as e:
            print(f"Ошибка с клиентом {client_id}: {e}")
        finally:
            client_socket.close()
            del self.clients[client_id]
            print(f"🔌 Отключен: {client_id}")
    
    def stop(self):
        """Остановка сервера"""
        self.running = False
        for client_id, client_data in list(self.clients.items()):
            try:
                client_data['socket'].close()
            except:
                pass
        try:
            self.server.close()
        except:
            pass
        print("✅ Сервер остановлен")

def main():
    """Запуск тестового сервера"""
    print("\\n" + "="*50)
    print("         TWCU VPN TEST SERVER")
    print("="*50)
    
    server = TWCUVPNTestServer('127.0.0.1', 8888)
    server.start()

if __name__ == "__main__":
    main()
'''

    def get_quick_code(self):
        """Код быстрого подключения"""
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TWCU VPN QUICK - Быстрое подключение
"""

import subprocess
import sys

def quick_connect():
    """Быстрое подключение одним кликом"""
    print("⚡ TWCU VPN Quick Connect")
    print("="*30)
    
    # Заранее заданные настройки (измените под себя)
    VPN_NAME = "TWCU-VPN"
    USERNAME = input("Логин: ").strip()
    
    import getpass
    PASSWORD = getpass.getpass("Пароль: ")
    
    print(f"\\n🔗 Подключаемся к {VPN_NAME}...")
    
    try:
        result = subprocess.run(
            f'rasdial "{VPN_NAME}" "{USERNAME}" "{PASSWORD}"',
            shell=True,
            capture_output=True,
            text=True,
            encoding='cp866'
        )
        
        if result.returncode == 0:
            print("✅ УСПЕШНО ПОДКЛЮЧЕНО!")
            
            # Показать IP
            ip_result = subprocess.run(
                "ipconfig | findstr IPv4",
                shell=True,
                capture_output=True,
                text=True,
                encoding='cp866'
            )
            print("\\n📍 Ваши IP адреса:")
            print(ip_result.stdout)
            
            print("\\nℹ️  Для отключения используйте:")
            print(f'   rasdial "{VPN_NAME}" /disconnect')
            
            input("\\nНажмите Enter для выхода...")
            
        else:
            print("❌ ОШИБКА ПОДКЛЮЧЕНИЯ!")
            print(f"\\nОшибка: {result.stderr}")
            input("\\nНажмите Enter для выхода...")
            
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        input("\\nНажмите Enter для выхода...")

def quick_disconnect():
    """Быстрое отключение"""
    print("🔌 Быстрое отключение VPN...")
    
    try:
        subprocess.run(
            'rasdial /disconnect',
            shell=True,
            capture_output=True
        )
        print("✅ VPN отключено")
    except:
        print("⚠️  Не удалось отключить VPN")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "disconnect":
        quick_disconnect()
    else:
        quick_connect()
'''

    def get_bat_code(self):
        """Код BAT файла"""
        return '''@echo off
chcp 65001 >nul
title TWCU VPN Launcher
cls

echo.
echo ========================================
echo         TWCU VPN LAUNCHER
echo ========================================
echo.
echo 1. Запустить VPN клиент
echo 2. Быстрое подключение
echo 3. Отключить VPN
echo 4. Тестовый сервер
echo 5. Выход
echo.
set /p choice="Выберите [1-5]: "

if "%choice%"=="1" goto CLIENT
if "%choice%"=="2" goto QUICK
if "%choice%"=="3" goto DISCONNECT
if "%choice%"=="4" goto SERVER
if "%choice%"=="5" exit

:CLIENT
cd /d "%~dp0"
python twcuvpn_client.py
goto END

:QUICK
cd /d "%~dp0"
python twcuvpn_quick.py
goto END

:DISCONNECT
rasdial /disconnect
echo VPN отключено
timeout /t 3 >nul
goto END

:SERVER
cd /d "%~dp0"
python twcuvpn_server.py
goto END

:END
pause
'''

    def install(self):
        """Основной метод установки"""
        self.print_banner()
        
        # Проверки
        if not self.check_python():
            return False
        
        input("Нажмите Enter для начала установки...")
        
        # Установка
        steps = [
            self.install_dependencies,
            self.create_app_directory,
            self.create_config,
            self.create_vpn_scripts,
            self.create_desktop_shortcut
        ]
        
        for i, step in enumerate(steps, 1):
            try:
                if not step():
                    print(f"\\n⚠️  Шаг {i} завершен с предупреждениями")
            except Exception as e:
                print(f"\\n❌ Ошибка на шаге {i}: {e}")
                continue
        
        print("\\n" + "="*50)
        print("✅ УСТАНОВКА ЗАВЕРШЕНА!")
        print("="*50)
        print()
        print("📂 Файлы установлены в:")
        print(f"   {self.app_dir}")
        print()
        print("🚀 Запустить можно:")
        print("   1. Двойной клик по 'TWCU VPN.bat' на рабочем столе")
        print("   2. Запуск 'twcuvpn_client.py' из папки TWCU_VPN")
        print()
        print("⚙️  Настройки хранятся в config.json")
        print()
        
        input("Нажмите Enter для завершения...")
        return True

def main():
    """Точка входа"""
    installer = TWCUVPNInstaller()
    installer.install()

if __name__ == "__main__":
    main()