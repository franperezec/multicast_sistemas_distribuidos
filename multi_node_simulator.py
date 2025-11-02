"""
Simulador de Múltiples Nodos
Ejecuta varios nodos multicast automáticamente para pruebas
"""

import subprocess
import threading
import time
import os
import sys
import random
import signal
from config import *

class MultiNodeSimulator:
    def __init__(self):
        """
        Inicializa el simulador de múltiples nodos
        """
        self.processes = []
        self.running = False
        self.node_configs = []
        
    def create_node_config(self, node_id):
        """
        Crea una configuración temporal para un nodo
        """
        config_content = f"""
# Configuración temporal para nodo simulado
import socket
import json
from datetime import datetime

MULTICAST_GROUP = '{MULTICAST_GROUP}'
PORT = {PORT}
BUFFER_SIZE = 1024
TTL = 2
NODE_NAME = "SimNode_{node_id}"
LOCAL_IP = ''
LOG_FILE = 'logs/sim_node_{node_id}.txt'
ENABLE_LOGGING = True
DEBUG_MODE = False

MESSAGE_TYPES = {{
    'MESSAGE': 'MESSAGE',
    'HELLO': 'HELLO',
    'GOODBYE': 'GOODBYE',
    'PING': 'PING',
    'PONG': 'PONG',
    'HEARTBEAT': 'HEARTBEAT'
}}

COLORS = {{
    'RESET': '\\033[0m',
    'RED': '\\033[91m',
    'GREEN': '\\033[92m',
    'YELLOW': '\\033[93m',
    'BLUE': '\\033[94m',
    'MAGENTA': '\\033[95m',
    'CYAN': '\\033[96m',
    'WHITE': '\\033[97m',
}}

def create_message(msg_type, content, node_name=NODE_NAME):
    message = {{
        'node_id': node_name,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'type': msg_type,
        'content': content
    }}
    return json.dumps(message)

def parse_message(data):
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None

def log_message(message, direction='INFO'):
    if not ENABLE_LOGGING:
        return
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{{timestamp}}] [{{direction}}] {{message}}\\n"
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except:
        pass

def print_colored(message, color='WHITE'):
    if color in COLORS:
        print(f"{{COLORS[color]}}{{message}}{{COLORS['RESET']}}")
    else:
        print(message)

def get_system_info():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return {{
            'hostname': hostname,
            'local_ip': local_ip,
            'multicast_group': MULTICAST_GROUP,
            'port': PORT
        }}
    except:
        return {{
            'hostname': 'Unknown',
            'local_ip': '127.0.0.1',
            'multicast_group': MULTICAST_GROUP,
            'port': PORT
        }}
"""
        
        # Guardar configuración temporal
        config_file = f"temp_config_{node_id}.py"
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        self.node_configs.append(config_file)
        return config_file
    
    def create_automated_node_script(self, node_id, behavior='normal'):
        """
        Crea un script de nodo automatizado con comportamiento específico
        """
        if behavior == 'chatty':
            # Nodo que envía muchos mensajes
            messages = [
                f"Hola, soy el nodo {node_id}",
                "¿Alguien me escucha?",
                "Probando comunicación multicast",
                "Este es un mensaje automático",
                f"Nodo {node_id} activo y funcionando",
                "Verificando conectividad",
                "Mensaje de prueba",
                f"Saludos desde SimNode_{node_id}"
            ]
            interval = random.uniform(3, 8)
            
        elif behavior == 'quiet':
            # Nodo que envía pocos mensajes
            messages = [
                f"Nodo {node_id} presente",
                "Confirmando recepción"
            ]
            interval = random.uniform(15, 30)
            
        elif behavior == 'ping':
            # Nodo que solo envía pings
            messages = []
            interval = 10
            
        else:  # normal
            messages = [
                f"Nodo {node_id} iniciado",
                "Ejecutando pruebas",
                f"Mensaje desde SimNode_{node_id}",
                "Sistema operativo"
            ]
            interval = random.uniform(5, 15)
        
        script_content = f"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar la configuración personalizada
import temp_config_{node_id} as config
sys.modules['config'] = config

from multicast_node import MulticastNode
import time
import random

def run_automated_node():
    node = MulticastNode("SimNode_{node_id}")
    
    if not node.setup_sockets():
        print("Error configurando sockets")
        return
    
    node.running = True
    
    # Iniciar threads
    import threading
    threads = []
    threads.append(threading.Thread(target=node.receiver_thread))
    threads.append(threading.Thread(target=node.sender_thread))
    threads.append(threading.Thread(target=node.heartbeat_thread))
    
    for t in threads:
        t.daemon = True
        t.start()
    
    # Enviar HELLO
    node.send_message("SimNode_{node_id} se ha conectado", 'HELLO')
    
    messages = {messages}
    behavior = '{behavior}'
    
    try:
        message_count = 0
        while True:
            time.sleep({interval} + random.uniform(-2, 2))
            
            if behavior == 'ping':
                node.send_message("Ping automático", 'PING')
            elif messages:
                msg = messages[message_count % len(messages)]
                node.send_message(msg, 'MESSAGE')
                message_count += 1
            
            # Ocasionalmente enviar ping
            if random.random() < 0.1:
                node.send_message("Ping aleatorio", 'PING')
                
    except KeyboardInterrupt:
        pass
    finally:
        node.send_message("SimNode_{node_id} se desconecta", 'GOODBYE')
        node.running = False
        time.sleep(1)

if __name__ == "__main__":
    run_automated_node()
"""
        
        script_file = f"temp_node_{node_id}.py"
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        return script_file
    
    def start_node(self, node_id, behavior='normal'):
        """
        Inicia un nodo simulado
        """
        # Crear archivos temporales
        config_file = self.create_node_config(node_id)
        script_file = self.create_automated_node_script(node_id, behavior)
        
        # Ejecutar el nodo en un proceso separado
        try:
            if os.name == 'nt':  # Windows
                process = subprocess.Popen(
                    ['python', script_file],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:  # Linux/Mac
                process = subprocess.Popen(
                    ['python3', script_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            self.processes.append({
                'id': node_id,
                'process': process,
                'config': config_file,
                'script': script_file,
                'behavior': behavior
            })
            
            print_colored(f"✅ Nodo SimNode_{node_id} iniciado ({behavior})", 'GREEN')
            return True
            
        except Exception as e:
            print_colored(f"❌ Error iniciando nodo {node_id}: {e}", 'RED')
            return False
    
    def stop_all_nodes(self):
        """
        Detiene todos los nodos simulados
        """
        print_colored("\n⏹ Deteniendo todos los nodos...", 'YELLOW')
        
        for node_info in self.processes:
            try:
                node_info['process'].terminate()
                print_colored(f"  • SimNode_{node_info['id']} detenido", 'YELLOW')
            except:
                pass
        
        # Esperar un poco
        time.sleep(2)
        
        # Forzar terminación si es necesario
        for node_info in self.processes:
            try:
                if node_info['process'].poll() is None:
                    node_info['process'].kill()
            except:
                pass
        
        # Limpiar archivos temporales
        self.cleanup_temp_files()
    
    def cleanup_temp_files(self):
        """
        Elimina archivos temporales creados
        """
        print_colored("\n🧹 Limpiando archivos temporales...", 'YELLOW')
        
        for node_info in self.processes:
            # Eliminar archivo de configuración
            try:
                os.remove(node_info['config'])
            except:
                pass
            
            # Eliminar script
            try:
                os.remove(node_info['script'])
            except:
                pass
            
            # Eliminar .pyc si existe
            try:
                os.remove(node_info['config'] + 'c')
            except:
                pass
        
        # Limpiar archivos huérfanos
        for file in os.listdir('.'):
            if file.startswith('temp_config_') or file.startswith('temp_node_'):
                try:
                    os.remove(file)
                except:
                    pass
    
    def show_status(self):
        """
        Muestra el estado de los nodos simulados
        """
        print_colored("\n📊 ESTADO DE NODOS SIMULADOS", 'MAGENTA')
        print_colored("="*40, 'MAGENTA')
        
        active = 0
        for node_info in self.processes:
            if node_info['process'].poll() is None:
                status = "🟢 Activo"
                active += 1
            else:
                status = "🔴 Detenido"
            
            print_colored(f"SimNode_{node_info['id']}: {status} ({node_info['behavior']})", 'WHITE')
        
        print_colored(f"\nTotal: {len(self.processes)} nodos, {active} activos", 'MAGENTA')
    
    def run_simulation(self, num_nodes, duration=None):
        """
        Ejecuta una simulación con múltiples nodos
        """
        print_colored(f"\n🚀 Iniciando simulación con {num_nodes} nodos", 'CYAN')
        
        # Definir comportamientos de los nodos
        behaviors = []
        if num_nodes <= 3:
            behaviors = ['normal'] * num_nodes
        else:
            # Mezcla de comportamientos
            behaviors = (
                ['chatty'] * (num_nodes // 3) +
                ['normal'] * (num_nodes // 3) +
                ['quiet'] * (num_nodes // 3) +
                ['ping'] * (num_nodes - 3 * (num_nodes // 3))
            )
            random.shuffle(behaviors)
        
        # Iniciar nodos
        for i in range(num_nodes):
            self.start_node(i + 1, behaviors[i])
            time.sleep(0.5)  # Pequeña pausa entre inicios
        
        print_colored(f"\n✅ {num_nodes} nodos iniciados", 'GREEN')
        
        # Ejecutar simulación
        try:
            if duration:
                print_colored(f"\n⏱️ Simulación ejecutándose por {duration} segundos...", 'CYAN')
                print_colored("Presiona Ctrl+C para detener antes", 'WHITE')
                
                for remaining in range(duration, 0, -1):
                    if remaining % 10 == 0:
                        self.show_status()
                    time.sleep(1)
            else:
                print_colored("\n⏱️ Simulación en ejecución", 'CYAN')
                print_colored("Presiona Ctrl+C para detener", 'WHITE')
                
                while True:
                    time.sleep(10)
                    self.show_status()
                    
        except KeyboardInterrupt:
            print_colored("\n⏹ Simulación interrumpida por usuario", 'YELLOW')
        
        finally:
            self.stop_all_nodes()


def main():
    """
    Función principal
    """
    print_colored("\n" + "="*60, 'CYAN')
    print_colored("   SIMULADOR DE MÚLTIPLES NODOS", 'CYAN')
    print_colored("="*60 + "\n", 'CYAN')
    
    # Verificar carpeta de logs
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    print_colored("Este simulador creará múltiples nodos automáticamente", 'YELLOW')
    print_colored("Útil para probar el sistema con varios participantes\n", 'YELLOW')
    
    # Menú de opciones
    print_colored("Opciones de simulación:", 'WHITE')
    print_colored("  1. Simulación rápida (3 nodos, 30 segundos)", 'WHITE')
    print_colored("  2. Simulación media (5 nodos, 60 segundos)", 'WHITE')
    print_colored("  3. Simulación completa (10 nodos, 120 segundos)", 'WHITE')
    print_colored("  4. Simulación de estrés (20 nodos, sin límite)", 'WHITE')
    print_colored("  5. Personalizada", 'WHITE')
    
    choice = input(f"\n{COLORS['CYAN']}Seleccionar opción (1-5): {COLORS['RESET']}")
    
    simulator = MultiNodeSimulator()
    
    if choice == '1':
        simulator.run_simulation(3, 30)
    elif choice == '2':
        simulator.run_simulation(5, 60)
    elif choice == '3':
        simulator.run_simulation(10, 120)
    elif choice == '4':
        print_colored("\n⚠️ ADVERTENCIA: Esto creará 20 nodos", 'YELLOW')
        confirm = input("¿Continuar? (s/n): ")
        if confirm.lower() == 's':
            simulator.run_simulation(20, None)
    elif choice == '5':
        num = int(input("Número de nodos (1-50): "))
        duration = input("Duración en segundos (Enter para sin límite): ")
        duration = int(duration) if duration else None
        simulator.run_simulation(num, duration)
    else:
        print_colored("Opción no válida", 'RED')
    
    print_colored("\n✅ Simulación completada", 'GREEN')
    print_colored("Revisa los logs en la carpeta 'logs' para detalles", 'YELLOW')


if __name__ == "__main__":
    main()
