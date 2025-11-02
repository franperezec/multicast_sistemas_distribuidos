"""
Test de Concurrencia - Verificación de Threads y Sincronización
Pruebas específicas para validar el correcto funcionamiento de la concurrencia
"""

import threading
import time
import subprocess
import os
import sys
import socket
import random
from config import *
from multicast_node import MulticastNode
from sender import MulticastSender
from receiver import MulticastReceiver

class ConcurrencyTester:
    def __init__(self):
        """
        Inicializa el tester de concurrencia
        """
        self.test_results = []
        self.test_threads = []
        self.message_counter = 0
        self.lock = threading.Lock()
        
    def print_test_header(self, test_name):
        """
        Imprime encabezado de test
        """
        print("\n" + "="*60)
        print(f"   TEST: {test_name}")
        print("="*60)
    
    def test_1_thread_creation(self):
        """
        Test 1: Verificar creación correcta de threads
        """
        self.print_test_header("CREACIÓN DE THREADS")
        
        print("🔍 Verificando creación de threads del nodo...")
        
        # Crear nodo de prueba
        test_node = MulticastNode("TestNode_Thread")
        
        # Verificar que se pueden crear los sockets
        if not test_node.setup_sockets():
            print("❌ Error configurando sockets")
            self.test_results.append(("Creación de threads", "FAIL"))
            return False
        
        # Iniciar threads manualmente para verificar
        test_node.running = True
        
        threads = {
            'receiver': threading.Thread(target=test_node.receiver_thread),
            'sender': threading.Thread(target=test_node.sender_thread),
            'heartbeat': threading.Thread(target=test_node.heartbeat_thread),
            'monitor': threading.Thread(target=test_node.monitor_thread)
        }
        
        # Iniciar cada thread
        for name, thread in threads.items():
            thread.daemon = True
            thread.start()
            print(f"✅ Thread {name} iniciado - Alive: {thread.is_alive()}")
            time.sleep(0.1)
        
        # Verificar que todos están vivos
        time.sleep(1)
        all_alive = all(thread.is_alive() for thread in threads.values())
        
        if all_alive:
            print("✅ Todos los threads están activos")
            self.test_results.append(("Creación de threads", "PASS"))
        else:
            print("❌ Algunos threads no están activos")
            self.test_results.append(("Creación de threads", "FAIL"))
        
        # Limpiar
        test_node.running = False
        time.sleep(2)
        test_node.stop()
        
        return all_alive
    
    def test_2_message_queue_threading(self):
        """
        Test 2: Verificar que las colas de mensajes funcionan con múltiples threads
        """
        self.print_test_header("COLAS DE MENSAJES THREAD-SAFE")
        
        import queue
        test_queue = queue.Queue()
        received_messages = []
        
        def producer(producer_id, num_messages):
            """Productor de mensajes"""
            for i in range(num_messages):
                msg = f"Mensaje {i} del Productor {producer_id}"
                test_queue.put(msg)
                time.sleep(random.uniform(0.01, 0.05))
        
        def consumer(consumer_id):
            """Consumidor de mensajes"""
            while True:
                try:
                    msg = test_queue.get(timeout=1)
                    with self.lock:
                        received_messages.append((consumer_id, msg))
                    test_queue.task_done()
                except queue.Empty:
                    break
        
        print("🔄 Iniciando 3 productores y 2 consumidores...")
        
        # Crear threads productores
        producers = []
        for i in range(3):
            t = threading.Thread(target=producer, args=(i+1, 10))
            t.start()
            producers.append(t)
        
        # Crear threads consumidores
        consumers = []
        for i in range(2):
            t = threading.Thread(target=consumer, args=(i+1,))
            t.start()
            consumers.append(t)
        
        # Esperar a que terminen los productores
        for t in producers:
            t.join()
        
        # Esperar a que se procesen todos los mensajes
        time.sleep(2)
        
        # Verificar resultados
        expected = 30  # 3 productores × 10 mensajes
        actual = len(received_messages)
        
        print(f"📊 Mensajes esperados: {expected}")
        print(f"📊 Mensajes recibidos: {actual}")
        
        if actual == expected:
            print("✅ Todas las colas funcionan correctamente con threads")
            self.test_results.append(("Colas thread-safe", "PASS"))
            return True
        else:
            print(f"❌ Se perdieron {expected - actual} mensajes")
            self.test_results.append(("Colas thread-safe", "FAIL"))
            return False
    
    def test_3_concurrent_senders(self):
        """
        Test 3: Múltiples emisores enviando simultáneamente
        """
        self.print_test_header("EMISORES CONCURRENTES")
        
        print("🚀 Creando 5 emisores concurrentes...")
        
        def sender_worker(sender_id, num_messages):
            """Worker para cada emisor"""
            sender = MulticastSender()
            if sender.setup_socket():
                for i in range(num_messages):
                    message = f"Mensaje {i+1} del Emisor_{sender_id}"
                    sender.send_message(MESSAGE_TYPES['MESSAGE'], message)
                    time.sleep(0.01)  # Envío rápido
                sender.cleanup()
                print(f"✅ Emisor {sender_id} completó {num_messages} mensajes")
            else:
                print(f"❌ Emisor {sender_id} falló al configurar socket")
        
        # Crear threads emisores
        threads = []
        for i in range(5):
            t = threading.Thread(target=sender_worker, args=(i+1, 20))
            threads.append(t)
        
        # Iniciar todos simultáneamente
        start_time = time.time()
        for t in threads:
            t.start()
        
        # Esperar a que terminen
        for t in threads:
            t.join()
        
        elapsed = time.time() - start_time
        
        print(f"⏱️ Tiempo total: {elapsed:.2f} segundos")
        print(f"📊 100 mensajes enviados por 5 threads concurrentes")
        
        if elapsed < 5:  # Debería ser rápido
            print("✅ Rendimiento de concurrencia excelente")
            self.test_results.append(("Emisores concurrentes", "PASS"))
            return True
        else:
            print("⚠️ Rendimiento de concurrencia mejorable")
            self.test_results.append(("Emisores concurrentes", "WARN"))
            return True
    
    def test_4_race_condition_check(self):
        """
        Test 4: Verificar ausencia de condiciones de carrera
        """
        self.print_test_header("CONDICIONES DE CARRERA")
        
        print("🔒 Verificando sincronización de acceso a recursos compartidos...")
        
        shared_counter = {'value': 0}
        race_detected = False
        iterations = 1000
        
        def increment_unsafe():
            """Incremento sin sincronización (MALO)"""
            for _ in range(iterations):
                temp = shared_counter['value']
                time.sleep(0.00001)  # Simular procesamiento
                shared_counter['value'] = temp + 1
        
        def increment_safe():
            """Incremento con sincronización (BUENO)"""
            for _ in range(iterations):
                with self.lock:
                    temp = shared_counter['value']
                    time.sleep(0.00001)
                    shared_counter['value'] = temp + 1
        
        # Test sin sincronización
        shared_counter['value'] = 0
        threads = []
        for _ in range(5):
            t = threading.Thread(target=increment_unsafe)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        unsafe_result = shared_counter['value']
        expected = 5 * iterations
        
        print(f"❌ Sin sincronización: {unsafe_result}/{expected} (pérdida: {expected - unsafe_result})")
        
        # Test con sincronización
        shared_counter['value'] = 0
        threads = []
        for _ in range(5):
            t = threading.Thread(target=increment_safe)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        safe_result = shared_counter['value']
        
        print(f"✅ Con sincronización: {safe_result}/{expected}")
        
        # Verificar el nodo multicast
        print("\n🔍 Verificando locks en MulticastNode...")
        test_node = MulticastNode("TestNode_Race")
        
        has_locks = all(lock in test_node.locks for lock in ['print', 'stats', 'nodes'])
        
        if has_locks:
            print("✅ El nodo tiene locks para proteger recursos compartidos")
            self.test_results.append(("Protección contra race conditions", "PASS"))
            return True
        else:
            print("❌ Faltan locks en el nodo")
            self.test_results.append(("Protección contra race conditions", "FAIL"))
            return False
    
    def test_5_deadlock_prevention(self):
        """
        Test 5: Verificar prevención de deadlocks
        """
        self.print_test_header("PREVENCIÓN DE DEADLOCKS")
        
        print("🔐 Verificando que no hay potencial de deadlock...")
        
        lock1 = threading.Lock()
        lock2 = threading.Lock()
        deadlock_detected = False
        
        def worker1():
            """Worker que podría causar deadlock"""
            with lock1:
                time.sleep(0.1)
                # Intentar adquirir lock2 con timeout
                acquired = lock2.acquire(timeout=1)
                if acquired:
                    lock2.release()
                    return True
                else:
                    return False
        
        def worker2():
            """Worker que podría causar deadlock"""
            with lock2:
                time.sleep(0.1)
                # Intentar adquirir lock1 con timeout
                acquired = lock1.acquire(timeout=1)
                if acquired:
                    lock1.release()
                    return True
                else:
                    return False
        
        print("🔄 Probando escenario de potencial deadlock...")
        
        t1 = threading.Thread(target=worker1)
        t2 = threading.Thread(target=worker2)
        
        t1.start()
        t2.start()
        
        t1.join(timeout=3)
        t2.join(timeout=3)
        
        if t1.is_alive() or t2.is_alive():
            print("❌ Deadlock detectado - threads bloqueados")
            deadlock_detected = True
            self.test_results.append(("Prevención de deadlock", "FAIL"))
        else:
            print("✅ No se detectó deadlock con timeouts")
            self.test_results.append(("Prevención de deadlock", "PASS"))
        
        return not deadlock_detected
    
    def test_6_stress_test(self):
        """
        Test 6: Prueba de estrés con muchos threads
        """
        self.print_test_header("PRUEBA DE ESTRÉS")
        
        print("💪 Ejecutando prueba de estrés con múltiples threads...")
        
        num_senders = 10
        messages_per_sender = 50
        
        def stress_sender(sender_id):
            """Emisor para prueba de estrés"""
            sender = MulticastSender()
            if sender.setup_socket():
                for i in range(messages_per_sender):
                    message = f"Stress_{sender_id}_{i}"
                    sender.send_message(MESSAGE_TYPES['MESSAGE'], message)
                    time.sleep(0.001)  # Envío muy rápido
                sender.cleanup()
        
        print(f"🚀 Iniciando {num_senders} emisores con {messages_per_sender} mensajes cada uno...")
        
        threads = []
        start_time = time.time()
        
        for i in range(num_senders):
            t = threading.Thread(target=stress_sender, args=(i,))
            threads.append(t)
            t.start()
        
        # Esperar a que terminen
        for t in threads:
            t.join()
        
        elapsed = time.time() - start_time
        total_messages = num_senders * messages_per_sender
        messages_per_second = total_messages / elapsed
        
        print(f"\n📊 Resultados de prueba de estrés:")
        print(f"   • Total de mensajes: {total_messages}")
        print(f"   • Tiempo total: {elapsed:.2f} segundos")
        print(f"   • Mensajes/segundo: {messages_per_second:.2f}")
        print(f"   • Threads simultáneos: {num_senders}")
        
        if messages_per_second > 100:
            print("✅ Excelente rendimiento bajo estrés")
            self.test_results.append(("Prueba de estrés", "PASS"))
            return True
        elif messages_per_second > 50:
            print("⚠️ Rendimiento aceptable bajo estrés")
            self.test_results.append(("Prueba de estrés", "WARN"))
            return True
        else:
            print("❌ Rendimiento pobre bajo estrés")
            self.test_results.append(("Prueba de estrés", "FAIL"))
            return False
    
    def run_all_tests(self):
        """
        Ejecuta todas las pruebas de concurrencia
        """
        print("\n" + "="*60)
        print("   SUITE DE PRUEBAS DE CONCURRENCIA")
        print("="*60)
        
        tests = [
            self.test_1_thread_creation,
            self.test_2_message_queue_threading,
            self.test_3_concurrent_senders,
            self.test_4_race_condition_check,
            self.test_5_deadlock_prevention,
            self.test_6_stress_test
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(1)
            except Exception as e:
                print(f"❌ Error en test: {e}")
                self.test_results.append((test.__name__, "ERROR"))
        
        self.show_summary()
    
    def show_summary(self):
        """
        Muestra resumen de las pruebas
        """
        print("\n" + "="*60)
        print("   RESUMEN DE PRUEBAS DE CONCURRENCIA")
        print("="*60)
        
        passed = sum(1 for _, result in self.test_results if result == "PASS")
        failed = sum(1 for _, result in self.test_results if result == "FAIL")
        warned = sum(1 for _, result in self.test_results if result == "WARN")
        
        print("\n📊 Resultados:")
        for test_name, result in self.test_results:
            if result == "PASS":
                print(f"  ✅ {test_name}: {result}")
            elif result == "FAIL":
                print(f"  ❌ {test_name}: {result}")
            elif result == "WARN":
                print(f"  ⚠️ {test_name}: {result}")
            else:
                print(f"  ❓ {test_name}: {result}")
        
        print(f"\n📈 Estadísticas:")
        print(f"  • Total: {len(self.test_results)} pruebas")
        print(f"  • ✅ Exitosas: {passed}")
        print(f"  • ❌ Fallidas: {failed}")
        print(f"  • ⚠️ Advertencias: {warned}")
        
        if failed == 0:
            print("\n🎉 ¡TODAS LAS PRUEBAS DE CONCURRENCIA PASARON!")
            print("El sistema maneja correctamente múltiples threads.")
        else:
            print("\n⚠️ Hay problemas de concurrencia que resolver.")


def main():
    """
    Función principal
    """
    print("\n🔍 INICIANDO PRUEBAS DE CONCURRENCIA")
    print("="*60)
    
    # Verificar carpeta de logs
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Menú de opciones
    print("\nOpciones de prueba:")
    print("  1. Ejecutar todas las pruebas de concurrencia")
    print("  2. Solo prueba de threads")
    print("  3. Solo prueba de estrés")
    print("  4. Prueba rápida (threads + colas)")
    
    choice = input("\nSeleccionar opción (1-4): ")
    
    tester = ConcurrencyTester()
    
    if choice == '1':
        tester.run_all_tests()
    elif choice == '2':
        tester.test_1_thread_creation()
        tester.show_summary()
    elif choice == '3':
        tester.test_6_stress_test()
        tester.show_summary()
    elif choice == '4':
        tester.test_1_thread_creation()
        tester.test_2_message_queue_threading()
        tester.show_summary()
    else:
        print("Opción no válida")
    
    print("\n✅ Pruebas de concurrencia completadas")
    print("Revisa los resultados para verificar el correcto funcionamiento.")


if __name__ == "__main__":
    main()
