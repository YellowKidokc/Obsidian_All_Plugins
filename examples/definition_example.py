"""
Example usage of the Definition Processor system
Demonstrates various ways to extract and process definitions
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.definition_processor import DefinitionProcessor
from utils.definition_helpers import *


def example_1_basic_extraction():
    """Example 1: Basic definition extraction from a file"""
    print("=" * 70)
    print("EXAMPLE 1: Basic Definition Extraction")
    print("=" * 70)
    
    processor = DefinitionProcessor()
    
    sample_text = """
    # Coherence in Theophysics
    
    Coherence (χ) is the fundamental measure of ordered correlation in a system.
    In physics, it represents the degree to which wave functions maintain phase
    relationships. In theology, it manifests as alignment with divine logos.
    
    Mathematical form: C = 1 - S_obs/S_max
    
    The coherence field χ appears in the Master Equation and governs the
    transition between quantum and classical regimes.
    """
    
    temp_file = "temp_example.txt"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(sample_text)
    
    print("\nExtracting definitions...")
    definitions = processor.extract_definitions_from_file(temp_file)
    
    print(f"Found {len(definitions)} terms")
    for term in definitions:
        print(f"  - {term.get('term', 'Unknown')}")
    
    os.remove(temp_file)
    print()


def example_2_interactive_chat():
    """Example 2: Interactive chat with the processor"""
    print("=" * 70)
    print("EXAMPLE 2: Interactive Chat")
    print("=" * 70)
    
    processor = DefinitionProcessor()
    
    questions = [
        "What is coherence in physics?",
        "How does it relate to entropy?",
        "What is the mathematical formulation?"
    ]
    
    for question in questions:
        print(f"\nQ: {question}")
        response = processor.chat(question)
        print(f"A: {response[:200]}...")  # Truncate for display
    
    print()


def example_3_create_definition():
    """Example 3: Create a YAML definition"""
    print("=" * 70)
    print("EXAMPLE 3: Create YAML Definition")
    print("=" * 70)
    
    processor = DefinitionProcessor()
    
    term_data = {
        'term': 'Coherence',
        'domain': 'physics',
        'definition': 'The measure of ordered correlation in a system',
        'symbol': 'χ',
        'latex': r'C = 1 - \frac{S_{\text{obs}}}{S_{\max}}'
    }
    
    print("\nCreating definition for:", term_data['term'])
    yaml_content = processor.create_definition(term_data)
    
    output_file = "coherence_example.yaml"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    
    print(f"Saved to: {output_file}")
    print()


def example_4_validate_definition():
    """Example 4: Validate a definition"""
    print("=" * 70)
    print("EXAMPLE 4: Validate Definition")
    print("=" * 70)
    
    sample_definition = {
        'uuid': '12345678-1234-1234-1234-123456789abc',
        'term': 'Coherence',
        'domains': {
            'primary': 'physics',
            'secondary': ['theology', 'consciousness']
        },
        'definitions': {
            'theophysics': {
                'formal': 'The measure of ordered correlation',
                'plain': 'How well things work together',
                'one_line': 'Ordered correlation measure'
            }
        },
        'meta': {
            'created': '2025-01-18',
            'status': 'draft'
        }
    }
    
    print("\nValidating definition...")
    is_valid, errors = validate_definition(sample_definition)
    
    if is_valid:
        print("✓ Definition is valid")
    else:
        print("✗ Definition has errors:")
        for error in errors:
            print(f"  - {error}")
    
    print()


def example_5_search_and_stats():
    """Example 5: Search and statistics"""
    print("=" * 70)
    print("EXAMPLE 5: Search and Statistics")
    print("=" * 70)
    
    definitions_dir = "./definitions"
    
    if not os.path.exists(definitions_dir):
        print(f"\nCreating {definitions_dir} directory...")
        os.makedirs(definitions_dir)
        
        processor = DefinitionProcessor()
        for term in ['Coherence', 'Entropy', 'Logos']:
            term_data = {'term': term, 'domain': 'physics'}
            yaml_content = processor.create_definition(term_data)
            
            with open(f"{definitions_dir}/{term.lower()}.yaml", 'w') as f:
                f.write(yaml_content)
    
    print("\nSearching for 'coherence'...")
    results = search_definitions(definitions_dir, "coherence")
    print(f"Found {len(results)} results")
    
    print("\nGetting statistics...")
    stats = get_definition_stats(definitions_dir)
    print(f"Total definitions: {stats['total_definitions']}")
    print(f"By domain: {stats['by_domain']}")
    
    print()


def example_6_convert_to_markdown():
    """Example 6: Convert definition to markdown"""
    print("=" * 70)
    print("EXAMPLE 6: Convert to Markdown")
    print("=" * 70)
    
    sample_definition = {
        'uuid': '12345678-1234-1234-1234-123456789abc',
        'term': 'Coherence',
        'domains': {
            'primary': 'physics',
            'secondary': ['theology']
        },
        'definitions': {
            'theophysics': {
                'formal': 'The measure of ordered correlation in a system',
                'plain': 'How well parts of a system work together in harmony',
                'one_line': 'Ordered correlation measure'
            }
        },
        'formalization': {
            'symbol': 'χ',
            'latex': r'C = 1 - \frac{S_{\text{obs}}}{S_{\max}}'
        },
        'cross_domain': {
            'physics': {
                'manifestation': 'Phase coherence in wave functions'
            },
            'theology': {
                'manifestation': 'Alignment with divine logos'
            }
        }
    }
    
    print("\nConverting to markdown...")
    markdown = format_definition_markdown(sample_definition)
    
    output_file = "coherence_example.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"Saved to: {output_file}")
    print("\nPreview:")
    print(markdown[:300] + "...")
    print()


def example_7_batch_processing():
    """Example 7: Batch process multiple files"""
    print("=" * 70)
    print("EXAMPLE 7: Batch Processing")
    print("=" * 70)
    
    temp_files = []
    for i, term in enumerate(['Coherence', 'Entropy', 'Logos'], 1):
        filename = f"temp_paper_{i}.md"
        content = f"""
        # {term}
        
        {term} is a fundamental concept in Theophysics.
        It bridges physics and theology through mathematical formalism.
        
        Definition: {term} represents the {term.lower()} aspect of reality.
        """
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        temp_files.append(filename)
    
    print(f"\nCreated {len(temp_files)} temporary files")
    
    processor = DefinitionProcessor()
    output_dir = "./batch_definitions"
    
    print(f"Processing files to {output_dir}...")
    processor.batch_process_files(temp_files, output_dir)
    
    for temp_file in temp_files:
        os.remove(temp_file)
    
    print("Batch processing complete!")
    print()


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "DEFINITION PROCESSOR EXAMPLES" + " " * 24 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")
    
    examples = [
        ("Basic Extraction", example_1_basic_extraction),
        ("Interactive Chat", example_2_interactive_chat),
        ("Create Definition", example_3_create_definition),
        ("Validate Definition", example_4_validate_definition),
        ("Search and Stats", example_5_search_and_stats),
        ("Convert to Markdown", example_6_convert_to_markdown),
        ("Batch Processing", example_7_batch_processing)
    ]
    
    print("Available examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print(f"  {len(examples) + 1}. Run all examples")
    print()
    
    choice = input("Select example (1-8): ").strip()
    
    if choice == str(len(examples) + 1):
        for name, func in examples:
            try:
                func()
            except Exception as e:
                print(f"Error in {name}: {e}\n")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        name, func = examples[int(choice) - 1]
        try:
            func()
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
