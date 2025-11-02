"""
Test de Dos Nodos Simulados
Simula dos nodos diferentes comunicandose
"""

import socket
import json
import threading
import time
from datetime import datetime

MULTICAST_GROUP = '224.1.1.1'
PORT = 5007
LOCAL_IP = '192.168.194.33'

class SimulatedNode:
    def __init__(self, node_name):
        self.node_name = node_name
        self.messages_received = []
        self.running = True

    def create_message(self, msg_type, content):
        return json.dumps({
            'node_id': self.node_name,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': msg_type,
            'content': content,
            'ip': LOCAL_IP
        })

    def receiver_thread(self):
        """Escucha mensajes"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Habilitar SO_REUSEPORT si esta disponible (permite multiples procesos)
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except:
                pass

            sock.bind(('', PORT))

            import struct
            mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            sock.settimeout(1.0)

            print(f"[{self.node_name}] Receptor iniciado")

            while self.running:
                try:
                    data, address = sock.recvfrom(1024)
                    message_str = data.decode('utf-8')
                    message = json.loads(message_str)

                    # Solo mostrar mensajes de OTROS nodos
                    if message.get('node_id') != self.node_name:
                        print(f"\n[{self.node_name}] RECIBIO:")
                        print(f"  De: {message.get('node_id')}")
                        print(f"  Tipo: {message.get('type')}")
                        print(f"  Contenido: {message.get('content')}")
                        self.messages_received.append(message)

                except socket.timeout:
                    continue
                except:
                    pass

            sock.close()
        except Exception as e:
            print(f"[{self.node_name}] Error en receptor: {e}")

    def sender_thread(self, messages_to_send):
        """Envia mensajes"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

            time.sleep(1)  # Esperar que el receptor este listo

            for i, content in enumerate(messages_to_send):
                message = self.create_message('MESSAGE', content)
                sock.sendto(message.encode('utf-8'), (MULTICAST_GROUP, PORT))
                print(f"[{self.node_name}] ENVIO: {content}")
                time.sleep(2)

            sock.close()
        except Exception as e:
            print(f"[{self.node_name}] Error en emisor: {e}")

    def start(self, messages_to_send):
        """Inicia el nodo"""
        receiver = threading.Thread(target=self.receiver_thread)
        receiver.daemon = True
        receiver.start()

        sender = threading.Thread(target=self.sender_thread, args=(messages_to_send,))
        sender.daemon = True
        sender.start()

        return receiver, sender

def main():
    print("="*60)
    print("   TEST DE DOS NODOS COMUNICANDOSE")
    print("="*60)
    print("\nSimulando Nodo_A y Nodo_B en la misma maquina\n")

    # Crear dos nodos
    nodo_a = SimulatedNode("Nodo_A")
    nodo_b = SimulatedNode("Nodo_B")

    # Mensajes que enviara cada nodo
    mensajes_a = [
        "Hola, soy Nodo_A",
        "Mensaje 1 desde A",
        "Mensaje 2 desde A"
    ]

    mensajes_b = [
        "Hola, soy Nodo_B",
        "Mensaje 1 desde B",
        "Mensaje 2 desde B"
    ]

    # Iniciar ambos nodos
    print("Iniciando nodos...")
    threads_a = nodo_a.start(mensajes_a)
    threads_b = nodo_b.start(mensajes_b)

    # Esperar a que terminen de enviar
    threads_a[1].join()
    threads_b[1].join()

    # Dar tiempo para recibir ultimos mensajes
    time.sleep(2)

    # Detener receptores
    nodo_a.running = False
    nodo_b.running = False

    time.sleep(1)

    # Resumen
    print("\n" + "="*60)
    print("   RESUMEN")
    print("="*60)
    print(f"\nNodo_A envio: {len(mensajes_a)} mensajes")
    print(f"Nodo_A recibio: {len(nodo_a.messages_received)} mensajes")

    print(f"\nNodo_B envio: {len(mensajes_b)} mensajes")
    print(f"Nodo_B recibio: {len(nodo_b.messages_received)} mensajes")

    if len(nodo_a.messages_received) > 0 and len(nodo_b.messages_received) > 0:
        print("\n✓ EXITO: Los nodos se comunicaron correctamente!")
    else:
        print("\n✗ ADVERTENCIA: Puede haber problemas de comunicacion")
        print("  Esto puede ser normal si el firewall esta bloqueando")

    print("\n" + "="*60)

if __name__ == "__main__":
    main()
