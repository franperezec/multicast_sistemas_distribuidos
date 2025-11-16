# Sistema Multicast con Concurrencia - Sistemas Distribuidos

**Universidad Técnica Particular de Loja**
**Proyecto de Sistemas Distribuidos**
**Noviembre 2025**

---

## Resumen Ejecutivo

Sistema completo de comunicación multicast implementado en Python con soporte avanzado de concurrencia. El proyecto demuestra conceptos fundamentales de sistemas distribuidos incluyendo comunicación en grupo, sincronización multi-hilo, descubrimiento automático de nodos y monitoreo en tiempo real. Incluye herramientas de simulación, diagnóstico y soporte para redes virtuales mediante ZeroTier.

### Estado del Proyecto
**COMPLETADO** - Todas las fases de desarrollo local funcionando correctamente.

- Fase 1: Comunicación Multicast Básica ✓
- Fase 2: Módulos Separados (Sender/Receiver) ✓
- Fase 3: Concurrencia y Threads ✓
- Fase 4: Red Virtual con ZeroTier ✓
- Sistema de Monitoreo y Estadísticas ✓
- Simulador Multi-nodo ✓
- Herramientas de Diagnóstico ✓

---

## Tabla de Contenidos

1. [Características Principales](#características-principales)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación](#instalación)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Guía de Uso](#guía-de-uso)
6. [Arquitectura del Sistema](#arquitectura-del-sistema)
7. [Configuración de Red Virtual (ZeroTier)](#configuración-de-red-virtual-zerotier)
8. [Solución de Problemas](#solución-de-problemas)
9. [Conceptos Implementados](#conceptos-implementados)
10. [Métricas de Rendimiento](#métricas-de-rendimiento)

---

## Características Principales

### Comunicación Multicast
- Envío y recepción de mensajes en grupo mediante UDP multicast
- Dirección de grupo configurable (default: 224.1.1.1:5007)
- Soporte para redes locales y virtuales (ZeroTier)

### Concurrencia
- Sistema multi-hilo con 4 threads concurrentes por nodo
- Sincronización thread-safe mediante locks y colas
- Prevención de race conditions y deadlocks

### Gestión de Nodos
- Detección automática de nodos mediante heartbeat
- Sistema de descubrimiento distribuido
- Timeout automático para nodos inactivos (90 segundos)

### Monitoreo y Análisis
- Monitor de red en tiempo real con estadísticas
- Sistema de agregación de datos independiente
- Generación automática de reportes
- Herramientas de diagnóstico de conectividad

### Simulación y Pruebas
- Simulador de múltiples nodos sin necesidad de máquinas adicionales
- Suite de pruebas de concurrencia (6 tests)
- Validación automática del sistema
- Orquestador de pruebas completas

---

## Requisitos del Sistema

### Software
- **Python**: 3.8 o superior
- **Sistema Operativo**: Windows 10/11, Linux, o macOS
- **Editor recomendado**: Visual Studio Code
- **ZeroTier One** (opcional, para pruebas en red virtual)
- **Wireshark** (opcional, para análisis de tráfico)

### Dependencias Python

El archivo `requirements.txt` contiene las dependencias del proyecto:

```
colorama>=0.4.6           # Opcional: Colores en consola Windows
python-dateutil>=0.8.2    # Opcional: Formato mejorado de logs
```

**Nota importante**: El proyecto funciona con la biblioteca estándar de Python. Las dependencias en `requirements.txt` son **opcionales** y mejoran la experiencia visual (colorama) y el formato de logs (python-dateutil), pero no son obligatorias para el funcionamiento básico.

---

## Instalación

### 1. Clonar o descargar el proyecto
```bash
cd multicast_sistemas_distribuidos
```

### 2. Instalar dependencias (opcional)
```bash
pip install -r requirements.txt
```

O instalar solo lo esencial:
```bash
pip install colorama
```

### 3. Configurar el nodo
Editar `config.py` y establecer un nombre único:
```python
NODE_NAME = "Nodo_TuNombre"  # Reemplazar con tu nombre
LOCAL_IP = '0.0.0.0'         # Para red local
```

### 4. Verificar instalación
```bash
python quick_check.py
```

Este script verifica que todo esté correctamente instalado y configurado.

---

## Estructura del Proyecto

### Componentes Principales

```
multicast_sistemas_distribuidos/
├── config.py                      # Configuración central del sistema
├── multicast_node.py              # Nodo completo con concurrencia (CORE)
│
├── network_monitor.py             # Monitor de red en tiempo real
├── multi_node_simulator.py        # Simulador de múltiples nodos
├── aggregate_stats.py             # Agregador de estadísticas
├── run_full_test.py               # Orquestador de pruebas completas
│
├── test_concurrency.py            # Suite de pruebas de concurrencia
├── test_multicast.py              # Diagnóstico de conectividad multicast
├── network_connectivity_test.py   # Test de conectividad de red
├── quick_check.py                 # Verificación rápida del sistema
│
├── zerotier_setup.py              # Asistente de configuración ZeroTier
├── zerotier_test.py               # Pruebas específicas de ZeroTier
├── verificar_firewall.py          # Diagnóstico de firewall
├── test_local_multicast.py        # Test de recepción local
│
├── manage_logs.py                 # Gestor interactivo de logs
├── clean_logs.py                  # Limpieza rápida de logs
│
├── requirements.txt               # Dependencias Python
├── readme.md                      # Este archivo (documentación principal)
│
├── logs/                          # Archivos de log y estadísticas
│   ├── node_stats/               # Estadísticas de nodos individuales
│   ├── aggregate_report_*.txt    # Reportes consolidados
│   └── connectivity_report_*.txt # Reportes de conectividad
│
└── capturas/                      # Screenshots para documentación
```

### Módulos Legacy (integrados en multicast_node.py)
- `sender.py` - Funcionalidad integrada
- `receiver.py` - Funcionalidad integrada
- `test_local.py` - Reemplazado por quick_check.py

---

## Guía de Uso

### Verificación Inicial

Antes de comenzar, ejecutar la verificación del sistema:
```bash
python quick_check.py
```

### Opción 1: Prueba Completa Automatizada (RECOMENDADO)

La forma más rápida de probar todo el sistema:

```bash
python run_full_test.py --test-option 2
```

**Opciones disponibles:**
- `--test-option 1`: 2 nodos, 30 segundos (prueba rápida)
- `--test-option 2`: 5 nodos, 60 segundos (prueba estándar)
- `--test-option 3`: 10 nodos, 120 segundos (prueba de carga)
- `--test-option 4`: 3 nodos, 180 segundos (prueba extendida)

Esta opción:
- Lanza automáticamente el monitor de red
- Ejecuta el simulador de nodos
- Genera reportes consolidados
- Muestra resumen de estadísticas

### Opción 2: Nodo Interactivo

Ejecutar un nodo completo con interfaz de comandos:

```bash
python multicast_node.py
```

**Comandos disponibles en el nodo:**
- `/help` - Mostrar ayuda
- `/status` - Ver estado del nodo y threads
- `/nodes` - Listar nodos activos detectados
- `/ping` - Enviar ping a todos los nodos
- `/stats` - Ver estadísticas detalladas
- `/clear` - Limpiar pantalla
- `/exit` - Salir del programa

### Opción 3: Simulador de Múltiples Nodos

```bash
python multi_node_simulator.py
```

**Escenarios de simulación:**
1. 2 nodos, 30 segundos - Comportamiento normal
2. 5 nodos, 60 segundos - Comportamiento variado
3. 10 nodos, 120 segundos - Alta carga (chatty)
4. 3 nodos, 180 segundos - Solo pings y heartbeats
5. Personalizado - Configura tus propios parámetros

### Opción 4: Monitor de Red en Tiempo Real

```bash
python network_monitor.py
```

Visualiza:
- Estadísticas generales (mensajes, bytes, nodos)
- Tasas de transferencia (actual y promedio)
- Top nodos por actividad
- Distribución de tipos de mensaje
- Gráfico de actividad en tiempo real
- Lista de nodos activos

### Herramientas de Diagnóstico

**Test de concurrencia:**
```bash
python test_concurrency.py
```
Valida 6 aspectos de la implementación concurrente.

**Diagnóstico de multicast:**
```bash
# Terminal 1 - Receptor
python test_multicast.py receiver

# Terminal 2 - Emisor
python test_multicast.py sender
```

**Test de conectividad completo:**
```bash
python network_connectivity_test.py
```

---

## Arquitectura del Sistema

### Componente Principal: Nodo Multicast

Cada nodo ejecuta **4 threads concurrentes:**

1. **receiver_thread**: Escucha mensajes del grupo multicast
2. **sender_thread**: Procesa y envía mensajes desde cola de salida
3. **heartbeat_thread**: Envía señales de vida cada 30 segundos
4. **monitor_thread**: Actualiza estadísticas cada 10 segundos

### Sincronización Thread-Safe

- **queue.Queue**: Colas para mensajes entrantes y salientes
- **threading.Lock**: Protección de recursos compartidos
- **Event Signaling**: Coordinación entre threads
- **Daemon Threads**: Terminación automática al salir

### Sistema de Agregación de Estadísticas

**Diseño independiente del multicast:**
- Cada nodo escribe estadísticas en archivos JSON
- Agregador central consolida datos sin depender de captura multicast
- Soluciona problemas de firewall bloqueando tráfico
- Permite análisis sin necesidad de captura de paquetes

### Flujo de Comunicación

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

### Gestión de Nodos

- **Detección automática**: Descubrimiento mediante heartbeats
- **Registro de nodos**: Almacenamiento de timestamp de última actividad
- **Limpieza automática**: Eliminación de nodos inactivos (> 90s)
- **Sincronización**: Locks para acceso concurrente a estructuras compartidas

---

## Configuración de Red Virtual (ZeroTier)

### Instalación de ZeroTier

**Windows:**
1. Descargar de https://www.zerotier.com/download/
2. Ejecutar instalador como Administrador
3. Verificar instalación:
```cmd
zerotier-cli info
```

**Linux:**
```bash
curl -s https://install.zerotier.com | sudo bash
sudo zerotier-cli info
```

**macOS:**
```bash
brew install --cask zerotier-one
zerotier-cli info
```

### Configuración de Red

#### Opción A: Crear Red (Coordinador del equipo)

1. Crear cuenta en https://my.zerotier.com
2. Click en "Create A Network"
3. Anotar Network ID (16 caracteres)
4. Configurar:
   - Name: `Multicast_SistemasDistribuidos`
   - Access Control: `Private`
   - IPv4 Auto-Assign: Activado
   - Rango: `192.168.195.*`

#### Opción B: Unirse a Red Existente

```cmd
zerotier-cli join [NETWORK_ID]
```

Esperar autorización del administrador (1-2 minutos).

### Configuración del Proyecto

1. **Ejecutar asistente de configuración:**
```bash
python zerotier_setup.py
# Seleccionar opción 4: Configurar proyecto
```

2. **Verificar IP asignada:**
```cmd
zerotier-cli listnetworks
```

3. **Actualizar config.py:**
```python
LOCAL_IP = '192.168.195.100'  # Tu IP de ZeroTier
NODE_NAME = 'Nodo_TuNombre'
```

### Pruebas de Conectividad

**Test completo:**
```bash
python network_connectivity_test.py
```

**Test específico de ZeroTier:**
```bash
python zerotier_test.py
```

### Configuración de Firewall (CRÍTICO)

El firewall de Windows bloquea por defecto el tráfico multicast UDP. Es necesario configurarlo antes de realizar pruebas.

**Diagnóstico:**
```bash
python verificar_firewall.py
```

**Configuración Windows (PowerShell como Administrador):**
```powershell
netsh advfirewall firewall add rule name="Multicast Port 5007" dir=in action=allow protocol=UDP localport=5007
```

**Verificación:**
```bash
python test_local_multicast.py
```

Resultado esperado: Mensajes enviados = Mensajes recibidos

**Configuración Linux:**
```bash
# UFW
sudo ufw allow 5007/udp

# Firewalld
sudo firewall-cmd --permanent --add-port=5007/udp
sudo firewall-cmd --reload
```

### Pruebas en Equipo

**Coordinador:**
```bash
python team_test_coordinator.py
# Opción 1: Coordinador
```

**Participantes:**
```bash
python team_test_coordinator.py
# Opción 2: Participante
```

### Análisis con Wireshark

1. Seleccionar interfaz ZeroTier (`zt*`)
2. Filtro: `udp.port == 5007 and ip.dst == 224.1.1.1`
3. Capturar durante 30-60 segundos
4. Guardar como: `multicast_zerotier_capture.pcapng`

**Capturas recomendadas para documentación:**
- Vista general de paquetes multicast
- Detalle de paquete (IP source/dest, protocolo, puerto)
- Payload mostrando JSON del mensaje
- Estadísticas: Conversations → IPv4
- Protocol Hierarchy

---

## Solución de Problemas

### Error: "Address already in use"

**Windows:**
```cmd
netstat -ano | findstr :5007
taskkill /F /PID [PID_NUMBER]
```

**Linux/Mac:**
```bash
lsof -i :5007
kill -9 [PID_NUMBER]
```

**Alternativa**: Cambiar puerto en `config.py`

### Nodos no se detectan entre sí

1. Verificar mismo `MULTICAST_GROUP` y `PORT` en `config.py`
2. Verificar firewall permite puerto 5007/UDP
3. Asegurarse de estar en la misma red (local o ZeroTier)
4. Ejecutar diagnóstico:
```bash
python network_connectivity_test.py
```

### Firewall bloqueando multicast

**Diagnóstico completo:**
```bash
python verificar_firewall.py
```

**Prueba de recepción local:**
```bash
python test_local_multicast.py
```

Si recibes 0 mensajes, el firewall está bloqueando el tráfico.

**Solución permanente:**
- Configurar regla de firewall para puerto 5007/UDP (ver sección ZeroTier)
- El sistema usa agregación de estadísticas basada en archivos como alternativa

### No se detecta IP de ZeroTier

1. Verificar autorización en ZeroTier Central (https://my.zerotier.com)
2. Esperar 2-3 minutos para asignación de IP
3. Reiniciar servicio:
```cmd
# Windows
net stop ZeroTierOneService
net start ZeroTierOneService

# Linux
sudo systemctl restart zerotier-one
```

### ZeroTier OFFLINE

Verificar estado:
```cmd
zerotier-cli info
```

Si muestra `OFFLINE`, reiniciar servicio (ver comando arriba).

### Threads no se detienen

- Usar `/exit` en lugar de Ctrl+C
- Si persiste, cerrar terminal completa
- Los threads están marcados como daemon y deberían terminar automáticamente

---

## Conceptos Implementados

### Sistemas Distribuidos
- Comunicación multicast (one-to-many)
- Descubrimiento automático de nodos
- Sistema de heartbeat distribuido
- Tolerancia a fallos (detección de nodos caídos)
- Coordinación distribuida

### Concurrencia
- Programación multi-hilo (4 threads por nodo)
- Sincronización con locks
- Colas thread-safe (producer-consumer pattern)
- Prevención de race conditions
- Prevención de deadlocks
- Manejo seguro de recursos compartidos

### Arquitectura de Software
- Separación de responsabilidades
- Modularización del código
- Configuración centralizada
- Logging estructurado y monitoreo
- Manejo robusto de errores
- Patrones de diseño (Observer, Producer-Consumer)

### Redes de Computadoras
- Protocolo UDP
- Direccionamiento multicast
- Sockets de red
- Time-To-Live (TTL) para multicast
- Redes virtuales privadas (ZeroTier)

---

## Métricas de Rendimiento

### Rendimiento Esperado
- **Latencia de mensajes**: < 100ms en red local, < 50ms en ZeroTier
- **Throughput**: > 100 mensajes/segundo
- **CPU por nodo**: < 5% en idle, < 15% en actividad
- **Memoria por nodo**: < 50 MB
- **Threads por nodo**: 4-5 threads activos
- **Tiempo de detección de nodo muerto**: ~90 segundos
- **Pérdida de paquetes**: 0% en condiciones normales

### Resultados de Prueba Exitosa

Al ejecutar `python run_full_test.py --test-option 2`:

```
============================================================
   RESUMEN DE ESTADÍSTICAS DE NODOS
============================================================

Total de mensajes: 322
Total de bytes: 36,130
Nodos detectados: 5
Errores: 0

Actividad por nodo:
   • SimNode_5: 99 mensajes, 11,098 bytes
   • SimNode_3: 92 mensajes, 10,324 bytes
   • SimNode_1: 77 mensajes, 8,637 bytes
   • SimNode_4: 49 mensajes, 5,512 bytes
   • SimNode_2: 5 mensajes, 559 bytes

Prueba finalizada.
```

---

## Gestión de Logs

### Opción 1: Gestor Interactivo (RECOMENDADO)
```bash
python manage_logs.py
```

Funciones:
- Ver estadísticas de logs
- Listar archivos
- Borrar por antigüedad (días)
- Borrar por tipo
- Borrar todos

### Opción 2: Limpieza Rápida
```bash
python clean_logs.py
```

### Ubicación de Logs
```
logs/
├── node_stats/                  # Estadísticas JSON por nodo
├── aggregate_report_*.txt       # Reportes consolidados
├── connectivity_report_*.txt    # Reportes de conectividad
├── network_monitor_*.log        # Logs del monitor
└── sim_node_*_err.log          # Errores de nodos simulados
```

---

## Checklist de Validación

### Configuración Inicial
- [ ] Python 3.8+ instalado
- [ ] Dependencias instaladas (opcional)
- [ ] Nombre de nodo configurado en `config.py`
- [ ] `quick_check.py` ejecutado exitosamente

### Pruebas Básicas
- [ ] `test_concurrency.py` - 6 tests pasados
- [ ] `test_multicast.py` - sender y receiver funcionan
- [ ] `test_local_multicast.py` - recepción local funciona

### Pruebas de Sistema
- [ ] `multicast_node.py` ejecuta sin errores
- [ ] Los 4 threads se inician correctamente
- [ ] Comandos `/status`, `/nodes`, `/ping` funcionan
- [ ] Heartbeats se envían automáticamente

### Pruebas Completas
- [ ] `run_full_test.py --test-option 2` exitoso
- [ ] 5 nodos simulados activos
- [ ] Reporte agregado generado
- [ ] Monitor muestra actividad en tiempo real

### ZeroTier (Fase 4)
- [ ] ZeroTier instalado y funcionando
- [ ] Unido a red del equipo
- [ ] IP de ZeroTier recibida
- [ ] Firewall configurado correctamente
- [ ] Comunicación exitosa con compañeros
- [ ] Captura Wireshark realizada

### Documentación
- [ ] Screenshots de pruebas
- [ ] Logs guardados
- [ ] Reportes generados
- [ ] Capturas de Wireshark (si aplica)

---

## Comandos Útiles de Referencia

### Ver logs
```bash
# Windows
type logs\aggregate_report_*.txt | more

# Linux/Mac
cat logs/aggregate_report_*.txt | less
```

### Verificar procesos Python activos
```bash
# Windows
wmic process where "name='python.exe'" get ProcessId,CommandLine

# Linux/Mac
ps aux | grep python
```

### Matar procesos Python (emergencia)
```bash
# Windows
taskkill /F /IM python.exe

# Linux/Mac
killall python
```

### Verificar puerto en uso
```bash
# Windows
netstat -ano | findstr :5007

# Linux/Mac
lsof -i :5007
```

---

## Recursos y Soporte

### Archivos Clave para Depuración
- `logs/sim_node_*_err.log` - Errores de nodos simulados
- `logs/node_stats/*.json` - Estadísticas individuales de nodos
- `logs/aggregate_report_*.txt` - Reporte consolidado de actividad

### Herramientas de Diagnóstico
1. `quick_check.py` - Verificación general del sistema
2. `verificar_firewall.py` - Diagnóstico de firewall
3. `test_local_multicast.py` - Test de recepción local
4. `network_connectivity_test.py` - Test completo de conectividad

### Para Más Información
- Documentación de ZeroTier: https://docs.zerotier.com
- Wireshark User Guide: https://www.wireshark.org/docs/
- Python Threading: https://docs.python.org/3/library/threading.html
- Python Sockets: https://docs.python.org/3/library/socket.html

---

## Licencia

Proyecto académico desarrollado para el curso de Sistemas Distribuidos.
Universidad Técnica Particular de Loja - 2025

---

**Última actualización**: Noviembre 2025
**Versión**: 1.0 - Proyecto Completo
