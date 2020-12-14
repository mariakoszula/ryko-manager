from rykomanager.models import School, Contract, Program, Week, Product, ProductType, Record, ProductName, Summary, Application, RecordState
from rykomanager import db, app
from abc import ABC, abstractmethod
import re
from sqlalchemy import func, exc, update, or_
import datetime
from rykomanager.DateConverter import DateConverter
from typing import Set

class DatabaseManager(ABC):

    def __init__(self):
        super(DatabaseManager, self).__init__()

    @abstractmethod
    def create_new(self):
        pass

    @staticmethod
    def modify():
        db.session.commit()

    @staticmethod
    def get_school(school_id):
        return School.query.filter_by(id=school_id).first()

    @staticmethod
    def get_contract(school_id, program_id):
        return Contract.query.filter(Contract.school_id==school_id).filter(Contract.program_id==program_id)\
            .filter(Contract.is_annex==False).first()

    @staticmethod
    def get_existing_annex(annex_id):
        return Contract.query.filter(Contract.id==annex_id).filter(Contract.is_annex == True).first()

    @staticmethod
    def get_annex(program_id, contract_id):
        return Contract.query.filter(Contract.program_id == program_id) \
            .filter(Contract.is_annex == True) \
            .filter(Contract.contract_no.like(f"{contract_id}/_%", escape="/")) \
            .order_by(Contract.validity_date).all()

    @staticmethod
    def get_contracts(program_id):
        return Contract.query.filter(Contract.program_id==program_id).filter(Contract.is_annex == False).order_by(Contract.contract_no).all()

    @staticmethod
    def is_annex(validity_date, school_id):
        rdate = validity_date if not isinstance(validity_date, datetime.datetime) else DateConverter.to_string(validity_date)
        return Contract.query.join(Contract.school).filter(School.id==school_id)\
            .filter(Contract.validity_date == DateConverter.to_date(rdate)).all()

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
    def get_all_schools_with_contract(program_id):
        return db.session.query(School).join(School.contracts).filter(
            Contract.program_id.like(program_id)).order_by(Contract.contract_no).all()


    @staticmethod
    def get_school(school_id):
        return db.session.query(School).filter(School.id.like(school_id)).first()

    @staticmethod
    def get_all_schools():
        return School.query.all()

    @staticmethod
    def get_all_contracts(school_id, program_id, asc = True):
        if asc:
            order = Contract.validity_date.asc()
        else:
            order = Contract.validity_date.desc()
        return Contract.query.filter(Contract.school_id == school_id).filter(Contract.program_id == program_id)\
            .order_by(order).all()

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
        gen_date = DateConverter.to_date(generation_date) if generation_date else None
        if gen_date:
            return Record.query.filter(Product.program_id.like(program_id)).filter(Record.date.like(cdate)).filter(Record.generation_date.like(gen_date)).all()
        return Record.query.filter(Product.program_id.like(program_id)).filter(Record.date.like(cdate)).all()

    @staticmethod
    def get_school_records(program_id, school_id):
        return Record.query.join(Record.contract).filter(Contract.program_id.like(program_id)).filter(Contract.school_id.like(school_id)).all()

    @staticmethod
    def get_product(product_id):
        return Product.query.filter(Product.id.like(product_id)).first()

    @staticmethod
    def get_products(program_id, product_type):
        return Product.query.filter(Product.program_id.like(program_id)).filter(Product.type.like(product_type)).filter(Product.min_amount > 0).all()

    @staticmethod
    def get_product_no(program_id, product_type, week_no=None):
        if not week_no:
            return Record.query.join(Record.contract).join(Record.product).join(Contract.school).filter(Contract.program_id == program_id).filter(Product.type.like(product_type))\
                .with_entities(School, Product, func.count(Product.name)).group_by(School.nick, Product.name).all()
        return Record.query.join(Record.contract).join(Record.product).join(Contract.school).join(Record.week).filter(Week.week_no.like(week_no))\
            .filter(Week.program_id.like(program_id)).filter(Product.type.like(product_type))\
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
    def get_product_amount(program_id, school_id, product_name, weeks: Set, state=(RecordState.DELIVERED, RecordState.DELIVERED)):
        product_type_qr = None
        try:
            product_type_qr = Product.query.filter(Product.name==product_name).filter(Product.program_id == program_id).with_entities(Product.type).one()
            if product_type_qr:
                product_type = product_type_qr[0]
                item_to_sum = Contract.fruitVeg_products if product_type == ProductType.FRUIT_VEG else Contract.dairy_products
                data = Record.query.join(Contract).join(Product).filter(Contract.program_id.like(program_id))\
                    .filter(Product.name == product_name).join(Week).filter(Week.week_no.in_(weeks)).filter(
                    Contract.school_id == school_id) \
                    .filter(or_(Record.state == state[0], Record.state == state[1])).with_entities(
                    func.sum(item_to_sum).label('product_amount')).one()
                return data.product_amount if data and data.product_amount else 0
        except:
            pass
        return 0

    @staticmethod
    def get_dates(program_id, week_no):
        week = Week.query.filter(Week.program_id==program_id).filter(Week.week_no==week_no).one()
        return "{0}-{1}\n{2}".format(DateConverter.to_string(week.start_date, "%d.%m"),
                                     DateConverter.to_string(week.end_date, "%d.%m"),
                                     DateConverter.to_string(week.end_date, "%Y"))

    @staticmethod
    def str_from_weeks(weeks, current_weeks: Set):
        week_to_use = list()
        for week in weeks:
            if week.week_no in current_weeks:
                week_to_use.append(f"{DateConverter.to_string(week.start_date, '%d.%m')}-{DateConverter.to_string(week.end_date, '%d.%m.%Y')}")
        return ','.join(week_to_use)


    @staticmethod
    def get_maxKids_perWeek(program_id, school_id, product_type, weeks: Set):
        item_to_sum = DatabaseManager.get_contract_products(product_type)
        data = Record.query.join(Contract).join(Product).filter(Product.type == product_type).join(Week).\
                filter(Week.program_id == program_id).\
                filter(Week.week_no.in_(weeks)).filter(Contract.school_id == school_id).with_entities(
                func.max(item_to_sum).label('max_amount')).one()
        return data.max_amount if data.max_amount else 0

    @staticmethod
    def get_contract_products(product_type):
        return Contract.fruitVeg_products if product_type == ProductType.FRUIT_VEG else Contract.dairy_products

    @staticmethod
    def get_summary(program_id, no):
        return Summary.query.filter(Summary.program_id.like(program_id)).\
                filter(Summary.no.like(no)).first()

    @staticmethod
    def get_summaries(program_id):
        return Summary.query.filter(Summary.program_id.like(program_id)).all()

    @staticmethod
    def get_school_with_summary(summary_id):
        return Application.query.filter(Application.summary_id==summary_id).all()

    @staticmethod
    def get_application(school_id, summary_id):
        return Application.query.filter(Application.school_id==school_id).filter(Application.summary_id==summary_id).all()

    @staticmethod
    def get_records(program_id, school_id, product_type, weeks: Set):
        item_to_sum = DatabaseManager.get_contract_products(product_type)
        data = Record.query.join(Contract).join(Product).filter(Product.type == product_type).join(Week).filter(Week.program_id == program_id).\
            filter(Week.week_no.in_(weeks)).filter(Contract.school_id == school_id).filter(Record.state == RecordState.DELIVERED).\
            order_by(Record.date).with_entities(Record.date.label("date"), item_to_sum.label("product_no"), Product).all()
        return data

    @staticmethod
    def is_any_record(program_id, school_id, week_no: int):
        data = Record.query.join(Contract).join(Week).\
            filter(Week.program_id == program_id).\
            filter(Contract.school_id == school_id).\
            filter(Record.state == RecordState.DELIVERED).\
            filter(Week.week_no == week_no).all()
        return len(data)

    @staticmethod
    def get_record(id):
        return Record.query.filter(Record.id.like(id)).one()

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

    @staticmethod
    def get_portion_perWeek(program_id, school_id, product_type, week_no):
        portion_no = Record.query.join(Record.contract).join(Record.product).join(Record.week).filter(Contract.program_id.like(program_id)).filter(Contract.school_id.like(school_id))\
            .filter(Week.week_no.like(week_no)).filter(Product.type.like(product_type)).count()
        return portion_no


    @staticmethod
    def get_existing_record(current_date, school_id, product_id):
        if not product_id:
            return None
        product_type = Product.query.filter(Product.id == product_id).one().type
        cdate = DateConverter.to_date(current_date)
        assert(product_type == ProductType.DAIRY or product_type == ProductType.FRUIT_VEG)
        return Record.query.join(Contract).join(Product).filter(Record.date.like(cdate)).filter(Contract.school_id == school_id)\
                .filter(Product.type.like(product_type)).first()

    @staticmethod
    def get_any_inconsistent_records_with_annex(program_id, school_id):
        inconsistent = list()
        records = DatabaseManager.get_school_records(program_id, school_id)
        contracts = DatabaseManager.get_all_contracts(school_id, program_id, asc=False)
        for record in records:
            if record.date < record.contract.validity_date:
                inconsistent.append(record)

        for record in records:
            proper_contract_id = None
            for contract in contracts:
                if record.date >= contract.validity_date:
                    proper_contract_id = contract.id
                    break
            if proper_contract_id != record.contract_id:
                inconsistent.append(record)
        return inconsistent


