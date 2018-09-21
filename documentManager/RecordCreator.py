from documentManager.DocumentCreator import DocumentCreator
from documentManager.DatabaseManager import DatabaseManager
from models import RecordState


class RecordCreator(DocumentCreator, DatabaseManager):

    def __init__(self, date):
        self.date = date
        self.state = RecordState.NOT_DELIVERED
        self.contract_id = None
        self.product_id = None

    def generate(self, new_doc_name):
        pass

    def create(self, contract_id=None, product_id=None):
        pass

    def update_row(self):
        pass

    def modify_row(self):
        pass


