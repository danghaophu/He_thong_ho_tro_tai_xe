
from flask import Flask, render_template, jsonify, request
from hotroweb import detect_drowsiness
import cv2
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/detect', methods=['POST'])
def detect():
    file = request.files.get('frame')
    language = request.form.get('lang')

    if file:
        npimg = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        result = detect_drowsiness(img, language=language)

        if isinstance(result, dict):
            return jsonify(result)  # chứa status + show_map
        else:
            return jsonify({'status': result})
    else:
        return jsonify({'status': 'Không nhận được ảnh'}), 400

@app.route('/detect', methods=['POST'])
def detect_drowsiness_route():
    file = request.files.get('frame')
    language = request.form.get('lang')  # ngôn ngữ từ trình duyệt
    if file:
        npimg = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        status = detect_drowsiness(img, language=language)
        return jsonify({'status': status})
    else:
        return jsonify({'status': 'Không nhận được ảnh'}), 400

if __name__ == '__main__':
    app.run(debug=True ,       
            ssl_context=(
            'E:/2025-2026/an toan mang/New folder/ss_local1/www.example.com.crt',
            'E:/2025-2026/an toan mang/New folder/ss_local1/www.example.com.key'
        )
    )
