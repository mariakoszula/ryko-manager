from flask import Flask
import logging.handlers
from flask_sqlalchemy import SQLAlchemy
import rykomanager.configuration as cfg
from flask_session import Session

app = Flask(__name__, template_folder='templates')
app.secret_key = 'vDMWkzeO1d'

handler = logging.handlers.RotatingFileHandler('ryko-manager.log', maxBytes=10*1024*1024, backupCount=1)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
app.logger.addHandler(handler)
sess = Session()
app.config['SQLALCHEMY_DATABASE_URI'] = cfg.database_location
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = "my_secret_key"

db = SQLAlchemy(app)
sess.init_app(app)
import rykomanager.views
