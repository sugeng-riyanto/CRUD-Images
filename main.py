from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secret key for session management
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# SQLite3 Database Setup
def create_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            image_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_table()

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM items')
    items = cursor.fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image = request.files['image']

        if image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)
        else:
            image_path = None

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO items (name, description, image_path) VALUES (?, ?, ?)', (name, description, image_path))
        conn.commit()
        conn.close()
        flash('Item added successfully', 'success')
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit(item_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = cursor.fetchone()
    conn.close()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image = request.files['image']

        if image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)
        else:
            image_path = item[3]

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE items SET name=?, description=?, image_path=? WHERE id=?', (name, description, image_path, item_id))
        conn.commit()
        conn.close()
        flash('Item updated successfully', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', item=item)

@app.route('/delete/<int:item_id>')
def delete(item_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT image_path FROM items WHERE id = ?', (item_id,))
    image_path = cursor.fetchone()[0]

    if image_path:
        os.remove(image_path)

    cursor.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    flash('Item deleted successfully', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
