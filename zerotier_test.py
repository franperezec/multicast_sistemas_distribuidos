"""
Script de Prueba de Red ZeroTier
Envía pings para verificar conectividad
"""

import socket
import time
import sys
import struct
from config import *


def send_test_ping():
    """Envía un ping de prueba"""
    try:
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)

        message = create_message(
            'PING', f'Test desde {NODE_NAME} en ZeroTier - IP: {LOCAL_IP}')
        data = message.encode('utf-8')

        print(f"Enviando ping a {MULTICAST_GROUP}:{PORT}")
        print(f"Desde IP: {LOCAL_IP}")
        sock.sendto(data, (MULTICAST_GROUP, PORT))

        print("[OK] Ping enviado")
        sock.close()
        return True
    except Exception as e:
        print(f"[ERROR] Error enviando ping: {e}")
        return False


def listen_test():
    """Escucha mensajes de prueba"""
    try:
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', PORT))

        mreq = struct.pack("4sl", socket.inet_aton(
            MULTICAST_GROUP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        sock.settimeout(5.0)

        print(f"Escuchando en {MULTICAST_GROUP}:{PORT} por 30 segundos...")
        print("Pide a un companero que envie un mensaje...")
        print("")

        end_time = time.time() + 30
        messages_received = 0

        while time.time() < end_time:
            try:
                data, address = sock.recvfrom(BUFFER_SIZE)
                message_str = data.decode('utf-8')
                message = parse_message(message_str)

                if message:
                    print(
                        f"[RECIBIDO] Mensaje de {message['node_id']} desde {address[0]}")
                    print(f"   Contenido: {message['content']}")
                    print(f"   Timestamp: {message['timestamp']}")
                    print("")
                    messages_received += 1
            except socket.timeout:
                remaining = int(end_time - time.time())
                if remaining > 0 and remaining % 10 == 0:
                    print(f"   ... {remaining} segundos restantes ...")
                continue
            except Exception as e:
                print(f"[ERROR] {e}")

        sock.close()

        if messages_received > 0:
            print(
                f"\n[OK] Test exitoso: {messages_received} mensajes recibidos")
        else:
            print("\n[ADVERTENCIA] No se recibieron mensajes")
            print("Posibles causas:")
            print("  - No hay otros nodos activos")
            print("  - Firewall bloqueando")
            print("  - Problemas de configuracion")

        return messages_received > 0
    except Exception as e:
        print(f"[ERROR] Error escuchando: {e}")
        return False


def continuous_ping():
    """Envía pings continuos cada 3 segundos"""
    print("Enviando pings continuos (Ctrl+C para detener)...")
    count = 1
    try:
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)

        while True:
            message = create_message(
                'PING', f'Ping #{count} desde {NODE_NAME} - IP: {LOCAL_IP}')
            data = message.encode('utf-8')
            sock.sendto(data, (MULTICAST_GROUP, PORT))
            print(f"[{count}] Ping enviado a las {time.strftime('%H:%M:%S')}")
            count += 1
            time.sleep(3)
    except KeyboardInterrupt:
        print("\n[DETENIDO] Pings detenidos por usuario")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        if 'sock' in locals():
            sock.close()


def show_config():
    """Muestra la configuración actual"""
    print("\n" + "="*50)
    print("   CONFIGURACION ACTUAL")
    print("="*50)
    print(f"NODE_NAME: {NODE_NAME}")
    print(f"LOCAL_IP: {LOCAL_IP}")
    print(f"MULTICAST_GROUP: {MULTICAST_GROUP}")
    print(f"PORT: {PORT}")
    print(f"TTL: {TTL}")

    # Verificar IP del sistema
    try:
        hostname = socket.gethostname()
        system_ip = socket.gethostbyname(hostname)
        print(f"Hostname: {hostname}")
        print(f"IP del sistema: {system_ip}")
    except:
        pass

    print("="*50 + "\n")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("   TEST DE RED ZEROTIER")
    print("="*50 + "\n")

    # Mostrar configuración
    show_config()

    # Verificar que LOCAL_IP está configurada
    if not LOCAL_IP or LOCAL_IP == '':
        print("[ERROR] LOCAL_IP no esta configurada en config.py")
        print("Ejecuta 'python zerotier_setup.py' opcion 4 primero")
        sys.exit(1)

    print("OPCIONES:")
    print("1. Enviar un ping de prueba")
    print("2. Escuchar mensajes (30 seg)")
    print("3. Enviar pings continuos")
    print("4. Enviar ping y luego escuchar")

    choice = input("\nSeleccionar opcion (1-4): ")

    if choice == '1':
        print("\nEnviando ping de prueba...")
        for i in range(3):
            send_test_ping()
            if i < 2:
                time.sleep(1)

    elif choice == '2':
        print("\nIniciando modo escucha...")
        listen_test()

    elif choice == '3':
        print("\nIniciando pings continuos...")
        continuous_ping()

    elif choice == '4':
        print("\nEnviando ping inicial...")
        send_test_ping()
        time.sleep(1)
        print("\nAhora escuchando respuestas...")
        listen_test()

    else:
        print("[ERROR] Opcion no valida")

    print("\n[FIN] Test completado")
