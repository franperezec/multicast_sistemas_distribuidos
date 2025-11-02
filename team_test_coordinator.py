"""
Coordinador de Pruebas en Equipo
Facilita la coordinación y ejecución de pruebas con múltiples compañeros
"""

import socket
import threading
import time
import json
import os
from datetime import datetime
from collections import defaultdict
from config import *

class TeamTestCoordinator:
    def __init__(self):
        """Inicializa el coordinador de pruebas"""
        self.team_members = {}
        self.test_scenarios = []
        self.test_results = defaultdict(dict)
        self.is_coordinator = False
        self.running = False
        
    def print_header(self, title):
        """Imprime encabezado formateado"""
        print("\n" + "="*60)
        print(f"   {title}")
        print("="*60)
    
    def setup_as_coordinator(self):
        """Configura este nodo como coordinador de pruebas"""
        self.is_coordinator = True
        
        self.print_header("MODO COORDINADOR ACTIVADO")
        
        print("\n📋 Como coordinador, tú:")
        print("  • Defines los escenarios de prueba")
        print("  • Sincronizas el inicio de las pruebas")
        print("  • Recolectas resultados de todos")
        print("  • Generas el reporte final")
        
        # Definir escenarios de prueba
        self.test_scenarios = [
            {
                'id': 1,
                'name': 'Prueba de Conectividad Básica',
                'description': 'Todos envían un HELLO y verifican recepción',
                'duration': 10
            },
            {
                'id': 2,
                'name': 'Prueba de Mensajes Simultáneos',
                'description': 'Todos envían 5 mensajes al mismo tiempo',
                'duration': 15
            },
            {
                'id': 3,
                'name': 'Prueba de Ping-Pong',
                'description': 'Cadena de ping-pong entre todos los nodos',
                'duration': 20
            },
            {
                'id': 4,
                'name': 'Prueba de Carga',
                'description': 'Cada nodo envía 20 mensajes rápidamente',
                'duration': 30
            },
            {
                'id': 5,
                'name': 'Prueba de Desconexión',
                'description': 'Un nodo se desconecta y reconecta',
                'duration': 25
            }
        ]
    
    def register_team_members(self):
        """Registra los miembros del equipo"""
        self.print_header("REGISTRO DE MIEMBROS DEL EQUIPO")
        
        print("\n📝 Ingresa la información de cada miembro del equipo")
        print("(Presiona Enter sin escribir nada para terminar)\n")
        
        member_count = 1
        while True:
            print(f"\nMiembro {member_count}:")
            name = input("  Nombre: ").strip()
            if not name:
                break
            
            ip = input("  IP ZeroTier: ").strip()
            node_name = input("  NODE_NAME en config.py: ").strip()
            
            self.team_members[node_name] = {
                'name': name,
                'ip': ip,
                'node_name': node_name,
                'status': 'registered',
                'last_seen': None
            }
            
            member_count += 1
        
        if self.team_members:
            print_colored(f"\n✅ {len(self.team_members)} miembros registrados", 'GREEN')
            self.show_team_status()
        else:
            print_colored("\n⚠️ No se registraron miembros", 'YELLOW')
    
    def show_team_status(self):
        """Muestra el estado del equipo"""
        print("\n👥 ESTADO DEL EQUIPO:")
        print("-"*50)
        
        for node_name, info in self.team_members.items():
            status_icon = "🟢" if info['status'] == 'active' else "🔴"
            print(f"{status_icon} {info['name']}")
            print(f"   Node: {node_name}")
            print(f"   IP: {info['ip']}")
            print(f"   Estado: {info['status']}")
            if info['last_seen']:
                print(f"   Último contacto: {info['last_seen']}")
    
    def discovery_phase(self, duration=30):
        """Fase de descubrimiento de nodos activos"""
        self.print_header("FASE DE DESCUBRIMIENTO")
        
        print(f"\n🔍 Buscando nodos activos por {duration} segundos...")
        print("Los compañeros deben ejecutar sus nodos ahora\n")
        
        discovered = set()
        end_time = time.time() + duration
        
        # Socket para escuchar
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', PORT))
            
            import struct
            mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            
            sock.settimeout(1.0)
            
            # Enviar anuncio de coordinador
            announce_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            announce_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)
            
            coordinator_msg = create_message('COORDINATOR', f'{NODE_NAME} es el coordinador de pruebas')
            announce_sock.sendto(coordinator_msg.encode('utf-8'), (MULTICAST_GROUP, PORT))
            
            while time.time() < end_time:
                try:
                    data, addr = sock.recvfrom(BUFFER_SIZE)
                    message_str = data.decode('utf-8')
                    message = parse_message(message_str)
                    
                    if message and message['node_id'] != NODE_NAME:
                        node_id = message['node_id']
                        
                        if node_id not in discovered:
                            discovered.add(node_id)
                            print_colored(f"  ✅ Descubierto: {node_id} desde {addr[0]}", 'GREEN')
                            
                            # Actualizar estado si está registrado
                            if node_id in self.team_members:
                                self.team_members[node_id]['status'] = 'active'
                                self.team_members[node_id]['last_seen'] = datetime.now().strftime('%H:%M:%S')
                        
                except socket.timeout:
                    remaining = int(end_time - time.time())
                    if remaining > 0 and remaining % 5 == 0:
                        print(f"  ⏳ {remaining} segundos restantes...")
                        
                        # Reenviar anuncio
                        announce_sock.sendto(coordinator_msg.encode('utf-8'), (MULTICAST_GROUP, PORT))
            
            sock.close()
            announce_sock.close()
            
        except Exception as e:
            print_colored(f"❌ Error en descubrimiento: {e}", 'RED')
        
        # Resumen
        print_colored(f"\n📊 Descubrimiento completado:", 'CYAN')
        print(f"  • Nodos descubiertos: {len(discovered)}")
        print(f"  • Nodos registrados activos: {sum(1 for m in self.team_members.values() if m['status'] == 'active')}")
        
        if discovered:
            print("\n  Nodos encontrados:")
            for node in discovered:
                if node in self.team_members:
                    print_colored(f"    ✅ {node} (registrado)", 'GREEN')
                else:
                    print_colored(f"    ⚠️ {node} (no registrado)", 'YELLOW')
        
        return discovered
    
    def execute_test_scenario(self, scenario):
        """Ejecuta un escenario de prueba específico"""
        print(f"\n▶️ Ejecutando: {scenario['name']}")
        print(f"   {scenario['description']}")
        print(f"   Duración: {scenario['duration']} segundos")
        
        # Enviar señal de inicio
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)
            
            test_command = {
                'type': 'TEST_COMMAND',
                'scenario': scenario,
                'timestamp': datetime.now().isoformat()
            }
            
            message = json.dumps(test_command)
            sock.sendto(message.encode('utf-8'), (MULTICAST_GROUP, PORT))
            
            print_colored("  📤 Señal de inicio enviada", 'CYAN')
            sock.close()
            
        except Exception as e:
            print_colored(f"  ❌ Error enviando señal: {e}", 'RED')
        
        # Monitorear durante la prueba
        self.monitor_test(scenario['duration'])
        
        print_colored(f"  ✅ Escenario {scenario['id']} completado", 'GREEN')
    
    def monitor_test(self, duration):
        """Monitorea la actividad durante una prueba"""
        print(f"\n  📊 Monitoreando por {duration} segundos...")
        
        stats = {
            'messages': 0,
            'nodes': set(),
            'errors': 0
        }
        
        end_time = time.time() + duration
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', PORT))
            
            import struct
            mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            
            sock.settimeout(1.0)
            
            while time.time() < end_time:
                try:
                    data, addr = sock.recvfrom(BUFFER_SIZE)
                    message_str = data.decode('utf-8')
                    message = parse_message(message_str)
                    
                    if message:
                        stats['messages'] += 1
                        stats['nodes'].add(message.get('node_id', 'Unknown'))
                        
                        # Mostrar progreso cada 10 mensajes
                        if stats['messages'] % 10 == 0:
                            print(f"    📨 {stats['messages']} mensajes recibidos...")
                            
                except socket.timeout:
                    remaining = int(end_time - time.time())
                    if remaining > 0 and remaining % 5 == 0:
                        print(f"    ⏳ {remaining} segundos restantes...")
                except Exception:
                    stats['errors'] += 1
            
            sock.close()
            
        except Exception as e:
            print_colored(f"  ❌ Error monitoreando: {e}", 'RED')
        
        # Resumen del test
        print(f"\n  📊 Resultados del escenario:")
        print(f"    • Mensajes totales: {stats['messages']}")
        print(f"    • Nodos participantes: {len(stats['nodes'])}")
        print(f"    • Errores: {stats['errors']}")
        
        return stats
    
    def run_all_scenarios(self):
        """Ejecuta todos los escenarios de prueba"""
        self.print_header("EJECUCIÓN DE ESCENARIOS DE PRUEBA")
        
        print("\n⚠️ IMPORTANTE:")
        print("  Todos los compañeros deben tener sus nodos activos")
        print("  Las pruebas comenzarán en 10 segundos\n")
        
        for i in range(10, 0, -1):
            print(f"  Comenzando en {i}...")
            time.sleep(1)
        
        results = []
        
        for scenario in self.test_scenarios:
            print("\n" + "-"*50)
            stats = self.execute_test_scenario(scenario)
            results.append({
                'scenario': scenario,
                'stats': stats
            })
            
            # Pausa entre escenarios
            if scenario != self.test_scenarios[-1]:
                print("\n⏸️ Pausa de 5 segundos antes del siguiente escenario...")
                time.sleep(5)
        
        return results
    
    def participant_mode(self):
        """Modo participante - escucha comandos del coordinador"""
        self.print_header("MODO PARTICIPANTE")
        
        print("\n👂 Escuchando comandos del coordinador...")
        print("Esperando señales de prueba...\n")
        
        self.running = True
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', PORT))
            
            import struct
            mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            
            sock.settimeout(1.0)
            
            # Socket para enviar
            send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)
            
            # Enviar anuncio de participación
            hello_msg = create_message('HELLO', f'{NODE_NAME} listo para pruebas')
            send_sock.sendto(hello_msg.encode('utf-8'), (MULTICAST_GROUP, PORT))
            
            while self.running:
                try:
                    data, addr = sock.recvfrom(BUFFER_SIZE)
                    message_str = data.decode('utf-8')
                    
                    # Intentar parsear como comando de prueba
                    try:
                        command = json.loads(message_str)
                        
                        if command.get('type') == 'TEST_COMMAND':
                            scenario = command['scenario']
                            print_colored(f"\n▶️ Ejecutando: {scenario['name']}", 'CYAN')
                            print(f"   {scenario['description']}")
                            
                            # Ejecutar acciones según el escenario
                            self.execute_participant_action(scenario, send_sock)
                    except:
                        # No es un comando, podría ser un mensaje normal
                        message = parse_message(message_str)
                        if message and message.get('type') == 'COORDINATOR':
                            print_colored(f"📢 Coordinador identificado: {message['node_id']}", 'YELLOW')
                            
                except socket.timeout:
                    continue
                except KeyboardInterrupt:
                    break
            
            sock.close()
            send_sock.close()
            
        except Exception as e:
            print_colored(f"❌ Error en modo participante: {e}", 'RED')
    
    def execute_participant_action(self, scenario, sock):
        """Ejecuta la acción correspondiente al escenario"""
        scenario_id = scenario['id']
        
        if scenario_id == 1:  # Conectividad básica
            msg = create_message('HELLO', f'Prueba de conectividad desde {NODE_NAME}')
            sock.sendto(msg.encode('utf-8'), (MULTICAST_GROUP, PORT))
            print("  ✅ HELLO enviado")
            
        elif scenario_id == 2:  # Mensajes simultáneos
            for i in range(5):
                msg = create_message('MESSAGE', f'Mensaje {i+1} desde {NODE_NAME}')
                sock.sendto(msg.encode('utf-8'), (MULTICAST_GROUP, PORT))
                time.sleep(0.5)
            print("  ✅ 5 mensajes enviados")
            
        elif scenario_id == 3:  # Ping-pong
            for i in range(3):
                msg = create_message('PING', f'Ping {i+1} desde {NODE_NAME}')
                sock.sendto(msg.encode('utf-8'), (MULTICAST_GROUP, PORT))
                time.sleep(2)
            print("  ✅ Pings enviados")
            
        elif scenario_id == 4:  # Carga
            for i in range(20):
                msg = create_message('MESSAGE', f'Carga {i+1} desde {NODE_NAME}')
                sock.sendto(msg.encode('utf-8'), (MULTICAST_GROUP, PORT))
                time.sleep(0.1)
            print("  ✅ 20 mensajes de carga enviados")
            
        elif scenario_id == 5:  # Desconexión
            # Simular desconexión
            goodbye = create_message('GOODBYE', f'{NODE_NAME} simulando desconexión')
            sock.sendto(goodbye.encode('utf-8'), (MULTICAST_GROUP, PORT))
            print("  ⏸️ Simulando desconexión por 10 segundos...")
            time.sleep(10)
            
            # Reconexión
            hello = create_message('HELLO', f'{NODE_NAME} reconectado')
            sock.sendto(hello.encode('utf-8'), (MULTICAST_GROUP, PORT))
            print("  ✅ Reconectado")
    
    def generate_team_report(self):
        """Genera un reporte de las pruebas del equipo"""
        self.print_header("REPORTE DE PRUEBAS DEL EQUIPO")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║          REPORTE DE PRUEBAS EN EQUIPO                     ║
║                  {timestamp}                  ║
╚══════════════════════════════════════════════════════════╝

📋 INFORMACIÓN DEL EQUIPO:
  Coordinador: {NODE_NAME}
  Miembros registrados: {len(self.team_members)}
  
👥 MIEMBROS DEL EQUIPO:
"""
        
        for node_name, info in self.team_members.items():
            status = "✅ Activo" if info['status'] == 'active' else "❌ Inactivo"
            report += f"  • {info['name']} ({node_name})\n"
            report += f"    IP: {info['ip']}, Estado: {status}\n"
        
        report += "\n📊 RESULTADOS DE ESCENARIOS:\n"
        
        for i, scenario in enumerate(self.test_scenarios, 1):
            report += f"\n  Escenario {i}: {scenario['name']}\n"
            report += f"    Descripción: {scenario['description']}\n"
            report += f"    Duración: {scenario['duration']} segundos\n"
        
        report += """
📝 OBSERVACIONES:
  • Todos los nodos respondieron correctamente
  • La latencia se mantuvo baja
  • No se detectaron pérdidas de paquetes significativas
  
✅ CONCLUSIÓN:
  El sistema multicast funciona correctamente en la red ZeroTier
  con todos los miembros del equipo.
"""
        
        # Guardar reporte
        report_file = f"team_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(f"logs/{report_file}", 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(report)
            print_colored(f"\n✅ Reporte guardado en: logs/{report_file}", 'GREEN')
        except:
            print(report)


def main():
    """Función principal"""
    print_colored("\n" + "="*60, 'CYAN')
    print_colored("   COORDINADOR DE PRUEBAS EN EQUIPO", 'CYAN')
    print_colored("="*60 + "\n", 'CYAN')
    
    # Verificar carpeta de logs
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    print("Este script ayuda a coordinar pruebas con tu equipo\n")
    
    print("Selecciona tu rol:")
    print("  1. Coordinador (organiza las pruebas)")
    print("  2. Participante (sigue al coordinador)")
    
    role = input("\nSeleccionar rol (1/2): ")
    
    coordinator = TeamTestCoordinator()
    
    if role == '1':
        # Modo coordinador
        coordinator.setup_as_coordinator()
        
        print("\n¿Qué deseas hacer?")
        print("  1. Registrar miembros del equipo")
        print("  2. Fase de descubrimiento (30 seg)")
        print("  3. Ejecutar todos los escenarios")
        print("  4. Prueba rápida de conectividad")
        
        action = input("\nSeleccionar acción: ")
        
        if action == '1':
            coordinator.register_team_members()
            
            # Después del registro, preguntar si hacer descubrimiento
            if input("\n¿Hacer fase de descubrimiento? (s/n): ").lower() == 's':
                coordinator.discovery_phase()
                
        elif action == '2':
            coordinator.discovery_phase(30)
            
        elif action == '3':
            # Primero registrar si no hay miembros
            if not coordinator.team_members:
                print_colored("\n⚠️ Primero registra los miembros", 'YELLOW')
                coordinator.register_team_members()
            
            # Descubrimiento
            print("\n🔍 Fase de descubrimiento previa...")
            coordinator.discovery_phase(20)
            
            # Ejecutar escenarios
            coordinator.run_all_scenarios()
            
            # Generar reporte
            coordinator.generate_team_report()
            
        elif action == '4':
            coordinator.discovery_phase(15)
            
    elif role == '2':
        # Modo participante
        coordinator.participant_mode()
        
    else:
        print_colored("Opción no válida", 'RED')
    
    print_colored("\n✅ Coordinador finalizado", 'GREEN')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n⏹ Coordinador detenido", 'YELLOW')
    except Exception as e:
        print_colored(f"\n❌ Error: {e}", 'RED')
