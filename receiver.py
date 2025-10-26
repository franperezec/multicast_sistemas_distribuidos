"""
Módulo Receptor Multicast
Recibe mensajes de todos los nodos en el grupo multicast
"""

import socket
import struct
import sys
from config import *


class MulticastReceiver:
    def __init__(self, group=MULTICAST_GROUP, port=PORT):
        """
        Inicializa el receptor multicast
        """
        self.group = group
        self.port = port
        self.sock = None
        self.running = False

        # Estadísticas
        self.messages_received = 0
        self.nodes_detected = set()

    def setup_socket(self):
        """
        Configura el socket para recibir mensajes multicast
        """
        try:
            # Crear socket UDP
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

            # Permitir reutilización de dirección
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # En Windows puede ser necesario SO_REUSEPORT
            try:
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except:
                pass

            # Bind al puerto (escuchar en todas las interfaces)
            self.sock.bind(('', self.port))

            # Configurar el socket para unirse al grupo multicast
            mreq = struct.pack("4sl", socket.inet_aton(
                self.group), socket.INADDR_ANY)
            self.sock.setsockopt(
                socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            print_colored(
                f"✓ Receptor configurado en {self.group}:{self.port}", 'GREEN')
            log_message(
                f"Receptor iniciado en {self.group}:{self.port}", 'SETUP')

            return True

        except Exception as e:
            print_colored(f"✗ Error configurando receptor: {e}", 'RED')
            log_message(f"Error en receptor: {e}", 'ERROR')
            return False

    def receive_messages(self):
        """
        Bucle principal para recibir mensajes
        """
        if not self.setup_socket():
            return

        self.running = True
        print_colored(
            "\n📡 Esperando mensajes... (Ctrl+C para salir)\n", 'CYAN')

        try:
            while self.running:
                # Recibir datos
                data, address = self.sock.recvfrom(BUFFER_SIZE)

                # Decodificar mensaje
                try:
                    message_str = data.decode('utf-8')
                    message = parse_message(message_str)

                    if message:
                        self.process_message(message, address)
                    else:
                        print_colored(
                            f"Mensaje inválido de {address}", 'YELLOW')

                except UnicodeDecodeError:
                    print_colored(
                        f"Error decodificando mensaje de {address}", 'YELLOW')

        except KeyboardInterrupt:
            print_colored("\n⏹ Deteniendo receptor...", 'YELLOW')
        except Exception as e:
            print_colored(f"✗ Error en receptor: {e}", 'RED')
        finally:
            self.cleanup()

    def process_message(self, message, address):
        """
        Procesa un mensaje recibido
        """
        self.messages_received += 1
        node_id = message.get('node_id', 'Unknown')
        msg_type = message.get('type', 'MESSAGE')
        content = message.get('content', '')
        timestamp = message.get('timestamp', '')

        # Registrar nodo
        self.nodes_detected.add(node_id)

        # Formatear y mostrar mensaje
        if msg_type == 'HELLO':
            print_colored(
                f"🟢 [{timestamp}] {node_id} se unió a la red", 'GREEN')
            print_colored(f"   Dirección: {address[0]}:{address[1]}", 'GREEN')

        elif msg_type == 'GOODBYE':
            print_colored(f"🔴 [{timestamp}] {node_id} abandonó la red", 'RED')

        elif msg_type == 'MESSAGE':
            print_colored(f"💬 [{timestamp}] {node_id}: {content}", 'BLUE')
            print_colored(f"   Desde: {address[0]}:{address[1]}", 'CYAN')

        elif msg_type == 'PING':
            print_colored(f"🏓 [{timestamp}] Ping de {node_id}", 'YELLOW')

        else:
            print_colored(
                f"📨 [{timestamp}] {node_id} [{msg_type}]: {content}", 'WHITE')

        # Registrar en log
        log_message(f"RX from {address}: {message}", 'RECEIVED')

        # Mostrar estadísticas cada 10 mensajes
        if self.messages_received % 10 == 0:
            self.show_stats()

    def show_stats(self):
        """
        Muestra estadísticas de recepción
        """
        print_colored(f"\n📊 Estadísticas:", 'MAGENTA')
        print_colored(
            f"   Mensajes recibidos: {self.messages_received}", 'MAGENTA')
        print_colored(
            f"   Nodos detectados: {len(self.nodes_detected)}", 'MAGENTA')
        print_colored(
            f"   Nodos: {', '.join(self.nodes_detected)}\n", 'MAGENTA')

    def cleanup(self):
        """
        Limpia recursos y cierra el socket
        """
        self.running = False
        if self.sock:
            try:
                # Salir del grupo multicast
                mreq = struct.pack("4sl", socket.inet_aton(
                    self.group), socket.INADDR_ANY)
                self.sock.setsockopt(
                    socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
            except:
                pass

            self.sock.close()
            print_colored("\n✓ Receptor cerrado correctamente", 'GREEN')

        # Mostrar estadísticas finales
        self.show_stats()
        log_message(
            f"Receptor cerrado. Total mensajes: {self.messages_received}", 'CLOSE')


def main():
    """
    Función principal para ejecutar el receptor standalone
    """
    print_colored("\n" + "="*50, 'CYAN')
    print_colored("   RECEPTOR MULTICAST - SISTEMAS DISTRIBUIDOS", 'CYAN')
    print_colored("="*50 + "\n", 'CYAN')

    # Mostrar información del sistema
    info = get_system_info()
    print_colored("Información del Sistema:", 'YELLOW')
    print_colored(f"  • Hostname: {info['hostname']}", 'WHITE')
    print_colored(f"  • IP Local: {info['local_ip']}", 'WHITE')
    print_colored(f"  • Grupo Multicast: {info['multicast_group']}", 'WHITE')
    print_colored(f"  • Puerto: {info['port']}", 'WHITE')

    # Crear y ejecutar receptor
    receiver = MulticastReceiver()
    receiver.receive_messages()


if __name__ == "__main__":
    main()
