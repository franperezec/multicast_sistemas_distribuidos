"""
Configuración central para el sistema Multicast
Proyecto: Implementación de Multicast y Concurrencia en Sistemas Distribuidos
Universidad Técnica Particular de Loja
Fecha: Noviembre 2025
"""

import socket
import json
from datetime import datetime

# ============================================
# CONFIGURACIÓN DE RED MULTICAST
# ============================================

# Grupo Multicast (rango 224.0.0.0 a 239.255.255.255)
MULTICAST_GROUP = '224.1.1.1'
PORT = 5007

# Configuración del socket
BUFFER_SIZE = 1024
TTL = 2  # Time-to-live (2 = red local y siguiente salto)

# ============================================
# CONFIGURACIÓN DEL NODO
# ============================================

# IMPORTANTE: Cambia este nombre por tu nombre o identificador único
NODE_NAME = "Nodo_TuNombre"  # <-- MODIFICAR ESTO

# Para pruebas locales usar '0.0.0.0' o ''
# Para ZeroTier usar la IP asignada (ej: '192.168.195.100')
LOCAL_IP = '0.0.0.0'  # Cambiar a tu IP de ZeroTier si usas red virtual

# ============================================
# TIPOS DE MENSAJES
# ============================================

MESSAGE_TYPES = {
    'MESSAGE': 'MESSAGE',      # Mensaje normal
    'HELLO': 'HELLO',          # Nodo se une a la red
    'GOODBYE': 'GOODBYE',      # Nodo abandona la red
    'PING': 'PING',            # Verificar conectividad
    'PONG': 'PONG'             # Respuesta a ping
}

# ============================================
# CONFIGURACIÓN DE LOGS
# ============================================

LOG_FILE = 'logs/multicast_log.txt'
ENABLE_LOGGING = True
DEBUG_MODE = True  # Mostrar mensajes de debug en consola

# ============================================
# COLORES PARA LA CONSOLA (opcional)
# ============================================

COLORS = {
    'RESET': '\033[0m',
    'RED': '\033[91m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'MAGENTA': '\033[95m',
    'CYAN': '\033[96m',
    'WHITE': '\033[97m',
}

# ============================================
# FUNCIONES AUXILIARES
# ============================================


def create_message(msg_type, content, node_name=NODE_NAME):
    """
    Crea un mensaje con formato JSON estándar
    """
    message = {
        'node_id': node_name,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'type': msg_type,
        'content': content
    }
    return json.dumps(message)


def parse_message(data):
    """
    Parsea un mensaje JSON recibido
    """
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def log_message(message, direction='INFO'):
    """
    Registra un mensaje en el archivo de log
    """
    if not ENABLE_LOGGING:
        return

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [{direction}] {message}\n"

    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except:
        pass


def print_colored(message, color='WHITE'):
    """
    Imprime mensaje con color en la consola
    """
    import sys
    try:
        if color in COLORS:
            print(f"{COLORS[color]}{message}{COLORS['RESET']}")
        else:
            print(message)
    except UnicodeEncodeError:
        # Si hay error de codificación, imprimir sin emojis
        message_clean = message.encode('ascii', 'ignore').decode('ascii')
        if color in COLORS:
            print(f"{COLORS[color]}{message_clean}{COLORS['RESET']}")
        else:
            print(message_clean)

# ============================================
# INFORMACIÓN DEL SISTEMA
# ============================================


def get_system_info():
    """
    Obtiene información del sistema
    """
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return {
            'hostname': hostname,
            'local_ip': local_ip,
            'multicast_group': MULTICAST_GROUP,
            'port': PORT
        }
    except:
        return {
            'hostname': 'Unknown',
            'local_ip': '127.0.0.1',
            'multicast_group': MULTICAST_GROUP,
            'port': PORT
        }
