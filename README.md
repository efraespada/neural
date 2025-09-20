# Neural AI

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![maintainer](https://img.shields.io/badge/maintainer-%40efrain.espada-blue.svg)](https://github.com/efrain.espada)

Custom integration for Home Assistant that provides local AI capabilities using Ollama or other local AI services. This integration allows you to interact with AI models directly from Home Assistant.

## 🚀 Features

- ✅ **Local AI integration** with Ollama support
- ✅ **Multiple AI models** support
- ✅ **Home Assistant sensors** for AI status
- ✅ **CLI interface** for AI interaction
- ✅ **Service calls** for AI communication
- ✅ **Real-time AI status** monitoring

## 📋 Requirements

- Home Assistant 2024.1.0 or higher
- Ollama or compatible local AI service running
- Python 3.9 or higher

## 🛠️ Installation

### Option 1: HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Add this repository as a custom integration in HACS
3. Search for "Neural AI" in the HACS store
4. Click "Download"
5. Restart Home Assistant
6. Go to **Settings** > **Devices & Services** > **Integrations**
7. Search for "Neural AI" and configure it

### Option 2: Manual installation

1. Download this repository
2. Copy the `neural` folder to `<config_dir>/custom_components/`
3. Restart Home Assistant
4. Configure the integration from the interface

## ⚙️ Configuration

1. Go to **Settings** > **Devices & Services** > **Integrations**
2. Search for "Neural AI" and click "Configure"
3. Enter your **AI service URL** (default: http://localhost:11434)
4. Enter your **default AI model** (default: llama3.2)
5. Done! The integration will start monitoring your AI service

## 🤖 AI Service Setup

### Ollama (Recommended)

1. Install Ollama on your system:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. Start Ollama service:
   ```bash
   ollama serve
   ```

3. Pull a model (e.g., Llama 3.2):
   ```bash
   ollama pull llama3.2
   ```

### Other AI Services

This integration supports any AI service that provides a compatible API endpoint. Configure the URL in the integration settings.

## 🎯 Usage

### Home Assistant Integration

Once configured, you'll have access to:

- **AI Status Sensor**: Shows the current status of your AI service
- **Service Calls**: Send messages to AI and get responses
- **Real-time Monitoring**: Track AI service health and performance

### Service Calls

You can interact with AI using Home Assistant service calls:

```yaml
# Send a message to AI
service: neural.send_message
data:
  message: "Hello, how are you?"
  model: "llama3.2"  # Optional, uses default if not specified
```

```yaml
# Get AI service status
service: neural.get_status
```

```yaml
# List available AI models
service: neural.list_models
```

### CLI Interface

The integration includes a command-line interface for direct AI interaction:

```bash
# Chat with AI
neural ai chat "Hello, how are you?"

# Check AI status
neural ai status

# List available models
neural ai models
```

## 🔧 Configuration Options

- **AI Service URL**: URL of your local AI service (default: http://localhost:11434)
- **Default Model**: Default AI model to use (default: llama3.2)
- **Scan Interval**: How often to check AI service status (default: 10 minutes)

## 📊 Entities

The integration creates the following entities:

- `sensor.neural_ai_chat`: Main AI interaction sensor
- Shows AI service status, available models, and last response time

## 🛠️ Development

### Project Structure

```
neural/
├── core/                    # Core business logic
│   ├── api/                # AI client and API
│   ├── repositories/       # Data access layer
│   ├── use_cases/         # Business logic
│   └── dependency_injection/ # DI container
├── cli/                    # Command-line interface
├── custom_components/      # Home Assistant integration
└── tests/                  # Test suite
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=core --cov-report=html
```

### CLI Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run CLI
python -m cli.main ai chat "Hello"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/efraespada/neural/issues)
- **Discussions**: [GitHub Discussions](https://github.com/efraespada/neural/discussions)

## 🙏 Acknowledgments

- Ollama team for the excellent local AI platform
- Home Assistant community for the integration framework
- All contributors and users

---

**Note**: This integration requires a local AI service to be running. Make sure your AI service is properly configured and accessible before using this integration.