# -*- coding: utf-8 -*-
"""
Script de diagnóstico para probar la conectividad multicast
"""

import socket
import struct
import json
from datetime import datetime

MULTICAST_GROUP = '224.1.1.1'
PORT = 5007


def test_sender():
    """Prueba envío de mensajes multicast"""
    print("=== TEST DE ENVÍO MULTICAST ===")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    message = {
        'node_id': 'TEST_SENDER',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'type': 'MESSAGE',
        'content': 'Mensaje de prueba'
    }
    data = json.dumps(message).encode('utf-8')

    print(f"Enviando mensaje a {MULTICAST_GROUP}:{PORT}")
    sock.sendto(data, (MULTICAST_GROUP, PORT))
    print(f"✓ Mensaje enviado: {len(data)} bytes")
    sock.close()


def test_receiver():
    """Prueba recepción de mensajes multicast"""
    print("\n=== TEST DE RECEPCIÓN MULTICAST ===")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except:
        pass

    sock.bind(('', PORT))

    mreq = struct.pack("4sl", socket.inet_aton(
        MULTICAST_GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    sock.settimeout(5.0)

    print(f"Escuchando en {MULTICAST_GROUP}:{PORT}")
    print("Esperando mensajes (timeout 5 segundos)...")

    try:
        data, address = sock.recvfrom(1024)
        print(f"✓ Mensaje recibido de {address}")
        print(f"  Contenido: {data.decode('utf-8')}")
    except socket.timeout:
        print("✗ No se recibieron mensajes (timeout)")
    except Exception as e:
        print(f"✗ Error: {e}")

    sock.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso:")
        print("  python test_multicast.py sender    # Enviar un mensaje")
        print("  python test_multicast.py receiver  # Escuchar mensajes")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == 'sender':
        test_sender()
    elif mode == 'receiver':
        test_receiver()
    else:
        print("Modo inválido. Use 'sender' o 'receiver'")
