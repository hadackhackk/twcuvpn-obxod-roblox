#!/usr/bin/env python3
"""
TWCU VPN Server - Учебный пример
Запуск: python vpn_server.py
"""

import socket
import threading
import hashlib
import json
import time
from datetime import datetime
import logging
from cryptography.fernet import Fernet
import base64
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TWCUVPNProtocol:
    """Протокол обмена данными TWCU VPN"""
    
    COMMANDS = {
        'AUTH': 'AUTHENTICATE',
        'CONNECT': 'CONNECT',
        'DISCONNECT': 'DISCONNECT',
        'DATA': 'DATA',
        'PING': 'PING',
        'STATS': 'STATISTICS'
    }
    
    @staticmethod
    def create_packet(command, data):
        """Создать пакет"""
        packet = {
            'command': command,
            'timestamp': time.time(),
            'data': data,
            'checksum': hashlib.md5(json.dumps(data).encode()).hexdigest()
        }
        return json.dumps(packet).encode()
    
    @staticmethod
    def parse_packet(data):
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

class TWCUVPNClient:
    """Клиент подключенный к VPN серверу"""
    
    def __init__(self, conn, addr, client_id):
        self.conn = conn
        self.addr = addr
        self.client_id = client_id
        self.username = None
        self.connected = False
        self.encryption_key = None
        self.cipher = None
        self.start_time = time.time()
        self.data_sent = 0
        self.data_received = 0
        self.last_active = time.time()
        
    def encrypt(self, data):
        """Шифрование данных"""
        if self.cipher:
            return self.cipher.encrypt(data)
        return data
    
    def decrypt(self, data):
        """Дешифрование данных"""
        if self.cipher:
            return self.cipher.decrypt(data)
        return data
    
    def update_stats(self, sent=0, received=0):
        """Обновить статистику"""
        self.data_sent += sent
        self.data_received += received
        self.last_active = time.time()
    
    def get_session_time(self):
        """Время сессии"""
        return time.time() - self.start_time

class TWCUVPNUserDB:
    """База данных пользователей VPN"""
    
    def __init__(self):
        self.users = {
            'student1': {
                'password': hashlib.sha256('pass123'.encode()).hexdigest(),
                'role': 'student',
                'max_bandwidth': 1024 * 1024,  # 1 MB/s
                'active': True
            },
            'teacher1': {
                'password': hashlib.sha256('teacher456'.encode()).hexdigest(),
                'role': 'teacher',
                'max_bandwidth': 10 * 1024 * 1024,  # 10 MB/s
                'active': True
            },
            'admin': {
                'password': hashlib.sha256('admin789'.encode()).hexdigest(),
                'role': 'admin',
                'max_bandwidth': 100 * 1024 * 1024,  # 100 MB/s
                'active': True
            }
        }
    
    def authenticate(self, username, password):
        """Аутентификация пользователя"""
        if username in self.users:
            user = self.users[username]
            if user['active'] and user['password'] == hashlib.sha256(password.encode()).hexdigest():
                return {'success': True, 'role': user['role'], 'bandwidth': user['max_bandwidth']}
        return {'success': False, 'error': 'Invalid credentials'}

class TWCUVPNTrafficManager:
    """Менеджер трафика VPN"""
    
    def __init__(self):
        self.routes = {}
        self.dns_cache = {}
        self.firewall_rules = []
        
    def add_route(self, client_id, network, gateway):
        """Добавить маршрут"""
        self.routes[client_id] = {'network': network, 'gateway': gateway}
        
    def resolve_dns(self, hostname):
        """DNS разрешение"""
        if hostname in self.dns_cache:
            if time.time() - self.dns_cache[hostname]['timestamp'] < 300:  # 5 минут кэш
                return self.dns_cache[hostname]['ip']
        
        # Здесь была бы реальная DNS логика
        fake_ips = {
            'university.twcu.edu': '192.168.1.100',
            'library.twcu.edu': '192.168.1.101',
            'mail.twcu.edu': '192.168.1.102',
            'vpn.twcu.edu': '10.0.0.1'
        }
        
        ip = fake_ips.get(hostname, '8.8.8.8')
        self.dns_cache[hostname] = {'ip': ip, 'timestamp': time.time()}
        return ip

class TWCUVPNHealthMonitor:
    """Монитор здоровья сервера"""
    
    def __init__(self):
        self.metrics = {
            'connections': 0,
            'bandwidth_up': 0,
            'bandwidth_down': 0,
            'errors': 0,
            'uptime': time.time()
        }
    
    def update_metric(self, metric, value):
        """Обновить метрику"""
        if metric in self.metrics:
            self.metrics[metric] += value
    
    def get_report(self):
        """Получить отчет"""
        report = self.metrics.copy()
        report['uptime'] = time.time() - report['uptime']
        return report

class TWCUVPNInstance:
    """Основной экземпляр VPN сервера"""
    
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server = None
        self.clients = {}
        self.user_db = TWCUVPNUserDB()
        self.traffic_manager = TWCUVPNTrafficManager()
        self.health_monitor = TWCUVPNHealthMonitor()
        self.running = False
        self.client_counter = 0
        
        # Загрузка конфигурации
        self.load_config()
        
    def load_config(self):
        """Загрузить конфигурацию"""
        self.config = {
            'max_clients': 100,
            'timeout': 300,
            'log_level': 'INFO',
            'encryption': True,
            'port_forwarding': False
        }
    
    def start(self):
        """Запуск VPN сервера"""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            self.server.settimeout(1)
            
            self.running = True
            logger.info(f"TWCU VPN Server запущен на {self.host}:{self.port}")
            logger.info("Ожидание подключений...")
            
            # Запуск потоков
            accept_thread = threading.Thread(target=self.accept_connections)
            monitor_thread = threading.Thread(target=self.monitor_clients)
            stats_thread = threading.Thread(target=self.print_stats)
            
            accept_thread.daemon = True
            monitor_thread.daemon = True
            stats_thread.daemon = True
            
            accept_thread.start()
            monitor_thread.start()
            stats_thread.start()
            
            # Основной цикл
            while self.running:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("Получен сигнал прерывания")
                    self.stop()
                    
        except Exception as e:
            logger.error(f"Ошибка запуска сервера: {e}")
            self.stop()
    
    def accept_connections(self):
        """Принимать новые подключения"""
        while self.running:
            try:
                conn, addr = self.server.accept()
                conn.settimeout(10)
                
                self.client_counter += 1
                client_id = f"client_{self.client_counter:04d}"
                
                logger.info(f"Новое подключение от {addr}, ID: {client_id}")
                
                client = TWCUVPNClient(conn, addr, client_id)
                self.clients[client_id] = client
                self.health_monitor.update_metric('connections', 1)
                
                # Обработка клиента в отдельном потоке
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client,)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    logger.error(f"Ошибка accept: {e}")
    
    def handle_client(self, client):
        """Обработка клиента"""
        try:
            # Фаза аутентификации
            auth_result = self.authenticate_client(client)
            if not auth_result['success']:
                client.conn.close()
                del self.clients[client.client_id]
                return
            
            client.connected = True
            client.username = auth_result['username']
            
            # Установка шифрования
            if self.config['encryption']:
                key = Fernet.generate_key()
                client.encryption_key = key
                client.cipher = Fernet(key)
                
                # Отправка ключа клиенту
                key_packet = TWCUVPNProtocol.create_packet(
                    TWCUVPNProtocol.COMMANDS['AUTH'],
                    {'key': key.decode(), 'status': 'authenticated'}
                )
                client.conn.send(key_packet)
            
            logger.info(f"Клиент {client.username} ({client.addr}) аутентифицирован")
            
            # Основной цикл обработки данных
            while client.connected and self.running:
                try:
                    # Получение данных
                    data = client.conn.recv(4096)
                    if not data:
                        break
                    
                    # Дешифрование
                    if client.cipher:
                        try:
                            data = client.decrypt(data)
                        except:
                            logger.warning(f"Ошибка дешифрования от {client.username}")
                            continue
                    
                    # Обработка пакета
                    packet = TWCUVPNProtocol.parse_packet(data)
                    if packet:
                        self.process_packet(client, packet)
                    else:
                        logger.warning(f"Неверный пакет от {client.username}")
                        
                except socket.timeout:
                    # Отправка ping
                    ping_packet = TWCUVPNProtocol.create_packet(
                        TWCUVPNProtocol.COMMANDS['PING'],
                        {'time': time.time()}
                    )
                    if client.cipher:
                        ping_packet = client.encrypt(ping_packet)
                    client.conn.send(ping_packet)
                    
                except Exception as e:
                    logger.error(f"Ошибка обработки клиента {client.username}: {e}")
                    break
        
        except Exception as e:
            logger.error(f"Ошибка handle_client: {e}")
        
        finally:
            # Завершение соединения
            self.disconnect_client(client)
    
    def authenticate_client(self, client):
        """Аутентификация клиента"""
        try:
            # Получение учетных данных
            auth_packet = client.conn.recv(1024)
            if not auth_packet:
                return {'success': False, 'error': 'No data'}
            
            packet = TWCUVPNProtocol.parse_packet(auth_packet)
            if not packet or packet['command'] != TWCUVPNProtocol.COMMANDS['AUTH']:
                return {'success': False, 'error': 'Invalid auth packet'}
            
            auth_data = packet['data']
            username = auth_data.get('username')
            password = auth_data.get('password')
            
            if not username or not password:
                return {'success': False, 'error': 'Missing credentials'}
            
            # Проверка в БД
            result = self.user_db.authenticate(username, password)
            if result['success']:
                return {'success': True, 'username': username, 'role': result['role']}
            else:
                return {'success': False, 'error': result['error']}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def process_packet(self, client, packet):
        """Обработка полученного пакета"""
        command = packet['command']
        
        if command == TWCUVPNProtocol.COMMANDS['CONNECT']:
            # Запрос на подключение к ресурсу
            target = packet['data'].get('target')
            if target:
                # Разрешение DNS
                ip = self.traffic_manager.resolve_dns(target)
                
                response = TWCUVPNProtocol.create_packet(
                    TWCUVPNProtocol.COMMANDS['CONNECT'],
                    {'target': target, 'ip': ip, 'status': 'connected'}
                )
                
                if client.cipher:
                    response = client.encrypt(response)
                
                client.conn.send(response)
                logger.info(f"Клиент {client.username} подключился к {target} ({ip})")
        
        elif command == TWCUVPNProtocol.COMMANDS['DATA']:
            # Пересылка данных
            data = packet['data'].get('data')
            target = packet['data'].get('target')
            
            client.update_stats(sent=len(str(data)))
            self.health_monitor.update_metric('bandwidth_up', len(str(data)))
            
            # Здесь была бы пересылка данных к целевому серверу
            response = TWCUVPNProtocol.create_packet(
                TWCUVPNProtocol.COMMANDS['DATA'],
                {'status': 'delivered', 'bytes': len(str(data))}
            )
            
            if client.cipher:
                response = client.encrypt(response)
            
            client.conn.send(response)
        
        elif command == TWCUVPNProtocol.COMMANDS['STATS']:
            # Запрос статистики
            stats = {
                'session_time': client.get_session_time(),
                'data_sent': client.data_sent,
                'data_received': client.data_received,
                'server_uptime': self.health_monitor.get_report()['uptime'],
                'active_clients': len([c for c in self.clients.values() if c.connected])
            }
            
            response = TWCUVPNProtocol.create_packet(
                TWCUVPNProtocol.COMMANDS['STATS'],
                stats
            )
            
            if client.cipher:
                response = client.encrypt(response)
            
            client.conn.send(response)
    
    def disconnect_client(self, client):
        """Отключение клиента"""
        if client.client_id in self.clients:
            client.connected = False
            try:
                client.conn.close()
            except:
                pass
            
            logger.info(f"Клиент {client.username} ({client.addr}) отключен")
            del self.clients[client.client_id]
            self.health_monitor.update_metric('connections', -1)
    
    def monitor_clients(self):
        """Мониторинг активности клиентов"""
        while self.running:
            time.sleep(60)  # Проверка каждую минуту
            
            current_time = time.time()
            to_disconnect = []
            
            for client_id, client in self.clients.items():
                if current_time - client.last_active > self.config['timeout']:
                    logger.warning(f"Таймаут клиента {client.username}")
                    to_disconnect.append(client_id)
            
            for client_id in to_disconnect:
                if client_id in self.clients:
                    self.disconnect_client(self.clients[client_id])
    
    def print_stats(self):
        """Вывод статистики сервера"""
        while self.running:
            time.sleep(30)
            
            report = self.health_monitor.get_report()
            active_clients = len([c for c in self.clients.values() if c.connected])
            
            logger.info(f"=== Статистика сервера ===")
            logger.info(f"Активных клиентов: {active_clients}")
            logger.info(f"Аптайм: {report['uptime']:.0f} сек")
            logger.info(f"Пропускная способность: ↑{report['bandwidth_up']} ↓{report['bandwidth_down']} байт")
            logger.info(f"==========================")
    
    def stop(self):
        """Остановка сервера"""
        self.running = False
        logger.info("Остановка сервера...")
        
        # Отключение всех клиентов
        for client_id in list(self.clients.keys()):
            self.disconnect_client(self.clients[client_id])
        
        if self.server:
            try:
                self.server.close()
            except:
                pass
        
        logger.info("Сервер остановлен")

def main():
    """Основная функция"""
    print("""
╔═══════════════════════════════════════╗
║         TWCU VPN SERVER v1.0         ║
╚═══════════════════════════════════════╝
    
Режимы запуска:
    1. Стандартный (порт 5555)
    2. Кастомный порт
    3. Только локальный хост
    4. Тестовый режим
    """)
    
    mode = input("Выберите режим [1-4]: ").strip()
    
    if mode == '1':
        server = TWCUVPNInstance('0.0.0.0', 5555)
    elif mode == '2':
        port = int(input("Введите порт: ").strip())
        server = TWCUVPNInstance('0.0.0.0', port)
    elif mode == '3':
        server = TWCUVPNInstance('127.0.0.1', 5555)
    elif mode == '4':
        print("Тестовый режим - логирование в консоль")
        server = TWCUVPNInstance('127.0.0.1', 9999)
    else:
        print("Неверный выбор, запуск в стандартном режиме")
        server = TWCUVPNInstance('0.0.0.0', 5555)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nСервер остановлен пользователем")

if __name__ == "__main__":
    main()