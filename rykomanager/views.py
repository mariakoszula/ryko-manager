from flask import render_template, request, flash, redirect, url_for, session
import datetime
from rykomanager import app
from rykomanager.documentManager.AnnexCreator import AnnexCreator
from rykomanager.documentManager.ContractCreator import ContractCreator
from rykomanager.documentManager.RegisterCreator import RegisterCreator
from rykomanager.documentManager.SummaryCreator import SummaryCreator
from rykomanager.documentManager.ApplicationCreator import ApplicationCreator
from rykomanager.models import ProductName, ProductType, School, Program, Week, Product, RecordState, Record, Contract
from rykomanager.documentManager.DatabaseManager import DatabaseManager
from rykomanager.documentManager.RecordCreator import RecordCreator
from rykomanager.DateConverter import DateConverter
from rykomanager.name_strings import RECORDS_NEW_NAME, INVALID_ID, FILL_STR, FILL_BY_SCHOOL, DEFAULT_DATE_STR, \
    FILL_STR_SCHOOL, ALL_RECORDS_DOC_NAME


@app.route("/")
def index():
    return redirect(url_for('program'))


@app.route('/podsumowanie_nabial', methods=['GET', 'POST'])
def dairy_summrize(weeks=(1, 12)):
    if not session.get('program_id'):
        return redirect(url_for('program'))
    school_data = dict()
    product_remaining = get_remaning_products(school_data, ProductType.DAIRY)
    state_of_record = (RecordState.DELIVERED, RecordState.NOT_DELIVERED)
    if request.method == 'POST' and request.form["weeks_form"]:
        weeks = request.form["weeks_form"]
        if not "-" in weeks:
            weeks = int(weeks), int(weeks)
        else:
            weeks = int(request.form["weeks_form"].split("-")[0]), int(request.form["weeks_form"].split("-")[1])
        state = request.form["state"]
        if state == "DELIVERED":
            state_of_record = (RecordState.DELIVERED, RecordState.DELIVERED)
        elif state == "ALL":
            state_of_record = (RecordState.NOT_DELIVERED, RecordState.DELIVERED)
    dairy_summary = get_dairy_summary(weeks, state=state_of_record)
    return render_template("dairy_summrize.html", weeks=weeks, dairy_summary=dairy_summary,
                           school_data=school_data, product_remaining=product_remaining)


def get_dairy_summary(weeks, state):
    dairy_summary = dict()
    dairy_summary['milk_all'] = 0
    dairy_summary['yoghurt_all'] = 0
    dairy_summary['kefir_all'] = 0
    dairy_summary['cheese_all'] = 0
    schools = DatabaseManager.get_all_schools_with_contract(session.get('program_id'))
    for school in schools:
        dairy = dict()
        dairy['milk'] = DatabaseManager.get_product_amount(session.get('program_id'), school.id, ProductName.MILK,
                                                           weeks, state)
        dairy['yoghurt'] = DatabaseManager.get_product_amount(session.get('program_id'), school.id, ProductName.YOGHURT,
                                                              weeks, state)
        dairy['kefir'] = DatabaseManager.get_product_amount(session.get('program_id'), school.id, ProductName.KEFIR,
                                                            weeks, state)
        dairy['cheese'] = DatabaseManager.get_product_amount(session.get('program_id'), school.id, ProductName.CHEESE,
                                                             weeks, state)
        dairy_summary['milk_all'] += dairy['milk']
        dairy_summary['yoghurt_all'] += dairy['yoghurt']
        dairy_summary['kefir_all'] += dairy['kefir']
        dairy_summary['cheese_all'] += dairy['cheese']
        dairy_summary[school.nick] = dairy
    return dairy_summary


def get_fruitVeg_summary(weeks, state):
    fruitVeg_summary = dict()
    fruitVeg_summary['apple_all'] = 0
    fruitVeg_summary['pear_all'] = 0
    fruitVeg_summary['plum_all'] = 0
    fruitVeg_summary['strawberry_all'] = 0
    fruitVeg_summary['juice_all'] = 0
    fruitVeg_summary['carrot_all'] = 0
    fruitVeg_summary['radish_all'] = 0
    fruitVeg_summary['pepper_all'] = 0
    fruitVeg_summary['tomato_all'] = 0
    fruitVeg_summary['kohlrabi_all'] = 0

    schools = DatabaseManager.get_all_schools_with_contract(session.get('program_id'))
    for school in schools:
        fruitVeg = dict()
        fruitVeg['apple'] = DatabaseManager.get_product_amount(session.get('program_id'), school.id, ProductName.APPLE,
                                                               weeks, state)
        fruitVeg['pear'] = DatabaseManager.get_product_amount(session.get('program_id'), school.id, ProductName.PEAR,
                                                              weeks, state)
        fruitVeg['plum'] = DatabaseManager.get_product_amount(session.get('program_id'), school.id, ProductName.PLUM,
                                                              weeks, state)
        fruitVeg['strawberry'] = DatabaseManager.get_product_amount(session.get('program_id'), school.id,
                                                                    ProductName.STRAWBERRY, weeks, state)
        fruitVeg['juice'] = DatabaseManager.get_product_amount(session.get('program_id'), school.id, ProductName.JUICE,
                                                               weeks, state)
        fruitVeg['carrot'] = DatabaseManager.get_product_amount(session.get('program_id'), school.id,
                                                                ProductName.CARROT, weeks, state)
        fruitVeg['radish'] = DatabaseManager.get_product_amount(session.get('program_id'), school.id,
                                                                ProductName.RADISH, weeks, state)
        fruitVeg['pepper'] = DatabaseManager.get_product_amount(session.get('program_id'), school.id,
                                                                ProductName.PEPPER, weeks, state)
        fruitVeg['tomato'] = DatabaseManager.get_product_amount(session.get('program_id'), school.id,
                                                                ProductName.TOMATO, weeks, state)
        fruitVeg['kohlrabi'] = DatabaseManager.get_product_amount(session.get('program_id'), school.id,
                                                                  ProductName.KOHLRABI, weeks, state)

        fruitVeg_summary['apple_all'] += fruitVeg['apple']
        fruitVeg_summary['pear_all'] += fruitVeg['pear']
        fruitVeg_summary['plum_all'] += fruitVeg['plum']
        fruitVeg_summary['strawberry_all'] += fruitVeg['strawberry']
        fruitVeg_summary['juice_all'] += fruitVeg['juice']
        fruitVeg_summary['carrot_all'] += fruitVeg['carrot']
        fruitVeg_summary['radish_all'] += fruitVeg['radish']
        fruitVeg_summary['pepper_all'] += fruitVeg['pepper']
        fruitVeg_summary['tomato_all'] += fruitVeg['tomato']
        fruitVeg_summary['kohlrabi_all'] += fruitVeg['kohlrabi']

        fruitVeg_summary[school.nick] = fruitVeg
    return fruitVeg_summary


class ProductStats(object):
    def __init__(self, product: Product, kids_no):
        self.product_name = product.get_name_mapping()
        self.min_amount = product.min_amount
        self.taken_product = 0
        self.kids_no = kids_no

    def get_remained(self):
        return self.min_amount - self.taken_product

    def decrease_product(self, amount):
        self.taken_product = amount

    def __getitem__(self, item):
        if item == 0:
            return self.product_name
        if item == 1:
            return self.given_product
        if item == 2:
            return self.get_remained()
        if item == 3:
            return self.get_remained() * self.kids_no


def get_remaning_products(school_data, product_type):
    data = DatabaseManager.get_product_no(session.get('program_id'), product_type)
    schools = DatabaseManager.get_all_schools_with_contract(session.get('program_id'))
    products = DatabaseManager.get_products(session.get('program_id'), product_type)

    for school in schools:
        kids_no = DatabaseManager.get_current_contract(school.id, session.get('program_id')).dairy_products
        if not kids_no or kids_no == 0:
            continue

        # Prepare empty statistics
        if not school_data.get(school.nick, None):
            school_data[school.nick] = list()
            for product in products:
                school_data[school.nick].append(ProductStats(product, kids_no))

        for d in data:
            if school == d[0]:
                for product_stats in school_data[school.nick]:
                    if product_stats.product_name == d[1].get_name_mapping(): # @TODO this comparizon should be moved to Product, check how to compare to objects
                        product_stats.decrease_product(d[2])

    product_remaining = dict()
    for key, value in school_data.items():
        for v in value:
            if not product_remaining.get(v.product_name, None):
                product_remaining[v.product_name] = 0
            product_remaining[v.product_name] += v[3]
    return product_remaining


@app.route('/podsumowanie_owoceWarzywa', methods=['GET', 'POST'])
def fruitVeg_summrize(weeks=(1, 12)):
    if not session.get('program_id'):
        return redirect(url_for('program'))
    school_data = dict()
    product_remaining = get_remaning_products(school_data, ProductType.FRUIT_VEG)
    state_of_record = (RecordState.DELIVERED, RecordState.NOT_DELIVERED)
    if request.method == 'POST' and request.form["weeks_form"]:
        weeks = request.form["weeks_form"]
        if not "-" in weeks:
            weeks = int(weeks), int(weeks)
        else:
            weeks = int(request.form["weeks_form"].split("-")[0]), int(request.form["weeks_form"].split("-")[1])
        state = request.form["state"]
        if state == "DELIVERED":
            state_of_record = (RecordState.DELIVERED, RecordState.DELIVERED)
        elif state == "ALL":
            state_of_record = (RecordState.NOT_DELIVERED, RecordState.DELIVERED)
    fruitVeg_summary = get_fruitVeg_summary(weeks, state=state_of_record)
    return render_template("fruitVeg_summrize.html", weeks=weeks, fruitVeg_summary=fruitVeg_summary,
                           school_data=school_data, product_remaining=product_remaining)


@app.route('/schools_with_contract')
def schools_with_contract():
    if not session.get('program_id'):
        return redirect(url_for('program'))
    all_schools = DatabaseManager.get_all_schools_with_contract(session.get('program_id'))
    return render_template("schools_all.html", Schools=all_schools, program_id=session.get('program_id'),
                           invalid_school_id=INVALID_ID)

@app.route('/schools_all')
def schools_all():
    if not session.get('program_id'):
        return redirect(url_for('program'))
    all_schools = DatabaseManager.get_all_schools()
    return render_template("schools_all.html", Schools=all_schools, program_id=session.get('program_id'),
                           invalid_school_id=INVALID_ID)

@app.route('/create_register')
def create_register():
    if not session.get('program_id'):
        return redirect(url_for('program'))
    RegisterCreator(session.get('program_id')).create()
    flash('Rejestr został wygenerowany pomyślnie', 'info')
    return schools_all()


def empty_if_none(value):
    if not value:
        return ""
    return value


@app.route('/school_form/<int:school_id>', methods=['GET', 'POST'])
def school_form(school_id=INVALID_ID):
    if not session.get('program_id'):
        return redirect(url_for('program'))
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
            return redirect(
                url_for('school_form', school_id=id_of_school_being_added.id, School=id_of_school_being_added))

    current_school = DatabaseManager.get_school(school_id)
    if request.method == 'POST':
        data_to_update = {"nick": empty_if_none(request.form["nick"]), "name": empty_if_none(request.form["name"]),
                          "address": empty_if_none(request.form["address"]),
                          "city": empty_if_none(request.form["city"]),
                          "nip": empty_if_none(request.form["nip"]), "regon": empty_if_none(request.form["regon"]),
                          "email": empty_if_none(request.form["email"]), "phone": empty_if_none(request.form["phone"]),
                          "responsible_person": empty_if_none(request.form["responsible_person"]),
                          "representative": empty_if_none(request.form["representative"]),
                          "representative_nip": empty_if_none(request.form["representative_nip"]),
                          "representative_regon": empty_if_none(request.form["representative_regon"])}
        school_id = DatabaseManager.update_school_data(current_school, **data_to_update)
        return redirect(url_for('school_form', school_id=current_school.id))
    return render_template("school_form.html", School=current_school,
                           Contracts=DatabaseManager.get_all_contracts(school_id, session.get('program_id')))


@app.route('/school_form/<int:school_id>/add_annex', methods=['GET', 'POST'])
def school_form_add_annex(school_id):
    if not session.get('program_id'):
        return redirect(url_for('program'))
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


@app.route('/school_form/<int:school_id>/edit_annex/<int:annex_id>', methods=['GET', 'POST'])
def school_form_edit_annex(school_id, annex_id):
    if not session.get('program_id'):
        return redirect(url_for('program'))
    school = DatabaseManager.get_school(school_id)
    annex: Contract = DatabaseManager.get_existing_annex(annex_id)
    if request.method == 'POST':
        date = DateConverter.to_date(request.form['contract_date'])
        date_valid = DateConverter.to_date(request.form['validity_date'])
        fruitVeg_products = request.form['fruitVeg_products']
        dairy_products = request.form['dairy_products']
        if annex:
            annex.update(date, date_valid, fruitVeg_products, dairy_products)
            AnnexCreator(annex.school_id, annex.program_id, annex).generate()

            return redirect(url_for('school_form', school_id=school_id))
    return render_template("add_annex_form.html", school=school, annex=annex)


@app.route('/school_form/<int:school_id>/add_contract/', methods=['GET', 'POST'])
def school_form_add_contract(school_id=INVALID_ID):
    if not session.get('program_id'):
        return redirect(url_for('program'))
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


@app.route('/contract_delete/<int:school_id>/delete/<int:contract_id>', methods=['GET', 'POST'])
def contract_delete(school_id, contract_id):
    if not str(session.get('program_id')):
        return redirect(url_for('program'))
    DatabaseManager.remove_contract(contract_id)
    return render_template("school_form.html", School=DatabaseManager.get_school(school_id),
                           Contracts=DatabaseManager.get_all_contracts(school_id, session.get('program_id')))


@app.route('/create_records', methods=['GET', 'POST'])
def create_records():
    if not str(session.get('program_id')):
        return redirect(url_for('program'))
    all_weeks = DatabaseManager.get_weeks(session.get('program_id'))
    all_schools = DatabaseManager.get_all_schools_with_contract(session.get('program_id'))
    if request.method == 'POST':
        school_id = request.form.get('wz_school', None)
        if school_id:
            return redirect(url_for('school_records', school_id=school_id))
    return render_template("create_records.html", Weeks=all_weeks, School=all_schools)


@app.route('/create_records/<int:week_id>', methods=['GET', 'POST'])
def create_records_per_week(week_id):
    if not str(session.get('program_id')):
        return redirect(url_for('program'))
    selected_schools_product_view = dict()
    all_schools = DatabaseManager.get_all_schools_with_contract(
        session.get('program_id'))  # schools which don't have record for this day
    record_context = {
        'schools_with_contracts': all_schools,
        'products_dairy': DatabaseManager.get_dairy_products(session.get('program_id')),
        'products_veg': DatabaseManager.get_fruitVeg_products(session.get('program_id')),
        'current_week': DatabaseManager.get_week(week_id, session.get('program_id')),
        'datetime': datetime,
        'weeks': DatabaseManager.get_weeks(session.get('program_id')),
        'selected_schools_product_view': selected_schools_product_view,
    }
    duplicated_records_set = set()
    if request.method == 'POST':
        # @TODO clean code: this is showing the school slector
        current_date = request.form.get('school_selector', None)
        if current_date and current_date not in record_context['selected_schools_product_view'].keys():
            record_context['selected_schools_product_view'][current_date] = list()
            school_list_req = request.form.getlist('schools_' + current_date)
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
                    if not product_id:
                        continue
                    product_record: Record = DatabaseManager.get_existing_record(current_date, school_id, product_id)
                    product: Product = DatabaseManager.get_product(product_id)
                    assert (isinstance(product_record, Record) or product_record is None)
                    if not product_record:
                        rc = RecordCreator(session.get('program_id'), current_date, school_id, product_id)
                        rc.create()
                        record_list.append(rc)
                    else:
                        duplicated_records_set.add("{}: '{}' istnieje WZ dla '{}'".format(DatabaseManager.get_school(school_id).nick, product.get_name_mapping(), product_record.product.get_name_mapping()))
            RecordCreator.generate_many(record_list, RECORDS_NEW_NAME)
            # REGENERATE_FOR_ALL
            generation_date = datetime.date.today()
            existing_daily_records = DatabaseManager.get_daily_records(session.get('program_id'), current_date,
                                                                       generation_date)
            RecordCreator.regenerate_documentation(existing_daily_records)
            dup_record_msg = ""
            if duplicated_records_set:
                dup_record_msg = ", ".join(duplicated_records_set)
            return redirect(url_for('record_created', current_date=current_date, week_id=week_id,
                                    duplicated_records=dup_record_msg))
    return render_template("create_records.html", **record_context)


@app.route('/create_records/<int:week_id>/<string:current_date>', methods=['GET', 'POST'])
def record_created(current_date, week_id, duplicated_records=""):
    if not str(session.get('program_id')):
        return redirect(url_for('program'))
    daily_records = DatabaseManager.get_daily_records(session.get('program_id'), current_date)
    if request.method == 'GET':
        duplicated_records = request.args.get('duplicated_records')
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
                generation_date = DatabaseManager.get_record(record_id).generation_date
                DatabaseManager.remove_record(record_id)
                if generation_date:
                    daily_records = DatabaseManager.get_daily_records(session.get('program_id'), current_date,
                                                                      generation_date)
                    RecordCreator.regenerate_documentation(daily_records)
                app.logger.info("Remove: Record.id %s", record_id)
        return redirect(
            url_for('record_created', daily_records=daily_records, current_date=current_date, week_id=week_id,
                    duplicated_records=duplicated_records))
    if duplicated_records:
        flash("Nie możesz dodać WZtek: {}".format(duplicated_records), 'error')
    return render_template("generated_record.html", daily_records=daily_records, current_date=current_date,
                           week_id=week_id, duplicated_records=duplicated_records)


@app.route('/school_records/<int:school_id>', methods=['GET', 'POST'])
def school_records(school_id):
    if not session.get('program_id'):
        return redirect(url_for('program'))
    records = DatabaseManager.get_school_records(session.get('program_id'), school_id)
    if request.method == 'POST':
        if request.form['action']:
            action_record_list = request.form['action'].split("_")
            action = action_record_list[0]
            record_id = action_record_list[1]
            if action == "update":
                DatabaseManager.get_record(record_id).set_to_delivered()
                app.logger.info("Update state to Delivered Record.id %s", record_id)
            if action == "modify":
                pass  # @TODO modify records
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


@app.route('/create_summary/<int:is_first>', methods=['POST'])
def create_summary(is_first=0):
    if not session.get('program_id'):
        return redirect(url_for('program'))

    if request.method == 'POST':
        application_date = request.form["application_date"]

        if not application_date:
            return redirect(url_for('program_form', program_id=session.get('program_id')))
        # summary_creator = SummaryCreator(session.get('program_id'), is_first)
        # summary = summary_creator.create()
        #
        # if summary:
        #     appCreators = list()
        #     for school in DatabaseManager.get_all_schools_with_contract(session.get('program_id')):
        #         app = ApplicationCreator(session.get('program_id'), school, summary, application_date)
        #         if app.create():
        #             appCreators.append(app)
        #
        #     for appCreator in appCreators:
        #         appCreator.generate()
        #
        #     summary_creator.generate()
        # else:
        #     app.logger.error("create_summary: summary is None. Can not create Application.")

        school_nick_second = ["SP 17","Drzonków","Muzyczna","Przylep"]
        summary_creator_first = SummaryCreator(session.get('program_id'), 1)
        summary = summary_creator_first.create()

        if summary:
            appCreators = list()
            for school in DatabaseManager.get_all_schools_with_contract(session.get('program_id')):
                if school.nick not in school_nick_second:
                    app = ApplicationCreator(session.get('program_id'), school, summary, application_date)
                    if app.create():
                        appCreators.append(app)

            for appCreator in appCreators:
                appCreator.generate()

            summary_creator_first.generate()
        else:
            app.logger.error("create_summary: summary is None. Can not create Application.")

        summary_creator_second = SummaryCreator(session.get('program_id'), 0)
        summary = summary_creator_second.create()

        if summary:
            appCreators = list()
            for school in DatabaseManager.get_all_schools_with_contract(session.get('program_id')):
                if school.nick in school_nick_second:
                    app = ApplicationCreator(session.get('program_id'), school, summary, application_date)
                    if app.create():
                        appCreators.append(app)

            for appCreator in appCreators:
                appCreator.generate()

            summary_creator_second.generate()
        else:
            app.logger.error("create_summary: summary is None. Can not create Application.")
    return redirect(url_for("index", weeks=(1, 12), dairy_summary=None, school_data="", product_remaining=""))

@app.route('/program')
def program():
    all_programs = DatabaseManager.get_programs_all()
    if not str(session.get('program_id')):
        session['program_id'] = DatabaseManager.get_program().id
    current = request.args.get('current')
    current_session_program = DatabaseManager.get_program(current) if current else DatabaseManager.get_program(
        session.get('program_id'))
    if current_session_program:
        session['program_id'] = current_session_program.id
    return render_template("program.html", Programs=all_programs, current=current_session_program,
                           invalid_program_id=INVALID_ID)


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
        data_to_update = {"semester_no": empty_if_none(request.form["semester_no"]),
                          "school_year": empty_if_none(request.form["school_year"]),
                          "fruitVeg_price": empty_if_none(request.form["fruitVeg_price"]),
                          "dairy_price": empty_if_none(request.form["dairy_price"]),
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
    current_program = request.args.get('program')
    if not current_program:
        current_program = DatabaseManager.get_program(program_id)
    if request.method == 'POST':
        if not request.form['week_no'] or not request.form['start_date'] or not request.form['end_date']:
            flash('Uzupełnij wszystkie dane', 'error')
        else:
            new_week = Week(week_no=request.form['week_no'],
                            start_date=DateConverter.to_date(request.form['start_date']),
                            end_date=DateConverter.to_date(request.form['end_date']), program_id=current_program.id)
            if DatabaseManager.add_row(new_week):
                return redirect(url_for("program_form", program_id=current_program.id))
    return render_template("add_week.html", program_id=program_id, program=current_program)


@app.route('/program_form/<int:program_id>/add_product/<int:product_type>', methods=['GET', 'POST'])
def add_product(program_id, product_type):
    current_program = DatabaseManager.get_program(program_id)
    if request.method == 'POST':
        if not product_type:
            product_type = request.form['type']
            return redirect(url_for("add_product", program_id=current_program.id, product_type=product_type,
                                    program=current_program))
        if product_type:
            if not request.form['name'] or not request.form['min_amount']:
                flash('Uzupełnij nazwe i liczbe podań', 'error')
            else:
                new_product = Product(name=ProductName(int(request.form['name'])).name,
                                      type=ProductType(int(product_type)).name,
                                      min_amount=int(request.form['min_amount']), program_id=current_program.id)
                if DatabaseManager.add_row(new_product):
                    return redirect(url_for("program_form", program_id=current_program.id))
    return render_template("add_product.html", program_id=current_program.id, program=current_program,
                           product_type=product_type)


@app.route('/program_form/<int:program_id>/generate_contracts', methods=['GET', 'POST'])
def generate_contracts(program_id):
    current_program = DatabaseManager.get_program(program_id)
    contract_date = request.form["contract_date"]
    if not contract_date or contract_date == "dd.mm.rrrr":
        flash('Uzupełnij datę zawarcia umów', 'error')
    else:
        if session.get('program_id') == program_id:
            all_schols = DatabaseManager.get_all_schools()
            for school in all_schols:
                if school.nick != FILL_STR_SCHOOL:  # Dont create contract for school with not full date filled
                    new_contract = ContractCreator(school, session.get('program_id'))
                    new_contract.create(DateConverter.to_date(contract_date))
            flash("Umowy zostały wygenerowane pomyślnie", 'success')
        else:
            flash('Możesz wygnerować umowy tylko dla akutalnie wybranego programu', 'error')
    return render_template("program_form.html", Program=current_program)


if __name__ == "__main__":
    app.run(debug=True)
