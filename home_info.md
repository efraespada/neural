# Mi Casa

## Descripción General
Casa de 4 plantas con sistema domótico completo.

## Plantas y Habitaciones

### Planta Sótano
- **Despensa**: Luces inteligentes
- **Trastero**: Lavadora, calentador de agua electrico y gas. Sensor consumo de agua.
- **Luces**: `light.depensa`
- **Temperatura**: `sensor.ecowitt_temperature_4`
- **Climatización**: `climate.caldera`

### Planta Baja
- **Salón**: Luces inteligentes, TV con Google Cast, sistema de sonido
- **Cocina**: Electrodomésticos conectados, cámaras de seguridad
- **Comedor**: Luces regulables, mesa para 6 personas
- **Luces**: `light.cocina`
- **Temperatura**: `sensor.ecowitt_temperature_3`
- **Climatización**: `climate.ac_planta_principal` y `climate.caldera`

### Primera Planta  
- **Dormitorio principal**: Climatización individual, persianas automáticas
- **Dormitorio infantil**: Cuna con cámara, luces nocturnas
- **Baño**: Calefacción por suelo radiante
- **Temperatura**: `sensor.ecowitt_temperature_2`
- **Climatización**: `climate.ac_habitaciones` y `climate.caldera`
- **Luces**: `light.distribuidor`

### Ático
- **Despacho**: Iluminación de trabajo, ventilación
- **Zona de juegos**: Consolas y juegos de mesa
- **Luces**: `light.atico`, dispone de la entidad `switch.sync_box_sincronizacion_de_luces` para sincronizar la iluminación con TV o música (Sync Box de HUE).
- **Temperatura**: `sensor.ecowitt_temperature_1`
- **Climatización**: `climate.caldera`

### Escalera
- **Luces**: `light.escalera`

### Garaje
- **Luces**: `light.garaje`

## Sistemas
- **Seguridad**: Alarma Verisure, 4 cámaras IP
- **Climatización**: La entidad global que controla toda la climatización es `input_boolean.climatizar`, pero se pueden definir distintas temperaturas por dispositivo `climate.ac_planta_principal`, `climate.ac_habitaciones` y `climate.caldera`.
- **Red**: WiFi mesh en toda la casa