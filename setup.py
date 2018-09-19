from flask import Flask
import logging
import logging.handlers
from flask_sqlalchemy import SQLAlchemy
import configuration as cfg

app = Flask(__name__)
app.secret_key = 'vDMWkzeO1d'
handler = logging.handlers.RotatingFileHandler('ryko-manager.log', maxBytes=10*1024*1024, backupCount=1)
handler.setLevel(logging.INFO)

app.logger.addHandler(handler)

app.config['SQLALCHEMY_DATABASE_URI'] = cfg.database_location
db = SQLAlchemy(app)

