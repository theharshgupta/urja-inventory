from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'codes'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

WHOOSH_BASE = 'site.db'

db = SQLAlchemy(app=app)
bcrypt = Bcrypt()
login_manager = LoginManager(app=app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
from flaskblog import routes
