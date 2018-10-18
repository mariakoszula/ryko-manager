from flask import render_template, request, flash, redirect, url_for
import datetime
from rykomanager import app
from rykomanager.documentManager.AnnexCreator import AnnexCreator
from rykomanager.documentManager.RecordCreator import RecordCreator
import rykomanager.configuration as cfg
from rykomanager.documentManager.DatabaseManager import DatabaseManager


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


@app.route('/create_records/<int:week_id>', methods=['GET', 'POST'])
def create_records_per_week(week_id):
    selected_schools_product_view = dict()
    schools = DatabaseManager.get_all_schools_with_contract(cfg.current_program_id) # schools which don't have record for this day
    weeks = DatabaseManager.get_product_no(week_no=1)
    print(weeks)
    record_context = {
        'schools_with_contracts': schools,
        'weekly_product': DatabaseManager.get_product_no(week_no=1),
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
            current_date = record_data.pop('record_selector')[0]
            record_list = list()
            for school_key, product_list in record_data.items():
                school_id = RecordCreator.extract_school_id(school_key)
                for product_id in product_list:
                    if product_id != "":
                        rc = RecordCreator(cfg.current_program_id, current_date, school_id, product_id)
                        rc.create()
                        record_list.append(rc)
                    else:
                        #@TODO warning msg display pop up
                        app.logger.warn("[$s] Product_id was not set for school_id: %s", "create_records_per_week", school_id)
            RecordCreator.generate_many(current_date, record_list)
            return redirect(url_for('record_created', current_date=current_date, week_id=week_id))

    return render_template("create_records.html", **record_context)


@app.route('/create_records/<int:week_id>/<string:current_date>', methods=['GET', 'POST'])
def record_created(current_date, week_id):
    daily_records = DatabaseManager.get_daily_records(current_date)
    if request.method == 'POST':
        if request.form['action']:
            action_record_list = request.form['action'].split("_")
            action = action_record_list[0]
            record_id = action_record_list[1]
            if action == "update":
                DatabaseManager.get_record(record_id).set_to_delivered()
                app.logger.info("Update state to Delivered Record.id %s", record_id)
            if action == "modify":
                pass
            if action == "update_product":
                pass
            if action == "delete":
                DatabaseManager.remove_record(record_id)
                app.logger.info("Remove: Record.id %s", record_id)
        return redirect(url_for('record_created', daily_records=daily_records, current_date=current_date, week_id=week_id))
    return render_template("generated_record.html", daily_records=daily_records, current_date=current_date, week_id=week_id)


@app.context_processor
def my_utility_processor():

    def update_record_state(record=None):
        if record:
            print(record.id)
    return dict(update_state=update_record_state)


if __name__ == "__main__":
    app.run(debug=True)