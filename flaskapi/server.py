from flask import Flask, jsonify, request, render_template, redirect
from mysql_utils import DBHelper
app = Flask(__name__)

# Initialize the database helper instance
db_helper = DBHelper(host='localhost', user='fastserver', password='Kishore123$', database='products')
db_helper.init_db_connection()
@app.route('/')
def root():
    """Redirect to the home page."""
    return redirect('/index')
@app.route('/index')
def home():
    """Render the home page."""
    return render_template('index.html')
@app.route('/item')
def item():
    return render_template('item.html')
@app.route('/view')
def view():
    return render_template('view.html')


@app.route('/add_data', methods=['POST'])
def add_data():
    data = request.get_json()
    # Assuming you have a method in DBHelper to add data
    result = db_helper.add_input(data['description'])
    return jsonify({'result': result})


# Sample data to simulate a database
data_store = {
    1: {"name": "Item 1", "description": "This is item 1"},
    2: {"name": "Item 2", "description": "This is item 2"},
}

@app.route('/api/items', methods=['GET'])
def get_items():
    """Get a list of all items."""
    items = db_helper.fetch_results("select * from products")
    return jsonify(items), 200

@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Get a single item by ID."""
    item = db_helper.fetch_results("select * from products where id = %s", (item_id,))
    if item:
        return jsonify(item), 200
    return jsonify({"error": "Item not found"}), 404

@app.route('/api/items', methods=['POST'])
def create_item():
    """Create a new item."""
    new_item = request.json
    insert_query="""
        INSERT INTO products (name, category, price, tag) 
        VALUES (%s, %s, %s, %s)
    """
    item_id =db_helper.insert_record(insert_query, (new_item['name'], new_item['category'], new_item['price'], new_item['tag'])) 
    data_store[item_id] = new_item
    return jsonify({"id": item_id, **new_item}), 201

@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """Update an existing item by ID."""
    # Fetch the item from the database
    item = db_helper.fetch_results("select * from items where id = %s", (item_id,))
    if not item:
        return jsonify({"error": "Item not found"}), 404

    # Get the updated data from the request
    updated_data = request.json
    if not updated_data:
        return jsonify({"error": "No data provided"}), 400

    # Prepare the update query
    update_query = """
        UPDATE items 
        SET name = %s, category = %s, price = %s, tag = %s 
        WHERE id = %s
    """
    
    # Execute the update query with all fields
    db_helper.update_record(update_query, (
        updated_data.get('name'),
        updated_data.get('category'),
        updated_data.get('price'),
        updated_data.get('tag'),
        item_id
    ))

    # Return the updated item
    updated_item = db_helper.fetch_results("select * from items where id = %s", (item_id,))
    return jsonify(updated_item[0]), 200

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Delete an item by ID."""
    # Prepare the delete query
    delete_query = "delete from products where id = %s"

    
    # Execute the delete operation
    result = db_helper.delete_record(delete_query, (item_id,))
    
    if result:  # Assuming delete_record returns the number of affected rows
        return jsonify({"message": "Item deleted"}), 204
    else:
        return jsonify({"error": "Item not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
