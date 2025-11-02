import socket
import json
import time
from datetime import datetime

MULTICAST_GROUP = '224.1.1.1'
PORT = 5007
LOCAL_IP = '192.168.194.33'
NODE_NAME = 'Nodo_Francisco'

print("Enviando mensajes de prueba...")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

for i in range(5):
    message = {
        'node_id': NODE_NAME,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'type': 'MESSAGE',
        'content': f'Mensaje de prueba #{i+1} desde emisor',
        'ip': LOCAL_IP
    }

    sock.sendto(json.dumps(message).encode('utf-8'), (MULTICAST_GROUP, PORT))
    print(f'  [{i+1}] Mensaje enviado: {message["content"]}')
    time.sleep(1)

sock.close()
print("\n[OK] Todos los mensajes enviados")
