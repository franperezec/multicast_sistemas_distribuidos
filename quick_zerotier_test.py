"""
Test Rapido de ZeroTier - Sin caracteres especiales
"""

import socket
import threading
import time
import json
from datetime import datetime

# Configuracion
MULTICAST_GROUP = '224.1.1.1'
PORT = 5007
LOCAL_IP = '0.0.0.0'  # Tu IP de ZeroTier - cambiar antes de usar
NODE_NAME = 'Nodo_TuNombre'  # Cambia esto por tu nombre


def create_simple_message(msg_type, content):
    """Crea un mensaje JSON simple"""
    return json.dumps({
        'node_id': NODE_NAME,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'type': msg_type,
        'content': content,
        'ip': LOCAL_IP
    })


def send_hello():
    """Envia un mensaje HELLO"""
    try:
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        message = create_simple_message(
            'HELLO', f'Hola desde {NODE_NAME} - IP: {LOCAL_IP}')
        sock.sendto(message.encode('utf-8'), (MULTICAST_GROUP, PORT))

        print(f"[ENVIADO] HELLO desde {LOCAL_IP}")
        sock.close()
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo enviar: {e}")
        return False


def listen_for_messages(duration=20):
    """Escucha mensajes por X segundos"""
    print(
        f"\n[ESCUCHANDO] Por {duration} segundos en {MULTICAST_GROUP}:{PORT}")
    print("-" * 50)

    messages_received = []

    try:
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', PORT))

        import struct
        mreq = struct.pack("4sl", socket.inet_aton(
            MULTICAST_GROUP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        sock.settimeout(1.0)

        end_time = time.time() + duration

        while time.time() < end_time:
            try:
                data, address = sock.recvfrom(1024)
                message_str = data.decode('utf-8')
                message = json.loads(message_str)

                # No mostrar mensajes propios
                if message.get('node_id') != NODE_NAME:
                    print(
                        f"\n[RECIBIDO] De: {message.get('node_id', 'Unknown')}")
                    print(f"  IP origen: {address[0]}")
                    print(f"  IP reportada: {message.get('ip', 'N/A')}")
                    print(f"  Tipo: {message.get('type', 'Unknown')}")
                    print(f"  Contenido: {message.get('content', '')}")
                    print(f"  Hora: {message.get('timestamp', '')}")

                    messages_received.append(message)
            except socket.timeout:
                remaining = int(end_time - time.time())
                if remaining > 0 and remaining % 5 == 0:
                    print(f"  ... {remaining} seg restantes ...")
            except json.JSONDecodeError:
                pass
            except Exception as e:
                pass

        sock.close()

    except Exception as e:
        print(f"[ERROR] Problema al escuchar: {e}")

    print("\n" + "-" * 50)
    print(f"[RESUMEN] Total mensajes recibidos: {len(messages_received)}")

    if messages_received:
        print("\nNodos detectados:")
        nodes = set(msg.get('node_id', 'Unknown') for msg in messages_received)
        for node in nodes:
            print(f"  - {node}")
    else:
        print("\n[!] No se recibieron mensajes de otros nodos")
        print("    Verifica que:")
        print("    1. Otros nodos estan activos")
        print("    2. Firewall no esta bloqueando")
        print("    3. Todos usan la misma configuracion")

    return len(messages_received) > 0


def send_continuous():
    """Envia mensajes cada 3 segundos"""
    print("\n[MODO CONTINUO] Enviando mensajes cada 3 segundos")
    print("Presiona Ctrl+C para detener\n")

    count = 1
    try:
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        while True:
            message = create_simple_message(
                'MESSAGE', f'Mensaje #{count} desde {NODE_NAME}')
            sock.sendto(message.encode('utf-8'), (MULTICAST_GROUP, PORT))

            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] Mensaje #{count} enviado")

            count += 1
            time.sleep(3)

    except KeyboardInterrupt:
        print("\n[DETENIDO] Envio detenido por usuario")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        if 'sock' in locals():
            sock.close()


def parallel_test():
    """Envia y recibe al mismo tiempo"""
    print("\n[PRUEBA PARALELA] Enviando y recibiendo simultaneamente")

    # Thread para escuchar
    def listener():
        listen_for_messages(30)

    listener_thread = threading.Thread(target=listener)
    listener_thread.daemon = True
    listener_thread.start()

    # Esperar que el listener este listo
    time.sleep(1)

    # Enviar mensajes cada 5 segundos
    try:
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        for i in range(6):  # 6 mensajes en 30 segundos
            message = create_simple_message('TEST', f'Prueba paralela #{i+1}')
            sock.sendto(message.encode('utf-8'), (MULTICAST_GROUP, PORT))
            print(f"\n[ENVIADO] Mensaje de prueba #{i+1}")
            time.sleep(5)

        sock.close()
    except Exception as e:
        print(f"[ERROR] {e}")

    # Esperar a que termine el listener
    listener_thread.join()


def main():
    print("\n" + "="*60)
    print("   TEST RAPIDO DE ZEROTIER")
    print("="*60)
    print(f"\nCONFIGURACION:")
    print(f"  Tu IP ZeroTier: {LOCAL_IP}")
    print(f"  Tu nombre de nodo: {NODE_NAME}")
    print(f"  Grupo Multicast: {MULTICAST_GROUP}")
    print(f"  Puerto: {PORT}")
    print("="*60)

    print("\nOPCIONES:")
    print("1. Enviar HELLO")
    print("2. Escuchar mensajes (20 seg)")
    print("3. Enviar mensajes continuos")
    print("4. Prueba paralela (enviar y recibir)")
    print("5. Test completo")

    choice = input("\nElige opcion (1-5): ")

    if choice == '1':
        send_hello()

    elif choice == '2':
        listen_for_messages(20)

    elif choice == '3':
        send_continuous()

    elif choice == '4':
        parallel_test()

    elif choice == '5':
        print("\n[TEST COMPLETO]")
        print("Paso 1: Enviando HELLO...")
        send_hello()
        time.sleep(1)

        print("\nPaso 2: Escuchando respuestas...")
        listen_for_messages(15)

    else:
        print("[!] Opcion no valida")

    print("\n[FIN] Prueba completada")


if __name__ == "__main__":
    main()
