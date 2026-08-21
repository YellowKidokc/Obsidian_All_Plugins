# Theophysics Backend - Definition Processor & Fruits of Spirit API

A comprehensive backend system for Theophysics research, combining term definition processing with spiritual fruit data and cross-domain mappings.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

### Definition Processor

- **AI-Powered Extraction**: Uses Ollama for intelligent term definition extraction
- **Comprehensive YAML Schema**: Full theophysics term definition template
- **Cross-Domain Mapping**: Bridge physics, theology, philosophy, and consciousness
- **Multiple Interfaces**: CLI, Python API, and Flask REST API
- **Validation & Search**: Built-in validation, search, and statistics

### Fruits of the Spirit API

- **Complete Dataset**: All 9 fruits with theological, physical, and consciousness mappings
- **Greek Etymology**: Original Greek terms and meanings
- **Physics Correlations**: Each fruit mapped to physics concepts (coherence, resonance, etc.)
- **Consciousness States**: Corresponding states of consciousness for each fruit
- **REST API**: Full CRUD operations and advanced queries

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/YellowKidokc/LOWES-BACKEND-CLAUDE.git
cd LOWES-BACKEND-CLAUDE

# Install dependencies
pip install -r requirements.txt

# Install Ollama (for AI features)
# Visit: https://ollama.ai/
```

### Run the API Server

```bash
python app.py
```

The server will start at `http://localhost:5000`

### CLI Usage

```bash
# Interactive chatbot mode
python scripts/definition_cli.py chat

# Extract definitions from a file
python scripts/definition_cli.py extract paper.md

# Get fruits of spirit data
curl http://localhost:5000/api/fruits-of-spirit/
```

## 📚 API Documentation

### Definition Endpoints

#### Chat with AI Processor

```http
POST /api/definitions/chat
Content-Type: application/json

{
  "message": "Extract definitions from this text...",
  "context": "Optional context"
}
```

#### Extract Definitions

```http
POST /api/definitions/extract
Content-Type: application/json

{
  "file_path": "/path/to/file.md"
}
```

#### Create Definition

```http
POST /api/definitions/create
Content-Type: application/json

{
  "term": "Coherence",
  "domain": "physics",
  "definition": "..."
}
```

### Fruits of Spirit Endpoints

#### Get All Fruits

```http
GET /api/fruits-of-spirit/
```

Response:

```json
{
  "fruits": [...],
  "count": 9
}
```

#### Get Specific Fruit

```http
GET /api/fruits-of-spirit/1
GET /api/fruits-of-spirit/name/Love
GET /api/fruits-of-spirit/greek/agape
```

#### Get Physics Mappings

```http
GET /api/fruits-of-spirit/physics-mapping
```

Response:

```json
{
  "mappings": [
    {
      "fruit": "Love",
      "physics_concept": "Coherence",
      "symbol": "χ_love",
      "equation": "C_love = max(correlation(self, other))"
    }
  ]
}
```

#### Get Consciousness Mappings

```http
GET /api/fruits-of-spirit/consciousness-mapping
```

#### Search Fruits

```http
GET /api/fruits-of-spirit/search?q=patience&domain=physics
```

#### Compare Fruits

```http
POST /api/fruits-of-spirit/compare
Content-Type: application/json

{
  "fruits": ["Love", "Joy", "Peace"]
}
```

#### Random Fruit (Daily Meditation)

```http
GET /api/fruits-of-spirit/random
```

#### Theophysics Integration View

```http
GET /api/fruits-of-spirit/theophysics-integration
```

## 🗂️ Project Structure

```
python_backend/
├── api/
│   ├── definition_api.py          # Definition processor endpoints
│   └── fruits_of_spirit_api.py    # Fruits of Spirit endpoints
├── engine/
│   └── definition_processor.py    # Core AI processor
├── utils/
│   └── definition_helpers.py      # Utility functions
├── scripts/
│   └── definition_cli.py          # Command-line interface
├── templates/theophysics/
│   └── term_definition_template.yaml  # YAML schema
├── data/
│   └── fruits_of_spirit.json      # Fruits dataset
├── examples/
│   └── definition_example.py      # Usage examples
├── app.py                         # Main Flask application
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🎯 Use Cases

### 1. Research Paper Analysis

Extract and catalog term definitions from Theophysics papers:

```bash
python scripts/definition_cli.py batch Paper-*.md --output ./definitions
```

### 2. Spiritual Practice Integration

Get daily fruit meditation:

```bash
curl http://localhost:5000/api/fruits-of-spirit/random
```

### 3. Cross-Domain Study

Compare theological concepts with physics:

```bash
curl http://localhost:5000/api/fruits-of-spirit/theophysics-integration
```

### 4. Definition Management

Build and maintain a comprehensive ontology:

```bash
python scripts/definition_cli.py search "coherence" --dir ./definitions
python scripts/definition_cli.py stats ./definitions
```

## 📖 Detailed Documentation

- **[Quick Start Guide](QUICKSTART_DEFINITIONS.md)** - Get started in 5 minutes
- **[Full Documentation](README_DEFINITION_PROCESSOR.md)** - Complete system documentation
- **[API Reference](API_REFERENCE.md)** - Detailed API documentation
- **[Examples](examples/)** - Code examples and tutorials

## 🔧 Configuration

### Ollama Setup

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Start Ollama server
ollama serve
```

### Environment Variables

```bash
export OLLAMA_URL=http://localhost:11434
export OLLAMA_MODEL=llama2
export FLASK_ENV=development
```

## 🧪 Testing

```bash
# Run examples
python examples/definition_example.py

# Test API endpoints
curl http://localhost:5000/api/definitions/status
curl http://localhost:5000/api/fruits-of-spirit/
```

## 📊 Data Schema

### Fruits of Spirit Structure

Each fruit includes:

- **Theological**: Greek term, definition, scripture reference
- **Physical**: Physics concept mapping, equations, symbols
- **Consciousness**: Corresponding consciousness states
- **Practical**: Manifestations, opposites, related virtues

### Definition Schema

Comprehensive YAML template with:

- Core identity (UUID, term, aliases)
- Domain tags (primary/secondary)
- Multiple definitions (theophysics, standard)
- Mathematical formalization
- Cross-domain mapping
- Integration with papers/axioms/laws
- Analogies and sources
- Provenance and metadata

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built for Theophysics research
- Integrates theology, physics, and consciousness studies
- Powered by Ollama AI

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🔗 Related Projects

- [Theophysics Papers](https://github.com/YellowKidokc/Theophysics-Papers)
- [Obsidian Plugin](https://github.com/YellowKidokc/Theophysics-Obsidian)

---

**Made with ❤️ for Theophysics Research**
