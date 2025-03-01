from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)

# Konfigurasi Database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///default.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Hubungkan Flask-Migrate dengan Flask dan SQLAlchemy

# Model User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Endpoint untuk menambahkan user dan langsung menampilkan daftar user
@app.route('/adduser/<string:name>', methods=['GET'])
def add_user(name):
    if not name:
        return jsonify({"error": "Nama tidak boleh kosong"}), 400

    new_user = User(name=name)
    db.session.add(new_user)
    db.session.commit()

    # Ambil semua user setelah penambahan
    users = User.query.all()
    user_list = [{"id": user.id, "name": user.name} for user in users]

    return jsonify({
        "message": "User berhasil ditambahkan",
        "user": {"id": new_user.id, "name": new_user.name},
        "all_users": user_list
    }), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [{"id": user.id, "name": user.name} for user in users]

    return jsonify({"users": user_list})

@app.route('/')
def index():
    return "Hello, Flask with PostgreSQL!"

if __name__ == '__main__':
    app.run(debug=True)
