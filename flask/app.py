from flask import Flask

app = Flask(__name__)

# No functionality yet

@app.route('/')
def hello_world():
    return 'Hello, World!'
