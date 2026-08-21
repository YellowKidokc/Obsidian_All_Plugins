#!/usr/bin/env python3
"""
Definition CLI - Command-line interface for definition processing
Quick access to definition extraction and formatting
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.definition_processor import DefinitionProcessor
from utils.definition_helpers import *
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Theophysics Definition CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive chatbot mode
  python definition_cli.py chat
  
  # Extract definitions from a file
  python definition_cli.py extract paper.md
  
  # Batch process multiple files
  python definition_cli.py batch file1.md file2.md --output ./definitions
  
  # Search existing definitions
  python definition_cli.py search "coherence"
  
  # Get statistics
  python definition_cli.py stats ./definitions
  
  # Validate a definition file
  python definition_cli.py validate definition.yaml
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Interactive chatbot mode')
    chat_parser.add_argument('--model', default='llama2', help='Ollama model')
    chat_parser.add_argument('--ollama-url', default='http://localhost:11434', help='Ollama URL')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract definitions from file')
    extract_parser.add_argument('file', help='File to extract from')
    extract_parser.add_argument('--output', help='Output file for definitions')
    extract_parser.add_argument('--format', choices=['yaml', 'json', 'markdown'], default='yaml')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch process files')
    batch_parser.add_argument('files', nargs='+', help='Files to process')
    batch_parser.add_argument('--output', default='./definitions', help='Output directory')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search definitions')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--dir', default='./definitions', help='Definitions directory')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Get definition statistics')
    stats_parser.add_argument('dir', help='Definitions directory')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate definition file')
    validate_parser.add_argument('file', help='Definition file to validate')
    
    # Find command
    find_parser = subparsers.add_parser('find', help='Find definition by term')
    find_parser.add_argument('term', help='Term to find')
    find_parser.add_argument('--dir', default='./definitions', help='Definitions directory')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert definition to markdown')
    convert_parser.add_argument('file', help='YAML definition file')
    convert_parser.add_argument('--output', help='Output markdown file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute commands
    if args.command == 'chat':
        processor = DefinitionProcessor(ollama_url=args.ollama_url, model=args.model)
        processor.interactive_definition_builder()
    
    elif args.command == 'extract':
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            return
        
        processor = DefinitionProcessor()
        definitions = processor.extract_definitions_from_file(args.file)
        
        print(f"\nExtracted {len(definitions)} definitions from {args.file}\n")
        
        for i, term_data in enumerate(definitions, 1):
            print(f"{i}. {term_data.get('term', 'Unknown')}")
            
            if args.output:
                yaml_content = processor.create_definition(term_data)
                output_file = args.output if len(definitions) == 1 else f"{args.output}_{i}.yaml"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(yaml_content)
                print(f"   Saved to: {output_file}")
        
        print()
    
    elif args.command == 'batch':
        processor = DefinitionProcessor()
        processor.batch_process_files(args.files, args.output)
        print(f"\nProcessed {len(args.files)} files. Output in {args.output}/")
    
    elif args.command == 'search':
        results = search_definitions(args.dir, args.query)
        
        print(f"\nFound {len(results)} matching definitions:\n")
        for result in results:
            print(f"- {result['term']} ({result['uuid'][:8]}...)")
            print(f"  File: {result['file_path']}")
            print()
    
    elif args.command == 'stats':
        stats = get_definition_stats(args.dir)
        
        print("\n=== Definition Statistics ===\n")
        print(f"Total Definitions: {stats['total_definitions']}")
        print(f"Total Cross-References: {stats['total_cross_references']}")
        
        print("\nBy Domain:")
        for domain, count in stats['by_domain'].items():
            print(f"  {domain}: {count}")
        
        print("\nBy Status:")
        for status, count in stats['by_status'].items():
            print(f"  {status}: {count}")
        print()
    
    elif args.command == 'validate':
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            return
        
        definition = load_definition(args.file)
        is_valid, errors = validate_definition(definition)
        
        if is_valid:
            print(f"✓ {args.file} is valid")
        else:
            print(f"✗ {args.file} has errors:\n")
            for error in errors:
                print(f"  - {error}")
    
    elif args.command == 'find':
        file_path = find_definitions_by_term(args.dir, args.term)
        
        if file_path:
            print(f"\nFound: {file_path}\n")
            definition = load_definition(file_path)
            print(format_definition_markdown(definition))
        else:
            print(f"\nNo definition found for term: {args.term}")
    
    elif args.command == 'convert':
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            return
        
        definition = load_definition(args.file)
        markdown = format_definition_markdown(definition)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"Converted to: {args.output}")
        else:
            print(markdown)


if __name__ == "__main__":
    main()
