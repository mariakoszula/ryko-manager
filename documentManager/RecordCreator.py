from documentManager.DocumentCreator import DocumentCreator
from documentManager.DatabaseManager import DatabaseManager
from models import RecordState, ProductType
import re
import configuration as cfg
from os import path
from setup import app

class RecordCreator(DocumentCreator, DatabaseManager):
    template_document = cfg.record_docx

    def __init__(self, program_id, date, school_id):
        self.program_id = program_id
        self.date = date
        self.state = RecordState.NOT_DELIVERED
        self.contract = DatabaseManager.get_current_contract(school_id, self.program_id)
        self.product = None
        output_directory = path.join(cfg.output_dir_main, self.contract.school.nick, cfg.record_folder_name)
        DocumentCreator.__init__(self, RecordCreator.template_document, output_directory)
        DatabaseManager.__init__(self)

    def create(self, product_id):
        self.product = DatabaseManager.get_product(self.program_id, product_id)
        print("Create record for:", self.product.name)

    def generate(self):
        self.document.merge(
            city=self.contract.School.city,
            current_date=self.date.strftime("%d.%m.%Y"),
            name=self.contract.School.name,
            address=self.contract.School.address,
            nip=self.contract.School.nip,
            regon=self.contract.School.regon,
            email=self.contract.School.email,
            kids_no=self._get_kids_no(),
            product_name=self.product.get_name_mapping(),
            record_title=self.product.get_record_title_mapping()
        )
        DocumentCreator.generate(self, "Aneks_" + self.contract_date.strftime("%d_%m_%Y") + ".docx")

    def _get_kids_no(self):
        kids_no = None
        if self.product.type == ProductType.FRUIT_VEG:
            kids_no = self.contract.fruitVeg_products
        elif self.product.type == ProductType.DAIRY:
            kids_no = self.contract.dairy_products
        else:
            app.logger.error("[%s] product type not found:%s. Kids no will be set to 0",
                            __class__.__name__, self.product.type)

        return kids_no if kids_no else 0

    def update_row(self):
        pass

    def modify_row(self):
        pass

    @staticmethod
    def extract_school_id(string_with_school_id):
        pattern = r'records_schoolId_(\d+)'
        return int(re.findall(pattern, string_with_school_id)[0])


