from flask import render_template, request, flash, redirect, url_for
from setup import app, db
from models import School, Contract
from documentManager.AnnexCreator import AnnexCreator


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/schools_all')
def schools_all():
    AllSchools = db.session.query(School).join(School.contracts).filter(Contract.program_id == 1).all() ## filtering by contract not working?!

    return render_template("schools_all.html", Schools=AllSchools)


@app.route('/school_form/<int:school_id>')
def school_form(school_id=None):
    return render_template("school_form.html",  School=School.query.filter_by(id=school_id).first_or_404(),
                                                Contracts=Contract.query.filter(Contract.school_id==school_id).all())


@app.route('/school_form/<int:school_id>/add_annex/', methods=['GET', 'POST'])
def school_form_add_annex(school_id=None):
    if request.method == 'POST':
        if not request.form['contract_date'] or not request.form['validity_date']:
            flash('Uzupełnij wszystkie daty', 'error')
        elif not request.form['fruitVeg_products'] and not request.form['dairy_products']:
            flash('Uzupełnij wartość produktu, którego liczba zmieniła się', 'error')
        else:
            ac = AnnexCreator(school_id)
            ac.create(request.form['contract_date'], request.form['validity_date'],
                       request.form['fruitVeg_products'], request.form['dairy_products'])

            return redirect(url_for('school_form', school_id=school_id))
    return render_template("add_annex_form.html", school=None)


if __name__ == "__main__":
    app.run(debug=True)