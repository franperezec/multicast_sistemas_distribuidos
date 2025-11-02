"""
Monitor de Red Multicast
Analiza y muestra estadísticas del tráfico multicast en tiempo real
"""

import socket
import struct
import threading
import time
import sys
import os
from datetime import datetime
from collections import defaultdict, deque
from config import *


class NetworkMonitor:
    def __init__(self):
        """
        Inicializa el monitor de red
        """
        self.running = False
        self.sock = None

        # Estadísticas
        self.stats = {
            'total_messages': 0,
            'total_bytes': 0,
            'messages_per_node': defaultdict(int),
            'bytes_per_node': defaultdict(int),
            'message_types': defaultdict(int),
            'nodes_seen': set(),
            'start_time': None,
            'errors': 0
        }

        # Historial para gráficos
        self.message_history = deque(maxlen=60)  # Últimos 60 segundos
        self.bandwidth_history = deque(maxlen=60)

        # Para cálculo de tasas
        self.last_message_count = 0
        self.last_byte_count = 0
        self.last_update_time = time.time()

        # Lock para thread-safety
        self.lock = threading.Lock()

    def setup_socket(self):
        """
        Configura el socket para monitorear
        """
        try:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            try:
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except:
                pass

            self.sock.bind(('', PORT))

            mreq = struct.pack("4sl", socket.inet_aton(
                MULTICAST_GROUP), socket.INADDR_ANY)
            self.sock.setsockopt(
                socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            self.sock.settimeout(1.0)

            print_colored(
                f"✓ Monitor configurado en {MULTICAST_GROUP}:{PORT}", 'GREEN')
            return True

        except Exception as e:
            print_colored(f"✗ Error configurando monitor: {e}", 'RED')
            return False

    def monitor_thread(self):
        """
        Thread principal de monitoreo
        """
        while self.running:
            try:
                data, address = self.sock.recvfrom(BUFFER_SIZE)

                # Procesar mensaje
                try:
                    message_str = data.decode('utf-8')
                    message = parse_message(message_str)

                    if message:
                        self.process_message(message, address, len(data))

                except UnicodeDecodeError:
                    with self.lock:
                        self.stats['errors'] += 1

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    with self.lock:
                        self.stats['errors'] += 1

    def process_message(self, message, address, size):
        """
        Procesa un mensaje capturado
        """
        with self.lock:
            # Actualizar estadísticas generales
            self.stats['total_messages'] += 1
            self.stats['total_bytes'] += size

            # Por nodo
            node_id = message.get('node_id', 'Unknown')
            self.stats['messages_per_node'][node_id] += 1
            self.stats['bytes_per_node'][node_id] += size
            self.stats['nodes_seen'].add(node_id)

            # Por tipo de mensaje
            msg_type = message.get('type', 'UNKNOWN')
            self.stats['message_types'][msg_type] += 1

    def update_rates_thread(self):
        """
        Thread para actualizar tasas de transferencia
        """
        while self.running:
            time.sleep(1)  # Actualizar cada segundo

            with self.lock:
                current_time = time.time()
                time_diff = current_time - self.last_update_time

                if time_diff > 0:
                    # Calcular mensajes por segundo
                    message_diff = self.stats['total_messages'] - \
                        self.last_message_count
                    messages_per_second = message_diff / time_diff
                    self.message_history.append(messages_per_second)

                    # Calcular bytes por segundo
                    byte_diff = self.stats['total_bytes'] - \
                        self.last_byte_count
                    bytes_per_second = byte_diff / time_diff
                    self.bandwidth_history.append(bytes_per_second)

                    # Actualizar referencias
                    self.last_message_count = self.stats['total_messages']
                    self.last_byte_count = self.stats['total_bytes']
                    self.last_update_time = current_time

    def display_thread(self):
        """
        Thread para mostrar estadísticas
        """
        while self.running:
            time.sleep(5)  # Actualizar display cada 5 segundos
            self.display_stats()

    def display_stats(self):
        """
        Muestra las estadísticas actuales
        """
        # Limpiar pantalla
        os.system('cls' if os.name == 'nt' else 'clear')

        with self.lock:
            # Calcular tiempo de ejecución
            if self.stats['start_time']:
                uptime = int(time.time() - self.stats['start_time'])
                hours = uptime // 3600
                minutes = (uptime % 3600) // 60
                seconds = uptime % 60
                uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                uptime_str = "00:00:00"

            # Calcular tasas actuales
            current_msg_rate = self.message_history[-1] if self.message_history else 0
            current_bw_rate = self.bandwidth_history[-1] if self.bandwidth_history else 0
            avg_msg_rate = sum(self.message_history) / \
                len(self.message_history) if self.message_history else 0
            avg_bw_rate = sum(self.bandwidth_history) / \
                len(self.bandwidth_history) if self.bandwidth_history else 0

            # Mostrar encabezado
            print(COLORS['CYAN'] + "="*70 + COLORS['RESET'])
            print(
                COLORS['CYAN'] + "   MONITOR DE RED MULTICAST - TIEMPO REAL" + COLORS['RESET'])
            print(COLORS['CYAN'] + "="*70 + COLORS['RESET'])

            # Información general
            print(
                f"\n{COLORS['YELLOW']}📊 ESTADÍSTICAS GENERALES{COLORS['RESET']}")
            print(f"   Tiempo activo: {uptime_str}")
            print(f"   Grupo Multicast: {MULTICAST_GROUP}:{PORT}")
            print(f"   Nodos detectados: {len(self.stats['nodes_seen'])}")
            print(f"   Total mensajes: {self.stats['total_messages']}")
            print(f"   Total bytes: {self.stats['total_bytes']:,}")
            print(f"   Errores: {self.stats['errors']}")

            # Tasas de transferencia
            print(
                f"\n{COLORS['YELLOW']}📈 TASAS DE TRANSFERENCIA{COLORS['RESET']}")
            print(f"   Mensajes/seg (actual): {current_msg_rate:.2f}")
            print(f"   Mensajes/seg (promedio): {avg_msg_rate:.2f}")
            print(f"   Ancho de banda (actual): {current_bw_rate:.2f} bytes/s")
            print(f"   Ancho de banda (promedio): {avg_bw_rate:.2f} bytes/s")

            # Top nodos por actividad
            if self.stats['messages_per_node']:
                print(
                    f"\n{COLORS['YELLOW']}👥 TOP NODOS POR ACTIVIDAD{COLORS['RESET']}")
                sorted_nodes = sorted(self.stats['messages_per_node'].items(),
                                      key=lambda x: x[1], reverse=True)[:5]
                for node, count in sorted_nodes:
                    percentage = (count / self.stats['total_messages']) * 100
                    bytes_sent = self.stats['bytes_per_node'][node]
                    print(
                        f"   {node}: {count} msgs ({percentage:.1f}%), {bytes_sent:,} bytes")

            # Distribución por tipo de mensaje
            if self.stats['message_types']:
                print(
                    f"\n{COLORS['YELLOW']}📨 TIPOS DE MENSAJES{COLORS['RESET']}")
                for msg_type, count in sorted(self.stats['message_types'].items(),
                                              key=lambda x: x[1], reverse=True):
                    percentage = (count / self.stats['total_messages']) * 100
                    bar_length = int(percentage / 2)
                    bar = "█" * bar_length
                    print(
                        f"   {msg_type:<12}: {bar} {count} ({percentage:.1f}%)")

            # Gráfico de actividad (últimos 20 segundos)
            if len(self.message_history) > 0:
                print(
                    f"\n{COLORS['YELLOW']}📉 ACTIVIDAD (msgs/seg - últimos 20 seg){COLORS['RESET']}")
                recent_history = list(self.message_history)[-20:]
                max_rate = max(recent_history) if recent_history else 1

                # Crear gráfico ASCII
                height = 5
                for h in range(height, 0, -1):
                    line = "   "
                    threshold = (h / height) * max_rate
                    for rate in recent_history:
                        if rate >= threshold:
                            line += "█"
                        else:
                            line += " "
                    print(line)
                print("   " + "-" * len(recent_history))
                print(f"   Max: {max_rate:.1f} msgs/seg")

            # Lista de nodos activos
            if self.stats['nodes_seen']:
                print(f"\n{COLORS['YELLOW']}🟢 NODOS ACTIVOS{COLORS['RESET']}")
                print(f"   {', '.join(sorted(self.stats['nodes_seen']))}")

            print(f"\n{COLORS['CYAN']}{'='*70}{COLORS['RESET']}")
            print(
                f"{COLORS['WHITE']}Presiona Ctrl+C para detener el monitor{COLORS['RESET']}")

    def save_report(self):
        """
        Guarda un reporte de las estadísticas
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/network_monitor_{timestamp}.txt"

        with self.lock:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("="*70 + "\n")
                    f.write("REPORTE DE MONITOR DE RED MULTICAST\n")
                    f.write(f"Fecha: {datetime.now()}\n")
                    f.write("="*70 + "\n\n")

                    # Información general
                    f.write("ESTADÍSTICAS GENERALES\n")
                    f.write("-"*30 + "\n")
                    f.write(
                        f"Duración del monitoreo: {int(time.time() - self.stats['start_time'])} segundos\n")
                    f.write(
                        f"Total de mensajes: {self.stats['total_messages']}\n")
                    f.write(f"Total de bytes: {self.stats['total_bytes']}\n")
                    f.write(
                        f"Nodos detectados: {len(self.stats['nodes_seen'])}\n")
                    f.write(f"Errores: {self.stats['errors']}\n\n")

                    # Nodos
                    f.write("ACTIVIDAD POR NODO\n")
                    f.write("-"*30 + "\n")
                    for node, count in sorted(self.stats['messages_per_node'].items()):
                        bytes_sent = self.stats['bytes_per_node'][node]
                        f.write(
                            f"{node}: {count} mensajes, {bytes_sent} bytes\n")

                    f.write("\n")

                    # Tipos de mensaje
                    f.write("TIPOS DE MENSAJES\n")
                    f.write("-"*30 + "\n")
                    for msg_type, count in sorted(self.stats['message_types'].items()):
                        f.write(f"{msg_type}: {count}\n")

                    f.write("\n" + "="*70 + "\n")

                print_colored(f"\n✅ Reporte guardado en: {filename}", 'GREEN')

            except Exception as e:
                print_colored(f"\n❌ Error guardando reporte: {e}", 'RED')

    def start(self, non_interactive=False):
        """
        Inicia el monitor
        """
        if not self.setup_socket():
            return False

        self.running = True
        self.stats['start_time'] = time.time()

        # Iniciar threads
        threads = [
            threading.Thread(target=self.monitor_thread, name="Monitor"),
            threading.Thread(target=self.update_rates_thread,
                             name="RateUpdater"),
        ]

        if not non_interactive:
            threads.append(threading.Thread(
                target=self.display_thread, name="Display"))

        for thread in threads:
            thread.daemon = True
            thread.start()

        print_colored(
            "\n✅ Monitor iniciado. Presiona Ctrl+C para detener.\n", 'GREEN')

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print_colored("\n\n⏹ Deteniendo monitor...", 'YELLOW')
            self.stop()

        return True

    def stop(self):
        """
        Detiene el monitor
        """
        self.running = False

        # Guardar reporte final
        self.save_report()

        # Cerrar socket
        if self.sock:
            try:
                mreq = struct.pack("4sl", socket.inet_aton(
                    MULTICAST_GROUP), socket.INADDR_ANY)
                self.sock.setsockopt(
                    socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
            except:
                pass
            self.sock.close()

        # Mostrar resumen final
        with self.lock:
            print_colored("\n📊 RESUMEN FINAL", 'MAGENTA')
            print_colored(
                f"   Total mensajes: {self.stats['total_messages']}", 'WHITE')
            print_colored(
                f"   Total bytes: {self.stats['total_bytes']:,}", 'WHITE')
            print_colored(
                f"   Nodos detectados: {len(self.stats['nodes_seen'])}", 'WHITE')

            if self.stats['total_messages'] > 0:
                avg_msg_size = self.stats['total_bytes'] / \
                    self.stats['total_messages']
                print_colored(
                    f"   Tamaño promedio mensaje: {avg_msg_size:.2f} bytes", 'WHITE')

        print_colored("\n✅ Monitor detenido correctamente", 'GREEN')


def main(non_interactive=False):
    """
    Función principal
    """
    monitor = NetworkMonitor()

    if not monitor.start(non_interactive):
        return

    try:
        # Esperar mientras el monitor esté corriendo
        while monitor.running:
            # En modo no interactivo, comprobar archivo de señal
            if non_interactive and os.path.exists('logs/stop_monitor.signal'):
                print_colored("\\n⏹ Señal de detención recibida", 'YELLOW')
                break
            time.sleep(1)

    except KeyboardInterrupt:
        print_colored("\\n\\n⏹ Deteniendo monitor...", 'YELLOW')

    finally:
        monitor.stop()


if __name__ == "__main__":
    # Asegurarse de que los logs existen
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Comprobar si se ejecuta en modo no interactivo
    non_interactive = "--non-interactive" in sys.argv
    main(non_interactive)
