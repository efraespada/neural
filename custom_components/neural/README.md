# Neural AI - Home Assistant Integration

Este complemento integra Neural AI con Home Assistant, permitiendo controlar tu hogar inteligente mediante comandos de voz procesados por IA.

## Características

- **Integración con Assist Pipeline**: Utiliza el sistema de reconocimiento de voz de Home Assistant
- **Múltiples Personalidades**: HAL 9000, JARVIS, KITT, Mother
- **Tres Modos de Trabajo**: Assistant, Supervisor, Autonomic
- **Modelos de IA**: Soporte para múltiples modelos a través de OpenRouter
- **Control Completo**: Ejecuta acciones en Home Assistant basadas en comandos de voz

## Instalación

1. Copia la carpeta `neural` a `custom_components/` en tu directorio de configuración de Home Assistant
2. Reinicia Home Assistant
3. Ve a Configuración > Dispositivos y Servicios > Añadir Integración
4. Busca "Neural AI" y configúralo

## Configuración

### Configuración Inicial

Durante la instalación se te pedirá:

- **Token de Home Assistant**: Long-lived access token
- **Token de OpenRouter**: API key de OpenRouter
- **Modo de Trabajo**: 
  - `assistant`: Ejecuta exactamente lo que pide el usuario
  - `supervisor`: Analiza el contexto y puede negar acciones
  - `autonomic`: Toma decisiones independientes
- **Personalidad**: 
  - `hal9000`: Calmado y metódico
  - `jarvis`: Sofisticado y eficiente
  - `kitt`: Amigable y con sentido del humor
  - `mother`: Cuidadoso y protector
- **Modelo de IA**: Selecciona entre los modelos disponibles
- **Configuración de Voz**: Idioma y timeout

### Configuración del Pipeline de Assist

Para usar comandos de voz, configura el pipeline de Assist:

1. Ve a Configuración > Asistente de Voz
2. Configura un pipeline con:
   - **Idioma**: Español (es)
   - **STT Engine**: Cloud o local
   - **TTS Engine**: Cloud o local
   - **Wake Word**: openWakeWord (opcional)
   - **Conversation Engine**: conversation

## Uso

### Comandos de Voz

Una vez configurado, puedes usar comandos como:

- "Hal, enciende las luces del salón"
- "Jarvis, ajusta la temperatura a 22 grados"
- "Kitt, activa la escena de cine"
- "Mother, revisa el estado de los sensores"

### Servicios

El complemento expone varios servicios:

- `neural.send_message`: Envía un mensaje a la IA
- `neural.get_status`: Obtiene el estado actual
- `neural.update_config`: Actualiza la configuración

### Sensores

- `sensor.neural_ai_status`: Estado de la IA
- `sensor.neural_ai_response`: Última respuesta de la IA

## Personalización

### Modos de Trabajo

- **Assistant**: Ideal para comandos directos
- **Supervisor**: Analiza el contexto antes de actuar
- **Autonomic**: Toma decisiones independientes

### Personalidades

Cada personalidad tiene su propio estilo de comunicación:

- **HAL 9000**: Metódico y a veces inquietante
- **JARVIS**: Sofisticado y eficiente
- **KITT**: Amigable y con humor
- **Mother**: Cuidadoso y protector

## Solución de Problemas

### El complemento no responde a comandos de voz

1. Verifica que el pipeline de Assist esté configurado correctamente
2. Asegúrate de que los tokens sean válidos
3. Revisa los logs para errores

### Errores de conexión

1. Verifica que el token de Home Assistant sea válido
2. Comprueba que el token de OpenRouter sea correcto
3. Asegúrate de que la conexión a internet funcione

## Desarrollo

Este complemento utiliza los casos de uso del CLI de Neural AI, proporcionando una integración completa con Home Assistant.

### Arquitectura

- **Coordinator**: Gestiona el estado y procesa comandos
- **Intent Handler**: Procesa comandos del pipeline de Assist
- **Services**: Expone funcionalidad a través de servicios
- **Sensors**: Proporciona información del estado

## Licencia

Ver el archivo LICENSE para más detalles.
