"""
Script Orquestador para Prueba Completa del Sistema Multicast

Este script automatiza la ejecución de una prueba de estrés y monitoreo:
1. Lanza el monitor de red (`network_monitor.py`) en un proceso separado.
2. Lanza el simulador de nodos (`multi_node_simulator.py`) con una opción de prueba predefinida.
3. Espera a que la simulación termine.
4. Detiene el monitor de red de forma limpia.

Uso:
    python run_full_test.py [--test-option <1-4>] [--monitor]

Argumentos:
    --test-option: Número de la prueba a ejecutar (por defecto: 2).
    --monitor: Lanza solo el monitor de red.
"""
import subprocess
import time
import os
import sys
import signal


def print_colored(message, color_code):
    """Imprime un mensaje con color en la terminal."""
    print(f"\033[{color_code}m{message}\033[0m")


def show_monitor_summary():
    """Muestra un resumen del reporte más reciente del monitor."""
    try:
        # Buscar el archivo de reporte más reciente
        log_files = [f for f in os.listdir('logs') if f.startswith(
            'network_monitor_') and f.endswith('.txt')]
        if not log_files:
            print_colored("\n⚠️  No se encontró reporte del monitor.", "93")
            return

        latest_log = max(log_files, key=lambda f: os.path.getmtime(
            os.path.join('logs', f)))
        log_path = os.path.join('logs', latest_log)

        # Leer el archivo
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extraer información clave
        print_colored("\n" + "="*60, "96")
        print_colored("   RESUMEN DEL MONITOR DE RED", "96")
        print_colored("="*60, "96")
        print_colored(f"\n📄 Reporte: {latest_log}", "97")

        # Buscar y mostrar estadísticas clave
        for line in content.split('\n'):
            if 'Duración del monitoreo:' in line or \
               'Total de mensajes:' in line or \
               'Total de bytes:' in line or \
               'Nodos detectados:' in line or \
               'Errores:' in line:
                print_colored(f"   {line.strip()}", "97")

        # Mostrar actividad por nodo si existe
        if 'ACTIVIDAD POR NODO' in content:
            print_colored("\n📊 Actividad por nodo:", "93")
            in_node_section = False
            for line in content.split('\n'):
                if 'ACTIVIDAD POR NODO' in line:
                    in_node_section = True
                    continue
                elif 'TIPOS DE MENSAJES' in line:
                    break
                elif in_node_section and line.strip() and not line.startswith('-'):
                    print_colored(f"   {line.strip()}", "97")

        print_colored("\n" + "="*60, "96")

    except Exception as e:
        print_colored(f"\n⚠️  Error leyendo reporte del monitor: {e}", "93")


def run_full_test(test_option=2):
    """
    Ejecuta la prueba completa, lanzando el monitor y el simulador.
    """
    monitor_process = None
    simulator_process = None

    # Obtener la ruta al ejecutable de Python
    python_executable = sys.executable

    try:
        print_colored("="*60, "96")
        print_colored("   INICIANDO PRUEBA COMPLETA AUTOMATIZADA", "96")
        print_colored("="*60, "96")

        # 1. Lanzar el monitor de red en segundo plano
        print_colored(
            "\n[1/3] 📊 Lanzando el monitor de red en segundo plano...", "93")
        monitor_command = [python_executable,
                           "network_monitor.py", "--non-interactive"]
        monitor_process = subprocess.Popen(monitor_command, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        time.sleep(2)  # Dar tiempo al monitor para que se inicie
        print_colored("     ✓ Monitor de red iniciado.", "92")

        # 2. Lanzar el simulador de nodos
        print_colored(
            f"\n[2/3] 🚀 Lanzando la simulación de nodos (Opción {test_option})...", "93")
        simulator_command = [
            python_executable, "multi_node_simulator.py", f"--test-option={test_option}"]
        # Usamos Popen en lugar de run para que no bloquee y podamos ver la salida en tiempo real si quisiéramos
        simulator_process = subprocess.Popen(simulator_command)

        # Esperar a que el simulador termine
        simulator_process.wait()
        print_colored("\n     ✓ Simulación de nodos completada.", "92")

    except KeyboardInterrupt:
        print_colored("\n\n🛑 Prueba interrumpida por el usuario.", "91")

    finally:
        # 3. Detener los procesos
        print_colored("\n[3/3] 🧹 Limpiando y deteniendo procesos...", "93")
        if simulator_process and simulator_process.poll() is None:
            print_colored("     - Deteniendo simulador...", "90")
            simulator_process.terminate()
            simulator_process.wait()

        if monitor_process and monitor_process.poll() is None:
            print_colored("     - Deteniendo monitor de red...", "90")
            # Crear archivo de señal para que el monitor sepa que debe detenerse
            with open('logs/stop_monitor.signal', 'w') as f:
                f.write('stop')
            # Dar tiempo al monitor para que detecte la señal y se detenga
            time.sleep(2)
            # Si aún está corriendo, terminarlo forzadamente
            if monitor_process.poll() is None:
                monitor_process.terminate()
                try:
                    monitor_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    monitor_process.kill()
            print_colored("     ✓ Monitor detenido.", "92")
            # Limpiar archivo de señal
            try:
                os.remove('logs/stop_monitor.signal')
            except:
                pass

        # Esperar un momento para que se guarden las estadísticas
        time.sleep(1)

        # Generar y mostrar reporte agregado de los nodos
        print_colored("\n[4/4] 📊 Generando reporte de estadísticas...", "93")
        try:
            from aggregate_stats import aggregate_node_stats, generate_aggregate_report

            # Generar reporte
            report_file = generate_aggregate_report()

            # Mostrar resumen
            stats = aggregate_node_stats()
            print_colored("\n" + "="*60, "96")
            print_colored("   RESUMEN DE ESTADÍSTICAS DE NODOS", "96")
            print_colored("="*60, "96")
            print_colored(
                f"\n📊 Total de mensajes: {stats['total_messages']}", "97")
            print_colored(f"📦 Total de bytes: {stats['total_bytes']:,}", "97")
            print_colored(
                f"👥 Nodos detectados: {len(stats['nodes_seen'])}", "97")
            print_colored(f"⚠️  Errores: {stats['errors']}", "97")

            if stats['messages_per_node']:
                print_colored("\n📈 Actividad por nodo:", "93")
                for node, count in sorted(stats['messages_per_node'].items(), key=lambda x: x[1], reverse=True):
                    bytes_total = stats['bytes_per_node'][node]
                    print_colored(
                        f"   • {node}: {count} mensajes, {bytes_total:,} bytes", "97")

            if report_file:
                print_colored(
                    f"\n📄 Reporte completo guardado en: {report_file}", "92")

            print_colored("\n" + "="*60, "96")
        except Exception as e:
            print_colored(f"\n⚠️  Error generando reporte: {e}", "93")

        print_colored("\n✅ Prueba finalizada.", "96")


def run_monitor_only():
    """
    Ejecuta solo el monitor de red de forma interactiva.
    """
    print_colored("📊 Lanzando solo el monitor de red...", "93")
    try:
        subprocess.run([sys.executable, "network_monitor.py"])
    except KeyboardInterrupt:
        print_colored("\n🛑 Monitor detenido por el usuario.", "91")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Orquestador de Pruebas del Sistema Multicast.")
    parser.add_argument("--test-option", type=int, default=2,
                        help="Número de la opción de prueba a ejecutar (1-4). Por defecto: 2.")
    parser.add_argument("--monitor", action="store_true",
                        help="Si se especifica, lanza solo el monitor de red.")

    args = parser.parse_args()

    if not os.path.exists('logs'):
        os.makedirs('logs')

    if args.monitor:
        run_monitor_only()
    else:
        run_full_test(args.test_option)
