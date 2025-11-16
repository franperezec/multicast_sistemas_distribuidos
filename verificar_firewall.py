"""
Verificador de Firewall para Multicast
Identifica si el firewall está bloqueando el puerto 5007/UDP
"""

import subprocess
import sys

print("="*70)
print("VERIFICACION DE FIREWALL - Puerto 5007/UDP")
print("="*70)

def run_command(cmd):
    """Ejecuta comando y retorna output"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=True
        )
        return result.stdout, result.returncode
    except Exception as e:
        return str(e), -1

# 1. Estado del Firewall
print("\n1. ESTADO DEL FIREWALL")
print("-" * 70)
output, code = run_command('netsh advfirewall show allprofiles state')
if code == 0:
    for line in output.split('\n'):
        if 'State' in line or 'Estado' in line:
            print(f"  {line.strip()}")
            if 'ON' in line.upper():
                print("  -> Firewall ACTIVO (puede estar bloqueando)")
else:
    print("  [ERROR] No se pudo verificar estado del firewall")

# 2. Reglas existentes para puerto 5007
print("\n2. REGLAS PARA PUERTO 5007")
print("-" * 70)
output, code = run_command('netsh advfirewall firewall show rule name=all | findstr /i "5007"')
if code == 0 and output.strip():
    print("  Reglas encontradas:")
    print(output)
else:
    print("  [INFO] NO hay reglas especificas para puerto 5007")
    print("  -> Esto significa que el puerto probablemente esta bloqueado por defecto")

# 3. Reglas que mencionen "Multicast" o "Python"
print("\n3. REGLAS RELACIONADAS CON MULTICAST O PYTHON")
print("-" * 70)
output, code = run_command('netsh advfirewall firewall show rule name=all | findstr /i "multicast python"')
if code == 0 and output.strip():
    print("  Reglas encontradas:")
    print(output)
else:
    print("  [INFO] No hay reglas para Multicast o Python")

# 4. Verificar política por defecto para UDP entrante
print("\n4. POLITICA POR DEFECTO PARA TRAFICO ENTRANTE")
print("-" * 70)
output, code = run_command('netsh advfirewall show allprofiles')
if code == 0:
    for line in output.split('\n'):
        if 'Inbound' in line or 'Entrada' in line:
            print(f"  {line.strip()}")

# 5. Verificar si Python tiene permisos
print("\n5. REGLAS PARA PYTHON.EXE")
print("-" * 70)
output, code = run_command('netsh advfirewall firewall show rule name=all | findstr /i "python.exe"')
if code == 0 and output.strip():
    print("  Reglas para Python encontradas:")
    lines = output.split('\n')
    for line in lines[:20]:  # Primeras 20 líneas
        if line.strip():
            print(f"  {line.strip()}")
    if len(lines) > 20:
        print(f"  ... y {len(lines) - 20} lineas mas")
else:
    print("  [INFO] NO hay reglas especificas para Python")
    print("  -> Python probablemente esta bloqueado por defecto")

# 6. Resumen y Diagnóstico
print("\n" + "="*70)
print("DIAGNOSTICO")
print("="*70)

# Analizar resultados
firewall_activo = False
regla_5007 = False
regla_python = False

output, code = run_command('netsh advfirewall show allprofiles state')
if 'ON' in output.upper():
    firewall_activo = True

output, code = run_command('netsh advfirewall firewall show rule name=all | findstr /i "5007"')
if code == 0 and output.strip():
    regla_5007 = True

output, code = run_command('netsh advfirewall firewall show rule name=all | findstr /i "python"')
if code == 0 and output.strip():
    regla_python = True

print("\nESTADO:")
print(f"  Firewall activo: {'SI' if firewall_activo else 'NO'}")
print(f"  Regla para puerto 5007: {'SI' if regla_5007 else 'NO'}")
print(f"  Regla para Python: {'SI' if regla_python else 'NO'}")

print("\nCONCLUSION:")
if firewall_activo and not regla_5007:
    print("  [PROBLEMA ENCONTRADO]")
    print("  El firewall esta ACTIVO pero NO hay regla para puerto 5007/UDP")
    print("  -> Esto esta bloqueando el trafico multicast")
    print("\n  SOLUCION:")
    print("  Ejecuta como Administrador:")
    print('  netsh advfirewall firewall add rule name="Multicast 5007" ^')
    print('  dir=in action=allow protocol=UDP localport=5007')
elif firewall_activo and regla_5007:
    print("  [INFO]")
    print("  El firewall esta activo PERO hay reglas para puerto 5007")
    print("  -> Verifica que las reglas permitan (action=allow) el trafico")
elif not firewall_activo:
    print("  [INFO]")
    print("  El firewall esta DESACTIVADO")
    print("  -> El problema NO es el firewall")
    print("  -> Verifica la configuracion de ZeroTier o la interfaz de red")

# 7. Comando recomendado
print("\n" + "="*70)
print("COMANDO RECOMENDADO PARA SOLUCIONAR")
print("="*70)
if firewall_activo and not regla_5007:
    print("\nEjecuta este comando en PowerShell como ADMINISTRADOR:\n")
    print('netsh advfirewall firewall add rule name="Multicast Port 5007" dir=in action=allow protocol=UDP localport=5007')
    print("\nDespues ejecuta de nuevo: python test_local_multicast.py")
else:
    print("\nEl firewall no parece ser el problema principal.")
    print("Verifica:")
    print("  1. Configuracion de ZeroTier (broadcast habilitado)")
    print("  2. Interfaz de red correcta")
    print("  3. Ejecuta: python test_local_multicast.py")

print("\n" + "="*70)
