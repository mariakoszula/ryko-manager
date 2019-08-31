from flask import render_template, request, flash, redirect, url_for
import datetime
from rykomanager import app
from rykomanager.documentManager.AnnexCreator import AnnexCreator
from rykomanager.documentManager.ContractCreator import ContractCreator
from rykomanager.documentManager.RecordCreator import RecordCreator
from rykomanager.documentManager.RegisterCreator import RegisterCreator
from rykomanager.documentManager.SummaryCreator import SummaryCreator
from rykomanager.documentManager.ApplicationCreator import ApplicationCreator
from rykomanager.models import ProductName, ProductType
import rykomanager.configuration as cfg
from rykomanager.documentManager.DatabaseManager import DatabaseManager
from rykomanager.documentManager.RecordCreator import RecordCreator
from rykomanager.DateConverter import DateConverter


@app.route('/', methods=['GET', 'POST'])
def index(weeks=(1,12)):
    school_data=dict()
    data = DatabaseManager.get_remaining_product()
    schools = DatabaseManager.get_all_schools_with_contract(session.get('program_id'))
    print("Program", session.get('program_id'), "SCHOOLDS", schools)
    for school in schools:
        for d in data:
            if (school == d[0]):
                if not school_data.get(school.nick, None):
                    school_data[school.nick]=list()
                kids_no = 0
                if d[1].type == ProductType.DAIRY:
                    kids_no = DatabaseManager.get_current_contract(school.id, session.get('program_id')).dairy_products
                elif d[1].type == ProductType.FRUIT_VEG:
                    kids_no = DatabaseManager.get_current_contract(school.id, session.get('program_id')).fruitVeg_products
                remaining_product = d[1].min_amount - d[2]
                school_data[school.nick].append((d[1].get_name_mapping(), d[2], remaining_product, remaining_product*kids_no))
    product_remaining = dict()
    for key, value in school_data.items():
        for v in value:
            if not product_remaining.get(v[0], None):
                product_remaining[v[0]] = 0
            product_remaining[v[0]] += v[3]

    if request.method == 'POST' and request.form["weeks_form"]:
        weeks = int(request.form["weeks_form"].split("-")[0]), int(request.form["weeks_form"].split("-")[1])
    dairy_summary = dict()
    dairy_summary['milk_all'] = 0
    dairy_summary['yoghurt_all'] = 0
    dairy_summary['kefir_all'] = 0
    dairy_summary['cheese_all'] = 0
    schools = DatabaseManager.get_all_schools_with_contract(session.get('program_id'))
    for school in schools:
        dairy = dict()
        dairy['milk']=DatabaseManager.get_product_amount(school.id, ProductName.MILK, weeks)
        dairy_summary['milk_all']+=dairy['milk']
        dairy['yoghurt']=DatabaseManager.get_product_amount(school.id, ProductName.YOGHURT, weeks)
        dairy_summary['yoghurt_all']+=dairy['yoghurt']
        dairy['kefir']=DatabaseManager.get_product_amount(school.id, ProductName.KEFIR, weeks)
        dairy_summary['kefir_all']+=dairy['kefir']
        dairy['cheese']=DatabaseManager.get_product_amount(school.id, ProductName.CHEESE, weeks)
        dairy_summary['cheese_all']+=dairy['cheese']
        dairy_summary[school.nick]=dairy

    return render_template("index.html", weeks=weeks, dairy_summary=dairy_summary,
                           school_data=school_data, product_remaining=product_remaining)


@app.route('/schools_all')
def schools_all():
    all_schools = DatabaseManager.get_all_schools()
    print("SCHOOLS", all_schools)
    return render_template("schools_all.html", Schools=all_schools, program_id=session.get('program_id'))


@app.route('/create_register')
def create_register():
    RegisterCreator().create()
    return schools_all()


@app.route('/school_form/<int:school_id>')
def school_form(school_id=None):
    return render_template("school_form.html",  School=DatabaseManager.get_school(school_id),
                                                Contracts=DatabaseManager.get_all_contracts(school_id, session.get('program_id')))


@app.route('/school_form/<int:school_id>/add_annex/', methods=['GET', 'POST'])
def school_form_add_annex(school_id):
    school = DatabaseManager.get_school(school_id)
    if request.method == 'POST':
        if not request.form['contract_date'] or not request.form['validity_date']:
            flash('Uzupełnij wszystkie daty', 'error')
        elif not request.form['fruitVeg_products'] and not request.form['dairy_products']:
            flash('Uzupełnij wartość produktu, którego liczba zmieniła się', 'error')
        else:
            ac = AnnexCreator(school_id, session.get('program_id'))
            ac.create(request.form['contract_date'], request.form['validity_date'],
                       request.form['fruitVeg_products'], request.form['dairy_products'])

            return redirect(url_for('school_form', school_id=school_id))
    return render_template("add_annex_form.html", school=school)


@app.route('/school_form/<int:school_id>/add_contract/', methods=['GET', 'POST'])
def school_form_add_contract(school_id):
    school = DatabaseManager.get_school(school_id)
    school_contract = DatabaseManager.get_contract(school_id, session.get('program_id'))
    if request.method == 'POST':
        date = DateConverter.to_date(request.form['contract_date'])
        fruitVeg_products = request.form['fruitVeg_products']
        dairy_products = request.form['dairy_products']

        if not school_contract:
            if not date:
                flash('Uzupełnij datę zawarcia umowy', 'error')
            else:
                new_contract = ContractCreator(school, session.get('program_id'))
                new_contract.create(date)
                return redirect(url_for('school_form', school_id=school_id))

        if school_contract:
            school_contract.update(date, date, fruitVeg_products, dairy_products)
            return redirect(url_for('school_form', school_id=school_id))
    return render_template("add_contract_form.html", school=school, contract=school_contract)


@app.route('/create_records', methods=['GET', 'POST'])
def create_records():
    weeks = DatabaseManager.get_weeks(session.get('program_id'))
    Schools = DatabaseManager.get_all_schools_with_contract(session.get('program_id'))
    if request.method == 'POST':
        school_id = request.form.get('wz_school', None)
        if school_id:
            return redirect(url_for('school_records', school_id=school_id))
    return render_template("create_records.html", Weeks=weeks, week=None, Schools=Schools)


@app.route('/create_records/<int:week_id>', methods=['GET', 'POST'])
def create_records_per_week(week_id):
    selected_schools_product_view = dict()
    schools = DatabaseManager.get_all_schools_with_contract(session.get('program_id')) # schools which don't have record for this day
    weeks = DatabaseManager.get_product_no(week_no=1)
    record_context = {
        'schools_with_contracts': schools,
        'weekly_product': DatabaseManager.get_product_no(week_no=1),
        'products_dairy': DatabaseManager.get_dairy_products(session.get('program_id')),
        'products_veg': DatabaseManager.get_fruitVeg_products(session.get('program_id')),
        'current_week': DatabaseManager.get_week(week_id, session.get('program_id')),
        'datetime': datetime,
        'weeks': DatabaseManager.get_weeks(session.get('program_id')),
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
                        rc = RecordCreator(session.get('program_id'), current_date, school_id, product_id)
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


@app.route('/school_records/<int:school_id>', methods=['GET', 'POST'])
def school_records(school_id):
    records = DatabaseManager.get_school_records(school_id)
    if request.method == 'POST':
        if request.form['action']:
            action_record_list = request.form['action'].split("_")
            action = action_record_list[0]
            record_id = action_record_list[1]
            if action == "update":
                DatabaseManager.get_record(record_id).set_to_delivered()
                app.logger.info("Update state to Delivered Record.id %s", record_id)
            if action == "modify":
                pass #@TODO modify records
            if action == "delete":
                DatabaseManager.remove_record(record_id)
                app.logger.info("Remove: Record.id %s", record_id)
        return redirect(url_for('school_records', school_id=school_id))
    return render_template("generated_record_per_school.html", records=records)


# @app.route('/school_records/<int:school_id>/<int:record_id>', methods=['GET', 'POST'])
# def modify_record(record_id):
#     record=DatabaseManager.get_record(record_id)
#     return render_template("modify_record.html", record=record)

@app.context_processor
def my_utility_processor():

    def update_record_state(record=None):
        if record:
            print(record.id)
    return dict(update_state=update_record_state)


@app.route('/create_summary/<int:week_id>')
def create_summary(week_id, week_no=6):
    print("MMMM")
    print(DatabaseManager.get_summary(program_id=session.get('program_id')) is None)
    summary = SummaryCreator(week_id, week_no, DatabaseManager.get_summary(program_id=session.get('program_id')) is None)
    summary.create()

    appCreators = list()
    for school in DatabaseManager.get_all_schools_with_contract(session.get('program_id')):
        app = ApplicationCreator(school.id, summary.get_id()) # TODO get proper summary_id form ids
        if app.create():
            appCreators.append(app)

    for appCreator in appCreators:
        appCreator.generate()

    summary.generate()
    return redirect(url_for("index", weeks=(1,12), dairy_summary=None, school_data="", product_remaining=""))


if __name__ == "__main__":
    app.run(debug=True)