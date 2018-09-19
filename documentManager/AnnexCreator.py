from documentManager.DocumentCreator import DocumentCreator
from documentManager.DatabaseManager import DatabaseManager
import configuration as cfg
from os import path
from models import Contract
from datetime import datetime
from setup import app


class AnnexCreator(DocumentCreator, DatabaseManager):
    template_document = cfg.annex_docx

    def __init__(self, school_id):
        self.school = DatabaseManager.get_school(school_id)
        self.contract = DatabaseManager.get_contract(school_id)
        self.contract_no = "{0}_{1}".format(self.contract.contract_no, DatabaseManager.get_next_annex_no(school_id))
        self.contract_year = self.contract.contract_year
        self.contract_date = None
        self.validity_date = None
        self.fruitVeg_products = None
        self.dairy_products = None
        output_directory = path.join(cfg.output_dir_main, self.school.nick, cfg.annex_folder_name)
        DocumentCreator.__init__(self, AnnexCreator.template_document, output_directory)
        DatabaseManager.__init__(self)

    def create(self, contract_date=None, validity_date=None, fruitVeg_products=None, dairy_products=None):
        self.contract_date = datetime.strptime(contract_date, "%d.%m.%Y")
        self.validity_date = datetime.strptime(validity_date, "%d.%m.%Y")
        self.fruitVeg_products = fruitVeg_products # @TODO if None get_the_latest_value
        self.dairy_products = dairy_products
        app.logger.info("[%s] Adding new annex: school_nick %s: city %s | current_date %s, | contract_no %s"
                        "| contract_year %s | validity_date %s | fruitVeg_products %s | dairy_products %s ",
                        __class__.__name__, self.school.nick, self.school.city, self.contract_date, self.contract_no,
                        self.contract_year, self.validity_date, self.fruitVeg_products, self.dairy_products)

        self.generate()
        self.update_row()

    def generate(self):
        self.document.merge(
            city=self.school.city,
            current_date=self.contract_date.strftime("%d.%m.%Y"),
            contract_no=str(self.contract_no),
            contract_year=str(self.contract_year),
            semester_no=DatabaseManager.get_current_sem(),
            school_year=DatabaseManager.get_school_year(),
            name=self.school.name,
            address=self.school.address,
            nip=self.school.nip,
            regon=self.school.regon,
            responsible_person=self.school.responsible_person,
            fruitveg_products=str(self.fruitVeg_products),
            dairy_products=str(self.dairy_products),
            validity_date=self.validity_date.strftime("%d.%m.%Y")
        )
        DocumentCreator.generate(self, "Aneks_" + self.contract_date.strftime("%d_%m_%Y") + ".docx")

    def update_row(self):
        annex = Contract(contract_no=self.contract_no, contract_year=self.contract_year, contract_date=self.contract_date,
                         validity_date=self.validity_date, fruitVeg_products=self.fruitVeg_products, dairy_products=self.dairy_products, is_annex=True,
                         school_id=self.school.id, program_id=cfg.current_program_id)
        DatabaseManager.add_row(annex)

    def modify_row(self):
        # for feature case after modification of Annex is ready from view
        pass

