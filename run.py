from flask import render_template, request
from setup import app, db
from models import School, Contract


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/schools_all')
def schools_all():
    AllSchools = db.session.query(School).join(School.contracts).filter(Contract.program_id == 1).all() ## filtering by contract not working?!

    return render_template("schools_all.html", Schools=AllSchools)


@app.route('/school_form/<int:school_id>')
def school_form(school_id=None):
    return render_template("school_form.html", School=School.query.filter_by(id=school_id).first_or_404())


if __name__ == "__main__":
    app.run(debug=True)