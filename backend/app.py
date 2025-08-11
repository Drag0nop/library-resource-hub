from flask import Flask, render_template
from flask_cors import CORS
from routes import api

app = Flask(__name__, template_folder='../static', static_folder='../static')
CORS(app)

app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)