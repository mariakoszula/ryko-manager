from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import configuration as cfg

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = cfg.database_location
db = SQLAlchemy(app)
