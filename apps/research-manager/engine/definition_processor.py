"""
Definition Processor - Extract and format term definitions using Ollama
Provides chatbot-style interaction to process definitions from files
"""

import os
import yaml
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests


class DefinitionProcessor:
    """Process term definitions with Ollama chatbot integration"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama2"):
        self.ollama_url = ollama_url
        self.model = model
        self.template_path = Path(__file__).parent.parent / "templates" / "theophysics" / "term_definition_template.yaml"
        self.conversation_history = []
        
    def load_template(self) -> str:
        """Load the YAML template"""
        with open(self.template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def chat(self, message: str, context: Optional[str] = None) -> str:
        """
        Send a message to Ollama and get a response
        
        Args:
            message: User message
            context: Optional context (file contents, previous definitions, etc.)
        
        Returns:
            Ollama's response
        """
        system_prompt = """You are a Theophysics definition extraction assistant. 
Your job is to help extract and format term definitions according to the Theophysics schema.
You understand physics, theology, philosophy, consciousness studies, and mathematics.
When given text, you can identify key terms and extract their definitions in the proper format.
Be precise, thorough, and maintain the cross-domain bridge between physics and theology."""
        
        if context:
            system_prompt += f"\n\nContext:\n{context}"
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                *self.conversation_history,
                {"role": "user", "content": message}
            ],
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            assistant_message = result['message']['content']
            
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
        except Exception as e:
            return f"Error communicating with Ollama: {str(e)}"
    
    def extract_definitions_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract term definitions from a file using Ollama
        
        Args:
            file_path: Path to the file to process
        
        Returns:
            List of extracted definitions
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        prompt = f"""Analyze this file and extract all key terms that need definitions.
For each term, identify:
1. The term name
2. Any definitions provided
3. The domain (physics, theology, philosophy, consciousness, mathematics)
4. Any mathematical formulations
5. Cross-domain connections

File content:
{content[:4000]}  # Limit context size

Return the terms as a JSON list."""
        
        response = self.chat(prompt)
        
        try:
            terms = json.loads(response)
            return terms if isinstance(terms, list) else []
        except json.JSONDecodeError:
            return []
    
    def create_definition(self, term_data: Dict[str, Any]) -> str:
        """
        Create a YAML definition file from extracted term data
        
        Args:
            term_data: Dictionary containing term information
        
        Returns:
            Formatted YAML string
        """
        template = self.load_template()
        
        term_uuid = str(uuid.uuid4())
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        replacements = {
            "{{UUID}}": term_uuid,
            "{{TERM}}": term_data.get('term', 'UNKNOWN'),
            "{{DATE}}": current_date,
        }
        
        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        
        return result
    
    def interactive_definition_builder(self, file_paths: Optional[List[str]] = None):
        """
        Interactive chatbot session for building definitions
        
        Args:
            file_paths: Optional list of files to process
        """
        print("=" * 70)
        print("THEOPHYSICS DEFINITION PROCESSOR")
        print("=" * 70)
        print("\nCommands:")
        print("  - 'extract <file>' - Extract definitions from a file")
        print("  - 'create <term>' - Create a new definition")
        print("  - 'help' - Show this help")
        print("  - 'quit' - Exit")
        print("\nOr just chat naturally about what you need!\n")
        
        if file_paths:
            print(f"Loaded {len(file_paths)} files for processing\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("  extract <file> - Extract definitions from file")
                print("  create <term> - Start creating a definition")
                print("  quit - Exit the processor\n")
                continue
            
            if user_input.lower().startswith('extract '):
                file_path = user_input[8:].strip()
                if os.path.exists(file_path):
                    print(f"\nExtracting definitions from {file_path}...")
                    definitions = self.extract_definitions_from_file(file_path)
                    print(f"Found {len(definitions)} terms\n")
                    for term in definitions:
                        print(f"  - {term.get('term', 'Unknown')}")
                    print()
                else:
                    print(f"File not found: {file_path}\n")
                continue
            
            if user_input.lower().startswith('create '):
                term = user_input[7:].strip()
                print(f"\nStarting definition creation for: {term}")
                print("I'll ask you some questions to build the definition...\n")
                
                response = self.chat(
                    f"Help me create a definition for the term '{term}'. "
                    f"Ask me questions to fill out the Theophysics definition schema."
                )
                print(f"Assistant: {response}\n")
                continue
            
            response = self.chat(user_input)
            print(f"\nAssistant: {response}\n")
    
    def batch_process_files(self, file_paths: List[str], output_dir: str):
        """
        Process multiple files and generate definition files
        
        Args:
            file_paths: List of files to process
            output_dir: Directory to save generated definitions
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for file_path in file_paths:
            print(f"Processing {file_path}...")
            definitions = self.extract_definitions_from_file(file_path)
            
            for term_data in definitions:
                term_name = term_data.get('term', 'unknown').lower().replace(' ', '_')
                output_file = os.path.join(output_dir, f"{term_name}_definition.yaml")
                
                yaml_content = self.create_definition(term_data)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(yaml_content)
                
                print(f"  Created: {output_file}")
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []


def main():
    """Main entry point for interactive use"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Theophysics Definition Processor")
    parser.add_argument('--ollama-url', default='http://localhost:11434', help='Ollama API URL')
    parser.add_argument('--model', default='llama2', help='Ollama model to use')
    parser.add_argument('--files', nargs='+', help='Files to process')
    parser.add_argument('--output-dir', default='./definitions', help='Output directory for definitions')
    parser.add_argument('--batch', action='store_true', help='Batch process files without interaction')
    
    args = parser.parse_args()
    
    processor = DefinitionProcessor(ollama_url=args.ollama_url, model=args.model)
    
    if args.batch and args.files:
        processor.batch_process_files(args.files, args.output_dir)
    else:
        processor.interactive_definition_builder(args.files)


if __name__ == "__main__":
    main()
