"""
Nodo Multicast Completo con Concurrencia
Combina emisor y receptor con manejo de threads para operación simultánea
"""

import socket
import struct
import threading
import time
import sys
import os
import queue
from datetime import datetime
from config import *

class MulticastNode:
    def __init__(self, node_name=None):
        """
        Inicializa un nodo completo con capacidades de envío y recepción
        """
        self.node_name = node_name or NODE_NAME
        self.group = MULTICAST_GROUP
        self.port = PORT
        
        # Sockets
        self.sender_sock = None
        self.receiver_sock = None
        
        # Control de threads
        self.running = False
        self.threads = {}
        self.locks = {
            'print': threading.Lock(),
            'stats': threading.Lock(),
            'nodes': threading.Lock()
        }
        
        # Colas de mensajes
        self.outgoing_queue = queue.Queue()
        self.incoming_queue = queue.Queue()
        
        # Estado del nodo
        self.active_nodes = {}  # {node_name: last_seen_time}
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'errors': 0,
            'start_time': time.time()
        }
        
        # Configuración
        self.heartbeat_interval = 30  # segundos
        self.node_timeout = 90  # segundos para considerar un nodo inactivo
        
    def setup_sockets(self):
        """
        Configura los sockets para envío y recepción
        """
        try:
            # Socket emisor
            self.sender_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.sender_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)
            
            # Socket receptor
            self.receiver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.receiver_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Intentar SO_REUSEPORT si está disponible
            try:
                self.receiver_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except:
                pass
            
            # Bind y unirse al grupo multicast
            self.receiver_sock.bind(('', self.port))
            mreq = struct.pack("4sl", socket.inet_aton(self.group), socket.INADDR_ANY)
            self.receiver_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            
            # Configurar timeout para el receptor
            self.receiver_sock.settimeout(1.0)
            
            self.safe_print(f"✓ Sockets configurados para {self.group}:{self.port}", 'GREEN')
            return True
            
        except Exception as e:
            self.safe_print(f"✗ Error configurando sockets: {e}", 'RED')
            return False
    
    def safe_print(self, message, color='WHITE'):
        """
        Imprime mensajes de forma thread-safe
        """
        with self.locks['print']:
            print_colored(message, color)
    
    def receiver_thread(self):
        """
        Thread para recibir mensajes continuamente
        """
        self.safe_print("📡 Thread receptor iniciado", 'CYAN')
        
        while self.running:
            try:
                data, address = self.receiver_sock.recvfrom(BUFFER_SIZE)
                
                # Decodificar mensaje
                message_str = data.decode('utf-8')
                message = parse_message(message_str)
                
                if message:
                    # Ignorar mensajes propios
                    if message.get('node_id') != self.node_name:
                        self.process_received_message(message, address)
                        
                        # Actualizar estadísticas
                        with self.locks['stats']:
                            self.stats['messages_received'] += 1
                            self.stats['bytes_received'] += len(data)
                    
            except socket.timeout:
                continue  # Timeout normal, continuar
            except Exception as e:
                if self.running:
                    self.safe_print(f"Error en receptor: {e}", 'YELLOW')
                    with self.locks['stats']:
                        self.stats['errors'] += 1
        
        self.safe_print("📡 Thread receptor detenido", 'YELLOW')
    
    def sender_thread(self):
        """
        Thread para enviar mensajes desde la cola
        """
        self.safe_print("📤 Thread emisor iniciado", 'CYAN')
        
        while self.running:
            try:
                # Esperar mensaje con timeout
                message = self.outgoing_queue.get(timeout=1)
                
                if message:
                    # Enviar mensaje
                    data = message.encode('utf-8')
                    self.sender_sock.sendto(data, (self.group, self.port))
                    
                    # Actualizar estadísticas
                    with self.locks['stats']:
                        self.stats['messages_sent'] += 1
                        self.stats['bytes_sent'] += len(data)
                    
                    # Log
                    log_message(f"TX: {message}", 'SENT')
                    
            except queue.Empty:
                continue  # Timeout normal
            except Exception as e:
                if self.running:
                    self.safe_print(f"Error en emisor: {e}", 'YELLOW')
                    with self.locks['stats']:
                        self.stats['errors'] += 1
        
        self.safe_print("📤 Thread emisor detenido", 'YELLOW')
    
    def heartbeat_thread(self):
        """
        Thread para enviar heartbeat/keepalive periódicamente
        """
        self.safe_print("💓 Thread heartbeat iniciado", 'CYAN')
        
        while self.running:
            try:
                # Enviar heartbeat
                message = create_message('HEARTBEAT', f"{self.node_name} activo", self.node_name)
                self.outgoing_queue.put(message)
                
                # Limpiar nodos inactivos
                self.cleanup_inactive_nodes()
                
                # Esperar hasta el próximo heartbeat
                for _ in range(self.heartbeat_interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.safe_print(f"Error en heartbeat: {e}", 'YELLOW')
        
        self.safe_print("💓 Thread heartbeat detenido", 'YELLOW')
    
    def monitor_thread(self):
        """
        Thread para monitorear el estado del sistema
        """
        self.safe_print("📊 Thread monitor iniciado", 'CYAN')
        
        while self.running:
            try:
                # Esperar 10 segundos entre actualizaciones
                for _ in range(10):
                    if not self.running:
                        break
                    time.sleep(1)
                
                if self.running:
                    self.show_status()
                    
            except Exception as e:
                self.safe_print(f"Error en monitor: {e}", 'YELLOW')
        
        self.safe_print("📊 Thread monitor detenido", 'YELLOW')
    
    def process_received_message(self, message, address):
        """
        Procesa mensajes recibidos de otros nodos
        """
        node_id = message.get('node_id', 'Unknown')
        msg_type = message.get('type', 'MESSAGE')
        content = message.get('content', '')
        timestamp = message.get('timestamp', '')
        
        # Actualizar nodo activo
        with self.locks['nodes']:
            self.active_nodes[node_id] = time.time()
        
        # Procesar según tipo de mensaje
        if msg_type == 'HELLO':
            self.safe_print(f"🟢 [{timestamp}] {node_id} se unió a la red", 'GREEN')
            self.safe_print(f"   Dirección: {address[0]}:{address[1]}", 'GREEN')
            
        elif msg_type == 'GOODBYE':
            self.safe_print(f"🔴 [{timestamp}] {node_id} abandonó la red", 'RED')
            with self.locks['nodes']:
                self.active_nodes.pop(node_id, None)
                
        elif msg_type == 'MESSAGE':
            self.safe_print(f"💬 [{timestamp}] {node_id}: {content}", 'BLUE')
            
        elif msg_type == 'PING':
            self.safe_print(f"🏓 [{timestamp}] Ping de {node_id}", 'YELLOW')
            # Responder con PONG
            pong = create_message('PONG', f"Pong desde {self.node_name}", self.node_name)
            self.outgoing_queue.put(pong)
            
        elif msg_type == 'PONG':
            self.safe_print(f"🏐 [{timestamp}] Pong de {node_id}", 'YELLOW')
            
        elif msg_type == 'HEARTBEAT':
            # Heartbeat silencioso (no mostrar)
            pass
            
        else:
            self.safe_print(f"📨 [{timestamp}] {node_id} [{msg_type}]: {content}", 'WHITE')
        
        # Log
        log_message(f"RX from {address}: {message}", 'RECEIVED')
    
    def cleanup_inactive_nodes(self):
        """
        Elimina nodos que no han enviado mensajes recientemente
        """
        current_time = time.time()
        inactive_nodes = []
        
        with self.locks['nodes']:
            for node_id, last_seen in self.active_nodes.items():
                if current_time - last_seen > self.node_timeout:
                    inactive_nodes.append(node_id)
            
            for node_id in inactive_nodes:
                del self.active_nodes[node_id]
                self.safe_print(f"⚠️ Nodo {node_id} marcado como inactivo", 'YELLOW')
    
    def send_message(self, content, msg_type='MESSAGE'):
        """
        Envía un mensaje a través de la cola
        """
        message = create_message(msg_type, content, self.node_name)
        self.outgoing_queue.put(message)
    
    def show_status(self):
        """
        Muestra el estado actual del nodo
        """
        with self.locks['stats']:
            uptime = int(time.time() - self.stats['start_time'])
            hours = uptime // 3600
            minutes = (uptime % 3600) // 60
            seconds = uptime % 60
            
            status_lines = [
                "\n" + "="*50,
                f"📊 ESTADO DEL NODO: {self.node_name}",
                "="*50,
                f"⏱️  Tiempo activo: {hours:02d}:{minutes:02d}:{seconds:02d}",
                f"📤 Mensajes enviados: {self.stats['messages_sent']}",
                f"📥 Mensajes recibidos: {self.stats['messages_received']}",
                f"📦 Bytes enviados: {self.stats['bytes_sent']}",
                f"📦 Bytes recibidos: {self.stats['bytes_received']}",
                f"⚠️  Errores: {self.stats['errors']}",
            ]
        
        with self.locks['nodes']:
            active_count = len(self.active_nodes)
            status_lines.append(f"👥 Nodos activos: {active_count}")
            if self.active_nodes:
                status_lines.append("   " + ", ".join(self.active_nodes.keys()))
        
        status_lines.append("="*50 + "\n")
        
        # Imprimir todo junto para evitar mezcla con otros mensajes
        with self.locks['print']:
            for line in status_lines:
                print(COLORS['MAGENTA'] + line + COLORS['RESET'])
    
    def interactive_mode(self):
        """
        Modo interactivo para el usuario
        """
        self.safe_print("\n" + "="*60, 'CYAN')
        self.safe_print(f"   NODO MULTICAST: {self.node_name}", 'CYAN')
        self.safe_print("="*60, 'CYAN')
        
        # Comandos disponibles
        commands = {
            '/help': 'Mostrar esta ayuda',
            '/status': 'Ver estado del nodo',
            '/nodes': 'Listar nodos activos',
            '/ping': 'Enviar ping a todos',
            '/stats': 'Ver estadísticas detalladas',
            '/clear': 'Limpiar pantalla',
            '/exit': 'Salir del programa'
        }
        
        self.safe_print("\n📝 Comandos disponibles:", 'YELLOW')
        for cmd, desc in commands.items():
            self.safe_print(f"  {cmd:<12} - {desc}", 'WHITE')
        
        self.safe_print("\n💡 Escribe un mensaje y presiona Enter para enviarlo\n", 'CYAN')
        
        try:
            while self.running:
                # Prompt
                message = input(f"{COLORS['CYAN']}[{self.node_name}] > {COLORS['RESET']}")
                
                if not message:
                    continue
                
                # Procesar comandos
                if message.lower() == '/exit':
                    break
                    
                elif message.lower() == '/help':
                    for cmd, desc in commands.items():
                        self.safe_print(f"  {cmd:<12} - {desc}", 'WHITE')
                        
                elif message.lower() == '/status':
                    self.show_status()
                    
                elif message.lower() == '/nodes':
                    with self.locks['nodes']:
                        if self.active_nodes:
                            self.safe_print(f"\n👥 Nodos activos ({len(self.active_nodes)}):", 'MAGENTA')
                            for node_id, last_seen in self.active_nodes.items():
                                ago = int(time.time() - last_seen)
                                self.safe_print(f"  • {node_id} (hace {ago}s)", 'WHITE')
                        else:
                            self.safe_print("No hay otros nodos activos", 'YELLOW')
                            
                elif message.lower() == '/ping':
                    self.send_message("Ping!", 'PING')
                    self.safe_print("🏓 Ping enviado", 'YELLOW')
                    
                elif message.lower() == '/stats':
                    with self.locks['stats']:
                        self.safe_print("\n📊 Estadísticas detalladas:", 'MAGENTA')
                        for key, value in self.stats.items():
                            if key != 'start_time':
                                self.safe_print(f"  • {key}: {value}", 'WHITE')
                                
                elif message.lower() == '/clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    
                else:
                    if message.startswith('/'):
                        self.safe_print(f"Comando desconocido: {message}", 'RED')
                    else:
                        # Enviar mensaje normal
                        self.send_message(message)
                        self.safe_print(f"✓ Mensaje enviado", 'GREEN')
                        
        except KeyboardInterrupt:
            self.safe_print("\n⏹ Interrumpido por usuario", 'YELLOW')
    
    def start(self):
        """
        Inicia el nodo y todos sus threads
        """
        # Configurar sockets
        if not self.setup_sockets():
            return False
        
        self.running = True
        
        # Enviar mensaje HELLO
        hello_msg = create_message('HELLO', f"{self.node_name} se ha unido", self.node_name)
        self.outgoing_queue.put(hello_msg)
        
        # Iniciar threads
        threads_config = [
            ('receiver', self.receiver_thread),
            ('sender', self.sender_thread),
            ('heartbeat', self.heartbeat_thread),
            ('monitor', self.monitor_thread)
        ]
        
        for name, target in threads_config:
            thread = threading.Thread(target=target, name=f"Thread-{name}")
            thread.daemon = True
            thread.start()
            self.threads[name] = thread
            time.sleep(0.1)  # Pequeña pausa entre threads
        
        self.safe_print(f"\n✅ Nodo {self.node_name} iniciado con {len(self.threads)} threads", 'GREEN')
        
        # Modo interactivo
        self.interactive_mode()
        
        # Detener nodo
        self.stop()
        return True
    
    def stop(self):
        """
        Detiene el nodo y todos sus threads
        """
        self.safe_print("\n⏹ Deteniendo nodo...", 'YELLOW')
        
        # Enviar mensaje GOODBYE
        goodbye_msg = create_message('GOODBYE', f"{self.node_name} abandona la red", self.node_name)
        self.outgoing_queue.put(goodbye_msg)
        time.sleep(0.5)  # Dar tiempo para enviar
        
        # Señalar detención
        self.running = False
        
        # Esperar a que terminen los threads
        for name, thread in self.threads.items():
            thread.join(timeout=2)
            if thread.is_alive():
                self.safe_print(f"⚠️ Thread {name} no respondió", 'YELLOW')
        
        # Cerrar sockets
        if self.receiver_sock:
            try:
                mreq = struct.pack("4sl", socket.inet_aton(self.group), socket.INADDR_ANY)
                self.receiver_sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
            except:
                pass
            self.receiver_sock.close()
        
        if self.sender_sock:
            self.sender_sock.close()
        
        # Mostrar estadísticas finales
        self.show_status()
        
        self.safe_print("✅ Nodo detenido correctamente", 'GREEN')
        log_message(f"Nodo {self.node_name} detenido", 'CLOSE')


def main():
    """
    Función principal
    """
    print_colored("\n" + "="*60, 'CYAN')
    print_colored("   NODO MULTICAST CON CONCURRENCIA", 'CYAN')
    print_colored("   SISTEMAS DISTRIBUIDOS", 'CYAN')
    print_colored("="*60 + "\n", 'CYAN')
    
    # Verificar/crear carpeta de logs
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Mostrar información del sistema
    info = get_system_info()
    print_colored("📋 Información del Sistema:", 'YELLOW')
    print_colored(f"  • Hostname: {info['hostname']}", 'WHITE')
    print_colored(f"  • IP Local: {info['local_ip']}", 'WHITE')
    print_colored(f"  • Grupo Multicast: {info['multicast_group']}", 'WHITE')
    print_colored(f"  • Puerto: {info['port']}", 'WHITE')
    print_colored(f"  • TTL: {TTL}", 'WHITE')
    
    # Verificar nombre del nodo
    if NODE_NAME == "Nodo_TuNombre":
        print_colored("\n⚠️ ADVERTENCIA: No has configurado NODE_NAME en config.py", 'YELLOW')
        custom_name = input("Ingresa un nombre para este nodo (o Enter para usar default): ")
        if custom_name:
            node_name = f"Nodo_{custom_name}"
        else:
            node_name = f"Nodo_{info['hostname']}"
    else:
        node_name = NODE_NAME
    
    print_colored(f"\n🚀 Iniciando nodo: {node_name}", 'GREEN')
    
    # Crear y ejecutar nodo
    node = MulticastNode(node_name)
    
    try:
        node.start()
    except Exception as e:
        print_colored(f"\n❌ Error fatal: {e}", 'RED')
        log_message(f"Error fatal: {e}", 'ERROR')
    
    print_colored("\n👋 Gracias por usar el sistema multicast", 'CYAN')


if __name__ == "__main__":
    main()
