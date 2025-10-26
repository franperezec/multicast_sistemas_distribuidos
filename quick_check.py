"""
Quick Check - Verificador Rápido del Sistema Multicast
Ejecutar antes de empezar para verificar que todo está listo
"""

import sys
import os
import socket
import platform
import subprocess


def print_banner():
    """Imprime el banner del verificador"""
    print("\n" + "="*50)
    print("   🔍 VERIFICADOR RÁPIDO DEL SISTEMA")
    print("="*50 + "\n")


def check_python_version():
    """Verifica la versión de Python"""
    print("📌 Verificando Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(
            f"  ✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor} - Necesitas 3.8+")
        return False


def check_imports():
    """Verifica que los módulos necesarios están disponibles"""
    print("\n📌 Verificando módulos...")
    modules = ['socket', 'threading', 'json', 'struct', 'time']
    all_ok = True

    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module} - OK")
        except ImportError:
            print(f"  ❌ {module} - NO DISPONIBLE")
            all_ok = False

    # Verificar colorama (opcional)
    try:
        import colorama
        print(f"  ✅ colorama - OK (opcional)")
    except ImportError:
        print(f"  ⚠️  colorama - No instalado (opcional)")
        print("     Instalar con: pip install colorama")

    return all_ok


def check_project_structure():
    """Verifica la estructura del proyecto"""
    print("\n📌 Verificando estructura del proyecto...")

    required_files = ['config.py', 'receiver.py', 'sender.py', 'test_local.py']
    required_dirs = ['logs', 'capturas']
    all_ok = True

    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file} - Existe")
        else:
            print(f"  ❌ {file} - NO ENCONTRADO")
            all_ok = False

    for dir in required_dirs:
        if os.path.exists(dir):
            print(f"  ✅ {dir}/ - Existe")
        else:
            print(f"  ⚠️  {dir}/ - No existe (se creará)")
            os.makedirs(dir, exist_ok=True)
            print(f"     ✅ {dir}/ - Creado")

    return all_ok


def check_network():
    """Verifica la configuración de red"""
    print("\n📌 Verificando red...")

    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"  ✅ Hostname: {hostname}")
        print(f"  ✅ IP Local: {local_ip}")

        # Verificar si puede crear socket multicast
        test_sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        test_sock.close()
        print(f"  ✅ Sockets UDP - OK")

        return True
    except Exception as e:
        print(f"  ❌ Error de red: {e}")
        return False


def check_firewall():
    """Advierte sobre el firewall"""
    print("\n📌 Recordatorios de Firewall...")

    os_name = platform.system()
    if os_name == "Windows":
        print("  ⚠️  Windows detectado")
        print("     Si no recibes mensajes:")
        print("     1. Permitir Python en Windows Defender Firewall")
        print("     2. O desactivar temporalmente el firewall para pruebas")
    elif os_name == "Linux":
        print("  ⚠️  Linux detectado")
        print("     Si tienes problemas: sudo ufw allow 5007/udp")
    else:
        print(f"  ℹ️  Sistema: {os_name}")


def check_config():
    """Verifica la configuración"""
    print("\n📌 Verificando configuración...")

    try:
        import config
        print(f"  ✅ Grupo Multicast: {config.MULTICAST_GROUP}")
        print(f"  ✅ Puerto: {config.PORT}")
        print(f"  ✅ TTL: {config.TTL}")

        if config.NODE_NAME == "Nodo_TuNombre":
            print(f"  ⚠️  Nombre del Nodo: {config.NODE_NAME}")
            print("     ¡IMPORTANTE! Cambia NODE_NAME en config.py")
        else:
            print(f"  ✅ Nombre del Nodo: {config.NODE_NAME}")

        return True
    except Exception as e:
        print(f"  ❌ Error en config.py: {e}")
        return False


def run_quick_test():
    """Ejecuta una prueba rápida de envío/recepción"""
    print("\n📌 Prueba rápida de funcionamiento...")

    try:
        # Intentar importar y crear instancias
        from sender import MulticastSender
        from receiver import MulticastReceiver

        sender = MulticastSender()
        if sender.setup_socket():
            print("  ✅ Emisor funciona")
            sender.cleanup()
        else:
            print("  ❌ Problema con el emisor")

        receiver = MulticastReceiver()
        if receiver.setup_socket():
            print("  ✅ Receptor funciona")
            receiver.cleanup()
        else:
            print("  ❌ Problema con el receptor")

        return True
    except Exception as e:
        print(f"  ❌ Error en prueba: {e}")
        return False


def show_next_steps():
    """Muestra los siguientes pasos"""
    print("\n" + "="*50)
    print("   📋 SIGUIENTES PASOS")
    print("="*50)

    print("\n1️⃣  IMPORTANTE: Editar config.py")
    print("   Cambiar NODE_NAME = 'Nodo_TuNombre'")

    print("\n2️⃣  Ejecutar prueba completa:")
    print("   python test_local.py")

    print("\n3️⃣  Probar emisor y receptor:")
    print("   Terminal 1: python receiver.py")
    print("   Terminal 2: python sender.py")

    print("\n4️⃣  Si todo funciona, continuar con Fase 3")
    print("   (Implementación de concurrencia)")


def main():
    """Función principal"""
    print_banner()

    results = []

    # Ejecutar verificaciones
    results.append(("Python", check_python_version()))
    results.append(("Módulos", check_imports()))
    results.append(("Estructura", check_project_structure()))
    results.append(("Red", check_network()))
    results.append(("Config", check_config()))

    check_firewall()

    results.append(("Test", run_quick_test()))

    # Mostrar resumen
    print("\n" + "="*50)
    print("   📊 RESUMEN DE VERIFICACIÓN")
    print("="*50)

    all_passed = True
    for name, passed in results:
        if passed:
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}")
            all_passed = False

    if all_passed:
        print("\n🎉 ¡TODO LISTO! El sistema está preparado.")
        show_next_steps()
    else:
        print("\n⚠️  Hay problemas que resolver antes de continuar.")
        print("Revisa los errores marcados con ❌ arriba.")

    print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    main()
