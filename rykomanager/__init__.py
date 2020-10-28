from flask import Flask
import logging.handlers
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from configparser import ConfigParser, ExtendedInterpolation
from os import path, getcwd
from shutil import copyfile

config_parser = ConfigParser(interpolation=ExtendedInterpolation())
config_template = path.join(getcwd(), "config.ini")
config_directory = path.join(path.split(getcwd())[0], 'rykomanager.ini')

if path.exists(config_template) and not path.exists(config_directory):
    print(f"Created configuration file {config_directory}")
    copyfile(config_template, config_directory)
config_parser.read_file(open(config_directory, encoding='utf-8'))

app = Flask(__name__, template_folder='templates')
app.secret_key = 'vDMWkzeO1d'

handler = logging.handlers.RotatingFileHandler('ryko-manager.log', maxBytes=10 * 1024 * 1024, backupCount=1)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
app.logger.addHandler(handler)
sess = Session()
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{config_parser.get('Database', 'name')}"
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = "my_secret_key"

db = SQLAlchemy(app)
sess.init_app(app)
import rykomanager.views
