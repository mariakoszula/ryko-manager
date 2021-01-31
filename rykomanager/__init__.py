from flask import Flask
import logging.handlers
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from configparser import ConfigParser, ExtendedInterpolation
from os import path, getcwd
from shutil import copyfile

config_parser = ConfigParser(interpolation=ExtendedInterpolation())
config_template = path.join(getcwd(), "config.ini")
config_file_name = 'rykomanager.ini'
config_file = path.join(path.split(getcwd())[0], config_file_name)

if path.exists(config_template) and not path.exists(config_file):
    print(f"Created configuration file {config_file}")
    copyfile(config_template, config_file)
print(f"Directory with program configuration: {config_file}")
config_parser.read_file(open(config_file, encoding='utf-8'))

app = Flask(__name__, template_folder='templates')

handler = logging.handlers.RotatingFileHandler('ryko-manager.log', maxBytes=10 * 1024 * 1024, backupCount=1)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
app.logger.addHandler(handler)
session = Session()

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{config_parser.get('Database', 'name')}"
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'vDMWkzeO1d'

db = SQLAlchemy(app)
session.init_app(app)
import rykomanager.views
