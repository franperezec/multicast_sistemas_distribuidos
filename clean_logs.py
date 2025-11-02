"""
Limpieza Rápida de Logs
Script simple para limpiar logs sin menú interactivo
"""

import sys
import os
from pathlib import Path
from config import print_colored

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

LOGS_DIR = "logs"


def clean_logs():
    """Limpia todos los logs"""
    logs_path = Path(LOGS_DIR)

    if not logs_path.exists():
        print_colored("  ℹ️ No hay carpeta de logs", 'YELLOW')
        return

    files = list(logs_path.glob('*'))

    if not files:
        print_colored("  ℹ️ No hay archivos de log para borrar", 'YELLOW')
        return

    # Calcular tamaño total
    total_size = sum(f.stat().st_size for f in files if f.is_file())
    count = len([f for f in files if f.is_file()])

    print_colored(f"\n  📊 Se encontraron {count} archivos ({total_size / 1024:.2f} KB)", 'CYAN')
    print_colored("  ⚠️ Esto eliminará TODOS los logs", 'YELLOW')

    confirm = input("  ¿Continuar? (s/n): ").strip().lower()

    if confirm == 's':
        deleted = 0
        for log_file in files:
            if log_file.is_file():
                log_file.unlink()
                deleted += 1

        print_colored(f"\n  ✅ Se eliminaron {deleted} archivos ({total_size / 1024:.2f} KB)", 'GREEN')
    else:
        print_colored("  ❌ Operación cancelada", 'YELLOW')


if __name__ == "__main__":
    print_colored("\n" + "="*60, 'CYAN')
    print_colored("   LIMPIEZA RÁPIDA DE LOGS", 'CYAN')
    print_colored("="*60 + "\n", 'CYAN')

    try:
        clean_logs()
    except KeyboardInterrupt:
        print_colored("\n\n  ⏹ Operación cancelada", 'YELLOW')
    except Exception as e:
        print_colored(f"\n  ❌ Error: {e}", 'RED')
