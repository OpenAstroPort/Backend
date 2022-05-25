from flask import Flask
import json, serial

app = Flask(__name__)

@app.route('/')
def home():
    return json.dumps({'name': 'OATREST', 'version': 'beta-1.0.0'})