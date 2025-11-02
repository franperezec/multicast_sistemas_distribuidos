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
import argparse
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
        config_content = f"""# -*- coding: utf-8 -*-
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
    import sys
    # Configurar stdout para UTF-8 en Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
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
        with open(config_file, 'w', encoding='utf-8') as f:
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

        script_content = f"""# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar la configuración personalizada
import temp_config_{node_id} as config
sys.modules['config'] = config

from multicast_node import MulticastNode
import time
import random
import json
import os

def save_node_stats(node):
    # Guarda las estadísticas del nodo en un archivo
    stats_dir = 'logs/node_stats'
    if not os.path.exists(stats_dir):
        os.makedirs(stats_dir)
    
    stats_file = os.path.join(stats_dir, 'node_' + node.node_name + '_stats.json')
    stats_data = {{
        'node_name': node.node_name,
        'messages_sent': node.stats['messages_sent'],
        'messages_received': node.stats['messages_received'],
        'bytes_sent': node.stats['bytes_sent'],
        'bytes_received': node.stats['bytes_received'],
        'errors': node.stats['errors'],
        'timestamp': time.time()
    }}
    
    try:
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, indent=2)
    except:
        pass

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
        stats_save_counter = 0
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
            
            # Guardar estadísticas cada 3 iteraciones
            stats_save_counter += 1
            if stats_save_counter >= 3:
                save_node_stats(node)
                stats_save_counter = 0
                
    except KeyboardInterrupt:
        pass
    finally:
        # Guardar estadísticas finales
        save_node_stats(node)
        node.send_message("SimNode_{node_id} se desconecta", 'GOODBYE')
        node.running = False
        time.sleep(1)

if __name__ == "__main__":
    run_automated_node()
"""

        script_file = f"temp_node_{node_id}.py"
        with open(script_file, 'w', encoding='utf-8') as f:
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
            # Usar sys.executable para asegurar el mismo intérprete de Python
            python_exe = sys.executable

            # Crear archivo de log para este nodo
            log_file = f"logs/sim_node_{node_id}.log"

            # Abrir archivos de log para stdout y stderr
            stdout_file = open(log_file, 'w', encoding='utf-8')
            stderr_file = open(
                f"logs/sim_node_{node_id}_err.log", 'w', encoding='utf-8')

            # Lanzar proceso en segundo plano (sin consola nueva)
            process = subprocess.Popen(
                [python_exe, script_file],
                stdout=stdout_file,
                stderr=stderr_file,
                cwd=os.getcwd(),
                # No usar CREATE_NEW_CONSOLE - ejecutar en segundo plano
            )

            self.processes.append({
                'id': node_id,
                'process': process,
                'config': config_file,
                'script': script_file,
                'behavior': behavior,
                'stdout_file': stdout_file,
                'stderr_file': stderr_file
            })

            print_colored(
                f"✅ Nodo SimNode_{node_id} iniciado ({behavior})", 'GREEN')
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
                print_colored(
                    f"  • SimNode_{node_info['id']} detenido", 'YELLOW')
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

        # Cerrar archivos de log
        for node_info in self.processes:
            try:
                if 'stdout_file' in node_info:
                    node_info['stdout_file'].close()
                if 'stderr_file' in node_info:
                    node_info['stderr_file'].close()
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

            print_colored(
                f"SimNode_{node_info['id']}: {status} ({node_info['behavior']})", 'WHITE')

        print_colored(
            f"\nTotal: {len(self.processes)} nodos, {active} activos", 'MAGENTA')

    def run_simulation(self, num_nodes, duration=None):
        """
        Ejecuta una simulación con múltiples nodos
        """
        print_colored(
            f"\n🚀 Iniciando simulación con {num_nodes} nodos", 'CYAN')

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
                print_colored(
                    f"\n⏱️ Simulación ejecutándose por {duration} segundos...", 'CYAN')
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
    Función principal para ejecutar el simulador
    """
    parser = argparse.ArgumentParser(
        description="Simulador de Múltiples Nodos Multicast.")
    parser.add_argument("--test-option", type=int,
                        help="Número de la opción de prueba a ejecutar automáticamente.")
    args = parser.parse_args()

    simulator = MultiNodeSimulator()

    if args.test_option:
        option = args.test_option
        print_colored(
            f"\\n🚀 Ejecutando opción de prueba automática: {option}", 'CYAN')
    else:
        print_colored("\\n" + "="*60, 'CYAN')
        print_colored("   SIMULADOR DE MÚLTIPLES NODOS", 'CYAN')
        print_colored("="*60, 'CYAN')
        print("\\nOpciones de prueba:")
        print("  1. 2 nodos, 30 segundos, comportamiento normal")
        print("  2. 5 nodos, 60 segundos, comportamiento variado")
        print("  3. 10 nodos, 120 segundos, alta carga (chatty)")
        print("  4. 3 nodos, 180 segundos, solo pings y heartbeats")
        print("  5. Personalizado")

        try:
            option = int(input("\\nSeleccionar opción (1-5): "))
        except ValueError:
            print_colored("Opción no válida. Saliendo.", 'RED')
            return

    if option == 1:
        simulator.run_simulation(2, 30)
    elif option == 2:
        simulator.run_simulation(5, 60)
    elif option == 3:
        simulator.run_simulation(10, 120)
    elif option == 4:
        simulator.run_simulation(3, 180)
    elif option == 5:
        try:
            num_nodes = int(input("Número de nodos: "))
            duration = int(input("Duración en segundos: "))
            simulator.run_simulation(num_nodes, duration)
        except ValueError:
            print_colored("Valores no válidos.", 'RED')
    else:
        print_colored("Opción no válida.", 'RED')


if __name__ == "__main__":
    main()
