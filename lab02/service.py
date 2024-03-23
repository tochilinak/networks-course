import json
from pathlib import Path

from flask import Flask, request, jsonify, abort, send_file


app = Flask(__name__)
products: dict[int, dict[str, int | str | None]] = {}
next_id = -1


@app.route('/')
def index():
    return "Hello, world!"


@app.route('/product', methods=['POST'])
def add_product():
    global next_id
    next_id += 1
    data = json.loads(request.data)
    data['id'] = next_id
    products[next_id] = data
    return jsonify(data)


@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    if product_id in products:
        return jsonify(products[product_id])
    else:
        abort(404)


@app.route('/product/<int:product_id>/image', methods=['POST'])
def add_product_image(product_id):
    if product_id in products:
        iconfile = request.files['Icon']
        path = Path(f"service_data/{product_id}/{iconfile.filename}")
        path.parent.mkdir(parents=True, exist_ok=True)
        iconfile.save(path)
        products[product_id]['icon'] = str(path)
        return jsonify(products[product_id])
    else:
        abort(404)


@app.route('/product/<int:product_id>/image', methods=['GET'])
def get_product_image(product_id):
    if product_id in products:
        iconfile = products[product_id].get('icon')
        if iconfile is None:
            abort(404)
        return send_file(iconfile)
    else:
        abort(404)

@app.route('/product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    if product_id not in products:
        abort(404)

    data = json.loads(request.data)
    for key, value in data.items():
        products[product_id][key] = value

    return jsonify(products[product_id])


@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    if product_id not in products:
        abort(404)

    data = products[product_id]
    products.pop(product_id)

    return jsonify(data)


@app.route('/products', methods=['GET'])
def list_product():
    data = [products[i] for i in products]
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
