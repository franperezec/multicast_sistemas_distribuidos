# 🌐 Sistema Multicast con Concurrencia - Sistemas Distribuidos

## 📋 Descripción
Implementación de un sistema de comunicación multicast con soporte para concurrencia, desarrollado en Python para el curso de Sistemas Distribuidos.

## 🚀 Instalación Rápida

### 1. Requisitos Previos
- Python 3.8 o superior
- Windows 10/11 (o Linux/Mac)
- VSCode (recomendado)

### 2. Instalar Dependencias
```bash
# Opcional - para colores en Windows
pip install colorama
```

## 📁 Estructura del Proyecto
```
multicast_sistemas_distribuidos/
├── config.py           # Configuración central
├── receiver.py         # Módulo receptor
├── sender.py           # Módulo emisor  
├── multicast_node.py   # Nodo completo (Fase 3)
├── test_local.py       # Pruebas locales
├── logs/              # Archivos de log
├── capturas/          # Screenshots Wireshark
└── requirements.txt    # Dependencias
```

## 🎮 Cómo Usar - FASE 2

### 🔴 IMPORTANTE: Configurar tu nombre
Antes de ejecutar, edita `config.py` línea 24:
```python
NODE_NAME = "Nodo_TuNombre"  # <-- Cambia TuNombre por tu nombre real
```

### 📡 Test 1: Prueba Local Básica
```bash
# En una terminal:
python test_local.py
# Seleccionar opción 1 para todas las pruebas
```

### 📡 Test 2: Receptor y Emisor Separados

**Terminal 1 - Receptor:**
```bash
python receiver.py
```

**Terminal 2 - Emisor:**
```bash
python sender.py
# Seleccionar opción 1 (Interactivo)
# Escribir mensajes y presionar Enter
```

### 📡 Test 3: Múltiples Nodos
Abrir 3 o más terminales:

**Terminal 1:**
```bash
python receiver.py
```

**Terminal 2:**
```bash
python sender.py
# Modo 1 - Escribir: "Hola desde Terminal 2"
```

**Terminal 3:**
```bash
python sender.py  
# Modo 1 - Escribir: "Saludos desde Terminal 3"
```

## 🔧 Modos de Operación

### Receptor (receiver.py)
- Escucha continuamente mensajes multicast
- Muestra estadísticas cada 10 mensajes
- `Ctrl+C` para detener

### Emisor (sender.py)
**Modo 1 - Interactivo:**
- Escribir mensajes manualmente
- Comandos especiales:
  - `/ping` - Enviar ping
  - `/stats` - Ver estadísticas
  - `/exit` - Salir

**Modo 2 - Automático:**
- Envía 5 mensajes de prueba
- Intervalo de 2 segundos

**Modo 3 - Burst:**
- Envía múltiples mensajes rápidamente
- Para pruebas de carga

## 📝 Comandos Útiles

### Verificar que funciona:
```bash
# Prueba rápida
python test_local.py
# Elegir opción 2
```

### Ver logs:
```bash
# Windows
type logs\multicast_log.txt

# Linux/Mac
cat logs/multicast_log.txt
```

### Limpiar logs:
```bash
# Windows
del logs\*.txt

# Linux/Mac  
rm logs/*.txt
```

## 🐛 Solución de Problemas

### Error: "Address already in use"
- Esperar 30 segundos
- O cambiar el puerto en `config.py`:
```python
PORT = 5008  # Cambiar a otro número
```

### No se reciben mensajes:
1. Verificar firewall de Windows
2. Ejecutar como administrador
3. Probar con `LOCAL_IP = '127.0.0.1'` en config.py

### Error de permisos:
- Ejecutar terminal como administrador
- O usar puerto > 1024

## ✅ Checklist Fase 2

- [x] Configurar nombre de nodo en config.py
- [x] Ejecutar test_local.py exitosamente
- [x] Probar receiver.py en una terminal
- [x] Probar sender.py en otra terminal
- [x] Ver mensajes enviados/recibidos
- [x] Verificar logs en carpeta logs/
- [x] Tomar screenshots para el informe

## 📊 Resultados Esperados

Al ejecutar `test_local.py` deberías ver:
```
✓ Módulos Python necesarios disponibles
✓ Socket emisor creado correctamente
✓ Socket receptor creado correctamente
✓ Mensaje recibido: Mensaje de prueba local
✓ Test de concurrencia completado
✓ Rendimiento excelente

🎉 ¡TODAS LAS PRUEBAS PASARON! 🎉
```

## 🚀 Siguiente Fase

Una vez que todo funcione localmente:
1. Continuar con Fase 3 (Concurrencia con multicast_node.py)
2. Configurar ZeroTier (Fase 4)
3. Coordinar pruebas con compañeros (Fase 5)

## 📧 Soporte

Si tienes problemas:
1. Revisar los logs en `logs/multicast_log.txt`
2. Verificar que el firewall permite Python
3. Asegurarse de usar Python 3.8+
4. Revisar que el puerto no esté en uso

---

**Proyecto de Sistemas Distribuidos**  
*Implementación de Multicast y Concurrencia*  
*2024*