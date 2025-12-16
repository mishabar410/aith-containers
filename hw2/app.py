from flask import Flask
import os
import redis
import socket

app = Flask(__name__)

r = redis.Redis(host='redis_db', port=6379, decode_responses=True)

@app.route('/')
def hello():
    hostname = socket.gethostname()
    return f"Hello from {hostname}! This demonstrates a working web app container."

@app.route('/data')
def data():
    data_path = '/app/data/init_info.txt'
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            content = f.read()
        return f"Data from volume: {content}"
    return "No data found in volume (init container might have failed)."

@app.route('/hits')
def hits():
    try:
        count = r.incr('hits')
        return f"This page has been viewed {count} times (stored in Redis)."
    except redis.ConnectionError:
        return "Could not connect to Redis."

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
