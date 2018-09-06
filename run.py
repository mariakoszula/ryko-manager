from flask import Flask, render_template
from database import db_session

app = Flask(__name__)

# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     db_session.remove()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/schools_all')
def schools_all():
    return render_template("schools_all.html")

# @app.route('/sign')
# def sign():
#     return render_template("sign.html")


if __name__ == "__main__":
    app.run(debug=True)