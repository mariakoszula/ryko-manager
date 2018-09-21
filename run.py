from flask import render_template, request, flash, redirect, url_for
from setup import app, db
from documentManager.AnnexCreator import AnnexCreator
import configuration as cfg
from documentManager.DatabaseManager import DatabaseManager

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/schools_all')
def schools_all():
    all_schools_with_contract = DatabaseManager.get_all_schools_with_contract(cfg.current_program_id)
    
    return render_template("schools_all.html", Schools=all_schools_with_contract)


@app.route('/school_form/<int:school_id>')
def school_form(school_id=None):
    return render_template("school_form.html",  School=DatabaseManager.get_school(school_id),
                                                Contracts=DatabaseManager.get_all_contracts(school_id, cfg.current_program_id))


@app.route('/school_form/<int:school_id>/add_annex/', methods=['GET', 'POST'])
def school_form_add_annex(school_id=None):
    if request.method == 'POST':
        if not request.form['contract_date'] or not request.form['validity_date']:
            flash('Uzupełnij wszystkie daty', 'error')
        elif not request.form['fruitVeg_products'] and not request.form['dairy_products']:
            flash('Uzupełnij wartość produktu, którego liczba zmieniła się', 'error')
        else:
            if request.form['is_contract']: # @TODO add properly action when checkbox is checked
                app.logger.warn("Var is_annex is not set: Creating contract is not yet implemented")
            else:
                ac = AnnexCreator(school_id, cfg.current_program_id)
                ac.create(request.form['contract_date'], request.form['validity_date'],
                           request.form['fruitVeg_products'], request.form['dairy_products'])

            return redirect(url_for('school_form', school_id=school_id))
    return render_template("add_annex_form.html", school=None)


if __name__ == "__main__":
    app.run(debug=True)