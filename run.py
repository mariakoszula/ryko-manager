from flask import render_template, request, flash, redirect, url_for
from setup import app, db
from documentManager.AnnexCreator import AnnexCreator
from documentManager.RecordCreator import RecordCreator
import configuration as cfg
from documentManager.DatabaseManager import DatabaseManager
import datetime
from werkzeug.datastructures import ImmutableMultiDict

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


@app.route('/create_records')
def create_records():
    weeks = DatabaseManager.get_weeks(cfg.current_program_id)
    return render_template("create_records.html", Weeks=weeks, week=None, Schools=None)


selected_schools_product_view = dict()


@app.route('/create_records/<int:week_id>', methods=['GET', 'POST'])
def create_records_per_week(week_id):
    record_context = {
        'schools_with_contracts': DatabaseManager.get_all_schools_with_contract(cfg.current_program_id),
        'products_dairy': DatabaseManager.get_dairy_products(cfg.current_program_id),
        'products_veg': DatabaseManager.get_fruitVeg_products(cfg.current_program_id),
        'current_week': DatabaseManager.get_week(week_id, cfg.current_program_id),
        'datetime': datetime,
        'weeks': DatabaseManager.get_weeks(cfg.current_program_id),
        'selected_schools_product_view': selected_schools_product_view
    }
    if request.method == 'POST':
        #@TODO clean code: this is showing the school slector
        current_date = request.form.get('school_selector', None)
        if current_date and current_date not in record_context['selected_schools_product_view'].keys():
            record_context['selected_schools_product_view'][current_date] = list()
            school_list_req = request.form.getlist('schools_'+current_date)
            if school_list_req:
                for school_id in school_list_req:
                    school = DatabaseManager.get_school(school_id)
                    record_context['selected_schools_product_view'][current_date].append(school)

            selected_schools_product_view.update(record_context['selected_schools_product_view'])

            return render_template("create_records.html", **record_context)
        if request.form['record_selector']:
            record_data = request.form.to_dict(flat=False)
            current_date = record_data.pop('record_selector')

            for school_key, product_list in record_data.items():
                school_id = RecordCreator.extract_school_id(school_key)
                rc = RecordCreator(cfg.current_program_id, current_date, school_id)
                for product_id in product_list:
                    rc.create(product_id)

            return redirect(url_for('record_created', current_date=current_date))

    return render_template("create_records.html", **record_context)


@app.route('/create_records/<string:current_date>')
def record_created(current_date):
    daily_records = DatabaseManager.get_daily_records(cfg.current_program_id, current_date)
    return render_template("generated_record.html", daily_records=daily_records, current_date=current_date)


if __name__ == "__main__":
    app.run(debug=True)