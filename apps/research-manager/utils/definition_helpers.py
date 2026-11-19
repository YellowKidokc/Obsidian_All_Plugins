"""
Definition Helpers - Utility functions for working with term definitions
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime


def load_definition(file_path: str) -> Dict[str, Any]:
    """Load a YAML definition file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_definition(definition: Dict[str, Any], output_path: str):
    """Save a definition to a YAML file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(definition, f, default_flow_style=False, allow_unicode=True)


def generate_uuid() -> str:
    """Generate a new UUID for a term"""
    return str(uuid.uuid4())


def validate_definition(definition: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate a definition against the schema
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    required_fields = ['uuid', 'term', 'definitions', 'domains', 'meta']
    
    for field in required_fields:
        if field not in definition:
            errors.append(f"Missing required field: {field}")
    
    if 'uuid' in definition and not definition['uuid']:
        errors.append("UUID cannot be empty")
    
    if 'term' in definition and not definition['term']:
        errors.append("Term name cannot be empty")
    
    if 'definitions' in definition:
        if 'theophysics' not in definition['definitions']:
            errors.append("Missing theophysics definition")
        else:
            theo_def = definition['definitions']['theophysics']
            if not isinstance(theo_def, dict):
                errors.append("Theophysics definition must be a dictionary")
            else:
                if 'formal' not in theo_def or not theo_def['formal']:
                    errors.append("Missing formal definition")
    
    return len(errors) == 0, errors


def merge_definitions(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two definitions, with updates taking precedence
    
    Args:
        base: Base definition
        updates: Updates to apply
    
    Returns:
        Merged definition
    """
    result = base.copy()
    
    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_definitions(result[key], value)
        else:
            result[key] = value
    
    result['meta']['last_updated'] = datetime.now().strftime("%Y-%m-%d")
    
    return result


def find_definitions_by_domain(definitions_dir: str, domain: str) -> List[str]:
    """
    Find all definition files for a specific domain
    
    Args:
        definitions_dir: Directory containing definition files
        domain: Domain to filter by (physics, theology, etc.)
    
    Returns:
        List of file paths
    """
    matching_files = []
    
    for file_path in Path(definitions_dir).glob('**/*.yaml'):
        try:
            definition = load_definition(str(file_path))
            if definition.get('domains', {}).get('primary') == domain:
                matching_files.append(str(file_path))
        except Exception:
            continue
    
    return matching_files


def find_definitions_by_term(definitions_dir: str, term: str) -> Optional[str]:
    """
    Find a definition file by term name
    
    Args:
        definitions_dir: Directory containing definition files
        term: Term to search for
    
    Returns:
        File path if found, None otherwise
    """
    term_lower = term.lower()
    
    for file_path in Path(definitions_dir).glob('**/*.yaml'):
        try:
            definition = load_definition(str(file_path))
            if definition.get('term', '').lower() == term_lower:
                return str(file_path)
            
            aliases = definition.get('aliases', [])
            if any(alias.lower() == term_lower for alias in aliases):
                return str(file_path)
        except Exception:
            continue
    
    return None


def extract_cross_references(definition: Dict[str, Any]) -> List[str]:
    """
    Extract all UUIDs referenced in a definition
    
    Args:
        definition: The definition to analyze
    
    Returns:
        List of referenced UUIDs
    """
    references = []
    
    if 'integration' in definition:
        integration = definition['integration']
        
        if 'axioms' in integration:
            for axiom in integration['axioms']:
                if 'uuid' in axiom:
                    references.append(axiom['uuid'])
        
        if 'theorems' in integration:
            for theorem in integration['theorems']:
                if 'uuid' in theorem:
                    references.append(theorem['uuid'])
    
    if 'meta' in definition and 'related_terms' in definition['meta']:
        references.extend(definition['meta']['related_terms'])
    
    return list(set(references))


def build_definition_graph(definitions_dir: str) -> Dict[str, List[str]]:
    """
    Build a graph of definition relationships
    
    Args:
        definitions_dir: Directory containing definition files
    
    Returns:
        Dictionary mapping UUIDs to lists of related UUIDs
    """
    graph = {}
    
    for file_path in Path(definitions_dir).glob('**/*.yaml'):
        try:
            definition = load_definition(str(file_path))
            uuid = definition.get('uuid')
            if uuid:
                references = extract_cross_references(definition)
                graph[uuid] = references
        except Exception:
            continue
    
    return graph


def format_definition_markdown(definition: Dict[str, Any]) -> str:
    """
    Convert a YAML definition to a readable Markdown format
    
    Args:
        definition: The definition dictionary
    
    Returns:
        Markdown formatted string
    """
    md = []
    
    md.append(f"# {definition.get('term', 'Unknown Term')}")
    md.append("")
    
    if 'definitions' in definition and 'theophysics' in definition['definitions']:
        theo_def = definition['definitions']['theophysics']
        md.append("## Definition")
        md.append("")
        md.append(f"**One-line:** {theo_def.get('one_line', 'N/A')}")
        md.append("")
        md.append(f"**Plain:** {theo_def.get('plain', 'N/A')}")
        md.append("")
        md.append(f"**Formal:** {theo_def.get('formal', 'N/A')}")
        md.append("")
    
    if 'domains' in definition:
        md.append("## Domains")
        md.append("")
        md.append(f"- **Primary:** {definition['domains'].get('primary', 'N/A')}")
        if 'secondary' in definition['domains']:
            md.append(f"- **Secondary:** {', '.join(definition['domains']['secondary'])}")
        md.append("")
    
    if 'formalization' in definition and definition['formalization'].get('symbol'):
        md.append("## Mathematical Formalization")
        md.append("")
        md.append(f"**Symbol:** {definition['formalization'].get('symbol', 'N/A')}")
        if 'latex' in definition['formalization']:
            md.append(f"**LaTeX:** `{definition['formalization']['latex']}`")
        md.append("")
    
    if 'cross_domain' in definition:
        md.append("## Cross-Domain Mapping")
        md.append("")
        for domain, info in definition['cross_domain'].items():
            if isinstance(info, dict) and 'manifestation' in info:
                md.append(f"### {domain.title()}")
                md.append(f"{info['manifestation']}")
                md.append("")
    
    if 'analogies' in definition and 'primary' in definition['analogies']:
        primary = definition['analogies']['primary']
        md.append("## Primary Analogy")
        md.append("")
        md.append(f"{primary.get('analogy', 'N/A')}")
        md.append("")
    
    return "\n".join(md)


def search_definitions(definitions_dir: str, query: str) -> List[Dict[str, Any]]:
    """
    Search definitions by query string
    
    Args:
        definitions_dir: Directory containing definition files
        query: Search query
    
    Returns:
        List of matching definitions with file paths
    """
    results = []
    query_lower = query.lower()
    
    for file_path in Path(definitions_dir).glob('**/*.yaml'):
        try:
            definition = load_definition(str(file_path))
            
            searchable_text = json.dumps(definition).lower()
            
            if query_lower in searchable_text:
                results.append({
                    'file_path': str(file_path),
                    'term': definition.get('term', 'Unknown'),
                    'uuid': definition.get('uuid', ''),
                    'definition': definition
                })
        except Exception:
            continue
    
    return results


def get_definition_stats(definitions_dir: str) -> Dict[str, Any]:
    """
    Get statistics about the definitions collection
    
    Args:
        definitions_dir: Directory containing definition files
    
    Returns:
        Dictionary with statistics
    """
    stats = {
        'total_definitions': 0,
        'by_domain': {},
        'by_status': {},
        'missing_fields': {},
        'total_cross_references': 0
    }
    
    for file_path in Path(definitions_dir).glob('**/*.yaml'):
        try:
            definition = load_definition(str(file_path))
            stats['total_definitions'] += 1
            
            domain = definition.get('domains', {}).get('primary', 'unknown')
            stats['by_domain'][domain] = stats['by_domain'].get(domain, 0) + 1
            
            status = definition.get('meta', {}).get('status', 'unknown')
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            refs = extract_cross_references(definition)
            stats['total_cross_references'] += len(refs)
            
        except Exception:
            continue
    
    return stats
