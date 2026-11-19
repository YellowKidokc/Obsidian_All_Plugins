# Quick Start: Definition Processor

Get started with the Theophysics Definition Processor in 5 minutes.

## Prerequisites

1. **Python 3.8+** installed
2. **Ollama** running locally (for AI features)
3. **Required packages**:
   ```bash
   pip install pyyaml requests flask
   ```

## Installation

```bash
cd python_backend
pip install -r requirements.txt
```

## Quick Examples

### 1. Interactive Chat (Recommended for First Time)

```bash
python scripts/definition_cli.py chat
```

**Try these commands:**

```
You: I need to extract definitions from a paper
You: extract path/to/paper.md
You: create coherence
You: help
```

### 2. Extract from a File

```bash
# Extract definitions
python scripts/definition_cli.py extract your_paper.md

# Save to YAML
python scripts/definition_cli.py extract your_paper.md --output coherence.yaml
```

### 3. Run Examples

```bash
python examples/definition_example.py
```

Select an example to see how the system works.

## Common Tasks

### Task 1: Process a New Paper

```bash
# Extract all terms
python scripts/definition_cli.py extract Paper-01.md --output p1_defs.yaml

# Review and validate
python scripts/definition_cli.py validate p1_defs.yaml

# Convert to markdown for documentation
python scripts/definition_cli.py convert p1_defs.yaml --output p1_defs.md
```

### Task 2: Build a Definition Library

```bash
# Process multiple papers
python scripts/definition_cli.py batch Paper-*.md --output ./definitions

# Get statistics
python scripts/definition_cli.py stats ./definitions

# Search for specific terms
python scripts/definition_cli.py search "quantum" --dir ./definitions
```

### Task 3: Interactive Definition Building

```bash
python scripts/definition_cli.py chat
```

Then in the chat:

```
You: I want to create a definition for "Coherence"
Assistant: I'll help you create a definition. Let me ask some questions...
You: It's a physics term related to wave functions
Assistant: Great! What's the mathematical formulation?
You: C = 1 - S_obs/S_max
...
```

## Using in Your Code

### Python Script

```python
from engine.definition_processor import DefinitionProcessor
from utils.definition_helpers import *

# Initialize
processor = DefinitionProcessor()

# Extract from file
definitions = processor.extract_definitions_from_file("paper.md")

# Create YAML
yaml_content = processor.create_definition({
    'term': 'Coherence',
    'domain': 'physics'
})

# Save
with open('coherence.yaml', 'w') as f:
    f.write(yaml_content)
```

### Flask API

```python
from flask import Flask
from api.definition_api import definition_bp

app = Flask(__name__)
app.register_blueprint(definition_bp)

if __name__ == '__main__':
    app.run(debug=True)
```

Then use the API:

```bash
# Extract definitions
curl -X POST http://localhost:5000/api/definitions/extract \
  -H "Content-Type: application/json" \
  -d '{"file_path": "paper.md"}'

# Chat
curl -X POST http://localhost:5000/api/definitions/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is coherence?"}'
```

## File Structure

After running the examples, you'll have:

```
python_backend/
├── definitions/           # Generated definitions
│   ├── coherence.yaml
│   ├── entropy.yaml
│   └── logos.yaml
├── coherence.md          # Markdown documentation
└── batch_definitions/    # Batch processed files
```

## Troubleshooting

### Ollama Not Running

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama (if needed)
ollama serve

# Pull a model
ollama pull llama2
```

### Import Errors

```bash
# Make sure you're in the right directory
cd python_backend

# Install dependencies
pip install -r requirements.txt
```

### File Not Found

Use absolute paths or check your current directory:

```bash
python scripts/definition_cli.py extract "$(pwd)/paper.md"
```

## Next Steps

1. **Read the full documentation**: `README_DEFINITION_PROCESSOR.md`
2. **Explore the template**: `templates/theophysics/term_definition_template.yaml`
3. **Try the examples**: `python examples/definition_example.py`
4. **Integrate with your workflow**: Add to your existing scripts

## Tips

- **Start with chat mode** to understand how the system works
- **Use batch processing** for multiple files
- **Validate definitions** before committing them
- **Search frequently** to avoid duplicate definitions
- **Convert to markdown** for documentation

## Getting Help

```bash
# CLI help
python scripts/definition_cli.py --help
python scripts/definition_cli.py extract --help

# In chat mode
You: help

# Check status
curl http://localhost:5000/api/definitions/status
```

## Example Workflow

```bash
# 1. Extract from papers
python scripts/definition_cli.py batch Paper-*.md --output ./defs

# 2. Validate all
for f in ./defs/*.yaml; do
  python scripts/definition_cli.py validate "$f"
done

# 3. Search for specific terms
python scripts/definition_cli.py search "coherence" --dir ./defs

# 4. Get overview
python scripts/definition_cli.py stats ./defs

# 5. Generate documentation
for f in ./defs/*.yaml; do
  python scripts/definition_cli.py convert "$f" --output "${f%.yaml}.md"
done
```

You're ready to go! Start with the interactive chat mode and explore from there.
