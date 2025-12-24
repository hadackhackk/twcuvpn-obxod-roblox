#!/usr/bin/env python3
"""
TWCU VPN Client - Учебный пример
Запуск: python vpn_client.py
"""

import socket
import json
import hashlib
import time
import threading
from cryptography.fernet import Fernet
import sys

class TWCUVPNClient:
    def __init__(self, server_host='127.0.0.1', server_port=5555):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.connected = False
        self.username = None
        self.cipher = None
        self.session_id = None
    
    def connect_to_server(self):
        """Подключение к VPN серверу"""
        try:
            print(f"Подключение к VPN серверу {self.server_host}:{self.server_port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.socket.settimeout(5)
            
            print("Соединение установлено")
            return True
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False
    
    def authenticate(self, username, password):
        """Аутентификация на сервере"""
        try:
            # Отправка учетных данных
            auth_packet = self.create_packet('AUTHENTICATE', {
                'username': username,
                'password': password
            })
            
            self.socket.send(auth_packet)
            
            # Получение ответа
            response = self.socket.recv(4096)
            packet = self.parse_packet(response)
            
            if packet and packet['command'] == 'AUTHENTICATE':
                if packet['data'].get('status') == 'authenticated':
                    key = packet['data'].get('key')
                    if key:
                        self.cipher = Fernet(key.encode())
                    
                    self.username = username
                    self.connected = True
                    print(f"Аутентификация успешна! Добро пожаловать, {username}")
                    return True
            
            print("Ошибка аутентификации")
            return False
            
        except Exception as e:
            print(f"Ошибка при аутентификации: {e}")
            return False
    
    def create_packet(self, command, data):
        """Создать пакет"""
        packet = {
            'command': command,
            'timestamp': time.time(),
            'data': data,
            'checksum': hashlib.md5(json.dumps(data).encode()).hexdigest()
        }
        return json.dumps(packet).encode()
    
    def parse_packet(self, data):
        """Разобрать пакет"""
        try:
            packet = json.loads(data.decode())
            if 'checksum' in packet:
                check = hashlib.md5(json.dumps(packet['data']).encode()).hexdigest()
                if check == packet['checksum']:
                    return packet
            return None
        except:
            return None
    
    def send_packet(self, command, data):
        """Отправить пакет"""
        if not self.connected:
            print("Не подключено к серверу")
            return None
        
        try:
            packet = self.create_packet(command, data)
            
            if self.cipher:
                packet = self.cipher.encrypt(packet)
            
            self.socket.send(packet)
            
            # Получение ответа
            response = self.socket.recv(4096)
            
            if self.cipher:
                response = self.cipher.decrypt(response)
            
            return self.parse_packet(response)
            
        except Exception as e:
            print(f"Ошибка отправки пакета: {e}")
            return None
    
    def connect_to_resource(self, resource):
        """Подключиться к ресурсу через VPN"""
        print(f"Подключение к {resource} через VPN...")
        
        response = self.send_packet('CONNECT', {'target': resource})
        
        if response and response['command'] == 'CONNECT':
            data = response['data']
            if data.get('status') == 'connected':
                print(f"Успешно подключено к {resource}")
                print(f"IP адрес: {data.get('ip')}")
                return True
        
        print(f"Ошибка подключения к {resource}")
        return False
    
    def get_statistics(self):
        """Получить статистику"""
        print("Запрос статистики...")
        
        response = self.send_packet('STATISTICS', {})
        
        if response and response['command'] == 'STATISTICS':
            stats = response['data']
            print("\n=== Статистика VPN ===")
            print(f"Время сессии: {stats.get('session_time', 0):.0f} сек")
            print(f"Отправлено данных: {stats.get('data_sent', 0)} байт")
            print(f"Получено данных: {stats.get('data_received', 0)} байт")
            print(f"Аптайм сервера: {stats.get('server_uptime', 0):.0f} сек")
            print(f"Активных клиентов: {stats.get('active_clients', 0)}")
            return True
        
        print("Ошибка получения статистики")
        return False
    
    def disconnect(self):
        """Отключиться от VPN"""
        if self.connected:
            print("Отключение от VPN...")
            self.send_packet('DISCONNECT', {})
            self.connected = False
        
        if self.socket:
            self.socket.close()
        
        print("Отключено")

def interactive_menu():
    """Интерактивное меню клиента"""
    print("""
╔═══════════════════════════════════════╗
║         TWCU VPN CLIENT v1.0         ║
╚═══════════════════════════════════════╝
    """)
    
    # Настройка подключения
    server_host = input("Адрес сервера VPN [127.0.0.1]: ").strip() or '127.0.0.1'
    server_port = input("Порт сервера [5555]: ").strip()
    server_port = int(server_port) if server_port else 5555
    
    client = TWCUVPNClient(server_host, server_port)
    
    if not client.connect_to_server():
        return
    
    # Аутентификация
    print("\n=== Аутентификация ===")
    username = input("Логин: ").strip()
    password = input("Пароль: ").strip()
    
    if not client.authenticate(username, password):
        client.disconnect()
        return
    
    # Основной цикл
    while client.connected:
        print("""
╔═══════════════════════════════════════╗
║           ГЛАВНОЕ МЕНЮ               ║
╠═══════════════════════════════════════╣
║ 1. Подключиться к ресурсу            ║
║ 2. Отправить данные                  ║
║ 3. Получить статистику               ║
║ 4. Проверить соединение              ║
║ 5. Отключиться                       ║
║ 6. Выход                             ║
╚═══════════════════════════════════════╝
        """)
        
        choice = input("Выберите действие [1-6]: ").strip()
        
        if choice == '1':
            resource = input("Введите адрес ресурса (например: university.twcu.edu): ").strip()
            client.connect_to_resource(resource)
        
        elif choice == '2':
            data = input("Введите данные для отправки: ").strip()
            response = client.send_packet('DATA', {'data': data, 'target': 'server'})
            if response:
                print(f"Ответ сервера: {response['data']}")
        
        elif choice == '3':
            client.get_statistics()
        
        elif choice == '4':
            response = client.send_packet('PING', {'time': time.time()})
            if response:
                print("Сервер доступен")
            else:
                print("Сервер не отвечает")
        
        elif choice == '5':
            client.disconnect()
            print("До свидания!")
            break
        
        elif choice == '6':
            client.disconnect()
            sys.exit(0)
        
        else:
            print("Неверный выбор")
        
        input("\nНажмите Enter для продолжения...")

def quick_connect():
    """Быстрое подключение"""
    client = TWCUVPNClient('127.0.0.1', 5555)
    
    if client.connect_to_server():
        if client.authenticate('student1', 'pass123'):
            print("Быстрое подключение успешно!")
            
            # Автоподключение к ресурсу
            client.connect_to_resource('university.twcu.edu')
            
            # Получение статистики
            client.get_statistics()
            
            # Удержание соединения
            input("\nНажмите Enter для отключения...")
            
            client.disconnect()

def main():
    """Основная функция"""
    print("Режимы запуска клиента:")
    print("1. Интерактивный режим")
    print("2. Быстрое подключение")
    print("3. Тестовый режим")
    
    mode = input("Выберите режим [1-3]: ").strip()
    
    if mode == '1':
        interactive_menu()
    elif mode == '2':
        quick_connect()
    elif mode == '3':
        # Тестовые вызовы
        test_vpn()
    else:
        interactive_menu()

def test_vpn():
    """Тестовые функции"""
    print("\n=== Тестовый режим ===")
    
    client = TWCUVPNClient('127.0.0.1', 5555)
    
    if client.connect_to_server():
        # Тест аутентификации
        test_users = [
            ('student1', 'pass123', True),
            ('teacher1', 'teacher456', True),
            ('admin', 'admin789', True),
            ('wrong', 'wrong', False)
        ]
        
        for username, password, should_succeed in test_users:
            print(f"\nТест: {username}/{password}")
            result = client.authenticate(username, password)
            if result == should_succeed:
                print(f"✓ Тест пройден")
            else:
                print(f"✗ Тест не пройден")
            
            if result:
                client.disconnect()
                client.connect_to_server()

if __name__ == "__main__":
    main()