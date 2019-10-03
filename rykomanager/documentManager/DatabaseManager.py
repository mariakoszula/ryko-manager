from rykomanager.models import School, Contract, Program, Week, Product, ProductType, Record, ProductName, Summary, Application, RecordState
from rykomanager import db, app
from abc import ABC, abstractmethod
import re
from sqlalchemy import func, exc, update
import datetime
from rykomanager.DateConverter import DateConverter
import rykomanager.configuration as cfg


class DatabaseManager(ABC):

    def __init__(self):
        super(DatabaseManager, self).__init__()

    @abstractmethod
    def update_row(self):
        pass

    @staticmethod
    def modify_row():
        db.session.commit()

    @staticmethod
    def get_school(school_id):
        return School.query.filter_by(id=school_id).first()

    @staticmethod
    def get_contract(school_id, program_id):
        return Contract.query.filter(Contract.school_id==school_id).filter(Contract.program_id==program_id)\
            .filter(Contract.is_annex==False).first()

    @staticmethod
    def get_annex(annex_id):
        return Contract.query.filter(Contract.id==annex_id).filter(Contract.is_annex==True).first()

    @staticmethod
    def get_contracts(program_id):
        return Contract.query.filter(Contract.program_id==program_id).order_by(Contract.school_id).order_by(Contract.contract_no).all()

    @staticmethod
    def is_annex(validity_date, school_id):
        rdate = validity_date if not isinstance(validity_date, datetime.datetime) else DateConverter.to_string(validity_date)
        return Contract.query.join(Contract.school).filter(School.id==school_id)\
            .filter(Contract.validity_date == DateConverter.to_date(rdate)).all()

    @staticmethod
    def is_summary(no, year):
        return Summary.query.filter_by(no=no).filter_by(year=year).all()

    @staticmethod
    def get_next_annex_no(school_id, program_id):
        contracts = Contract.query.filter(Contract.school_id == school_id).filter(Contract.program_id == program_id).all()
        annex_no_list = [int(re.findall(r"\d+_(\d+)", contract.contract_no)[0]) for contract in contracts if "_" in str(contract.contract_no)]
        if not annex_no_list:
            return 1
        else:
            return max(annex_no_list) + 1

    @staticmethod
    def get_next_contract_no(program_id):
        last_contract = Contract.query.filter(Contract.program_id == program_id).filter(Contract.is_annex==False).order_by(Contract.contract_no.desc()).first()
        if not last_contract:
            return 1
        else:
            return last_contract.contract_no + 1

    @staticmethod
    def get_contract_year(program_id):
        return 2019

    @staticmethod
    def get_all_schools_with_contract(program_id):
        return db.session.query(School).join(School.contracts).filter(
            Contract.program_id.like(program_id)).all()

    @staticmethod
    def get_school(school_id):
        return db.session.query(School).filter(School.id.like(school_id)).first()

    @staticmethod
    def get_all_schools():
        return School.query.all()

    @staticmethod
    def get_all_contracts(school_id, program_id):
        return Contract.query.filter(Contract.school_id == school_id).filter(Contract.program_id == program_id).all()

    @staticmethod
    def get_current_contract(school_id, program_id, date=None):
        date_to_compare = DateConverter.to_date(date) if date else datetime.datetime.now()
        res = School.query.filter(School.id.like(school_id)).first()
        for contract in res.contracts:
            if contract.program_id == program_id and contract.validity_date.date() <= date_to_compare.date():
                return contract
        return None

    @staticmethod
    def get_weeks(program_id):
        return Week.query.filter(Week.program_id == program_id).all()

    @staticmethod
    def get_week(week_id, program_id):
        return Week.query.filter(Week.program_id == program_id).filter(Week.id == week_id).first()

    @staticmethod
    def get_week_by_date(date):
        rdate = date if isinstance(date, datetime.datetime) else DateConverter.to_date(date, pattern="%Y-%m-%d %H:%M:%S")
        return Week.query.filter(Week.start_date <= rdate).filter(Week.end_date >= rdate).first()

    @staticmethod
    def get_fruitVeg_products(program_id):
        return Product.query.filter(Product.program_id.like(program_id)).filter(Product.type.like(ProductType.FRUIT_VEG)).all()

    @staticmethod
    def get_dairy_products(program_id):
        return Product.query.filter(Product.program_id.like(program_id)).filter(Product.type.like(ProductType.DAIRY)).all()

    @staticmethod
    def get_daily_records(program_id, current_date, generation_date=None):
        cdate = DateConverter.to_date(current_date)
        gen_date = DateConverter.to_date(generation_date)
        print(cdate, type(cdate), gen_date, type(gen_date))
        if gen_date:
            return Record.query.filter(Product.program_id.like(program_id)).filter(Record.date.like(cdate)).filter(Record.generation_date.like(gen_date)).all()
        return Record.query.filter(Product.program_id.like(program_id)).filter(Record.date.like(cdate)).all()

    @staticmethod
    def get_school_records(program_id, school_id):
        return Record.query.join(Record.contract).join(Contract.school).filter(Program.id.like(program_id)).filter(School.id.like(school_id)).all()

    @staticmethod
    def get_product(program_id, product_id):
        return Product.query.filter(Product.program_id.like(program_id)).filter(Product.id.like(product_id)).first()

    @staticmethod
    def get_product_no(program_id, week_no=None):
        if not week_no:
            return Record.query.join(Record.contract).join(Record.product).join(Contract.school).filter(Contract.program_id == program_id)\
                .with_entities(School, Product, func.count(Product.name)).group_by(School.nick, Product.name).all()
        return Record.query.join(Record.contract).join(Record.product).join(Contract.school).join(Record.week).filter(Week.week_no.like(week_no))\
            .filter(Week.program_id == program_id)\
            .with_entities(School, Product, func.count(Product.type)).group_by(School.nick, Product.type).all()

    @staticmethod
    def remove_record(id):
        Record.query.filter(Record.id == id).delete()
        db.session.commit()

    @staticmethod
    def remove_application(id):
        #@TODO acutally check if deleted
        Application.query.filter(Application.id == id).delete()
        db.session.commit()
        return True

    @staticmethod
    def remove_contract(id):
        Contract.query.filter(Contract.id == id).delete()
        db.session.commit()

    @staticmethod
    def add_row(model=None):
        if isinstance(model, db.Model):
            #@TODO fix to handle incerting unique values
            try:
                db.session.add(model)
                db.session.commit()
            except exc.IntegrityError as e:
                app.logger.error("Exception occured when adding row: ", e)
                return False
            except exc.InvalidRequestError as e:
                app.logger.error("Exception occured when adding row: ", e)
                return False
        else:
            app.logger.warn("[%s] %s is not an instance of db.Model", __class__.__name__, model)
        app.logger.info("[%s] Update database %s", __class__.__name__, model)
        return True

    @staticmethod
    def get_next_summary_no(program_id):
        return DatabaseManager.get_summary(program_id=program_id).no + 1

    @staticmethod
    def get_product_amount(program_id, school_id, product_name, weeks=list()):
        product_type_qr = None
        try:
            product_type_qr = Product.query.filter(Product.name==product_name).filter(Product.program_id == program_id).with_entities(Product.type).one()
            if product_type_qr:
                product_type = product_type_qr[0]
                item_to_sum = Contract.fruitVeg_products if product_type == ProductType.FRUIT_VEG else Contract.dairy_products
                data = Record.query.join(Contract).join(Product).filter(Contract.program_id == program_id). \
                    filter(Product.name == product_name).join(Week).filter(Week.week_no >= weeks[0],
                                                                           Week.week_no <= weeks[1]).filter(
                    Contract.school_id == school_id) \
                    .filter(Record.state == RecordState.DELIVERED).with_entities(
                    func.sum(item_to_sum).label('product_amount')).one()
                return data.product_amount if data and data.product_amount else 0
        except:
            app.logger.warning("No data for program")
        return 0

    @staticmethod
    def get_fruit_price():
        return 0.75

    @staticmethod
    def get_milk_price():
        return 0.75

    @staticmethod
    def get_dates(program_id, week_no):
        week = Week.query.filter(Week.program_id==program_id).filter(Week.week_no==week_no).one()
        return "{0}-{1}\n{2}".format(DateConverter.to_string(week.start_date, "%d.%m"),
                                     DateConverter.to_string(week.end_date, "%d.%m"),
                                     DateConverter.to_string(week.end_date, "%Y"))

    @staticmethod
    def str_from_weeks(weeks, week_range=(1,12)):
        weeks_list=list()
        for week in weeks:
            if week.week_no in list(range(week_range[0], week_range[1]+1)):
                weeks_list.append("{0}-{1}".format(DateConverter.to_string(week.start_date, "%d.%m"),
                                  DateConverter.to_string(week.end_date, "%d.%m.%Y")))
        return ','.join(weeks_list)


    @staticmethod
    def get_maxKids_perWeek(program_id, school_id, product_type, weeks=(1,12)):
        item_to_sum = DatabaseManager.get_contract_products(product_type)
        data = Record.query.join(Contract).join(Product).filter(Product.type == product_type).join(Week).\
                filter(Week.program_id == program_id).\
                filter(Week.week_no >= weeks[0], Week.week_no <= weeks[1]).filter(Contract.school_id == school_id).with_entities(
                func.max(item_to_sum).label('max_amount')).one()
        return data.max_amount if data.max_amount else 0

    @staticmethod
    def get_contract_products(product_type):
        return Contract.fruitVeg_products if product_type == ProductType.FRUIT_VEG else Contract.dairy_products

    @staticmethod
    def get_summary(summary_id=None, program_id=None):
        if summary_id:
            return Summary.query.filter_by(id=summary_id).first()
        if program_id:
            return Summary.query.filter(Summary.program_id == program_id).order_by(Summary.no.desc()).first()
        return None

    @staticmethod
    def get_school_with_summary(summary_id):
        return Application.query.filter(Application.summary_id==summary_id).all()

    @staticmethod
    def get_application(school_id, summary_id):
        return Application.query.filter(Application.school_id==school_id).filter(Application.summary_id==summary_id).all()

    @staticmethod
    def get_records(program_id, school_id, product_type, weeks=(1, 12)):
        item_to_sum = DatabaseManager.get_contract_products(product_type)
        data = Record.query.join(Contract).join(Product).filter(Product.type == product_type).join(Week).filter(Week.program_id == program_id).\
            filter(Week.week_no >= weeks[0], Week.week_no <= weeks[1]).filter(Contract.school_id == school_id).filter(Record.state == RecordState.DELIVERED).\
            order_by(Record.date).with_entities(Record.date.label("date"), item_to_sum.label("product_no"), Product.name.label("product")).all()
        return data

    @staticmethod
    def get_record(id):
        return Record.query.filter(Record.id.like(id)).one()

    @staticmethod
    def get_remaining_product(program_id):
        return DatabaseManager.get_product_no(program_id)

    @staticmethod
    def get_program(program_id = None):
        if program_id:
            return Program.query.filter(Program.id.like(program_id)).first()
        else:
            return Program.query.order_by(Program.id.desc()).first()

    @staticmethod
    def get_programs_all():
        return Program.query.all()

    @staticmethod
    def update_program_data(program, **data_to_update):
        if isinstance(program, Program):
            program.semester_no = data_to_update['semester_no']
            program.school_year = data_to_update['school_year']
            program.fruitVeg_price = float(data_to_update['fruitVeg_price'].replace(",", "."))
            program.dairy_price = float(data_to_update['dairy_price'].replace(",", "."))
            program.start_date = data_to_update['start_date']
            program.end_date = data_to_update['end_date']
            program.dairy_min_per_week = data_to_update['dairy_min_per_week']
            program.fruitVeg_min_per_week = data_to_update['fruitVeg_min_per_week']
            program.dairy_amount = data_to_update['dairy_amount']
            program.fruitVeg_amount = data_to_update['fruitVeg_amount']

            db.session.commit()
            return program.id

    @staticmethod
    def update_school_data(school, **data_to_update):
        if isinstance(school, School):
            school.nick = data_to_update['nick']
            school.name = data_to_update['name']
            school.address = data_to_update['address']
            school.regon = data_to_update['regon']
            school.city = data_to_update['city']
            school.email = data_to_update['email']
            school.phone = data_to_update['phone']
            school.nip = data_to_update['nip']
            school.responsible_person = data_to_update['responsible_person']
            school.representative_nip = data_to_update['representative_nip']
            school.representative = data_to_update['representative']
            school.representative_regon = data_to_update['representative_regon']

            db.session.commit()
            return school.id

    @staticmethod
    def id_of_school_being_added(depicting_str):
        return School.query.filter(School.nick == depicting_str).first()

    @staticmethod
    def id_of_program_being_added(depicting_str):
        return Program.query.filter(Program.semester_no == depicting_str).first()