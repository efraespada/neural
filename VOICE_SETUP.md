# Configuración de Voz para Neural AI

## Resumen
Para que tu complemento Neural AI reciba texto del asistente de voz "Hal" en Home Assistant, necesitas configurar el pipeline de asistencia correctamente.

## Pasos de Configuración

### 1. Instalar Complementos Requeridos

#### Opción A: Procesamiento en la Nube (Recomendado para empezar)
- **No se requieren complementos adicionales**
- Usa los servicios de Google/Amazon para STT/TTS
- Más rápido pero requiere conexión a internet

#### Opción B: Procesamiento Local (Recomendado para privacidad)
Instala estos complementos desde HACS:

1. **Whisper** (Speech-to-Text)
   - Busca "Whisper" en HACS
   - Instala y configura con idioma "es"
   - Activa "Vigilancia" y "Actualización automática"

2. **Piper** (Text-to-Speech)
   - Busca "Piper" en HACS
   - Instala y configura con voz en español
   - Recomendado: "es-carlfm-x-low"

3. **OpenWakeWord** (Detección de palabra de activación)
   - Busca "OpenWakeWord" en HACS
   - Instala para detección local de "Hey Hal"

### 2. Configurar el Asistente de Voz

1. Ve a **Ajustes** > **Asistentes de voz**
2. Crea un nuevo asistente llamado **"Hal"**
3. Configura los siguientes parámetros:

#### Para Procesamiento con Neural AI (Recomendado):
- **Idioma**: Español (es)
- **Voz a texto**: Neural (usando OpenRouter + Whisper)
- **Texto a voz**: Google Cloud (o Amazon)
- **Voz**: es-ES-Standard-A
- **Palabra de activación**: "Hey Hal" (OpenWakeWord)

#### Para Procesamiento Local TTS:
- **Idioma**: Español (es)
- **Voz a texto**: Neural (usando OpenRouter + Whisper)
- **Texto a voz**: Piper
- **Voz**: es-carlfm-x-low
- **Palabra de activación**: "Hey Hal" (OpenWakeWord)

### 3. Configurar el Pipeline de Asistencia

Añade esta configuración a tu `configuration.yaml`:

```yaml
assist_pipeline:
  - name: "Neural AI"
    language: "es"
    conversation_engine: "conversation"
    conversation_language: "es"
    stt_engine: "neural"  # Motor STT personalizado usando OpenRouter
    stt_language: "es"
    tts_engine: "cloud"  # o "piper" para local
    tts_language: "es"
    tts_voice: "es-ES-Standard-A"  # o "es-carlfm-x-low" para local
    wake_word_engine: "openwakeword"
    wake_word_id: "neural"
```

### 4. Reiniciar Home Assistant

Después de la configuración, reinicia Home Assistant para que los cambios surtan efecto.

## Cómo Funciona

1. **Detección de Voz**: Cuando dices "Hey Hal", OpenWakeWord detecta la palabra de activación
2. **Conversión de Voz a Texto**: El motor STT "neural" envía el audio a OpenRouter + Whisper para convertir tu voz en texto
3. **Procesamiento**: El texto se envía al componente Neural AI a través del intent handler
4. **Respuesta de IA**: Neural AI procesa el comando y genera una respuesta
5. **Conversión de Texto a Voz**: Google Cloud (o Piper local) convierte la respuesta en voz
6. **Reproducción**: Hal reproduce la respuesta por los altavoces

## Verificación

Para verificar que todo funciona:

1. **Revisa los logs**: Ve a **Configuración** > **Sistema** > **Logs**
2. **Busca mensajes de Neural AI**: Deberías ver logs como "Processing Neural AI intent"
3. **Prueba un comando**: Di "Hey Hal, enciende las luces" y verifica que responda

## Solución de Problemas

### El asistente no responde
- Verifica que el micrófono esté funcionando
- Comprueba que OpenWakeWord esté detectando "Hey Hal"
- Revisa los logs de errores

### No se convierte voz a texto
- Verifica la configuración de Whisper o Google Cloud
- Comprueba la conexión a internet (si usas servicios en la nube)
- Asegúrate de que el idioma esté configurado en español

### No se reproduce la respuesta
- Verifica la configuración de Piper o Google Cloud
- Comprueba que los altavoces estén funcionando
- Revisa la configuración de audio de Home Assistant

## Comandos de Ejemplo

Una vez configurado, puedes usar comandos como:
- "Hey Hal, enciende las luces del salón"
- "Hey Hal, ¿qué temperatura hace?"
- "Hey Hal, reproduce música"
- "Hey Hal, abre las persianas"

El componente Neural AI procesará estos comandos y ejecutará las acciones correspondientes en tu hogar.
