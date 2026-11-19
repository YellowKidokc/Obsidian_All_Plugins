"""
Definition API - Flask endpoints for term definition processing
Provides REST API access to the definition processor
"""

from flask import Blueprint, request, jsonify
from engine.definition_processor import DefinitionProcessor
import os
from pathlib import Path

definition_bp = Blueprint('definition', __name__, url_prefix='/api/definitions')

processor = DefinitionProcessor()


@definition_bp.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint for interactive definition building
    
    Request body:
    {
        "message": "Your message here",
        "context": "Optional context",
        "reset": false
    }
    """
    data = request.json
    message = data.get('message', '')
    context = data.get('context')
    reset = data.get('reset', False)
    
    if reset:
        processor.reset_conversation()
        return jsonify({"status": "conversation reset"})
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    response = processor.chat(message, context)
    
    return jsonify({
        "response": response,
        "conversation_length": len(processor.conversation_history)
    })


@definition_bp.route('/extract', methods=['POST'])
def extract_definitions():
    """
    Extract definitions from a file
    
    Request body:
    {
        "file_path": "/path/to/file.md",
        "content": "Optional: provide content directly instead of file path"
    }
    """
    data = request.json
    file_path = data.get('file_path')
    content = data.get('content')
    
    if not file_path and not content:
        return jsonify({"error": "Either file_path or content must be provided"}), 400
    
    if file_path:
        if not os.path.exists(file_path):
            return jsonify({"error": f"File not found: {file_path}"}), 404
        
        definitions = processor.extract_definitions_from_file(file_path)
    else:
        temp_file = Path("temp_extract.txt")
        temp_file.write_text(content, encoding='utf-8')
        definitions = processor.extract_definitions_from_file(str(temp_file))
        temp_file.unlink()
    
    return jsonify({
        "definitions": definitions,
        "count": len(definitions)
    })


@definition_bp.route('/create', methods=['POST'])
def create_definition():
    """
    Create a YAML definition from term data
    
    Request body:
    {
        "term": "Term name",
        "domain": "physics",
        "definition": "The definition...",
        "additional_data": {}
    }
    """
    data = request.json
    
    if 'term' not in data:
        return jsonify({"error": "Term name is required"}), 400
    
    yaml_content = processor.create_definition(data)
    
    return jsonify({
        "yaml": yaml_content,
        "term": data.get('term')
    })


@definition_bp.route('/batch', methods=['POST'])
def batch_process():
    """
    Batch process multiple files
    
    Request body:
    {
        "file_paths": ["/path/to/file1.md", "/path/to/file2.md"],
        "output_dir": "/path/to/output"
    }
    """
    data = request.json
    file_paths = data.get('file_paths', [])
    output_dir = data.get('output_dir', './definitions')
    
    if not file_paths:
        return jsonify({"error": "No file paths provided"}), 400
    
    missing_files = [f for f in file_paths if not os.path.exists(f)]
    if missing_files:
        return jsonify({"error": f"Files not found: {missing_files}"}), 404
    
    try:
        processor.batch_process_files(file_paths, output_dir)
        return jsonify({
            "status": "success",
            "processed": len(file_paths),
            "output_dir": output_dir
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@definition_bp.route('/template', methods=['GET'])
def get_template():
    """Get the YAML template"""
    template = processor.load_template()
    return jsonify({
        "template": template
    })


@definition_bp.route('/status', methods=['GET'])
def status():
    """Check processor status"""
    return jsonify({
        "status": "online",
        "model": processor.model,
        "ollama_url": processor.ollama_url,
        "conversation_length": len(processor.conversation_history)
    })


@definition_bp.route('/guided', methods=['POST'])
def guided_extraction():
    """
    Guided definition extraction with specific instructions
    
    Request body:
    {
        "file_path": "/path/to/file.md",
        "instructions": "Extract all physics terms related to quantum mechanics",
        "format": "yaml|json"
    }
    """
    data = request.json
    file_path = data.get('file_path')
    instructions = data.get('instructions', 'Extract all key terms and their definitions')
    output_format = data.get('format', 'yaml')
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Valid file_path is required"}), 400
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    prompt = f"""{instructions}

File: {file_path}
Content:
{content[:4000]}

Extract the terms and format them according to the Theophysics definition schema.
Return as {output_format.upper()}."""
    
    response = processor.chat(prompt)
    
    return jsonify({
        "result": response,
        "file": file_path,
        "format": output_format
    })
