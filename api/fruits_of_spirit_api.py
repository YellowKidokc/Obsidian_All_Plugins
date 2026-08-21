"""
Fruits of the Spirit API - REST endpoints for accessing spiritual fruit data
Provides theological, physical, and consciousness mappings
"""

from flask import Blueprint, request, jsonify
import json
import os
from pathlib import Path

fruits_bp = Blueprint('fruits', __name__, url_prefix='/api/fruits-of-spirit')

DATA_FILE = Path(__file__).parent.parent / "data" / "fruits_of_spirit.json"


def load_fruits_data():
    """Load the fruits of spirit data from JSON file"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


@fruits_bp.route('/', methods=['GET'])
def get_all_fruits():
    """
    Get all fruits of the spirit
    
    Query parameters:
    - include_metadata: bool (default: false)
    """
    data = load_fruits_data()
    include_metadata = request.args.get('include_metadata', 'false').lower() == 'true'
    
    response = {
        'fruits': data['fruits_of_spirit'],
        'count': len(data['fruits_of_spirit'])
    }
    
    if include_metadata:
        response['metadata'] = data['metadata']
    
    return jsonify(response)


@fruits_bp.route('/<int:fruit_id>', methods=['GET'])
def get_fruit_by_id(fruit_id):
    """Get a specific fruit by ID"""
    data = load_fruits_data()
    
    fruit = next((f for f in data['fruits_of_spirit'] if f['id'] == fruit_id), None)
    
    if not fruit:
        return jsonify({'error': f'Fruit with ID {fruit_id} not found'}), 404
    
    return jsonify(fruit)


@fruits_bp.route('/name/<string:name>', methods=['GET'])
def get_fruit_by_name(name):
    """Get a specific fruit by name (case-insensitive)"""
    data = load_fruits_data()
    
    fruit = next((f for f in data['fruits_of_spirit'] 
                  if f['name'].lower() == name.lower()), None)
    
    if not fruit:
        return jsonify({'error': f'Fruit "{name}" not found'}), 404
    
    return jsonify(fruit)


@fruits_bp.route('/greek/<string:greek_word>', methods=['GET'])
def get_fruit_by_greek(greek_word):
    """Get a fruit by its Greek name"""
    data = load_fruits_data()
    
    fruit = next((f for f in data['fruits_of_spirit'] 
                  if f['greek'].lower() == greek_word.lower()), None)
    
    if not fruit:
        return jsonify({'error': f'Fruit with Greek word "{greek_word}" not found'}), 404
    
    return jsonify(fruit)


@fruits_bp.route('/physics-mapping', methods=['GET'])
def get_physics_mappings():
    """Get all physics mappings for the fruits"""
    data = load_fruits_data()
    
    mappings = [
        {
            'fruit': fruit['name'],
            'physics_concept': fruit['physics_mapping']['concept'],
            'description': fruit['physics_mapping']['description'],
            'symbol': fruit['physics_mapping']['symbol'],
            'equation': fruit['physics_mapping'].get('equation', 'N/A')
        }
        for fruit in data['fruits_of_spirit']
    ]
    
    return jsonify({
        'mappings': mappings,
        'count': len(mappings)
    })


@fruits_bp.route('/consciousness-mapping', methods=['GET'])
def get_consciousness_mappings():
    """Get all consciousness mappings for the fruits"""
    data = load_fruits_data()
    
    mappings = [
        {
            'fruit': fruit['name'],
            'consciousness_state': fruit['consciousness_mapping']['state'],
            'description': fruit['consciousness_mapping']['description']
        }
        for fruit in data['fruits_of_spirit']
    ]
    
    return jsonify({
        'mappings': mappings,
        'count': len(mappings)
    })


@fruits_bp.route('/search', methods=['GET'])
def search_fruits():
    """
    Search fruits by various criteria
    
    Query parameters:
    - q: search query (searches name, definition, manifestations)
    - domain: filter by domain (physics, consciousness, theology)
    """
    data = load_fruits_data()
    query = request.args.get('q', '').lower()
    domain = request.args.get('domain', '').lower()
    
    results = []
    
    for fruit in data['fruits_of_spirit']:
        match = False
        
        if query:
            searchable_text = (
                fruit['name'].lower() + ' ' +
                fruit['definition'].lower() + ' ' +
                ' '.join(fruit['practical_manifestations']).lower()
            )
            if query in searchable_text:
                match = True
        
        if domain:
            if domain == 'physics' and 'physics_mapping' in fruit:
                match = True
            elif domain == 'consciousness' and 'consciousness_mapping' in fruit:
                match = True
            elif domain == 'theology':
                match = True
        
        if match or (not query and not domain):
            results.append(fruit)
    
    return jsonify({
        'results': results,
        'count': len(results),
        'query': query,
        'domain': domain
    })


@fruits_bp.route('/opposites', methods=['GET'])
def get_opposites():
    """Get all fruits with their opposite vices"""
    data = load_fruits_data()
    
    opposites = [
        {
            'fruit': fruit['name'],
            'vices': fruit['opposite_vices']
        }
        for fruit in data['fruits_of_spirit']
    ]
    
    return jsonify({
        'opposites': opposites,
        'count': len(opposites)
    })


@fruits_bp.route('/related-virtues', methods=['GET'])
def get_related_virtues():
    """Get all fruits with their related virtues"""
    data = load_fruits_data()
    
    virtues = [
        {
            'fruit': fruit['name'],
            'related': fruit['related_virtues']
        }
        for fruit in data['fruits_of_spirit']
    ]
    
    return jsonify({
        'virtues': virtues,
        'count': len(virtues)
    })


@fruits_bp.route('/manifestations', methods=['GET'])
def get_all_manifestations():
    """Get practical manifestations of all fruits"""
    data = load_fruits_data()
    
    manifestations = [
        {
            'fruit': fruit['name'],
            'manifestations': fruit['practical_manifestations']
        }
        for fruit in data['fruits_of_spirit']
    ]
    
    return jsonify({
        'manifestations': manifestations,
        'count': len(manifestations)
    })


@fruits_bp.route('/compare', methods=['POST'])
def compare_fruits():
    """
    Compare multiple fruits
    
    Request body:
    {
        "fruits": ["Love", "Joy", "Peace"]
    }
    """
    fruit_names = request.json.get('fruits', [])
    
    if not fruit_names:
        return jsonify({'error': 'No fruits specified for comparison'}), 400
    
    data = load_fruits_data()
    
    comparison = []
    for name in fruit_names:
        fruit = next((f for f in data['fruits_of_spirit'] 
                     if f['name'].lower() == name.lower()), None)
        if fruit:
            comparison.append({
                'name': fruit['name'],
                'greek': fruit['greek'],
                'definition': fruit['definition'],
                'physics_concept': fruit['physics_mapping']['concept'],
                'consciousness_state': fruit['consciousness_mapping']['state']
            })
    
    return jsonify({
        'comparison': comparison,
        'count': len(comparison)
    })


@fruits_bp.route('/metadata', methods=['GET'])
def get_metadata():
    """Get metadata about the fruits of spirit dataset"""
    data = load_fruits_data()
    return jsonify(data['metadata'])


@fruits_bp.route('/random', methods=['GET'])
def get_random_fruit():
    """Get a random fruit for daily meditation"""
    import random
    data = load_fruits_data()
    
    fruit = random.choice(data['fruits_of_spirit'])
    
    return jsonify({
        'fruit': fruit,
        'meditation_prompt': f"Reflect on {fruit['name']} today. How can you manifest {fruit['practical_manifestations'][0].lower()} in your life?"
    })


@fruits_bp.route('/theophysics-integration', methods=['GET'])
def get_theophysics_integration():
    """Get the complete theophysics integration view"""
    data = load_fruits_data()
    
    integration = []
    for fruit in data['fruits_of_spirit']:
        integration.append({
            'fruit': fruit['name'],
            'theological': {
                'greek': fruit['greek'],
                'meaning': fruit['theological_meaning'],
                'scripture': fruit['scripture_reference']
            },
            'physical': {
                'concept': fruit['physics_mapping']['concept'],
                'symbol': fruit['physics_mapping']['symbol'],
                'equation': fruit['physics_mapping'].get('equation', 'N/A')
            },
            'consciousness': {
                'state': fruit['consciousness_mapping']['state'],
                'description': fruit['consciousness_mapping']['description']
            }
        })
    
    return jsonify({
        'integration': integration,
        'framework': 'Theophysics - Bridging Theology, Physics, and Consciousness',
        'count': len(integration)
    })
