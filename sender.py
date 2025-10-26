"""
Módulo Emisor Multicast
Envía mensajes a todos los nodos en el grupo multicast
"""

import socket
import time
import sys
from config import *


class MulticastSender:
    def __init__(self, group=MULTICAST_GROUP, port=PORT):
        """
        Inicializa el emisor multicast
        """
        self.group = group
        self.port = port
        self.sock = None
        self.ttl = TTL

        # Estadísticas
        self.messages_sent = 0

    def setup_socket(self):
        """
        Configura el socket para enviar mensajes multicast
        """
        try:
            # Crear socket UDP
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

            # Configurar TTL (Time To Live) para multicast
            # TTL = 1: Red local
            # TTL = 2: Red local y siguiente salto
            self.sock.setsockopt(
                socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.ttl)

            # Opcional: Configurar interfaz de salida si hay múltiples interfaces
            if LOCAL_IP:
                self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF,
                                     socket.inet_aton(LOCAL_IP))

            print_colored(
                f"✓ Emisor configurado para {self.group}:{self.port}", 'GREEN')
            print_colored(f"  TTL configurado en: {self.ttl}", 'WHITE')
            log_message(
                f"Emisor iniciado para {self.group}:{self.port}", 'SETUP')

            return True

        except Exception as e:
            print_colored(f"✗ Error configurando emisor: {e}", 'RED')
            log_message(f"Error en emisor: {e}", 'ERROR')
            return False

    def send_message(self, msg_type, content):
        """
        Envía un mensaje al grupo multicast
        """
        if not self.sock:
            if not self.setup_socket():
                return False

        try:
            # Crear mensaje JSON
            message = create_message(msg_type, content, NODE_NAME)

            # Codificar y enviar
            data = message.encode('utf-8')
            self.sock.sendto(data, (self.group, self.port))

            self.messages_sent += 1

            # Feedback visual
            if msg_type == 'HELLO':
                print_colored(f"✓ Mensaje HELLO enviado", 'GREEN')
            elif msg_type == 'GOODBYE':
                print_colored(f"✓ Mensaje GOODBYE enviado", 'YELLOW')
            else:
                print_colored(f"✓ Mensaje enviado: {content[:50]}...", 'BLUE')

            # Log
            log_message(f"TX: {message}", 'SENT')

            return True

        except Exception as e:
            print_colored(f"✗ Error enviando mensaje: {e}", 'RED')
            log_message(f"Error enviando: {e}", 'ERROR')
            return False

    def send_hello(self):
        """
        Envía mensaje de HELLO al unirse a la red
        """
        info = get_system_info()
        content = f"Nodo {NODE_NAME} conectado desde {info['hostname']}"
        return self.send_message(MESSAGE_TYPES['HELLO'], content)

    def send_goodbye(self):
        """
        Envía mensaje de GOODBYE al salir de la red
        """
        content = f"Nodo {NODE_NAME} abandonando la red"
        return self.send_message(MESSAGE_TYPES['GOODBYE'], content)

    def send_ping(self):
        """
        Envía un PING para verificar conectividad
        """
        content = f"Ping desde {NODE_NAME}"
        return self.send_message(MESSAGE_TYPES['PING'], content)

    def interactive_sender(self):
        """
        Modo interactivo para enviar mensajes
        """
        if not self.setup_socket():
            return

        print_colored("\n" + "="*50, 'CYAN')
        print_colored("   EMISOR MULTICAST INTERACTIVO", 'CYAN')
        print_colored("="*50, 'CYAN')

        # Enviar mensaje HELLO al iniciar
        self.send_hello()

        print_colored("\nComandos disponibles:", 'YELLOW')
        print_colored("  • Escribir mensaje y Enter para enviar", 'WHITE')
        print_colored("  • /ping - Enviar ping", 'WHITE')
        print_colored("  • /stats - Ver estadísticas", 'WHITE')
        print_colored("  • /exit o /quit - Salir", 'WHITE')
        print_colored("  • /help - Ver esta ayuda\n", 'WHITE')

        try:
            while True:
                # Leer entrada del usuario
                message = input(
                    f"{COLORS['CYAN']}📤 {NODE_NAME} > {COLORS['RESET']}")

                if not message:
                    continue

                # Procesar comandos
                if message.lower() in ['/exit', '/quit', '/q']:
                    break

                elif message.lower() == '/ping':
                    self.send_ping()

                elif message.lower() == '/stats':
                    self.show_stats()

                elif message.lower() == '/help':
                    print_colored("Comandos:", 'YELLOW')
                    print_colored("  /ping - Enviar ping", 'WHITE')
                    print_colored("  /stats - Ver estadísticas", 'WHITE')
                    print_colored("  /exit - Salir", 'WHITE')

                else:
                    # Enviar mensaje normal
                    if message.startswith('/'):
                        print_colored(f"Comando desconocido: {message}", 'RED')
                    else:
                        self.send_message(MESSAGE_TYPES['MESSAGE'], message)

        except KeyboardInterrupt:
            print_colored("\n⏹ Interrumpido por usuario", 'YELLOW')

        finally:
            # Enviar mensaje GOODBYE antes de salir
            self.send_goodbye()
            time.sleep(0.5)  # Dar tiempo para que se envíe
            self.cleanup()

    def automated_sender(self, messages, interval=1):
        """
        Envía mensajes automáticamente para pruebas
        """
        if not self.setup_socket():
            return

        print_colored(f"\n🤖 Modo automático: {len(messages)} mensajes", 'CYAN')
        self.send_hello()
        time.sleep(1)

        try:
            for i, msg in enumerate(messages, 1):
                print_colored(
                    f"\n[{i}/{len(messages)}] Enviando: {msg}", 'YELLOW')
                self.send_message(MESSAGE_TYPES['MESSAGE'], msg)

                if i < len(messages):
                    print_colored(
                        f"   Esperando {interval} segundos...", 'WHITE')
                    time.sleep(interval)

        except KeyboardInterrupt:
            print_colored("\n⏹ Interrumpido", 'YELLOW')

        finally:
            self.send_goodbye()
            time.sleep(0.5)
            self.cleanup()

    def show_stats(self):
        """
        Muestra estadísticas de envío
        """
        print_colored(f"\n📊 Estadísticas del Emisor:", 'MAGENTA')
        print_colored(f"   Mensajes enviados: {self.messages_sent}", 'MAGENTA')
        print_colored(f"   Grupo Multicast: {self.group}", 'MAGENTA')
        print_colored(f"   Puerto: {self.port}", 'MAGENTA')
        print_colored(f"   TTL: {self.ttl}\n", 'MAGENTA')

    def cleanup(self):
        """
        Limpia recursos y cierra el socket
        """
        if self.sock:
            self.sock.close()
            print_colored("\n✓ Emisor cerrado correctamente", 'GREEN')

        self.show_stats()
        log_message(
            f"Emisor cerrado. Total mensajes: {self.messages_sent}", 'CLOSE')


def main():
    """
    Función principal para ejecutar el emisor standalone
    """
    print_colored("\n" + "="*50, 'CYAN')
    print_colored("   EMISOR MULTICAST - SISTEMAS DISTRIBUIDOS", 'CYAN')
    print_colored("="*50 + "\n", 'CYAN')

    # Mostrar información
    info = get_system_info()
    print_colored("Configuración:", 'YELLOW')
    print_colored(f"  • Nodo: {NODE_NAME}", 'WHITE')
    print_colored(f"  • Hostname: {info['hostname']}", 'WHITE')
    print_colored(f"  • Grupo Multicast: {MULTICAST_GROUP}:{PORT}", 'WHITE')

    # Preguntar modo de operación
    print_colored("\nModos de operación:", 'YELLOW')
    print_colored("  1. Interactivo (escribir mensajes manualmente)", 'WHITE')
    print_colored("  2. Automático (enviar mensajes de prueba)", 'WHITE')
    print_colored(
        "  3. Burst (enviar múltiples mensajes rápidamente)", 'WHITE')

    mode = input(
        f"\n{COLORS['CYAN']}Seleccionar modo (1/2/3): {COLORS['RESET']}")

    sender = MulticastSender()

    if mode == '1':
        sender.interactive_sender()

    elif mode == '2':
        messages = [
            "Mensaje de prueba 1",
            "Este es el mensaje número 2",
            "Probando multicast - mensaje 3",
            "Verificando concurrencia - mensaje 4",
            "Último mensaje de prueba - 5"
        ]
        sender.automated_sender(messages, interval=2)

    elif mode == '3':
        num = int(input("¿Cuántos mensajes enviar? "))
        messages = [f"Mensaje burst #{i}" for i in range(1, num+1)]
        sender.automated_sender(messages, interval=0.1)

    else:
        print_colored("Opción no válida", 'RED')


if __name__ == "__main__":
    main()
