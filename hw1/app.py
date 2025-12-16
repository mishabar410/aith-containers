from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from the Containerized App!"

@app.route('/data')
def data():
    data_path = '/app/data/info.txt'
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            return f.read()
    return "No data found in volume."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
