from flask import Flask, logging
from logging.handlers import RotatingFileHandler
from flask_sqlalchemy import SQLAlchemy
import configuration as cfg

app = Flask(__name__)
app.secret_key = 'vDMWkzeO1d'
# handler = RotatingFileHandler('ryko-manager.log', maxBytes=10000, backupCount=1)
# handler.setLevel(logging.INFO)
#
# app.logger.setLevel(logging.INFO)
# app.logger.addHandler(handler)

app.config['SQLALCHEMY_DATABASE_URI'] = cfg.database_location
db = SQLAlchemy(app)

