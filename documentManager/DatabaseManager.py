from abc import ABC, abstractmethod
from models import School, Contract, Program, Week, Product, ProductType, Record
from setup import db, app
import datetime
import re
class DatabaseManager(ABC):

    def __init__(self):
        super(DatabaseManager, self).__init__()

    @abstractmethod
    def update_row(self):
        pass

    @abstractmethod
    def modify_row(self):
        pass

    @staticmethod
    def date_from_str(date, pattern=None):
        if isinstance(date, str):
            pattern_used = '%Y-%m-%d' if not pattern else pattern
            return datetime.datetime.strptime(date, pattern_used)
        elif isinstance(date, datetime.datetime):
            return date
        else:
            print("LOG ERROR")

    @staticmethod
    def str_from_date(date, pattern=None):
        # @TODO check if given strig has this pattern
        pattern_used = '%Y-%m-%d' if not pattern else pattern
        return datetime.datetime.strftime(date, pattern_used)

    @staticmethod
    def get_school(school_id):
        return School.query.filter_by(id=school_id).first()

    @staticmethod
    def get_contract(school_id):
        return Contract.query.filter(Contract.school_id==school_id).filter(Contract.is_annex==False).one()

    @staticmethod
    def get_current_sem():
        return "I" #@TODO fill with sql query

    @staticmethod
    def get_school_year():
        return "2018/2019"  #@TODO fill with sql query

    @staticmethod
    def get_next_annex_no(school_id, program_id):
        contracts = Contract.query.filter(Contract.school_id == school_id).filter(Contract.program_id == program_id).all()
        annex_no_list = [int(re.findall(r"\d+_(\d+)", contract.contract_no)[0]) for contract in contracts if "_" in str(contract.contract_no)]
        if not annex_no_list:
            return 1
        else:
            return min(annex_no_list) + 1

    @staticmethod
    def get_all_schools_with_contract(program_id):
        return db.session.query(School).join(School.contracts).filter(
            Program.id.like(program_id)).all()

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
    def get_current_contract(school_id, program_id):
        now = datetime.datetime.now()
        res = School.query.filter(School.id.like(school_id)).first()
        for contract in res.contracts:
            if contract.program_id == program_id and contract.validity_date.date() <= now.date():
                return contract
        return None

    @staticmethod
    def get_weeks(program_id):
        return Week.query.filter(Program.id == program_id).all()

    @staticmethod
    def get_week(week_id, program_id):
        return Week.query.filter(Program.id == program_id).filter(Week.id == week_id).first()

    @staticmethod
    def get_week_by_date(date):
        rdate = date if not isinstance(date, datetime.datetime) else DatabaseManager.date_from_str(date)
        return Week.query.filter(Week.start_date <= rdate).filter(Week.end_date >= rdate).first()

    @staticmethod
    def get_fruitVeg_products(program_id):
        return Product.query.filter(Program.id.like(program_id)).filter(Product.type.like(ProductType.FRUIT_VEG)).all()

    @staticmethod
    def get_dairy_products(program_id):
        return Product.query.filter(Program.id.like(program_id)).filter(Product.type.like(ProductType.DAIRY)).all()

    @staticmethod
    def get_daily_records(current_date):
        g_date = current_date if isinstance(current_date, datetime.datetime) else DatabaseManager.date_from_str(current_date)
        return Record.query.filter(Record.date.like(g_date)).all()

    @staticmethod
    def get_product(program_id, product_id):
        return Product.query.filter(Program.id.like(program_id)).filter(Product.id.like(product_id)).first()

    @staticmethod
    def get_product_no(contract_id, week_no=None):
        if not week_no:
            pass
        return 0

    @staticmethod
    def get_record(id):
        return Record.query.filter(Record.id.like(id)).one()

    @staticmethod
    def add_row(models=None):
        if not isinstance(models, list):
            model = models
            models = list()
            models.append(model)
        for model in models:
            if isinstance(model, db.Model):
                db.session.add(model)
            else:
                app.logger.warn("[%s] %s is not an instance of db.Model", __class__.__name__, model)
            app.logger.info("[%s] Update database %s", __class__.__name__, model)
        db.session.commit()

