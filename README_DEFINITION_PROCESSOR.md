# Theophysics Definition Processor

A comprehensive system for extracting, formatting, and managing term definitions with Ollama chatbot integration.

## Features

- **YAML Template**: Comprehensive schema for Theophysics term definitions
- **Ollama Integration**: Chatbot-style interaction for definition extraction
- **CLI Interface**: Command-line tools for quick access
- **Flask API**: REST endpoints for programmatic access
- **Utility Functions**: Helper functions for validation, search, and conversion

## Files Created

```
python_backend/
├── templates/theophysics/
│   └── term_definition_template.yaml    # Comprehensive YAML schema
├── engine/
│   └── definition_processor.py          # Core processor with Ollama integration
├── api/
│   └── definition_api.py                # Flask REST API endpoints
├── utils/
│   └── definition_helpers.py            # Utility functions
└── scripts/
    └── definition_cli.py                # Command-line interface
```

## Quick Start

### 1. Interactive Chatbot Mode

```bash
cd python_backend
python scripts/definition_cli.py chat
```

This opens an interactive session where you can:

- Ask questions about definitions
- Extract terms from files
- Get help formatting definitions
- Build definitions through conversation

### 2. Extract Definitions from Files

```bash
# Extract from a single file
python scripts/definition_cli.py extract path/to/paper.md

# Save to output file
python scripts/definition_cli.py extract paper.md --output coherence_def.yaml
```

### 3. Batch Process Multiple Files

```bash
python scripts/definition_cli.py batch file1.md file2.md file3.md --output ./definitions
```

### 4. Search Existing Definitions

```bash
python scripts/definition_cli.py search "coherence" --dir ./definitions
```

### 5. Get Statistics

```bash
python scripts/definition_cli.py stats ./definitions
```

## Using the API

### Start Flask Server

First, integrate the definition API into your Flask app:

```python
from api.definition_api import definition_bp

app = Flask(__name__)
app.register_blueprint(definition_bp)
```

### API Endpoints

#### Chat with the Processor

```bash
POST /api/definitions/chat
Content-Type: application/json

{
  "message": "Extract definitions from this text: ...",
  "context": "Optional context",
  "reset": false
}
```

#### Extract Definitions

```bash
POST /api/definitions/extract
Content-Type: application/json

{
  "file_path": "/path/to/file.md"
}
```

#### Create Definition

```bash
POST /api/definitions/create
Content-Type: application/json

{
  "term": "Coherence",
  "domain": "physics",
  "definition": "The measure of correlation...",
  "additional_data": {}
}
```

#### Batch Process

```bash
POST /api/definitions/batch
Content-Type: application/json

{
  "file_paths": ["/path/to/file1.md", "/path/to/file2.md"],
  "output_dir": "./definitions"
}
```

#### Get Template

```bash
GET /api/definitions/template
```

#### Check Status

```bash
GET /api/definitions/status
```

## Python API Usage

### Basic Usage

```python
from engine.definition_processor import DefinitionProcessor

# Initialize processor
processor = DefinitionProcessor(
    ollama_url="http://localhost:11434",
    model="llama2"
)

# Extract definitions from a file
definitions = processor.extract_definitions_from_file("paper.md")

# Chat with the processor
response = processor.chat("What is coherence in physics?")

# Create a YAML definition
yaml_content = processor.create_definition({
    'term': 'Coherence',
    'domain': 'physics',
    'definition': '...'
})
```

### Using Helper Functions

```python
from utils.definition_helpers import *

# Load a definition
definition = load_definition("coherence_def.yaml")

# Validate it
is_valid, errors = validate_definition(definition)

# Search for definitions
results = search_definitions("./definitions", "quantum")

# Get statistics
stats = get_definition_stats("./definitions")

# Convert to markdown
markdown = format_definition_markdown(definition)

# Find by term
file_path = find_definitions_by_term("./definitions", "coherence")
```

## CLI Commands Reference

```bash
# Interactive chat
python definition_cli.py chat [--model MODEL] [--ollama-url URL]

# Extract from file
python definition_cli.py extract FILE [--output FILE] [--format yaml|json|markdown]

# Batch process
python definition_cli.py batch FILE1 FILE2 ... [--output DIR]

# Search definitions
python definition_cli.py search QUERY [--dir DIR]

# Get statistics
python definition_cli.py stats DIR

# Validate definition
python definition_cli.py validate FILE

# Find by term
python definition_cli.py find TERM [--dir DIR]

# Convert to markdown
python definition_cli.py convert FILE [--output FILE]
```

## YAML Schema Overview

The template includes:

- **Core Identity**: UUID, term name, aliases, near terms
- **Domain Tags**: Primary and secondary domains
- **Definitions**: Theophysics (formal, plain, one-line) and standard definitions
- **Mathematical Formalization**: Symbols, LaTeX, equations
- **Cross-Domain Mapping**: Physics, theology, philosophy, consciousness
- **Theophysics Integration**: Papers, axioms, laws, theorems
- **Analogies**: Primary and secondary analogies
- **External Sources**: Wikipedia, SEP, PhilPapers, arXiv
- **Provenance**: Origin, etymology, evolution
- **Metadata**: Status, confidence, related terms

## Integration with Ollama

The system uses Ollama for intelligent definition extraction. Make sure Ollama is running:

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Pull a model if needed
ollama pull llama2
```

Configure the model in your code:

```python
processor = DefinitionProcessor(
    ollama_url="http://localhost:11434",
    model="llama2"  # or "mistral", "codellama", etc.
)
```

## Example Workflow

1. **Extract terms from papers**:

   ```bash
   python definition_cli.py extract Paper-01.md --output ./defs/p1_terms.yaml
   ```

2. **Interactive refinement**:

   ```bash
   python definition_cli.py chat
   # Then: "Refine the definition of coherence to include quantum aspects"
   ```

3. **Validate all definitions**:

   ```bash
   for file in ./definitions/*.yaml; do
     python definition_cli.py validate "$file"
   done
   ```

4. **Generate markdown documentation**:

   ```bash
   python definition_cli.py convert coherence_def.yaml --output coherence.md
   ```

5. **Search and analyze**:
   ```bash
   python definition_cli.py search "quantum" --dir ./definitions
   python definition_cli.py stats ./definitions
   ```

## Customization

### Custom Ollama Prompts

Edit `definition_processor.py` to customize the system prompt:

```python
system_prompt = """Your custom prompt here..."""
```

### Template Modifications

Edit `term_definition_template.yaml` to add or remove fields.

### API Extensions

Add new endpoints in `definition_api.py`:

```python
@definition_bp.route('/custom', methods=['POST'])
def custom_endpoint():
    # Your logic here
    pass
```

## Troubleshooting

### Ollama Connection Issues

```python
# Test connection
import requests
response = requests.get("http://localhost:11434/api/tags")
print(response.json())
```

### File Not Found

Make sure to use absolute paths or correct relative paths:

```python
from pathlib import Path
file_path = Path("paper.md").absolute()
```

### YAML Parsing Errors

Validate YAML syntax:

```bash
python -c "import yaml; yaml.safe_load(open('def.yaml'))"
```

## Next Steps

1. **Integrate with main app**: Add the definition API to your Flask application
2. **Create definition database**: Store definitions in SQLite or PostgreSQL
3. **Add version control**: Track definition changes over time
4. **Build web UI**: Create a web interface for definition management
5. **Automated extraction**: Set up pipelines to extract definitions from new papers

## Support

For issues or questions, check:

- Ollama documentation: https://ollama.ai/
- Flask documentation: https://flask.palletsprojects.com/
- PyYAML documentation: https://pyyaml.org/
