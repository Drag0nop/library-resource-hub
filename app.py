from flask import Flask, render_template, redirect, url_for, flash, session
from config import Config
from models.database import init_db
from routes.books import books_bp
from routes.members import members_bp
from routes.transactions import transactions_bp
from routes.auth import auth_bp

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
init_db()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(books_bp, url_prefix='/books')
app.register_blueprint(members_bp, url_prefix='/members')
app.register_blueprint(transactions_bp, url_prefix='/transactions')

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('home.html')

@app.context_processor
def inject_user():
    return dict(logged_in=('user_id' in session))

if __name__ == '__main__':
    app.run(debug=True)