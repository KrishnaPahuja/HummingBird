from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'some_random_characters' # is setup when dealing with forms
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # path where db is located
# /// indicate relative path of current directory
db = SQLAlchemy(app) # db instance

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login' # function name for our login route
login_manager.login_message_category = 'warning'

from main import routes

