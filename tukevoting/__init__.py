from turtle import position
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads



app = Flask(__name__)
app.config['SECRET_KEY'] = '6c873d2051c8a755aaa19e3969893ebd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db?check_same_thread=False'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['UPLOADED_PHOTOS_DEST'] = 'tukevoting/images'



photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager() 
login_manager.init_app(app)
login_manager.login_view="login"
login_manager.login_message_category = 'info'



from tukevoting import routes