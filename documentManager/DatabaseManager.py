from abc import ABC, abstractmethod
from models import School, Contract
from setup import db, app


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
        return "I"

    @staticmethod
    def get_school_year():
        return "2018/2019"

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