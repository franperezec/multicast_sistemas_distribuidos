"""
Verificador de Conectividad de Red
Prueba la conectividad con otros nodos en la red ZeroTier
"""

import socket
import struct
import threading
import time
import subprocess
import platform
import json
import os
import sys
from datetime import datetime
from config import *

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class ConnectivityTester:
    def __init__(self):
        """Inicializa el tester de conectividad"""
        self.test_results = {
            'local_tests': {},
            'network_tests': {},
            'multicast_tests': {},
            'peer_tests': {}
        }
        self.peers_discovered = set()
        
    def print_header(self, title):
        """Imprime encabezado formateado"""
        print("\n" + "="*60)
        print(f"   {title}")
        print("="*60)
    
    def test_1_local_config(self):
        """Test 1: Verificar configuración local"""
        self.print_header("TEST 1: CONFIGURACIÓN LOCAL")
        
        results = []
        
        # Verificar config.py
        print("\n🔍 Verificando configuración...")
        
        try:
            print(f"  • Grupo Multicast: {MULTICAST_GROUP}")
            print(f"  • Puerto: {PORT}")
            print(f"  • NODE_NAME: {NODE_NAME}")
            print(f"  • LOCAL_IP: {LOCAL_IP if LOCAL_IP else 'No configurada'}")
            
            if LOCAL_IP and LOCAL_IP.startswith('192.168.'):
                print_colored("  ✅ IP parece ser de ZeroTier", 'GREEN')
                results.append(True)
            elif not LOCAL_IP:
                print_colored("  ⚠️ LOCAL_IP no configurada", 'YELLOW')
                results.append(False)
            else:
                print_colored("  ⚠️ IP no parece ser de ZeroTier", 'YELLOW')
                results.append(False)
                
        except Exception as e:
            print_colored(f"  ❌ Error leyendo configuración: {e}", 'RED')
            results.append(False)
        
        # Verificar hostname y red local
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"\n  • Hostname: {hostname}")
            print(f"  • IP Local del sistema: {local_ip}")
            results.append(True)
        except Exception as e:
            print_colored(f"  ❌ Error obteniendo info de red: {e}", 'RED')
            results.append(False)
        
        self.test_results['local_tests']['config'] = all(results)
        return all(results)
    
    def test_2_zerotier_status(self):
        """Test 2: Verificar estado de ZeroTier"""
        self.print_header("TEST 2: ESTADO DE ZEROTIER")
        
        try:
            # Verificar servicio ZeroTier
            print("\n🔍 Verificando servicio ZeroTier...")
            
            if platform.system() == "Windows":
                result = subprocess.run(['zerotier-cli', 'info'], 
                                      capture_output=True, text=True, shell=True)
            else:
                result = subprocess.run(['sudo', 'zerotier-cli', 'info'], 
                                      capture_output=True, text=True)
            
            if result.returncode == 0:
                info = result.stdout.strip()
                print_colored(f"  ✅ ZeroTier activo: {info}", 'GREEN')
                
                # Listar redes
                if platform.system() == "Windows":
                    result = subprocess.run(['zerotier-cli', 'listnetworks'], 
                                          capture_output=True, text=True, shell=True)
                else:
                    result = subprocess.run(['sudo', 'zerotier-cli', 'listnetworks'], 
                                          capture_output=True, text=True)
                
                if result.returncode == 0:
                    networks = result.stdout.strip()
                    if networks:
                        print_colored("\n  📡 Redes ZeroTier:", 'CYAN')
                        lines = networks.split('\n')
                        for line in lines:
                            if line.strip():
                                print(f"    {line}")
                        
                        self.test_results['network_tests']['zerotier'] = True
                        return True
                    else:
                        print_colored("  ⚠️ No hay redes configuradas", 'YELLOW')
                        self.test_results['network_tests']['zerotier'] = False
                        return False
            else:
                print_colored("  ❌ ZeroTier no está activo", 'RED')
                self.test_results['network_tests']['zerotier'] = False
                return False
                
        except FileNotFoundError:
            print_colored("  ❌ ZeroTier no está instalado", 'RED')
            self.test_results['network_tests']['zerotier'] = False
            return False
        except Exception as e:
            print_colored(f"  ❌ Error: {e}", 'RED')
            self.test_results['network_tests']['zerotier'] = False
            return False
    
    def test_3_socket_binding(self):
        """Test 3: Verificar binding de sockets"""
        self.print_header("TEST 3: BINDING DE SOCKETS")
        
        results = []
        
        # Test socket UDP básico
        print("\n🔍 Probando socket UDP...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', PORT))
            sock.close()
            print_colored("  ✅ Socket UDP funciona", 'GREEN')
            results.append(True)
        except Exception as e:
            print_colored(f"  ❌ Error con socket UDP: {e}", 'RED')
            results.append(False)
        
        # Test socket multicast
        print("\n🔍 Probando socket multicast...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind
            sock.bind(('', PORT))
            
            # Unirse al grupo multicast
            mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            
            sock.close()
            print_colored("  ✅ Socket multicast funciona", 'GREEN')
            results.append(True)
        except Exception as e:
            print_colored(f"  ❌ Error con socket multicast: {e}", 'RED')
            results.append(False)
        
        # Test socket con IP específica si está configurada
        if LOCAL_IP:
            print(f"\n🔍 Probando socket con IP {LOCAL_IP}...")
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, 
                              socket.inet_aton(LOCAL_IP))
                sock.close()
                print_colored(f"  ✅ Socket funciona con IP {LOCAL_IP}", 'GREEN')
                results.append(True)
            except Exception as e:
                print_colored(f"  ❌ Error con IP específica: {e}", 'RED')
                results.append(False)
        
        self.test_results['local_tests']['sockets'] = all(results)
        return all(results)
    
    def test_4_multicast_loopback(self):
        """Test 4: Prueba de loopback multicast"""
        self.print_header("TEST 4: LOOPBACK MULTICAST")
        
        print("\n🔍 Enviando y recibiendo mensaje de prueba...")
        
        received = threading.Event()
        test_message = f"Test loopback desde {NODE_NAME} - {datetime.now()}"
        
        def receiver():
            """Thread receptor"""
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('', PORT))
                
                mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                
                sock.settimeout(5.0)
                
                data, addr = sock.recvfrom(BUFFER_SIZE)
                message = data.decode('utf-8')
                
                if test_message in message:
                    print_colored("  ✅ Mensaje recibido correctamente", 'GREEN')
                    received.set()
                
                sock.close()
            except socket.timeout:
                print_colored("  ⚠️ Timeout esperando mensaje", 'YELLOW')
            except Exception as e:
                print_colored(f"  ❌ Error en receptor: {e}", 'RED')
        
        # Iniciar receptor
        receiver_thread = threading.Thread(target=receiver)
        receiver_thread.daemon = True
        receiver_thread.start()
        
        # Esperar un poco para que el receptor esté listo
        time.sleep(1)
        
        # Enviar mensaje
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)
            
            message = create_message('TEST', test_message)
            sock.sendto(message.encode('utf-8'), (MULTICAST_GROUP, PORT))
            
            print_colored("  ✅ Mensaje enviado", 'GREEN')
            sock.close()
        except Exception as e:
            print_colored(f"  ❌ Error enviando: {e}", 'RED')
        
        # Esperar resultado
        success = received.wait(timeout=5)
        
        self.test_results['multicast_tests']['loopback'] = success
        
        if success:
            print_colored("\n  ✅ Loopback multicast funciona correctamente", 'GREEN')
        else:
            print_colored("\n  ❌ Loopback multicast falló", 'RED')
        
        return success
    
    def test_5_ping_peers(self):
        """Test 5: Hacer ping a peers en la red"""
        self.print_header("TEST 5: PING A PEERS")
        
        print("\n📡 Enviando ping multicast...")
        print("⏳ Esperando respuestas por 10 segundos...")
        
        responses = []
        
        def listen_for_pongs():
            """Escucha respuestas de ping"""
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('', PORT))
                
                mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                
                sock.settimeout(1.0)
                
                end_time = time.time() + 10
                
                while time.time() < end_time:
                    try:
                        data, addr = sock.recvfrom(BUFFER_SIZE)
                        message_str = data.decode('utf-8')
                        message = parse_message(message_str)
                        
                        if message and message['node_id'] != NODE_NAME:
                            msg_type = message.get('type', '')
                            if msg_type in ['PONG', 'MESSAGE', 'HELLO', 'PING']:
                                self.peers_discovered.add(message['node_id'])
                                responses.append({
                                    'node': message['node_id'],
                                    'type': msg_type,
                                    'address': addr[0]
                                })
                                print_colored(f"  ✅ Respuesta de {message['node_id']} desde {addr[0]}", 'GREEN')
                    except socket.timeout:
                        continue
                
                sock.close()
            except Exception as e:
                print_colored(f"  ❌ Error escuchando: {e}", 'RED')
        
        # Iniciar listener
        listener_thread = threading.Thread(target=listen_for_pongs)
        listener_thread.daemon = True
        listener_thread.start()
        
        # Enviar ping
        time.sleep(0.5)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)
            
            ping_msg = create_message('PING', f'Ping de conectividad desde {NODE_NAME}')
            sock.sendto(ping_msg.encode('utf-8'), (MULTICAST_GROUP, PORT))
            
            print_colored(f"  📤 Ping enviado a {MULTICAST_GROUP}:{PORT}", 'CYAN')
            sock.close()
        except Exception as e:
            print_colored(f"  ❌ Error enviando ping: {e}", 'RED')
        
        # Esperar respuestas
        listener_thread.join()
        
        # Resultados
        if responses:
            print_colored(f"\n  ✅ {len(responses)} respuestas recibidas", 'GREEN')
            print_colored(f"  👥 Peers descubiertos: {', '.join(self.peers_discovered)}", 'CYAN')
            self.test_results['peer_tests']['ping'] = True
            return True
        else:
            print_colored("\n  ⚠️ No se recibieron respuestas", 'YELLOW')
            print_colored("  Posibles causas:", 'YELLOW')
            print_colored("    • No hay otros nodos activos", 'WHITE')
            print_colored("    • Firewall bloqueando", 'WHITE')
            print_colored("    • Problemas de red", 'WHITE')
            self.test_results['peer_tests']['ping'] = False
            return False
    
    def test_6_zerotier_peers(self):
        """Test 6: Verificar peers de ZeroTier"""
        self.print_header("TEST 6: PEERS DE ZEROTIER")
        
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['zerotier-cli', 'listpeers'], 
                                      capture_output=True, text=True, shell=True)
            else:
                result = subprocess.run(['sudo', 'zerotier-cli', 'listpeers'], 
                                      capture_output=True, text=True)
            
            if result.returncode == 0:
                peers = result.stdout.strip()
                if peers:
                    lines = peers.split('\n')
                    peer_count = len(lines) - 1  # Menos el header
                    
                    print_colored(f"\n  ✅ {peer_count} peers detectados en ZeroTier", 'GREEN')
                    
                    # Mostrar algunos peers
                    print_colored("\n  📡 Primeros peers:", 'CYAN')
                    for i, line in enumerate(lines[:6]):  # Mostrar máx 5 peers
                        if i == 0:
                            print(f"    {line}")  # Header
                        else:
                            # Parsear info del peer
                            parts = line.split()
                            if len(parts) >= 5:
                                peer_id = parts[0][:10] + "..."
                                role = parts[2]
                                latency = parts[3]
                                print(f"    • {peer_id} - Rol: {role}, Latencia: {latency}")
                    
                    self.test_results['network_tests']['zerotier_peers'] = True
                    return True
                else:
                    print_colored("  ⚠️ No se detectaron peers", 'YELLOW')
                    self.test_results['network_tests']['zerotier_peers'] = False
                    return False
            else:
                print_colored("  ❌ Error obteniendo peers", 'RED')
                self.test_results['network_tests']['zerotier_peers'] = False
                return False
                
        except Exception as e:
            print_colored(f"  ❌ Error: {e}", 'RED')
            self.test_results['network_tests']['zerotier_peers'] = False
            return False
    
    def test_7_bandwidth_test(self):
        """Test 7: Prueba básica de ancho de banda"""
        self.print_header("TEST 7: PRUEBA DE ANCHO DE BANDA")
        
        print("\n📊 Enviando ráfaga de mensajes...")
        
        num_messages = 50
        message_size = 512  # bytes
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)
            
            # Crear mensaje de prueba
            test_data = "X" * message_size
            
            start_time = time.time()
            
            for i in range(num_messages):
                message = create_message('BANDWIDTH_TEST', f"{i:03d}:{test_data}")
                sock.sendto(message.encode('utf-8'), (MULTICAST_GROUP, PORT))
            
            elapsed = time.time() - start_time
            
            sock.close()
            
            # Calcular estadísticas
            messages_per_second = num_messages / elapsed
            bytes_sent = num_messages * (message_size + 100)  # +100 for JSON overhead
            bandwidth = bytes_sent / elapsed
            
            print_colored(f"\n  📊 Resultados:", 'CYAN')
            print(f"    • Mensajes enviados: {num_messages}")
            print(f"    • Tiempo total: {elapsed:.2f} segundos")
            print(f"    • Mensajes/segundo: {messages_per_second:.2f}")
            print(f"    • Ancho de banda: {bandwidth/1024:.2f} KB/s")
            
            if messages_per_second > 100:
                print_colored("  ✅ Excelente rendimiento", 'GREEN')
                self.test_results['network_tests']['bandwidth'] = 'excellent'
            elif messages_per_second > 50:
                print_colored("  ✅ Buen rendimiento", 'GREEN')
                self.test_results['network_tests']['bandwidth'] = 'good'
            else:
                print_colored("  ⚠️ Rendimiento mejorable", 'YELLOW')
                self.test_results['network_tests']['bandwidth'] = 'poor'
            
            return True
            
        except Exception as e:
            print_colored(f"  ❌ Error en prueba: {e}", 'RED')
            self.test_results['network_tests']['bandwidth'] = 'error'
            return False
    
    def generate_report(self):
        """Genera un reporte de conectividad"""
        self.print_header("REPORTE DE CONECTIVIDAD")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║          REPORTE DE CONECTIVIDAD DE RED                   ║
║                  {timestamp}                  ║
╚══════════════════════════════════════════════════════════╝

📋 CONFIGURACIÓN:
  • Nodo: {NODE_NAME}
  • Grupo Multicast: {MULTICAST_GROUP}
  • Puerto: {PORT}
  • IP Local: {LOCAL_IP if LOCAL_IP else 'No configurada'}

📊 RESULTADOS DE PRUEBAS:
"""
        
        # Tests locales
        if self.test_results['local_tests']:
            report += "\n  🖥️ Tests Locales:\n"
            for test, result in self.test_results['local_tests'].items():
                status = "✅" if result else "❌"
                report += f"    {status} {test}\n"
        
        # Tests de red
        if self.test_results['network_tests']:
            report += "\n  🌐 Tests de Red:\n"
            for test, result in self.test_results['network_tests'].items():
                if isinstance(result, bool):
                    status = "✅" if result else "❌"
                else:
                    status = "📊"
                report += f"    {status} {test}: {result}\n"
        
        # Tests multicast
        if self.test_results['multicast_tests']:
            report += "\n  📡 Tests Multicast:\n"
            for test, result in self.test_results['multicast_tests'].items():
                status = "✅" if result else "❌"
                report += f"    {status} {test}\n"
        
        # Tests de peers
        if self.test_results['peer_tests']:
            report += "\n  👥 Tests de Peers:\n"
            for test, result in self.test_results['peer_tests'].items():
                status = "✅" if result else "⚠️"
                report += f"    {status} {test}\n"
        
        # Peers descubiertos
        if self.peers_discovered:
            report += f"\n  🔍 Peers Descubiertos: {', '.join(self.peers_discovered)}\n"
        
        # Guardar reporte
        report_file = f"connectivity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(f"logs/{report_file}", 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(report)
            print_colored(f"\n✅ Reporte guardado en: logs/{report_file}", 'GREEN')
        except:
            print(report)
        
        return report
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas de conectividad"""
        print_colored("\n🚀 INICIANDO PRUEBAS DE CONECTIVIDAD", 'CYAN')
        print_colored("="*60, 'CYAN')
        
        tests = [
            ("Configuración Local", self.test_1_local_config),
            ("Estado ZeroTier", self.test_2_zerotier_status),
            ("Binding de Sockets", self.test_3_socket_binding),
            ("Loopback Multicast", self.test_4_multicast_loopback),
            ("Ping a Peers", self.test_5_ping_peers),
            ("Peers ZeroTier", self.test_6_zerotier_peers),
            ("Ancho de Banda", self.test_7_bandwidth_test)
        ]
        
        passed = 0
        failed = 0
        
        for name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print_colored(f"❌ Error en {name}: {e}", 'RED')
                failed += 1
            
            time.sleep(1)
        
        # Resumen
        print_colored("\n" + "="*60, 'MAGENTA')
        print_colored("   RESUMEN DE PRUEBAS", 'MAGENTA')
        print_colored("="*60, 'MAGENTA')
        print_colored(f"  ✅ Pruebas exitosas: {passed}", 'GREEN')
        print_colored(f"  ❌ Pruebas fallidas: {failed}", 'RED')
        
        if failed == 0:
            print_colored("\n🎉 ¡TODAS LAS PRUEBAS PASARON!", 'GREEN')
            print_colored("La red está lista para usar", 'GREEN')
        elif passed > failed:
            print_colored("\n⚠️ La red funciona parcialmente", 'YELLOW')
            print_colored("Revisa las pruebas fallidas", 'YELLOW')
        else:
            print_colored("\n❌ Hay problemas de conectividad", 'RED')
            print_colored("Revisa la configuración", 'RED')
        
        # Generar reporte
        self.generate_report()


def main():
    """Función principal"""
    print_colored("\n" + "="*60, 'CYAN')
    print_colored("   VERIFICADOR DE CONECTIVIDAD DE RED", 'CYAN')
    print_colored("="*60 + "\n", 'CYAN')
    
    # Verificar carpeta de logs
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    print("Este script verificará:")
    print("  • Configuración local")
    print("  • Estado de ZeroTier")
    print("  • Conectividad multicast")
    print("  • Comunicación con peers")
    print("  • Ancho de banda\n")
    
    print("Opciones:")
    print("  1. Ejecutar todas las pruebas")
    print("  2. Solo pruebas locales")
    print("  3. Solo pruebas de red")
    print("  4. Prueba rápida de ping")
    
    choice = input("\nSeleccionar opción (1-4): ")
    
    tester = ConnectivityTester()
    
    if choice == '1':
        tester.run_all_tests()
    elif choice == '2':
        tester.test_1_local_config()
        tester.test_3_socket_binding()
        tester.test_4_multicast_loopback()
    elif choice == '3':
        tester.test_2_zerotier_status()
        tester.test_5_ping_peers()
        tester.test_6_zerotier_peers()
    elif choice == '4':
        tester.test_5_ping_peers()
    else:
        print_colored("Opción no válida", 'RED')
    
    print_colored("\n✅ Verificación completada", 'GREEN')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n⏹ Verificación cancelada", 'YELLOW')
    except Exception as e:
        print_colored(f"\n❌ Error: {e}", 'RED')
