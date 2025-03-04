from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from datetime import datetime

app = Flask(__name__)

# Konfigurasi Database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///default.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Konfigurasi Folder Upload
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Batas 100MB

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Model Video
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

# Render Halaman Utama
@app.route('/')
def index():
    videos = Video.query.order_by(Video.uploaded_at.desc()).all()
    return render_template('index.html', videos=videos)

# Endpoint untuk Upload Video
@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({"error": "Tidak ada file yang diunggah"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nama file kosong"}), 400

    # Simpan file ke folder upload
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Simpan info video ke database
    new_video = Video(filename=file.filename, filepath=filepath)
    db.session.add(new_video)
    db.session.commit()

    return jsonify({
        "message": "Upload berhasil",
        "video": {
            "id": new_video.id,
            "filename": new_video.filename,
            "filepath": new_video.filepath,
            "uploaded_at": new_video.uploaded_at
        }
    }), 201

# Endpoint untuk Menampilkan Video
@app.route('/videos/<filename>')
def get_video(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
