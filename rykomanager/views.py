from flask import render_template, request, flash, redirect, url_for, session
import datetime
from rykomanager import app
from rykomanager.documentManager.AnnexCreator import AnnexCreator
from rykomanager.documentManager.ContractCreator import ContractCreator
from rykomanager.documentManager.RegisterCreator import RegisterCreator
from rykomanager.documentManager.SummaryCreator import SummaryCreator
from rykomanager.documentManager.ApplicationCreator import ApplicationCreator
from rykomanager.models import ProductName, ProductType, School, Program, Week
from rykomanager.documentManager.DatabaseManager import DatabaseManager
from rykomanager.documentManager.RecordCreator import RecordCreator
from rykomanager.DateConverter import DateConverter

INVALID_ID = 0xFFFF
FILL_STR = 0
DEFAULT_DATE_STR = "1990-01-01"
FILL_STR_SCHOOL = ""
FILL_BY_SCHOOL = ".........................................."


@app.route('/', methods=['GET', 'POST'])
def index(weeks=(1,12)):
    session['program_id'] = DatabaseManager.get_program().id if DatabaseManager.get_program() else None
    if not session['program_id']:
        return redirect(url_for('program'))
    school_data=dict()
    data = DatabaseManager.get_remaining_product(session['program_id'])
    schools = DatabaseManager.get_all_schools_with_contract(session['program_id'])
    for school in schools:
        for d in data:
            if (school == d[0]):
                if not school_data.get(school.nick, None):
                    school_data[school.nick]=list()
                kids_no = 0
                if d[1].type == ProductType.DAIRY:
                    kids_no = DatabaseManager.get_current_contract(school.id, session['program_id']).dairy_products
                elif d[1].type == ProductType.FRUIT_VEG:
                    kids_no = DatabaseManager.get_current_contract(school.id, session['program_id']).fruitVeg_products
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
    schools = DatabaseManager.get_all_schools_with_contract(session['program_id'])


    for school in schools:
        dairy = dict()
        dairy['milk']=DatabaseManager.get_product_amount(session['program_id'], school.id, ProductName.MILK, weeks)
        dairy_summary['milk_all']+=dairy['milk']
        dairy['yoghurt']=DatabaseManager.get_product_amount(session['program_id'], school.id, ProductName.YOGHURT, weeks)
        dairy_summary['yoghurt_all']+=dairy['yoghurt']
        dairy['kefir']=DatabaseManager.get_product_amount(session['program_id'], school.id, ProductName.KEFIR, weeks)
        dairy_summary['kefir_all']+=dairy['kefir']
        dairy['cheese']=DatabaseManager.get_product_amount(session['program_id'], school.id, ProductName.CHEESE, weeks)
        dairy_summary['cheese_all']+=dairy['cheese']
        dairy_summary[school.nick]=dairy

    return render_template("index.html", weeks=weeks, dairy_summary=dairy_summary,
                           school_data=school_data, product_remaining=product_remaining)


@app.route('/schools_all')
def schools_all():
    all_schools = DatabaseManager.get_all_schools()
    return render_template("schools_all.html", Schools=all_schools, program_id=session['program_id'], invalid_school_id=INVALID_ID)


@app.route('/create_register')
def create_register():
    RegisterCreator(session['program_id']).create()
    flash('Rejestr został wygenerowany pomyślnie', 'info')
    return schools_all()


def empty_if_none(value):
    if not value:
        return ""
    return value

@app.route('/school_form/<int:school_id>', methods=['GET', 'POST'])
def school_form(school_id=INVALID_ID):
    if school_id == INVALID_ID:
        id_of_school_being_added = DatabaseManager.id_of_school_being_added(FILL_STR_SCHOOL)
        if not id_of_school_being_added:
            new_school = School(nick=FILL_STR_SCHOOL, name=FILL_STR_SCHOOL,
                            address=FILL_STR_SCHOOL,
                            city=FILL_STR_SCHOOL, regon=FILL_STR_SCHOOL,
                            email=FILL_STR_SCHOOL, responsible_person=FILL_STR_SCHOOL + FILL_BY_SCHOOL,
                            phone=FILL_STR_SCHOOL + FILL_BY_SCHOOL)
            if DatabaseManager.add_row(new_school):
                return redirect(url_for('school_form', school_id=new_school.id, School=new_school))
            else:
                return redirect(url_for('school_form', school_id=INVALID_ID))
        else:
            return redirect(url_for('school_form', school_id=id_of_school_being_added.id, School=id_of_school_being_added))

    current_school = DatabaseManager.get_school(school_id)
    contracts = DatabaseManager.get_all_contracts(school_id, session['program_id'])
    if request.method == 'POST':
            data_to_update = {"nick": empty_if_none(request.form["nick"]), "name": empty_if_none(request.form["name"]),
                              "address": empty_if_none(request.form["address"]), "city": empty_if_none(request.form["city"]),
                              "nip": empty_if_none(request.form["nip"]), "regon": empty_if_none(request.form["regon"]),
                              "email": empty_if_none(request.form["email"]), "phone": empty_if_none(request.form["phone"]),
                              "responsible_person": empty_if_none(request.form["responsible_person"]),
                              "representative": empty_if_none(request.form["representative"]),
                              "representative_nip": empty_if_none(request.form["representative_nip"]),
                              "representative_regon": empty_if_none(request.form["representative_regon"])}
            school_id = DatabaseManager.update_school_data(current_school, **data_to_update)
            return redirect(url_for('school_form', school_id=current_school.id))
    return render_template("school_form.html",  School=current_school,
                                                Contracts=DatabaseManager.get_all_contracts(school_id, session['program_id']))


@app.route('/school_form/<int:school_id>/add_annex/', methods=['GET', 'POST'])
def school_form_add_annex(school_id):
    school = DatabaseManager.get_school(school_id)
    if request.method == 'POST':
        if not request.form['contract_date'] or not request.form['validity_date']:
            flash('Uzupełnij wszystkie daty', 'error')
        elif not request.form['fruitVeg_products'] and not request.form['dairy_products']:
            flash('Uzupełnij wartość produktu, którego liczba zmieniła się', 'error')
        else:
            ac = AnnexCreator(school_id, session['program_id'])
            ac.create(request.form['contract_date'], request.form['validity_date'],
                       request.form['fruitVeg_products'], request.form['dairy_products'])

            return redirect(url_for('school_form', school_id=school_id))
    return render_template("add_annex_form.html", school=school)


@app.route('/school_form/<int:school_id>/add_contract/', methods=['GET', 'POST'])
def school_form_add_contract(school_id=INVALID_ID):
    school = DatabaseManager.get_school(school_id)
    school_contract = DatabaseManager.get_contract(school_id, session['program_id'])
    if request.method == 'POST':
        date = DateConverter.to_date(request.form['contract_date'])
        fruitVeg_products = request.form['fruitVeg_products']
        dairy_products = request.form['dairy_products']

        if not school_contract:
            if not date:
                flash('Uzupełnij datę zawarcia umowy', 'error')
            else:
                new_contract = ContractCreator(school, session['program_id'])
                new_contract.create(date)
                return redirect(url_for('school_form', school_id=school_id))

        if school_contract:
            school_contract.update(date, date, fruitVeg_products, dairy_products)
            return redirect(url_for('school_form', school_id=school_id))
    return render_template("add_contract_form.html", school=school, contract=school_contract)


@app.route('/create_records', methods=['GET', 'POST'])
def create_records():
    weeks = DatabaseManager.get_weeks(session['program_id'])
    Schools = DatabaseManager.get_all_schools_with_contract(session['program_id'])
    if request.method == 'POST':
        school_id = request.form.get('wz_school', None)
        if school_id:
            return redirect(url_for('school_records', school_id=school_id))
    return render_template("create_records.html", Weeks=weeks, week=None, Schools=Schools)


@app.route('/create_records/<int:week_id>', methods=['GET', 'POST'])
def create_records_per_week(week_id):
    selected_schools_product_view = dict()
    schools = DatabaseManager.get_all_schools_with_contract(session['program_id']) # schools which don't have record for this day
    weeks = DatabaseManager.get_product_no(session['program_id'], week_no=1)
    record_context = {
        'schools_with_contracts': schools,
        'weekly_product': DatabaseManager.get_product_no(session['program_id'], week_no=1),
        'products_dairy': DatabaseManager.get_dairy_products(session['program_id']),
        'products_veg': DatabaseManager.get_fruitVeg_products(session['program_id']),
        'current_week': DatabaseManager.get_week(week_id, session['program_id']),
        'datetime': datetime,
        'weeks': DatabaseManager.get_weeks(session['program_id']),
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
                        rc = RecordCreator(session['program_id'], current_date, school_id, product_id)
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
    daily_records = DatabaseManager.get_daily_records(session['program_id'], current_date)
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
    records = DatabaseManager.get_school_records(session['program_id'], school_id)
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
    summary_craetor = SummaryCreator(session['program_id'], week_id, week_no)
    summary = summary_craetor.create()

    if summary:
        appCreators = list()
        for school in DatabaseManager.get_all_schools_with_contract(session['program_id']):
            app = ApplicationCreator(session['program_id'], school, summary)
            if app.create():
                appCreators.append(app)

        for appCreator in appCreators:
            appCreator.generate()

        summary_craetor.generate()
    else:
        app.logger.error("create_summary: summary is None. Can not create Application.")
    return redirect(url_for("index", weeks=(1,12), dairy_summary=None, school_data="", product_remaining=""))


@app.route('/program')
def program():
    all_programs=DatabaseManager.get_programs_all()
    current = request.args.get('current')
    current_session_program = DatabaseManager.get_program(current) if current else DatabaseManager.get_program(session['program_id'])
    if current_session_program:
        session['program_id'] = current_session_program.id
    return render_template("program.html", Programs=all_programs, current=current_session_program, invalid_program_id=INVALID_ID)


@app.route('/program_form/<int:program_id>', methods=['GET', 'POST'])
def program_form(program_id=INVALID_ID):
    if program_id == INVALID_ID:
        id_of_program_being_added = DatabaseManager.id_of_program_being_added(FILL_STR)
        if not id_of_program_being_added:
            new_program = Program(semester_no=FILL_STR, school_year=FILL_STR, fruitVeg_price=FILL_STR,
                                  dairy_price=FILL_STR, start_date=DateConverter.to_date(DEFAULT_DATE_STR),
                                  end_date=DateConverter.to_date(DEFAULT_DATE_STR),
                                  dairy_min_per_week=FILL_STR, fruitVeg_min_per_week=FILL_STR, dairy_amount=FILL_STR,
                                  fruitVeg_amount=FILL_STR)
            if DatabaseManager.add_row(new_program):
                return redirect(url_for('program_form', program_id=new_program.id))
            else:
                return redirect(url_for('program_form', program_id=INVALID_ID))
        else:
            return redirect(url_for('program_form', program_id=id_of_program_being_added.id))

    current_program = DatabaseManager.get_program(program_id)
    if request.method == 'POST':
        data_to_update = {"semester_no": empty_if_none(request.form["semester_no"]), "school_year": empty_if_none(request.form["school_year"]),
                          "fruitVeg_price": empty_if_none(request.form["fruitVeg_price"]), "dairy_price": empty_if_none(request.form["dairy_price"]),
                          "start_date": empty_if_none(DateConverter.to_date(request.form["start_date"])),
                          "end_date": empty_if_none(DateConverter.to_date(request.form["end_date"])),
                          "dairy_min_per_week": empty_if_none(request.form["dairy_min_per_week"]),
                          "fruitVeg_min_per_week": empty_if_none(request.form["fruitVeg_min_per_week"]),
                          "dairy_amount": empty_if_none(request.form["dairy_amount"]),
                          "fruitVeg_amount": empty_if_none(request.form["fruitVeg_amount"])}
        program_id = DatabaseManager.update_program_data(current_program, **data_to_update)
        return redirect(url_for('program_form', program_id=program_id))
    return render_template("program_form.html", Program=current_program)


@app.route('/program_form/<int:program_id>/add_week', methods=['GET', 'POST'])
def add_week(program_id):
    program = request.args.get('program')
    if not program:
        program = DatabaseManager.get_program(program_id)
    if request.method == 'POST':
        if not request.form['week_no'] or not request.form['start_date'] or not request.form['end_date']:
            flash('Uzupełnij wszystkie dane', 'error')
        else:
            new_week = Week(week_no=request.form['week_no'], start_date=DateConverter.to_date(request.form['start_date']),
                            end_date=DateConverter.to_date(request.form['end_date']), program_id=program.id)
            if DatabaseManager.add_row(new_week):
                return redirect(url_for("program_form", program_id=program.id))
    return render_template("add_week.html", program=program)


@app.route('/program_form/<int:program_id>/generate_contracts', methods=['GET', 'POST'])
def generate_contracts(program_id):
    current_program = DatabaseManager.get_program(program_id)
    contract_date = request.form["contract_date"]
    if not contract_date or contract_date == "dd.mm.rrrr":
        flash('Uzupełnij datę zawarcia umów', 'error')
    else:
        if session['program_id'] == program_id :
            all_schols = DatabaseManager.get_all_schools()
            for school in all_schols:
                if school.nick != FILL_STR_SCHOOL: #Dont create contract for school with not full date filled
                    new_contract = ContractCreator(school, session['program_id'])
                    new_contract.create(DateConverter.to_date(contract_date))
            flash("Umowy zostały wygenerowane pomyślnie", 'success')
        else:
            flash('Możesz wygnerować umowy tylko dla akutalnie wybranego programu', 'error')
    return render_template("program_form.html", Program=current_program)


if __name__ == "__main__":
    app.run(debug=True)