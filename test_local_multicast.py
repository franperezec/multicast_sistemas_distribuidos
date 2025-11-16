"""
Test Local de Multicast
Prueba envío y recepción en la misma máquina
"""

import socket
import struct
import threading
import time
import json
from datetime import datetime

# Configuración
MULTICAST_GROUP = '224.1.1.1'
PORT = 5007
LOCAL_IP = '0.0.0.0'  # Usar 0.0.0.0 para red local o tu IP de ZeroTier
TEST_DURATION = 10  # segundos

# Contadores
mensajes_enviados = 0
mensajes_recibidos = 0
receptor_activo = False

print("="*70)
print("TEST LOCAL DE MULTICAST")
print("="*70)
print(f"\nConfiguracion:")
print(f"  Grupo Multicast: {MULTICAST_GROUP}")
print(f"  Puerto: {PORT}")
print(f"  IP Local: {LOCAL_IP}")
print(f"  Duracion del test: {TEST_DURATION} segundos")
print("\n" + "="*70)


def receptor_thread():
    """Thread receptor que escucha mensajes multicast"""
    global mensajes_recibidos, receptor_activo

    print("\n[RECEPTOR] Iniciando...")

    try:
        # Crear socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Intentar SO_REUSEPORT (no siempre disponible en Windows)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except:
            pass

        # Bind al puerto
        sock.bind(('', PORT))
        print(f"[RECEPTOR] Bind exitoso en puerto {PORT}")

        # Unirse al grupo multicast
        mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        print(f"[RECEPTOR] Unido al grupo {MULTICAST_GROUP}")

        # Configurar timeout para poder salir del loop
        sock.settimeout(1.0)

        receptor_activo = True
        print("[RECEPTOR] Esperando mensajes...\n")

        while receptor_activo:
            try:
                data, address = sock.recvfrom(1024)

                # Decodificar mensaje
                message_str = data.decode('utf-8')
                message = json.loads(message_str)

                mensajes_recibidos += 1

                # Mostrar mensaje recibido
                print(f"\n[RECIBIDO #{mensajes_recibidos}]")
                print(f"  De: {address[0]}:{address[1]}")
                print(f"  Nodo: {message.get('node_id', 'Unknown')}")
                print(f"  Tipo: {message.get('type', 'Unknown')}")
                print(f"  Contenido: {message.get('content', '')}")
                print(f"  Timestamp: {message.get('timestamp', '')}")

            except socket.timeout:
                continue
            except Exception as e:
                if receptor_activo:  # Solo mostrar si no es cierre intencional
                    print(f"[RECEPTOR ERROR] {e}")

        # Limpiar
        print("\n[RECEPTOR] Cerrando...")
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
        sock.close()
        print("[RECEPTOR] Cerrado correctamente")

    except Exception as e:
        print(f"\n[RECEPTOR ERROR CRITICO] {e}")
        import traceback
        traceback.print_exc()


def emisor_thread():
    """Thread emisor que envía mensajes multicast"""
    global mensajes_enviados

    # Esperar a que el receptor esté listo
    time.sleep(2)

    print("\n[EMISOR] Iniciando...")

    try:
        # Crear socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # Configurar TTL
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        # Configurar interfaz de salida
        try:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF,
                           socket.inet_aton(LOCAL_IP))
            print(f"[EMISOR] Usando interfaz: {LOCAL_IP}")
        except Exception as e:
            print(f"[EMISOR] No se pudo configurar interfaz {LOCAL_IP}: {e}")
            print(f"[EMISOR] Usando interfaz por defecto")

        # Habilitar loopback para recibir propios mensajes
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        print("[EMISOR] Loopback habilitado (recibiremos nuestros mensajes)")

        print(f"\n[EMISOR] Enviando mensajes durante {TEST_DURATION} segundos...\n")

        start_time = time.time()
        mensaje_num = 0

        while (time.time() - start_time) < TEST_DURATION:
            mensaje_num += 1

            # Crear mensaje
            message = {
                'node_id': 'TEST_LOCAL',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                'type': 'TEST',
                'content': f'Mensaje de prueba #{mensaje_num}',
                'numero': mensaje_num
            }

            # Enviar
            data = json.dumps(message).encode('utf-8')
            sock.sendto(data, (MULTICAST_GROUP, PORT))

            mensajes_enviados += 1
            print(f"[ENVIADO #{mensajes_enviados}] Mensaje #{mensaje_num}")

            # Esperar entre mensajes
            time.sleep(2)

        print("\n[EMISOR] Cerrando...")
        sock.close()
        print("[EMISOR] Cerrado correctamente")

    except Exception as e:
        print(f"\n[EMISOR ERROR CRITICO] {e}")
        import traceback
        traceback.print_exc()


# Iniciar threads
print("\n[MAIN] Iniciando test local...\n")

receptor = threading.Thread(target=receptor_thread, daemon=True)
emisor = threading.Thread(target=emisor_thread, daemon=True)

receptor.start()
time.sleep(1)  # Dar tiempo al receptor para iniciar
emisor.start()

# Esperar a que termine el emisor
emisor.join()

# Dar tiempo para recibir últimos mensajes
time.sleep(2)

# Detener receptor
receptor_activo = False
receptor.join(timeout=3)

# Resultados
print("\n" + "="*70)
print("RESULTADOS DEL TEST")
print("="*70)

print(f"\nMensajes enviados:   {mensajes_enviados}")
print(f"Mensajes recibidos:  {mensajes_recibidos}")

if mensajes_recibidos == 0:
    print("\n[ERROR] NO SE RECIBIO NINGUN MENSAJE")
    print("\nPOSIBLES CAUSAS:")
    print("  1. Firewall bloqueando puerto 5007/UDP")
    print("  2. ZeroTier no soporta multicast (no habilitado en configuracion web)")
    print("  3. Interfaz de red incorrecta")
    print("\nSOLUCIONES:")
    print("  1. Desactiva temporalmente el firewall:")
    print("     - Panel de Control > Firewall de Windows")
    print("     - O ejecuta como Administrador:")
    print('       netsh advfirewall firewall add rule name="Multicast" dir=in action=allow protocol=UDP localport=5007')
    print("\n  2. Habilita broadcast en ZeroTier:")
    print("     - Ve a https://my.zerotier.com")
    print("     - Selecciona tu red")
    print("     - En Advanced, marca 'Enable Broadcast'")

elif mensajes_recibidos < mensajes_enviados:
    print(f"\n[ADVERTENCIA] Se perdieron {mensajes_enviados - mensajes_recibidos} mensajes")
    print("  Esto podria ser normal en algunas condiciones de red")

else:
    print("\n[EXITO] El multicast funciona correctamente!")
    print("  Puedes proceder a probar con tus companeros")
    print("\nPROXIMOS PASOS:")
    print("  1. Asegurate que tus companeros:")
    print("     - Esten conectados a la misma red ZeroTier")
    print("     - Tengan IP de ZeroTier asignada (mismo rango)")
    print("     - Tengan firewall configurado")
    print("  2. Ejecuten: python multicast_node.py")
    print("  3. Coordinen estar online al mismo tiempo")

print("\n" + "="*70)
