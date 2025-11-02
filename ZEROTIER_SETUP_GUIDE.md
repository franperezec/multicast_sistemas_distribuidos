# 🌐 GUÍA COMPLETA DE CONFIGURACIÓN ZEROTIER - FASE 4

## 📋 ÍNDICE
1. [Instalación de ZeroTier](#1-instalación-de-zerotier)
2. [Crear o Unirse a una Red](#2-crear-o-unirse-a-una-red)
3. [Configuración del Proyecto](#3-configuración-del-proyecto)
4. [Pruebas de Conectividad](#4-pruebas-de-conectividad)
5. [Pruebas con Compañeros](#5-pruebas-con-compañeros)
6. [Captura con Wireshark](#6-captura-con-wireshark)
7. [Solución de Problemas](#7-solución-de-problemas)

---

## 1. INSTALACIÓN DE ZEROTIER

### Windows
1. **Descargar ZeroTier One**
   - Ve a: https://www.zerotier.com/download/
   - Descarga "ZeroTier One for Windows"
   - Ejecuta el instalador como Administrador

2. **Instalación**
   - Sigue el asistente de instalación
   - Acepta los permisos de red
   - ZeroTier se minimizará en la bandeja del sistema

3. **Verificar instalación**
   ```cmd
   zerotier-cli info
   ```
   Deberías ver algo como:
   ```
   200 info 1a2b3c4d5e 1.12.2 ONLINE
   ```
   
   **📸 CAPTURA 1:** Screenshot del resultado de `zerotier-cli info`

### Linux/Mac
```bash
# Linux
curl -s https://install.zerotier.com | sudo bash

# Mac
brew install --cask zerotier-one

# Verificar
sudo zerotier-cli info
```

---

## 2. CREAR O UNIRSE A UNA RED

### OPCIÓN A: CREAR TU PROPIA RED (Recomendado para el líder del grupo)

1. **Crear cuenta en ZeroTier Central**
   - Ve a: https://my.zerotier.com
   - Crea una cuenta gratuita
   - Confirma tu email

2. **Crear una red**
   - Click en "Create A Network"
   - Se generará un Network ID de 16 caracteres
   - Ejemplo: `8056c2e21c123456`
   
   **📸 CAPTURA 2:** Screenshot de ZeroTier Central mostrando el Network ID

3. **Configurar la red**
   - Click en el Network ID para entrar a configuración
   - **Settings:**
     - Name: `Multicast_SistemasDistribuidos`
     - Access Control: `Private` ✅
   - **Advanced:**
     - Managed Routes: Dejar default
     - IPv4 Auto-Assign: ✅ Activado
     - Rango: `192.168.195.*` (Easy)
   
   **📸 CAPTURA 3:** Screenshot de la configuración de la red

### OPCIÓN B: UNIRSE A RED EXISTENTE

1. **Obtener el Network ID del coordinador**
   ```
   Ejemplo: 8056c2e21c123456
   ```

2. **Unirse a la red**
   ```cmd
   zerotier-cli join 8056c2e21c123456
   ```
   
   Respuesta esperada:
   ```
   200 join OK
   ```

3. **Esperar autorización**
   - El admin debe autorizar tu dispositivo
   - Toma 1-2 minutos recibir IP

---

## 3. CONFIGURACIÓN DEL PROYECTO

### Paso 1: Ejecutar el asistente de configuración
```bash
python zerotier_setup.py
```

**Menú del asistente:**
1. Verificar instalación ✅
2. Unirse a red (si no lo has hecho)
3. Ver redes actuales
4. **Configurar proyecto** ← IMPORTANTE
5. Crear scripts de prueba

**📸 CAPTURA 4:** Screenshot ejecutando opción 4 del asistente

### Paso 2: Verificar IP asignada
```cmd
zerotier-cli listnetworks
```

Deberías ver algo como:
```
200 listnetworks 8056c2e21c123456 multicast_net 7c:88:5b:xx:xx:xx OK PRIVATE 192.168.195.100/24
```

Tu IP es: `192.168.195.100`

**📸 CAPTURA 5:** Screenshot mostrando tu IP de ZeroTier

### Paso 3: Actualizar config.py
El asistente lo hace automáticamente, pero verifica:

```python
# config.py
LOCAL_IP = '192.168.195.100'  # Tu IP de ZeroTier
NODE_NAME = 'Nodo_TuNombre'   # Tu identificador único
```

---

## 4. PRUEBAS DE CONECTIVIDAD

### Test 1: Verificación completa
```bash
python network_connectivity_test.py
# Opción 1: Todas las pruebas
```

**Resultados esperados:**
- ✅ Configuración Local
- ✅ Estado ZeroTier
- ✅ Binding de Sockets
- ✅ Loopback Multicast
- ⚠️ Ping a Peers (normal si no hay otros nodos)

**📸 CAPTURA 6:** Screenshot del test de conectividad pasando

### Test 2: Prueba de red ZeroTier
```bash
python zerotier_test.py
# Opción 1: Enviar ping
```

---

## 5. PRUEBAS CON COMPAÑEROS

### COORDINACIÓN INICIAL

1. **Compartir información en el grupo:**
   ```
   EQUIPO MULTICAST - INFORMACIÓN
   ================================
   Network ID: 8056c2e21c123456
   
   MIEMBRO 1 (Coordinador):
   - Nombre: Juan
   - Node ID: 1a2b3c4d5e
   - IP: 192.168.195.100
   - NODE_NAME: Nodo_Juan
   
   MIEMBRO 2:
   - Nombre: María
   - Node ID: 2b3c4d5e6f
   - IP: 192.168.195.101
   - NODE_NAME: Nodo_Maria
   
   [...]
   ```

2. **Autorización (Solo el admin)**
   - En https://my.zerotier.com
   - Sección "Members"
   - Marcar checkbox ✅ para cada miembro
   - Verificar que tengan IP asignada
   
   **📸 CAPTURA 7:** Screenshot de Members con todos autorizados

### EJECUCIÓN DE PRUEBAS COORDINADAS

#### Escenario 1: Prueba básica (2 personas)
**Persona A:**
```bash
python multicast_node.py
# Enviar: Hola desde Nodo A
```

**Persona B:**
```bash
python multicast_node.py
# Enviar: Hola desde Nodo B
```

**📸 CAPTURA 8:** Screenshot mostrando mensajes recibidos de otro nodo

#### Escenario 2: Prueba con coordinador (3+ personas)
**Coordinador:**
```bash
python team_test_coordinator.py
# Opción 1: Coordinador
# Registrar miembros
# Ejecutar escenarios
```

**Participantes:**
```bash
python team_test_coordinator.py
# Opción 2: Participante
```

**📸 CAPTURA 9:** Screenshot del coordinador con todos los nodos activos

#### Escenario 3: Monitor de red
**Una persona ejecuta:**
```bash
python network_monitor.py
```

**Otros ejecutan:**
```bash
python multicast_node.py
# Enviar mensajes
```

**📸 CAPTURA 10:** Screenshot del monitor mostrando actividad de múltiples nodos

---

## 6. CAPTURA CON WIRESHARK

### Configuración de Wireshark

1. **Abrir Wireshark**
2. **Seleccionar interfaz ZeroTier**
   - Buscar: `ZeroTier` o `zt#`
   - Ejemplo: `zt2lrule7hj`

3. **Configurar filtro**
   ```
   udp and ip.dst == 224.1.1.1
   ```
   O más específico:
   ```
   udp.port == 5007 and ip.dst == 224.1.1.1
   ```

4. **Iniciar captura**
   - Click en el tiburón azul
   - Ejecutar los nodos y enviar mensajes
   - Detener captura después de 30-60 segundos

### Capturas importantes para el informe:

**📸 CAPTURA 11:** Vista general de paquetes multicast capturados
**📸 CAPTURA 12:** Detalle de un paquete mostrando:
- Source IP (IP ZeroTier del emisor)
- Destination IP (224.1.1.1)
- Protocol: UDP
- Port: 5007

**📸 CAPTURA 13:** Contenido del payload mostrando JSON del mensaje
**📸 CAPTURA 14:** Estadísticas → Conversations → IPv4
**📸 CAPTURA 15:** Estadísticas → Protocol Hierarchy

### Guardar captura
- File → Save As
- Formato: `.pcapng`
- Nombre: `multicast_zerotier_capture.pcapng`

---

## 7. SOLUCIÓN DE PROBLEMAS

### PROBLEMA: "No se detecta IP de ZeroTier"
**Solución:**
```cmd
zerotier-cli listnetworks
```
Si no hay IP:
- Verificar autorización en ZeroTier Central
- Esperar 2-3 minutos
- Reiniciar servicio ZeroTier

### PROBLEMA: "No recibo mensajes de otros nodos"
**Solución:**
1. Verificar firewall:
   ```cmd
   # Windows - Permitir Python
   netsh advfirewall firewall add rule name="Python Multicast" dir=in action=allow program="C:\path\to\python.exe"
   ```

2. Verificar que todos usan:
   - Mismo MULTICAST_GROUP (224.1.1.1)
   - Mismo PORT (5007)
   - IPs de ZeroTier en LOCAL_IP

### PROBLEMA: "Address already in use"
**Solución:**
```cmd
# Windows
netstat -ano | findstr :5007
taskkill /F /PID [número_pid]

# Linux/Mac
lsof -i :5007
kill -9 [pid]
```

### PROBLEMA: "ZeroTier OFFLINE"
**Solución:**
```cmd
# Windows - Reiniciar servicio
net stop ZeroTierOneService
net start ZeroTierOneService

# Linux
sudo systemctl restart zerotier-one
```

---

## ✅ CHECKLIST FINAL FASE 4

### Configuración:
- [ ] ZeroTier instalado y funcionando
- [ ] Unido a la red del equipo
- [ ] Autorizado por el admin
- [ ] IP de ZeroTier recibida
- [ ] config.py actualizado con LOCAL_IP
- [ ] network_connectivity_test.py pasando

### Pruebas:
- [ ] Comunicación exitosa con 1 compañero
- [ ] Comunicación exitosa con 3+ compañeros
- [ ] Monitor mostrando actividad
- [ ] Coordinador de pruebas ejecutado

### Capturas (15 mínimas):
- [ ] 1. zerotier-cli info
- [ ] 2. Network ID en ZeroTier Central
- [ ] 3. Configuración de la red
- [ ] 4. Asistente opción 4
- [ ] 5. IP asignada
- [ ] 6. Test de conectividad
- [ ] 7. Members autorizados
- [ ] 8. Mensajes entre nodos
- [ ] 9. Coordinador activo
- [ ] 10. Monitor con múltiples nodos
- [ ] 11. Wireshark - Vista general
- [ ] 12. Wireshark - Detalle de paquete
- [ ] 13. Wireshark - Payload JSON
- [ ] 14. Wireshark - Conversations
- [ ] 15. Wireshark - Protocol Hierarchy

### Documentación:
- [ ] Logs guardados
- [ ] Reporte de conectividad generado
- [ ] Reporte de equipo generado
- [ ] Captura .pcapng guardada

---

## 📊 MÉTRICAS DE ÉXITO

Si todo funciona correctamente deberías obtener:
- **Latencia entre nodos:** < 50ms
- **Pérdida de paquetes:** 0%
- **Mensajes/segundo:** > 100
- **Nodos detectados:** Todos los del equipo
- **Wireshark:** Capturas claras del tráfico multicast

---

## 🎉 ¡FASE 4 COMPLETADA!

Con todas estas pruebas y capturas tienes evidencia completa de:
1. ✅ Red virtual funcionando
2. ✅ Comunicación multicast en red no local
3. ✅ Múltiples nodos concurrentes
4. ✅ Análisis de tráfico con Wireshark
5. ✅ Sistema completamente funcional

**Siguiente paso:** Fase 5 - Redacción del informe final
