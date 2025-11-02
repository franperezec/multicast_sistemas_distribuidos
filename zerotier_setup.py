"""
Asistente de Configuración de ZeroTier
Ayuda a configurar la red virtual y actualizar el proyecto
"""

import os
import sys
import socket
import subprocess
import json
import time
import platform
from datetime import datetime

# Colores para output
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

def print_colored(message, color='WHITE'):
    """Imprime mensaje con color"""
    print(f"{COLORS.get(color, '')}{message}{COLORS['RESET']}")

def print_header(title):
    """Imprime encabezado formateado"""
    print_colored("\n" + "="*60, 'CYAN')
    print_colored(f"   {title}", 'CYAN')
    print_colored("="*60, 'CYAN')

def check_zerotier_installed():
    """Verifica si ZeroTier está instalado"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['zerotier-cli', 'info'], 
                                  capture_output=True, text=True, shell=True)
        else:
            result = subprocess.run(['sudo', 'zerotier-cli', 'info'], 
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            print_colored("✓ ZeroTier está instalado", 'GREEN')
            return True
        else:
            print_colored("✗ ZeroTier no está instalado o no está ejecutándose", 'RED')
            return False
    except FileNotFoundError:
        print_colored("✗ ZeroTier no está instalado", 'RED')
        return False
    except Exception as e:
        print_colored(f"✗ Error verificando ZeroTier: {e}", 'RED')
        return False

def get_zerotier_info():
    """Obtiene información de ZeroTier"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['zerotier-cli', 'info'], 
                                  capture_output=True, text=True, shell=True)
        else:
            result = subprocess.run(['sudo', 'zerotier-cli', 'info'], 
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            info = result.stdout.strip()
            print_colored(f"Info ZeroTier: {info}", 'CYAN')
            
            # Extraer el ID del nodo
            parts = info.split()
            if len(parts) >= 1:
                node_id = parts[0]
                print_colored(f"Tu Node ID: {node_id}", 'GREEN')
                return node_id
        return None
    except Exception as e:
        print_colored(f"Error obteniendo info: {e}", 'RED')
        return None

def list_networks():
    """Lista las redes ZeroTier actuales"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['zerotier-cli', 'listnetworks'], 
                                  capture_output=True, text=True, shell=True)
        else:
            result = subprocess.run(['sudo', 'zerotier-cli', 'listnetworks'], 
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            networks = result.stdout.strip()
            if networks and networks != "":
                print_colored("\nRedes actuales:", 'YELLOW')
                lines = networks.split('\n')
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 4:
                            network_id = parts[2]
                            name = parts[3] if len(parts) > 3 else "Sin nombre"
                            status = parts[4] if len(parts) > 4 else "Unknown"
                            
                            # Intentar obtener IPs asignadas
                            if len(parts) >= 9:
                                ips = parts[8]
                                print_colored(f"  • Red: {network_id}", 'WHITE')
                                print_colored(f"    Nombre: {name}", 'WHITE')
                                print_colored(f"    Estado: {status}", 'WHITE')
                                print_colored(f"    IPs: {ips}", 'GREEN')
                            else:
                                print_colored(f"  • Red: {network_id} - {status}", 'WHITE')
                return True
            else:
                print_colored("No hay redes configuradas", 'YELLOW')
                return False
    except Exception as e:
        print_colored(f"Error listando redes: {e}", 'RED')
        return False

def join_network(network_id):
    """Une el nodo a una red ZeroTier"""
    try:
        print_colored(f"\nUniendo a la red {network_id}...", 'YELLOW')
        
        if platform.system() == "Windows":
            result = subprocess.run(['zerotier-cli', 'join', network_id], 
                                  capture_output=True, text=True, shell=True)
        else:
            result = subprocess.run(['sudo', 'zerotier-cli', 'join', network_id], 
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            print_colored(f"✓ Solicitud enviada para unirse a {network_id}", 'GREEN')
            print_colored("\n⚠️  IMPORTANTE:", 'YELLOW')
            print_colored("1. Ve a https://my.zerotier.com", 'WHITE')
            print_colored("2. Autoriza este dispositivo en la red", 'WHITE')
            print_colored("3. Espera a que se asigne una IP", 'WHITE')
            return True
        else:
            print_colored(f"✗ Error uniéndose a la red: {result.stderr}", 'RED')
            return False
    except Exception as e:
        print_colored(f"Error: {e}", 'RED')
        return False

def leave_network(network_id):
    """Abandona una red ZeroTier"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['zerotier-cli', 'leave', network_id], 
                                  capture_output=True, text=True, shell=True)
        else:
            result = subprocess.run(['sudo', 'zerotier-cli', 'leave', network_id], 
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            print_colored(f"✓ Red {network_id} abandonada", 'GREEN')
            return True
        else:
            print_colored(f"✗ Error abandonando la red", 'RED')
            return False
    except Exception as e:
        print_colored(f"Error: {e}", 'RED')
        return False

def get_zerotier_ip(network_id=None):
    """Obtiene la IP asignada por ZeroTier"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['zerotier-cli', 'listnetworks'], 
                                  capture_output=True, text=True, shell=True)
        else:
            result = subprocess.run(['sudo', 'zerotier-cli', 'listnetworks'], 
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) >= 9:
                    if network_id is None or network_id in line:
                        # Buscar IPs (formato: 192.168.xxx.xxx/24)
                        for part in parts[8:]:
                            if '/' in part and '.' in part:
                                ip = part.split('/')[0]
                                return ip
        return None
    except Exception as e:
        print_colored(f"Error obteniendo IP: {e}", 'RED')
        return None

def update_config_file(ip_address):
    """Actualiza el archivo config.py con la IP de ZeroTier"""
    try:
        config_file = "config.py"
        backup_file = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        
        # Hacer backup
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                content = f.read()
            
            with open(backup_file, 'w') as f:
                f.write(content)
            
            print_colored(f"✓ Backup creado: {backup_file}", 'GREEN')
            
            # Actualizar LOCAL_IP
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('LOCAL_IP'):
                    lines[i] = f"LOCAL_IP = '{ip_address}'  # IP de ZeroTier"
                    break
            
            # Escribir archivo actualizado
            with open(config_file, 'w') as f:
                f.write('\n'.join(lines))
            
            print_colored(f"✓ config.py actualizado con IP: {ip_address}", 'GREEN')
            return True
        else:
            print_colored("✗ No se encontró config.py", 'RED')
            return False
    except Exception as e:
        print_colored(f"Error actualizando config: {e}", 'RED')
        return False

def test_multicast_binding(ip_address):
    """Prueba si se puede hacer bind al socket multicast con la IP"""
    try:
        import socket
        import struct
        
        MULTICAST_GROUP = '224.1.1.1'
        PORT = 5007
        
        # Intentar crear socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind
        sock.bind(('', PORT))
        
        # Unirse al grupo multicast
        mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        sock.close()
        
        print_colored("✓ Socket multicast funciona correctamente", 'GREEN')
        return True
    except Exception as e:
        print_colored(f"✗ Error con socket multicast: {e}", 'RED')
        return False

def create_network_test_script():
    """Crea un script de prueba para la red ZeroTier"""
    script_content = '''"""
Script de Prueba de Red ZeroTier
Envía pings para verificar conectividad
"""

import socket
import time
import sys
from config import *

def send_test_ping():
    """Envía un ping de prueba"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)
        
        message = create_message('PING', f'Test desde {NODE_NAME} en ZeroTier')
        data = message.encode('utf-8')
        
        print(f"Enviando ping a {MULTICAST_GROUP}:{PORT}")
        sock.sendto(data, (MULTICAST_GROUP, PORT))
        
        print_colored("✓ Ping enviado", 'GREEN')
        sock.close()
        return True
    except Exception as e:
        print_colored(f"✗ Error enviando ping: {e}", 'RED')
        return False

def listen_test():
    """Escucha mensajes de prueba"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', PORT))
        
        import struct
        mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        sock.settimeout(5.0)
        
        print(f"Escuchando en {MULTICAST_GROUP}:{PORT} por 30 segundos...")
        print("Pide a un compañero que envíe un mensaje...")
        
        end_time = time.time() + 30
        messages_received = 0
        
        while time.time() < end_time:
            try:
                data, address = sock.recvfrom(BUFFER_SIZE)
                message_str = data.decode('utf-8')
                message = parse_message(message_str)
                
                if message:
                    print_colored(f"✓ Mensaje recibido de {message['node_id']} desde {address[0]}", 'GREEN')
                    print(f"   Contenido: {message['content']}")
                    messages_received += 1
            except socket.timeout:
                continue
        
        sock.close()
        
        if messages_received > 0:
            print_colored(f"\\n✓ Test exitoso: {messages_received} mensajes recibidos", 'GREEN')
        else:
            print_colored("\\n⚠️ No se recibieron mensajes", 'YELLOW')
            
        return messages_received > 0
    except Exception as e:
        print_colored(f"✗ Error escuchando: {e}", 'RED')
        return False

if __name__ == "__main__":
    print_colored("\\n" + "="*50, 'CYAN')
    print_colored("   TEST DE RED ZEROTIER", 'CYAN')
    print_colored("="*50 + "\\n", 'CYAN')
    
    info = get_system_info()
    print(f"IP Local: {info['local_ip']}")
    print(f"IP ZeroTier (LOCAL_IP): {LOCAL_IP if LOCAL_IP else 'No configurada'}")
    
    print("\\n1. Enviar ping de prueba")
    print("2. Escuchar mensajes (30 seg)")
    print("3. Ambos")
    
    choice = input("\\nSeleccionar opción: ")
    
    if choice == '1':
        for i in range(5):
            send_test_ping()
            time.sleep(2)
    elif choice == '2':
        listen_test()
    elif choice == '3':
        send_test_ping()
        time.sleep(1)
        listen_test()
'''
    
    with open('zerotier_test.py', 'w') as f:
        f.write(script_content)
    
    print_colored("✓ Script de prueba creado: zerotier_test.py", 'GREEN')

def show_instructions():
    """Muestra instrucciones detalladas"""
    print_header("INSTRUCCIONES DE CONFIGURACIÓN")
    
    print_colored("\n📋 PASO 1: INSTALAR ZEROTIER", 'YELLOW')
    print_colored("1. Ve a https://www.zerotier.com/download/", 'WHITE')
    print_colored("2. Descarga e instala ZeroTier One", 'WHITE')
    print_colored("3. Ejecuta ZeroTier (se minimiza en la bandeja del sistema)", 'WHITE')
    
    print_colored("\n📋 PASO 2: CREAR O UNIRSE A UNA RED", 'YELLOW')
    print_colored("\nOpción A - Crear tu propia red:", 'CYAN')
    print_colored("1. Ve a https://my.zerotier.com", 'WHITE')
    print_colored("2. Crea una cuenta gratuita", 'WHITE')
    print_colored("3. Click en 'Create A Network'", 'WHITE')
    print_colored("4. Copia el Network ID (16 caracteres)", 'WHITE')
    print_colored("5. En configuración de la red:", 'WHITE')
    print_colored("   • Access Control: Private", 'WHITE')
    print_colored("   • IPv4 Auto-Assign: Activo", 'WHITE')
    print_colored("   • Rango sugerido: 192.168.195.0/24", 'WHITE')
    
    print_colored("\nOpción B - Unirse a red existente:", 'CYAN')
    print_colored("1. Obtén el Network ID del compañero", 'WHITE')
    print_colored("2. Ejecuta este script opción 2", 'WHITE')
    
    print_colored("\n📋 PASO 3: AUTORIZACIÓN", 'YELLOW')
    print_colored("1. El admin de la red debe autorizar tu dispositivo", 'WHITE')
    print_colored("2. En https://my.zerotier.com → Members", 'WHITE')
    print_colored("3. Marcar checkbox de autorización", 'WHITE')
    print_colored("4. Esperar asignación de IP (1-2 minutos)", 'WHITE')
    
    print_colored("\n📋 PASO 4: CONFIGURAR PROYECTO", 'YELLOW')
    print_colored("1. Ejecutar opción 4 de este script", 'WHITE')
    print_colored("2. Verificar que config.py tiene la IP correcta", 'WHITE')
    print_colored("3. Ejecutar zerotier_test.py para probar", 'WHITE')

def create_team_coordinator():
    """Crea un archivo para coordinar con el equipo"""
    content = """# 📋 INFORMACIÓN DEL EQUIPO - ZEROTIER

## 🌐 Información de la Red

**Network ID:** [PEGAR_AQUI_EL_NETWORK_ID]
**Nombre de Red:** Multicast_SistemasDistribuidos
**Rango IP:** 192.168.195.0/24

## 👥 Miembros del Equipo

| Nombre | Node ID | IP Asignada | Estado | Puerto |
|--------|---------|-------------|--------|--------|
| [TU_NOMBRE] | [TU_NODE_ID] | [TU_IP] | ✅ Activo | 5007 |
| Compañero1 | - | - | ⏳ Pendiente | 5007 |
| Compañero2 | - | - | ⏳ Pendiente | 5007 |
| Compañero3 | - | - | ⏳ Pendiente | 5007 |

## 📅 Horarios de Prueba

- **Prueba 1:** [FECHA] a las [HORA]
- **Prueba 2:** [FECHA] a las [HORA]
- **Prueba Final:** [FECHA] a las [HORA]

## ✅ Checklist de Configuración

- [ ] ZeroTier instalado
- [ ] Unido a la red
- [ ] Autorizado por admin
- [ ] IP asignada
- [ ] config.py actualizado
- [ ] Prueba local exitosa
- [ ] Prueba con 1 compañero
- [ ] Prueba con todos

## 📝 Notas

- Grupo Multicast: 224.1.1.1
- Puerto: 5007
- TTL: 2

## 🔧 Comandos Útiles

```bash
# Ver estado
zerotier-cli info

# Ver redes
zerotier-cli listnetworks

# Unirse a red
zerotier-cli join [NETWORK_ID]

# Salir de red
zerotier-cli leave [NETWORK_ID]

# Ver peers
zerotier-cli listpeers
```

## 📞 Contacto

- Admin de Red: [NOMBRE] - [CONTACTO]
- Grupo WhatsApp/Discord: [LINK]
"""
    
    with open('TEAM_ZEROTIER.md', 'w') as f:
        f.write(content)
    
    print_colored("✓ Archivo de coordinación creado: TEAM_ZEROTIER.md", 'GREEN')
    print_colored("  Edítalo con la información de tu equipo", 'YELLOW')

def main_menu():
    """Menú principal del asistente"""
    print_header("ASISTENTE DE CONFIGURACIÓN ZEROTIER")
    
    while True:
        print_colored("\n📌 MENÚ PRINCIPAL", 'YELLOW')
        print_colored("1. Verificar instalación de ZeroTier", 'WHITE')
        print_colored("2. Unirse a una red", 'WHITE')
        print_colored("3. Ver redes actuales", 'WHITE')
        print_colored("4. Configurar proyecto (actualizar config.py)", 'WHITE')
        print_colored("5. Crear scripts de prueba", 'WHITE')
        print_colored("6. Abandonar una red", 'WHITE')
        print_colored("7. Ver instrucciones completas", 'WHITE')
        print_colored("8. Crear archivo de coordinación del equipo", 'WHITE')
        print_colored("9. Salir", 'WHITE')
        
        choice = input(f"\n{COLORS['CYAN']}Seleccionar opción: {COLORS['RESET']}")
        
        if choice == '1':
            if check_zerotier_installed():
                node_id = get_zerotier_info()
                if node_id:
                    print_colored(f"\n📝 Tu Node ID es: {node_id}", 'GREEN')
                    print_colored("Compártelo con el admin de la red para que te autorice", 'YELLOW')
        
        elif choice == '2':
            network_id = input("Ingresa el Network ID (16 caracteres): ")
            if len(network_id) == 16:
                if join_network(network_id):
                    print_colored("\n⏳ Esperando autorización...", 'YELLOW')
                    print_colored("Una vez autorizado, usa opción 4 para configurar", 'WHITE')
            else:
                print_colored("Network ID debe tener 16 caracteres", 'RED')
        
        elif choice == '3':
            list_networks()
            
        elif choice == '4':
            # Obtener IP de ZeroTier
            ip = get_zerotier_ip()
            if ip:
                print_colored(f"\n✓ IP de ZeroTier detectada: {ip}", 'GREEN')
                
                # Actualizar config.py
                if update_config_file(ip):
                    # Probar binding
                    print_colored("\n🔍 Probando socket multicast...", 'YELLOW')
                    test_multicast_binding(ip)
            else:
                print_colored("\n✗ No se detectó IP de ZeroTier", 'RED')
                print_colored("Asegúrate de:", 'YELLOW')
                print_colored("1. Estar unido a una red", 'WHITE')
                print_colored("2. Estar autorizado por el admin", 'WHITE')
                print_colored("3. Tener una IP asignada", 'WHITE')
                
                manual_ip = input("\n¿Ingresar IP manualmente? (s/n): ")
                if manual_ip.lower() == 's':
                    ip = input("Ingresa tu IP de ZeroTier: ")
                    update_config_file(ip)
        
        elif choice == '5':
            create_network_test_script()
            print_colored("\nEjecútalo con: python zerotier_test.py", 'YELLOW')
        
        elif choice == '6':
            list_networks()
            network_id = input("\nIngresa el Network ID a abandonar: ")
            if len(network_id) == 16:
                leave_network(network_id)
        
        elif choice == '7':
            show_instructions()
        
        elif choice == '8':
            create_team_coordinator()
        
        elif choice == '9':
            break
        
        else:
            print_colored("Opción no válida", 'RED')
    
    print_colored("\n✅ Asistente finalizado", 'GREEN')

if __name__ == "__main__":
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('config.py'):
        print_colored("⚠️ ADVERTENCIA: No se encontró config.py", 'YELLOW')
        print_colored("Asegúrate de ejecutar este script en la carpeta del proyecto", 'YELLOW')
        input("\nPresiona Enter para continuar...")
    
    try:
        main_menu()
    except KeyboardInterrupt:
        print_colored("\n\n✋ Asistente cancelado por usuario", 'YELLOW')
    except Exception as e:
        print_colored(f"\n❌ Error: {e}", 'RED')
