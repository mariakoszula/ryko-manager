from abc import ABC, abstractmethod
from models import School, Contract, Program
from setup import db, app
import datetime

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
        annex_no_list = [int(contract.contract_no[2:]) for contract in contracts if "_" in str(contract.contract_no)]
        if not annex_no_list:
            return 1
        else:
            return min(annex_no_list) + 1

    @staticmethod
    def get_all_schools_with_contract(program_id):
        return db.session.query(School).join(School.contracts).filter(
            Program.id.like(program_id)).all()

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