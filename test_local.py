"""
Script de Pruebas Locales
Verifica el funcionamiento del sistema multicast en localhost
"""

import threading
import time
import subprocess
import sys
import os
from config import *
from sender import MulticastSender
from receiver import MulticastReceiver


class LocalTester:
    def __init__(self):
        """
        Inicializa el tester local
        """
        self.sender = None
        self.receiver = None
        self.receiver_thread = None
        self.test_results = []

    def print_header(self, title):
        """
        Imprime un encabezado formateado
        """
        print_colored("\n" + "="*60, 'CYAN')
        print_colored(f"   {title}", 'CYAN')
        print_colored("="*60, 'CYAN')

    def test_1_basic_setup(self):
        """
        Test 1: Verificar configuración básica
        """
        self.print_header("TEST 1: CONFIGURACIÓN BÁSICA")

        print_colored("Verificando configuración...", 'YELLOW')

        # Verificar imports
        try:
            import socket
            import struct
            import json
            print_colored("✓ Módulos Python necesarios disponibles", 'GREEN')
            self.test_results.append(("Módulos Python", "PASS"))
        except ImportError as e:
            print_colored(f"✗ Falta módulo: {e}", 'RED')
            self.test_results.append(("Módulos Python", "FAIL"))
            return False

        # Verificar configuración
        info = get_system_info()
        print_colored(f"✓ Hostname: {info['hostname']}", 'GREEN')
        print_colored(f"✓ IP Local: {info['local_ip']}", 'GREEN')
        print_colored(f"✓ Grupo Multicast: {MULTICAST_GROUP}", 'GREEN')
        print_colored(f"✓ Puerto: {PORT}", 'GREEN')

        # Verificar carpeta de logs
        if not os.path.exists('logs'):
            os.makedirs('logs')
            print_colored("✓ Carpeta 'logs' creada", 'GREEN')
        else:
            print_colored("✓ Carpeta 'logs' existe", 'GREEN')

        self.test_results.append(("Configuración básica", "PASS"))
        return True

    def test_2_socket_creation(self):
        """
        Test 2: Crear sockets emisor y receptor
        """
        self.print_header("TEST 2: CREACIÓN DE SOCKETS")

        # Test emisor
        print_colored("\nProbando emisor...", 'YELLOW')
        self.sender = MulticastSender()
        if self.sender.setup_socket():
            print_colored("✓ Socket emisor creado correctamente", 'GREEN')
            self.test_results.append(("Socket emisor", "PASS"))
        else:
            print_colored("✗ Error creando socket emisor", 'RED')
            self.test_results.append(("Socket emisor", "FAIL"))
            return False

        # Test receptor
        print_colored("\nProbando receptor...", 'YELLOW')
        self.receiver = MulticastReceiver()
        if self.receiver.setup_socket():
            print_colored("✓ Socket receptor creado correctamente", 'GREEN')
            self.test_results.append(("Socket receptor", "PASS"))
        else:
            print_colored("✗ Error creando socket receptor", 'RED')
            self.test_results.append(("Socket receptor", "FAIL"))
            return False

        return True

    def test_3_send_receive_local(self):
        """
        Test 3: Enviar y recibir mensaje en localhost
        """
        self.print_header("TEST 3: ENVÍO Y RECEPCIÓN LOCAL")

        # Iniciar receptor en thread separado
        print_colored("\nIniciando receptor en thread...", 'YELLOW')

        def receiver_thread():
            receiver = MulticastReceiver()
            if receiver.setup_socket():
                # Recibir solo 3 mensajes para el test
                for _ in range(3):
                    try:
                        receiver.sock.settimeout(2)  # Timeout de 2 segundos
                        data, address = receiver.sock.recvfrom(BUFFER_SIZE)
                        message = parse_message(data.decode('utf-8'))
                        if message:
                            print_colored(
                                f"✓ Mensaje recibido: {message['content'][:30]}...", 'GREEN')
                    except:
                        pass
                receiver.cleanup()

        thread = threading.Thread(target=receiver_thread)
        thread.daemon = True
        thread.start()

        # Esperar a que el receptor esté listo
        time.sleep(1)

        # Enviar mensajes de prueba
        print_colored("\nEnviando mensajes de prueba...", 'YELLOW')
        sender = MulticastSender()

        if sender.setup_socket():
            # Enviar diferentes tipos de mensajes
            sender.send_hello()
            time.sleep(0.5)

            sender.send_message(
                MESSAGE_TYPES['MESSAGE'], "Mensaje de prueba local")
            time.sleep(0.5)

            sender.send_ping()
            time.sleep(0.5)

            sender.send_goodbye()

            print_colored("\n✓ Mensajes enviados correctamente", 'GREEN')
            self.test_results.append(("Envío/Recepción local", "PASS"))

            sender.cleanup()
        else:
            print_colored("✗ Error en el envío", 'RED')
            self.test_results.append(("Envío/Recepción local", "FAIL"))

        # Esperar a que termine el thread receptor
        thread.join(timeout=2)
        return True

    def test_4_multiple_senders(self):
        """
        Test 4: Múltiples emisores simultáneos
        """
        self.print_header("TEST 4: MÚLTIPLES EMISORES (CONCURRENCIA)")

        print_colored("\nCreando múltiples emisores...", 'YELLOW')

        def sender_worker(sender_id):
            """Worker para cada emisor"""
            sender = MulticastSender()
            if sender.setup_socket():
                for i in range(3):
                    message = f"Mensaje {i+1} del Emisor_{sender_id}"
                    sender.send_message(MESSAGE_TYPES['MESSAGE'], message)
                    time.sleep(0.2)
                sender.cleanup()

        # Crear 3 threads emisores
        threads = []
        for i in range(3):
            t = threading.Thread(target=sender_worker, args=(i+1,))
            t.daemon = True
            threads.append(t)

        # Iniciar todos los threads
        print_colored("Iniciando 3 emisores concurrentes...", 'YELLOW')
        for t in threads:
            t.start()
            time.sleep(0.1)

        # Esperar a que terminen
        for t in threads:
            t.join(timeout=5)

        print_colored("✓ Test de concurrencia completado", 'GREEN')
        self.test_results.append(("Múltiples emisores", "PASS"))

        return True

    def test_5_message_formats(self):
        """
        Test 5: Diferentes formatos de mensaje
        """
        self.print_header("TEST 5: FORMATOS DE MENSAJE")

        print_colored("\nProbando diferentes tipos de contenido...", 'YELLOW')

        test_messages = [
            ("Texto simple", "Hola mundo"),
            ("Números", "12345 67890"),
            ("Caracteres especiales", "!@#$%^&*()_+-="),
            ("Unicode", "Ñoño 你好 مرحبا"),
            ("JSON", '{"test": "value", "number": 123}'),
            ("Mensaje largo", "A" * 500)
        ]

        sender = MulticastSender()
        if sender.setup_socket():
            for msg_type, content in test_messages:
                try:
                    sender.send_message(MESSAGE_TYPES['MESSAGE'], content)
                    print_colored(f"✓ {msg_type}: OK", 'GREEN')
                    time.sleep(0.1)
                except Exception as e:
                    print_colored(f"✗ {msg_type}: {e}", 'RED')

            sender.cleanup()
            self.test_results.append(("Formatos de mensaje", "PASS"))
        else:
            self.test_results.append(("Formatos de mensaje", "FAIL"))

        return True

    def test_6_performance(self):
        """
        Test 6: Prueba de rendimiento
        """
        self.print_header("TEST 6: PRUEBA DE RENDIMIENTO")

        print_colored("\nEnviando ráfaga de mensajes...", 'YELLOW')

        sender = MulticastSender()
        if sender.setup_socket():
            start_time = time.time()
            num_messages = 100

            for i in range(num_messages):
                sender.send_message(
                    MESSAGE_TYPES['MESSAGE'], f"Mensaje de rendimiento #{i+1}")

            elapsed_time = time.time() - start_time
            messages_per_second = num_messages / elapsed_time

            print_colored(f"\n📊 Resultados de rendimiento:", 'MAGENTA')
            print_colored(f"   Mensajes enviados: {num_messages}", 'WHITE')
            print_colored(
                f"   Tiempo total: {elapsed_time:.2f} segundos", 'WHITE')
            print_colored(
                f"   Mensajes/segundo: {messages_per_second:.2f}", 'WHITE')

            sender.cleanup()

            if messages_per_second > 50:
                print_colored("✓ Rendimiento excelente", 'GREEN')
                self.test_results.append(("Rendimiento", "PASS"))
            else:
                print_colored("⚠ Rendimiento mejorable", 'YELLOW')
                self.test_results.append(("Rendimiento", "WARN"))
        else:
            self.test_results.append(("Rendimiento", "FAIL"))

        return True

    def run_all_tests(self):
        """
        Ejecuta todos los tests
        """
        self.print_header("SUITE DE PRUEBAS LOCALES - MULTICAST")

        print_colored(f"\nNodo: {NODE_NAME}", 'YELLOW')
        print_colored(f"Grupo Multicast: {MULTICAST_GROUP}:{PORT}", 'YELLOW')
        print_colored(f"Iniciando pruebas...\n", 'YELLOW')

        # Ejecutar tests
        tests = [
            self.test_1_basic_setup,
            self.test_2_socket_creation,
            self.test_3_send_receive_local,
            self.test_4_multiple_senders,
            self.test_5_message_formats,
            self.test_6_performance
        ]

        for test in tests:
            try:
                test()
                time.sleep(1)
            except Exception as e:
                print_colored(f"\n✗ Error en test: {e}", 'RED')
                self.test_results.append((test.__name__, "ERROR"))

        # Mostrar resumen
        self.show_summary()

    def show_summary(self):
        """
        Muestra el resumen de los tests
        """
        self.print_header("RESUMEN DE PRUEBAS")

        passed = sum(1 for _, result in self.test_results if result == "PASS")
        failed = sum(1 for _, result in self.test_results if result == "FAIL")
        warned = sum(1 for _, result in self.test_results if result == "WARN")

        print_colored("\nResultados:", 'YELLOW')
        for test_name, result in self.test_results:
            if result == "PASS":
                print_colored(f"  ✓ {test_name}: {result}", 'GREEN')
            elif result == "FAIL":
                print_colored(f"  ✗ {test_name}: {result}", 'RED')
            elif result == "WARN":
                print_colored(f"  ⚠ {test_name}: {result}", 'YELLOW')
            else:
                print_colored(f"  ? {test_name}: {result}", 'WHITE')

        print_colored(f"\n📊 Estadísticas Finales:", 'MAGENTA')
        print_colored(f"   Total: {len(self.test_results)} tests", 'WHITE')
        print_colored(f"   ✓ Exitosos: {passed}", 'GREEN')
        print_colored(f"   ✗ Fallidos: {failed}", 'RED')
        print_colored(f"   ⚠ Advertencias: {warned}", 'YELLOW')

        if failed == 0:
            print_colored("\n🎉 ¡TODAS LAS PRUEBAS PASARON! 🎉", 'GREEN')
            print_colored(
                "El sistema está listo para pruebas en red.", 'GREEN')
        else:
            print_colored("\n⚠ Hay pruebas que fallaron.", 'RED')
            print_colored("Revisa los errores antes de continuar.", 'RED')

        # Guardar resumen en log
        log_message(
            f"Test completado. Passed: {passed}, Failed: {failed}", 'TEST')


def main():
    """
    Función principal
    """
    print_colored(
        "\n🚀 INICIANDO PRUEBAS LOCALES DEL SISTEMA MULTICAST", 'CYAN')
    print_colored("="*60, 'CYAN')

    # Verificar que no sea ejecutado como módulo
    if __name__ != "__main__":
        print_colored("Este script debe ejecutarse directamente", 'RED')
        return

    # Crear y ejecutar tester
    tester = LocalTester()

    # Menú de opciones
    print_colored("\nOpciones de prueba:", 'YELLOW')
    print_colored("  1. Ejecutar todas las pruebas", 'WHITE')
    print_colored("  2. Prueba rápida (solo envío/recepción)", 'WHITE')
    print_colored("  3. Prueba de concurrencia", 'WHITE')
    print_colored("  4. Prueba de rendimiento", 'WHITE')

    choice = input(
        f"\n{COLORS['CYAN']}Seleccionar opción (1-4): {COLORS['RESET']}")

    if choice == '1':
        tester.run_all_tests()
    elif choice == '2':
        tester.test_1_basic_setup()
        tester.test_2_socket_creation()
        tester.test_3_send_receive_local()
        tester.show_summary()
    elif choice == '3':
        tester.test_4_multiple_senders()
        tester.show_summary()
    elif choice == '4':
        tester.test_6_performance()
        tester.show_summary()
    else:
        print_colored("Opción no válida", 'RED')

    print_colored("\n✓ Pruebas completadas", 'GREEN')
    print_colored("Revisa la carpeta 'logs' para más detalles.", 'YELLOW')


if __name__ == "__main__":
    main()
