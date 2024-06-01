from flask import Blueprint, jsonify, request
from .shared.util import purificarHTML, partirHTML

main = Blueprint('main', __name__)

# Dados de exemplo
items = [
    {'id': 1, 'name': 'Item 1', 'price': 10.0},
    {'id': 2, 'name': 'Item 2', 'price': 20.0},
]

@main.route('/api/items', methods=['GET'])
def get_items():
    return jsonify(items)

@main.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    if item:
        return jsonify(item)
    else:
        return jsonify({'message': 'Item not found'}), 404

@main.route('/api/html', methods=['POST'])
def create_item():
    data = request.get_json()
    htmlPurificado = util.purificarHTML(data.get('html', ''))
    htmlPartido = util.partirHTML(htmlPurificado)
    return jsonify(htmlPartido), 201

@main.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    if item:
        data = request.get_json()
        item.update(data)
        return jsonify(item)
    else:
        return jsonify({'message': 'Item not found'}), 404

@main.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global items
    items = [item for item in items if item['id'] != item_id]
    return jsonify({'message': 'Item deleted'})