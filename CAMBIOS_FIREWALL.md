# Cambios para Solución de Problemas de Multicast

## Problema Identificado
El firewall de Windows bloqueaba el tráfico multicast UDP en puerto 5007, impidiendo que los nodos recibieran mensajes.

## Solución Implementada

### 1. Herramientas de Diagnóstico Añadidas

#### `verificar_firewall.py`
Script de diagnóstico que verifica:
- Estado del firewall de Windows
- Existencia de reglas para puerto 5007/UDP
- Reglas para Python
- Política por defecto de tráfico entrante

**Uso:**
```bash
python verificar_firewall.py
```

#### `test_local_multicast.py`
Script de prueba que envía y recibe mensajes multicast en la misma máquina para verificar configuración.

**Uso:**
```bash
python test_local_multicast.py
```

**Resultado esperado:**
- Mensajes enviados: 5
- Mensajes recibidos: 5 ✅

Si recibes 0 mensajes, el firewall está bloqueando.

### 2. Documentación Actualizada

#### `ZEROTIER_SETUP_GUIDE.md`
Se añadió la **Sección 7: CONFIGURACIÓN DE FIREWALL (CRÍTICO)** que incluye:

- Diagnóstico del firewall antes de las pruebas
- Comandos específicos para configurar firewall en Windows/Linux/macOS
- Pasos de verificación
- Solución paso a paso para problemas de recepción de mensajes

### 3. Configuración de Firewall

**Comando recomendado (Windows):**
```powershell
netsh advfirewall firewall add rule name="Multicast Port 5007" dir=in action=allow protocol=UDP localport=5007
```

Ejecutar como Administrador en PowerShell.

## Archivos Eliminados

Los siguientes archivos fueron eliminados por contener información personal o ser temporales:

- `INFO_ZEROTIER.txt` - Contenía IPs y Node IDs personales
- `config_backup_20251110_212508.py` - Backup temporal
- `diagnostico_multicast.py` - Reemplazado por `diagnostico_simple.py`
- `__pycache__/` - Archivos compilados de Python

## Archivos Añadidos a .gitignore

```
INFO_ZEROTIER.txt
config_backup_*.py
```

Estos archivos no se subirán a GitHub para proteger información personal.

## Flujo de Diagnóstico Recomendado

1. **Verificar firewall:**
   ```bash
   python verificar_firewall.py
   ```

2. **Configurar firewall** (si está bloqueando)

3. **Probar recepción local:**
   ```bash
   python test_local_multicast.py
   ```

4. **Si pasa el test local, probar con compañeros:**
   ```bash
   python multicast_node.py
   ```

## Notas para el Informe

Este problema de firewall es común en Windows y debe documentarse en el informe como:
- Problema encontrado durante las pruebas
- Solución implementada con scripts de diagnóstico
- Comando específico para configuración
- Verificación exitosa de la solución

---

**Fecha:** 15 de Noviembre, 2025
**Cambios:** Solución de problemas de firewall bloqueando multicast
