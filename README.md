# Multi-Agent System with MetaGPT

A comprehensive multi-agent system built with MetaGPT featuring automated audiobook generation, adaptive game creation, and intelligent agent coordination.

## 🚀 Features

- **Automated Audiobook System**: Fully automated multi-agent audiobook generation with LangGraph Swarm technology
- **Adaptive Game Generator**: AI-powered educational game creation with progressive difficulty
- **Multi-Agent Coordination**: Seamless agent-to-agent communication and task handoff
- **Station-Based Architecture**: Modular design with Station 1 (content generation) and Station 2 (processing)
- **Interactive CLI**: Command-line interfaces for testing and manual operation

## 📋 Prerequisites

- Python 3.8+
- Git
- OpenAI API key (for MetaGPT functionality)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/arjunthilak05/multiagentcode.git
cd multiagentcode
```

### 2. Install Dependencies

```bash
# Install MetaGPT and dependencies
pip install -r MetaGPT/requirements.txt

# Install additional dependencies for the multi-agent system
pip install langgraph langchain openai
```

### 3. Configure MetaGPT

```bash
cd MetaGPT
cp config/config2.example.yaml config/config2.yaml
```

Edit `config/config2.yaml` and add your OpenAI API key:

```yaml
OPENAI_API_KEY: "your-api-key-here"
```

## 🎮 Usage

### Automated Audiobook System

Run the fully automated multi-agent audiobook system:

```bash
python automated_runner.py
```

### Testing and Development

**Test the entire system:**
```bash
python test_stations.py
```

**Test automation:**
```bash
python test_automated_swarm.py
# or
python demo_automated_system.py
```

**Run individual stations:**
```bash
# Station 1 (Content Generation)
python station1_cli.py

# Station 2 (Processing)
python station2_cli.py
```

### Adaptive Game Generation

Generate educational games with progressive difficulty:

```bash
cd MetaGPT
python adaptive_game_generator.py
```

## 🏗️ Architecture

### Station-Based Design

- **Station 1**: Content generation and initial processing
- **Station 2**: Advanced processing and output generation
- **Automated Runner**: Coordinates seamless Station 1 → Station 2 execution

### Key Components

- `automated_runner.py`: Main automation orchestrator
- `station1_cli.py`: Station 1 command-line interface
- `station2_cli.py`: Station 2 command-line interface
- `test_stations.py`: Comprehensive system testing
- `MetaGPT/`: MetaGPT framework and adaptive game generator

## 🎯 Generated Content

The system generates:

- **Audiobooks**: Automated multi-agent audiobook creation
- **Educational Games**: Progressive HTML5 games with adaptive difficulty
- **Interactive Content**: Engaging learning experiences

## 📁 Project Structure

```
multiagentcode/
├── automated_runner.py          # Main automation orchestrator
├── station1_cli.py             # Station 1 CLI
├── station2_cli.py             # Station 2 CLI
├── test_stations.py            # System testing
├── test_automated_swarm.py     # Automation testing
├── demo_automated_system.py    # Demo system
├── MetaGPT/                    # MetaGPT framework
│   ├── adaptive_game_generator.py
│   ├── adaptive_games/         # Generated games
│   ├── config/                 # Configuration files
│   └── requirements.txt
└── README.md
```

## 🔧 Configuration

### MetaGPT Configuration

Edit `MetaGPT/config/config2.yaml`:

```yaml
OPENAI_API_KEY: "your-openai-api-key"
MODEL: "gpt-4"  # or your preferred model
```

### System Configuration

The system uses environment variables and configuration files for:
- API keys and authentication
- Model selection and parameters
- Output directories and file paths
- Agent coordination settings

## 🧪 Testing

### Run All Tests

```bash
python test_stations.py
```

### Test Individual Components

```bash
# Test automation
python test_automated_swarm.py

# Test demo system
python demo_automated_system.py

# Test individual stations
python station1_cli.py
python station2_cli.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MetaGPT](https://github.com/geekan/MetaGPT) - The multi-agent framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent coordination
- [OpenAI](https://openai.com/) - Language models

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/arjunthilak05/multiagentcode/issues) page
2. Create a new issue with detailed information
3. Include system information and error logs

## 🔄 Updates

Stay updated with the latest features and improvements:

```bash
git pull origin main
pip install -r MetaGPT/requirements.txt --upgrade
```

---

**Happy coding with multi-agent systems! 🚀**
