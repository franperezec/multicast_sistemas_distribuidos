"""
Gestor de Logs para el Sistema de Multicast
Permite limpiar y gestionar los archivos de log generados
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from config import print_colored

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

LOGS_DIR = "logs"


class LogManager:
    def __init__(self):
        self.logs_dir = Path(LOGS_DIR)

    def get_log_stats(self):
        """Obtiene estadísticas de los logs"""
        if not self.logs_dir.exists():
            return None

        stats = {
            'total_files': 0,
            'total_size': 0,
            'by_type': {},
            'oldest': None,
            'newest': None
        }

        for log_file in self.logs_dir.glob('*'):
            if log_file.is_file():
                stats['total_files'] += 1
                size = log_file.stat().st_size
                stats['total_size'] += size

                # Clasificar por tipo
                if 'connectivity' in log_file.name:
                    log_type = 'connectivity'
                elif 'simulation' in log_file.name:
                    log_type = 'simulation'
                elif 'stats' in log_file.name:
                    log_type = 'stats'
                elif 'network' in log_file.name:
                    log_type = 'network'
                else:
                    log_type = 'other'

                if log_type not in stats['by_type']:
                    stats['by_type'][log_type] = {'count': 0, 'size': 0}

                stats['by_type'][log_type]['count'] += 1
                stats['by_type'][log_type]['size'] += size

                # Fecha del archivo
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if stats['oldest'] is None or mtime < stats['oldest']:
                    stats['oldest'] = mtime
                if stats['newest'] is None or mtime > stats['newest']:
                    stats['newest'] = mtime

        return stats

    def show_stats(self):
        """Muestra estadísticas de logs"""
        print_colored("\n" + "="*60, 'CYAN')
        print_colored("   ESTADÍSTICAS DE LOGS", 'CYAN')
        print_colored("="*60, 'CYAN')

        stats = self.get_log_stats()

        if not stats or stats['total_files'] == 0:
            print_colored("\n  ℹ️ No hay archivos de log", 'YELLOW')
            return

        print(f"\n  📊 Total de archivos: {stats['total_files']}")
        print(f"  💾 Tamaño total: {self._format_size(stats['total_size'])}")

        if stats['oldest']:
            print(f"  📅 Log más antiguo: {stats['oldest'].strftime('%Y-%m-%d %H:%M:%S')}")
        if stats['newest']:
            print(f"  📅 Log más reciente: {stats['newest'].strftime('%Y-%m-%d %H:%M:%S')}")

        if stats['by_type']:
            print("\n  📁 Por tipo:")
            for log_type, data in stats['by_type'].items():
                print(f"    • {log_type}: {data['count']} archivos ({self._format_size(data['size'])})")

    def list_logs(self, limit=20):
        """Lista los archivos de log"""
        print_colored("\n" + "="*60, 'CYAN')
        print_colored("   ARCHIVOS DE LOG", 'CYAN')
        print_colored("="*60, 'CYAN')

        if not self.logs_dir.exists():
            print_colored("\n  ℹ️ No hay archivos de log", 'YELLOW')
            return

        files = sorted(self.logs_dir.glob('*'), key=lambda x: x.stat().st_mtime, reverse=True)

        if not files:
            print_colored("\n  ℹ️ No hay archivos de log", 'YELLOW')
            return

        print(f"\n  Mostrando los {min(limit, len(files))} archivos más recientes:\n")

        for i, log_file in enumerate(files[:limit], 1):
            size = self._format_size(log_file.stat().st_size)
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            age = datetime.now() - mtime

            age_str = self._format_age(age)

            print(f"  {i:2d}. {log_file.name}")
            print(f"      Tamaño: {size} | Edad: {age_str}")

        if len(files) > limit:
            print(f"\n  ... y {len(files) - limit} archivos más")

    def delete_old_logs(self, days):
        """Elimina logs más antiguos que X días"""
        if not self.logs_dir.exists():
            print_colored("  ℹ️ No hay carpeta de logs", 'YELLOW')
            return 0

        cutoff_date = datetime.now() - timedelta(days=days)
        deleted = 0
        total_size = 0

        for log_file in self.logs_dir.glob('*'):
            if log_file.is_file():
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff_date:
                    size = log_file.stat().st_size
                    log_file.unlink()
                    deleted += 1
                    total_size += size

        if deleted > 0:
            print_colored(f"\n  ✅ Se eliminaron {deleted} archivos ({self._format_size(total_size)})", 'GREEN')
        else:
            print_colored(f"\n  ℹ️ No hay logs anteriores a {days} días", 'YELLOW')

        return deleted

    def delete_by_type(self, log_type):
        """Elimina logs de un tipo específico"""
        if not self.logs_dir.exists():
            print_colored("  ℹ️ No hay carpeta de logs", 'YELLOW')
            return 0

        pattern = f"*{log_type}*"
        deleted = 0
        total_size = 0

        for log_file in self.logs_dir.glob(pattern):
            if log_file.is_file():
                size = log_file.stat().st_size
                log_file.unlink()
                deleted += 1
                total_size += size

        if deleted > 0:
            print_colored(f"\n  ✅ Se eliminaron {deleted} archivos de tipo '{log_type}' ({self._format_size(total_size)})", 'GREEN')
        else:
            print_colored(f"\n  ℹ️ No se encontraron logs de tipo '{log_type}'", 'YELLOW')

        return deleted

    def delete_all_logs(self):
        """Elimina todos los logs"""
        if not self.logs_dir.exists():
            print_colored("  ℹ️ No hay carpeta de logs", 'YELLOW')
            return 0

        deleted = 0
        total_size = 0

        for log_file in self.logs_dir.glob('*'):
            if log_file.is_file():
                size = log_file.stat().st_size
                log_file.unlink()
                deleted += 1
                total_size += size

        if deleted > 0:
            print_colored(f"\n  ✅ Se eliminaron {deleted} archivos ({self._format_size(total_size)})", 'GREEN')
        else:
            print_colored("  ℹ️ No hay archivos de log", 'YELLOW')

        return deleted

    def _format_size(self, size_bytes):
        """Formatea el tamaño en bytes a formato legible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def _format_age(self, age):
        """Formatea la edad del archivo"""
        if age.days > 0:
            return f"{age.days} día(s)"
        elif age.seconds >= 3600:
            return f"{age.seconds // 3600} hora(s)"
        elif age.seconds >= 60:
            return f"{age.seconds // 60} minuto(s)"
        else:
            return "reciente"


def show_menu():
    """Muestra el menú principal"""
    print_colored("\n" + "="*60, 'CYAN')
    print_colored("   GESTOR DE LOGS", 'CYAN')
    print_colored("="*60, 'CYAN')

    print("\n  Opciones:")
    print("    1. Ver estadísticas de logs")
    print("    2. Listar archivos de log")
    print("    3. Borrar logs antiguos (por días)")
    print("    4. Borrar logs por tipo")
    print("    5. Borrar TODOS los logs")
    print("    0. Salir")


def main():
    """Función principal"""
    manager = LogManager()

    while True:
        show_menu()
        choice = input("\n  Seleccionar opción: ").strip()

        if choice == '0':
            print_colored("\n  👋 ¡Hasta luego!", 'CYAN')
            break

        elif choice == '1':
            manager.show_stats()

        elif choice == '2':
            manager.list_logs()

        elif choice == '3':
            try:
                days = int(input("\n  ¿Borrar logs anteriores a cuántos días? "))
                if days < 0:
                    print_colored("  ❌ El número de días debe ser positivo", 'RED')
                    continue

                print_colored(f"\n  ⚠️ Esto eliminará todos los logs de más de {days} días", 'YELLOW')
                confirm = input("  ¿Continuar? (s/n): ").strip().lower()

                if confirm == 's':
                    manager.delete_old_logs(days)
                else:
                    print_colored("  ❌ Operación cancelada", 'YELLOW')

            except ValueError:
                print_colored("  ❌ Debe ingresar un número válido", 'RED')

        elif choice == '4':
            print("\n  Tipos disponibles:")
            print("    • connectivity")
            print("    • simulation")
            print("    • stats")
            print("    • network")

            log_type = input("\n  Tipo de log a borrar: ").strip()

            if log_type:
                print_colored(f"\n  ⚠️ Esto eliminará todos los logs de tipo '{log_type}'", 'YELLOW')
                confirm = input("  ¿Continuar? (s/n): ").strip().lower()

                if confirm == 's':
                    manager.delete_by_type(log_type)
                else:
                    print_colored("  ❌ Operación cancelada", 'YELLOW')
            else:
                print_colored("  ❌ Debe especificar un tipo", 'RED')

        elif choice == '5':
            print_colored("\n  ⚠️ ADVERTENCIA: Esto eliminará TODOS los archivos de log", 'RED')
            confirm = input("  ¿Está SEGURO? (escriba 'BORRAR' para confirmar): ").strip()

            if confirm == 'BORRAR':
                manager.delete_all_logs()
            else:
                print_colored("  ❌ Operación cancelada", 'YELLOW')

        else:
            print_colored("  ❌ Opción no válida", 'RED')

        input("\n  Presione Enter para continuar...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n  ⏹ Gestor cerrado", 'YELLOW')
    except Exception as e:
        print_colored(f"\n  ❌ Error: {e}", 'RED')
