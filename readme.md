# 🌐 Sistema Multicast con Concurrencia - Sistemas Distribuidos

## 📋 Descripción
Implementación completa de un sistema de comunicación multicast con soporte para concurrencia avanzada, desarrollado en Python para el curso de Sistemas Distribuidos. El sistema incluye gestión automática de nodos, monitoreo en tiempo real, y herramientas de simulación y diagnóstico.

## ✨ Características Principales
- ✅ **Comunicación Multicast** - Envío y recepción de mensajes en grupo
- ✅ **Concurrencia con Threads** - 4 threads simultáneos por nodo
- ✅ **Detección Automática de Nodos** - Sistema de heartbeat y discovery
- ✅ **Monitoreo en Tiempo Real** - Estadísticas y gráficos de actividad
- ✅ **Simulador Multi-nodo** - Pruebas sin necesidad de múltiples usuarios
- ✅ **Sistema de Agregación** - Recolección de estadísticas independiente del multicast
- ✅ **Herramientas de Diagnóstico** - Tests de conectividad y validación

## 🚀 Instalación Rápida

### 1. Requisitos Previos
- Python 3.8 o superior
- Windows 10/11, Linux o macOS
- VSCode (recomendado)

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

## 📁 Estructura del Proyecto
```
multicast_sistemas_distribuidos/
├── config.py                      # ⚙️ Configuración central del sistema
├── multicast_node.py              # 🎯 Nodo completo con concurrencia (CORE)
│
├── network_monitor.py             # 📊 Monitor de red en tiempo real
├── multi_node_simulator.py        # 🔄 Simulador de múltiples nodos
├── aggregate_stats.py             # 📈 Agregador de estadísticas
├── run_full_test.py               # 🚀 Orquestador de pruebas completas
│
├── test_concurrency.py            # 🧪 Pruebas de concurrencia (6 tests)
├── test_multicast.py              # 🔍 Diagnóstico de conectividad
├── network_connectivity_test.py   # 🔍 Test de conectividad de red
├── quick_check.py                 # ✅ Verificación rápida del sistema
│
├── manage_logs.py                 # 🧹 Gestor interactivo de logs
├── clean_logs.py                  # 🗑️ Limpieza rápida de logs
│
├── logs/                          # 📝 Archivos de log y estadísticas
│   ├── node_stats/               # Estadísticas de nodos individuales
│   ├── aggregate_report_*.txt    # Reportes consolidados
│   └── connectivity_report_*.txt # Reportes de conectividad
├── capturas/                      # 📸 Screenshots para documentación
└── requirements.txt               # 📦 Dependencias Python
```

**Nota:** Los módulos `sender.py`, `receiver.py` y `test_local.py` fueron removidos por redundancia, ya que su funcionalidad está completamente integrada en `multicast_node.py`.

## 🎮 Guía de Uso

### 🔴 IMPORTANTE: Configuración Inicial
Antes de ejecutar, edita `config.py` y configura tu nombre:
```python
NODE_NAME = "Nodo_TuNombre"  # <-- Cambia TuNombre por tu nombre real
```

### � Verificación Rápida del Sistema
```bash
python quick_check.py
```
Este script verifica que todo esté correctamente instalado y configurado.

### 🎯 Opción 1: Prueba Completa Automatizada (RECOMENDADO)
La forma más rápida de probar todo el sistema:

```bash
# Ejecuta simulación completa con 5 nodos y genera reporte
python run_full_test.py --test-option 2
```

Opciones disponibles:
- `--test-option 1`: 2 nodos, 30 segundos (prueba rápida)
- `--test-option 2`: 5 nodos, 60 segundos (prueba estándar)
- `--test-option 3`: 10 nodos, 120 segundos (prueba de carga)
- `--test-option 4`: 3 nodos, 180 segundos (prueba extendida)

### 🎯 Opción 2: Nodo Completo con Concurrencia
Ejecuta un nodo interactivo completo:

```bash
python multicast_node.py
```

**Comandos disponibles:**
- `/help` - Mostrar ayuda
- `/status` - Ver estado del nodo
- `/nodes` - Listar nodos activos
- `/ping` - Enviar ping a todos
- `/stats` - Ver estadísticas detalladas
- `/clear` - Limpiar pantalla
- `/exit` - Salir del programa

### 🎯 Opción 3: Pruebas Básicas (Legacy)

**Test Local Básico:**
```bash
python test_local.py
```

**Receptor y Emisor Separados:**
```bash
# Terminal 1 - Receptor
python receiver.py

# Terminal 2 - Emisor
python sender.py
```

## � Herramientas de Análisis y Diagnóstico

### 📊 Monitor de Red en Tiempo Real
```bash
python network_monitor.py
```
Muestra:
- Estadísticas generales (mensajes, bytes, nodos)
- Tasas de transferencia (actual y promedio)
- Top nodos por actividad
- Distribución de tipos de mensaje
- Gráfico de actividad en tiempo real
- Lista de nodos activos

### 🧪 Simulador de Múltiples Nodos
```bash
python multi_node_simulator.py
```
Opciones de simulación:
1. 2 nodos, 30 segundos - Comportamiento normal
2. 5 nodos, 60 segundos - Comportamiento variado
3. 10 nodos, 120 segundos - Alta carga (chatty)
4. 3 nodos, 180 segundos - Solo pings y heartbeats
5. Personalizado - Configura tus propios parámetros

### 🔍 Test de Concurrencia
```bash
python test_concurrency.py
```
Valida:
- Creación y gestión de threads
- Colas thread-safe (Queue)
- Prevención de race conditions
- Prevención de deadlocks
- Manejo de recursos compartidos con locks

### 🌐 Diagnóstico de Conectividad Multicast
```bash
# Test de envío
python test_multicast.py sender

# Test de recepción (en otra terminal)
python test_multicast.py receiver
```

## 🏗️ Arquitectura del Sistema

### Componentes Principales

#### 1. Nodo Multicast (`multicast_node.py`)
- **4 Threads Concurrentes:**
  - `receiver_thread`: Recibe mensajes del grupo multicast
  - `sender_thread`: Envía mensajes desde cola de salida
  - `heartbeat_thread`: Envía señales de vida cada 30s
  - `monitor_thread`: Actualiza estadísticas cada 10s

- **Sincronización Thread-Safe:**
  - `queue.Queue` para mensajes entrantes/salientes
  - `threading.Lock` para proteger recursos compartidos
  - Prevención de race conditions y deadlocks

- **Gestión de Nodos:**
  - Detección automática de nodos activos
  - Timeout de 90 segundos para nodos inactivos
  - Sistema de heartbeat distribuido

#### 2. Sistema de Agregación de Estadísticas
- **Independiente del Multicast:** No depende de captura de red
- **Basado en Archivos:** Cada nodo escribe sus stats en JSON
- **Agregación Centralizada:** `aggregate_stats.py` consolida datos
- **Solución al Firewall:** Evita bloqueos de Windows Firewall

#### 3. Orquestador de Pruebas (`run_full_test.py`)
- Lanza monitor y simulador automáticamente
- Gestiona ciclo de vida de procesos
- Genera reportes consolidados
- Muestra resumen al finalizar

### Flujo de Datos
```
Nodo A                    Nodo B                    Nodo C
  |                         |                         |
  |--[Mensaje Multicast]--->|                         |
  |                         |--[Mensaje Multicast]--->|
  |<--[Heartbeat]-----------|                         |
  |                         |<--[Heartbeat]-----------|
  |                         |                         |
  v                         v                         v
[Stats JSON]            [Stats JSON]            [Stats JSON]
  |                         |                         |
  +------------+------------+                         |
               |                                      |
               v                                      |
       [aggregate_stats.py]<--------------------------+
               |
               v
       [Reporte Consolidado]
```

## � Resultados Esperados

### Prueba Completa Exitosa
Al ejecutar `python run_full_test.py --test-option 2`, deberías ver:

```
============================================================
   INICIANDO PRUEBA COMPLETA AUTOMATIZADA
============================================================

[1/3] 📊 Lanzando el monitor de red en segundo plano...
     ✓ Monitor de red iniciado.

[2/3] 🚀 Lanzando la simulación de nodos (Opción 2)...

🚀 Iniciando simulación con 5 nodos
✅ Nodo SimNode_1 iniciado (normal)
✅ Nodo SimNode_2 iniciado (quiet)
✅ Nodo SimNode_3 iniciado (chatty)
✅ Nodo SimNode_4 iniciado (ping)
✅ Nodo SimNode_5 iniciado (ping)

📊 ESTADO DE NODOS SIMULADOS
SimNode_1: 🟢 Activo (normal)
SimNode_2: 🟢 Activo (quiet)
SimNode_3: 🟢 Activo (chatty)
SimNode_4: 🟢 Activo (ping)
SimNode_5: 🟢 Activo (ping)

[4/4] 📊 Generando reporte de estadísticas...

============================================================
   RESUMEN DE ESTADÍSTICAS DE NODOS
============================================================

📊 Total de mensajes: 322
📦 Total de bytes: 36,130
👥 Nodos detectados: 5
⚠️  Errores: 0

📈 Actividad por nodo:
   • SimNode_5: 99 mensajes, 11,098 bytes
   • SimNode_3: 92 mensajes, 10,324 bytes
   • SimNode_1: 77 mensajes, 8,637 bytes
   • SimNode_4: 49 mensajes, 5,512 bytes
   • SimNode_2: 5 mensajes, 559 bytes

✅ Prueba finalizada.
```

### Métricas de Rendimiento
- **Latencia de mensajes:** < 100ms en red local
- **Mensajes por segundo:** > 100 msgs/s
- **CPU por nodo:** < 5% en idle, < 15% activo
- **Memoria por nodo:** < 50 MB
- **Threads por nodo:** 4-5 threads activos
- **Tiempo de detección de nodo muerto:** 90 segundos

## �🐛 Solución de Problemas

### Error: "Python no encontrado" o "no se encontró Python"
**Windows:**
- Instalar Python desde https://www.python.org/
- Marcar "Add Python to PATH" durante instalación
- O usar el launcher: `py quick_check.py` en lugar de `python quick_check.py`

### Error: "Address already in use"
```bash
# Windows - Liberar puerto
netstat -ano | findstr :5007
taskkill /F /PID [PID_NUMBER]

# Linux/Mac
lsof -i :5007
kill -9 [PID_NUMBER]
```
O cambiar el puerto en `config.py`:
```python
PORT = 5008  # Cambiar a otro número
```

### Firewall Bloqueando Multicast
**Solución Temporal:**
1. Desactivar Windows Firewall temporalmente
2. Ejecutar pruebas
3. Reactivar firewall

**Solución Permanente:**
- El sistema usa agregación de estadísticas basada en archivos
- No depende de captura multicast para reportes
- Los nodos SÍ se comunican por multicast entre ellos

### Nodos no se detectan entre sí
1. Verificar que todos usan mismo `MULTICAST_GROUP` y `PORT` en `config.py`
2. Verificar firewall permite Python
3. Asegurarse de estar en la misma red local
4. Probar con `test_multicast.py` para diagnóstico

### Error de Encoding/UTF-8 en Windows
Si ves caracteres extraños:
```python
# En tu terminal PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### Threads no se detienen al salir
- Usar `/exit` en lugar de Ctrl+C
- Si persiste, cerrar la terminal completa
- Los threads están marcados como daemon y deberían terminar automáticamente

## ✅ Checklist de Validación

### Configuración Inicial
- [ ] Python 3.8+ instalado y en PATH
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Nombre de nodo configurado en `config.py`
- [ ] Verificación rápida ejecutada (`python quick_check.py`)

### Pruebas Básicas
- [ ] `test_local.py` ejecutado exitosamente
- [ ] `test_concurrency.py` - todas las pruebas pasan
- [ ] `test_multicast.py` - sender y receiver funcionan

### Pruebas de Concurrencia
- [ ] `multicast_node.py` se ejecuta sin errores
- [ ] Los 4 threads se inician correctamente
- [ ] Comandos `/help`, `/status`, `/ping`, `/nodes` funcionan
- [ ] Heartbeats se envían automáticamente
- [ ] Nodos se detectan mutuamente

### Pruebas Completas
- [ ] `run_full_test.py --test-option 1` ejecutado exitosamente
- [ ] `run_full_test.py --test-option 2` muestra 5 nodos activos
- [ ] Reporte agregado generado con estadísticas
- [ ] Monitor de red muestra actividad en tiempo real

### Para el Informe
- [ ] Screenshots de pruebas exitosas
- [ ] Capturas del monitor mostrando estadísticas
- [ ] Logs guardados en carpeta `logs/`
- [ ] Reporte agregado más reciente revisado

## 📸 Capturas Recomendadas para el Informe

1. **Verificación del Sistema:**
   - Salida de `quick_check.py`
   - Salida de `test_concurrency.py` (todas las pruebas pasadas)

2. **Nodo Completo:**
   - `multicast_node.py` ejecutándose con comando `/status`
   - Comando `/nodes` mostrando nodos detectados
   - Comando `/stats` mostrando estadísticas detalladas

3. **Simulación Multi-nodo:**
   - `multi_node_simulator.py` con 5 nodos activos
   - Estado mostrando nodos 🟢 Activo

4. **Prueba Completa:**
   - Salida completa de `run_full_test.py --test-option 2`
   - Resumen de estadísticas mostrando mensajes y bytes

5. **Monitor de Red:**
   - `network_monitor.py` mostrando gráficos de actividad
   - Distribución de mensajes por nodo
   - Tasas de transferencia

6. **Reporte Agregado:**
   - Contenido de `logs/aggregate_report_[timestamp].txt`

## 📝 Comandos Útiles

### Ver logs
```bash
# Windows
type logs\aggregate_report_*.txt | more

# Linux/Mac
cat logs/aggregate_report_*.txt | less
```

### 🧹 Gestión de Logs

#### Opción 1: Gestor Interactivo (RECOMENDADO)
```bash
python manage_logs.py
```
Funciones:
- Ver estadísticas de logs (total, tamaño, antigüedad)
- Listar archivos de log
- Borrar logs antiguos (por días)
- Borrar logs por tipo (connectivity, simulation, stats, network)
- Borrar TODOS los logs

#### Opción 2: Limpieza Rápida
```bash
python clean_logs.py
```
Borra todos los logs con confirmación simple.

#### Opción 3: Comandos Manuales
```bash
# Windows
Remove-Item -Path "logs\sim_node_*" -Force
Remove-Item -Path "logs\node_stats\*" -Force

# Linux/Mac
rm -f logs/sim_node_*
rm -f logs/node_stats/*
```

### Verificar procesos Python activos
```bash
# Windows
wmic process where "name='python.exe'" get ProcessId,CommandLine

# Linux/Mac
ps aux | grep python
```

### Matar todos los procesos Python (si es necesario)
```bash
# Windows
taskkill /F /IM python.exe

# Linux/Mac
killall python
```

## 🎓 Conceptos Implementados

### Sistemas Distribuidos
- ✅ Comunicación por Multicast (one-to-many)
- ✅ Descubrimiento automático de nodos
- ✅ Sistema de heartbeat distribuido
- ✅ Tolerancia a fallos (detección de nodos caídos)

### Concurrencia
- ✅ Programación con threads (4 por nodo)
- ✅ Sincronización con locks
- ✅ Colas thread-safe (producer-consumer)
- ✅ Prevención de race conditions
- ✅ Prevención de deadlocks

### Arquitectura de Software
- ✅ Separación de responsabilidades
- ✅ Modularización del código
- ✅ Configuración centralizada
- ✅ Logging y monitoreo
- ✅ Manejo de errores

## 🚀 Próximos Pasos

### Fase 4: Red Virtual con ZeroTier
1. Instalar ZeroTier One
2. Crear/unirse a una red virtual
3. Modificar `LOCAL_IP` en `config.py` con IP de ZeroTier
4. Coordinar pruebas con compañeros de clase

### Fase 5: Pruebas en Red Real
1. Ejecutar nodos en diferentes máquinas
2. Validar comunicación entre nodos remotos
3. Analizar latencia y rendimiento
4. Documentar resultados para el informe final

## 📧 Soporte y Recursos

**Si tienes problemas:**
1. Ejecutar `python quick_check.py` para diagnóstico
2. Revisar logs en `logs/aggregate_report_*.txt`
3. Verificar firewall y permisos
4. Consultar sección "Solución de Problemas" arriba

**Archivos Clave para Depuración:**
- `logs/sim_node_*_err.log` - Errores de nodos simulados
- `logs/node_stats/*.json` - Estadísticas individuales
- `logs/aggregate_report_*.txt` - Reporte consolidado

---

## 🏆 Estado del Proyecto

**✅ COMPLETADO - Todas las fases de desarrollo local funcionando**

- ✅ Fase 1: Comunicación Multicast Básica
- ✅ Fase 2: Módulos Separados (Sender/Receiver)
- ✅ Fase 3: Concurrencia y Threads
- ✅ Sistema de Monitoreo y Estadísticas
- ✅ Simulador Multi-nodo
- ✅ Herramientas de Diagnóstico
- 🔄 Fase 4: Red Virtual (Siguiente)

**Progreso:** 75% completado 🎉

---

**Proyecto de Sistemas Distribuidos**  
*Implementación de Multicast y Concurrencia*  
*Universidad Técnica Particular de Loja*  
*Noviembre 2025*