from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
import requests

app = Flask(__name__)
CORS(app)  # CORS 설정 추가

# API 키 설정
API_KEY = os.environ.get("GOOGLE_CLOUD_API_KEY")

# MySQL 설정
db_config = {
    'user': 'your_username',
    'password': 'your_password',
    'host': 'localhost',
    'database': 'voicebridge'
}

@app.route('/messages', methods=['GET'])
def get_messages():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM messages')
    messages = cursor.fetchall()
    conn.close()
    return jsonify(messages)

@app.route('/messages', methods=['POST'])
def add_message():
    data = request.json
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (content) VALUES (%s)', (data['content'],))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Message added successfully'}), 201

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    audio_data = request.files['audio'].read()
    audio_content = base64.b64encode(audio_data).decode('utf-8')

    url = f"https://speech.googleapis.com/v1/speech:recognize?key={API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "config": {
            "encoding": "LINEAR16",
            "sampleRateHertz": 16000,
            "languageCode": "ko-KR"
        },
        "audio": {
            "content": audio_content
        }
    }

    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()

    if 'error' in response_data:
        return jsonify({'error': response_data['error']['message']}), 400

    transcript = ' '.join(result['alternatives'][0]['transcript'] for result in response_data['results'])
    return jsonify({'transcript': transcript})

if __name__ == '__main__':
    app.run(debug=True)
