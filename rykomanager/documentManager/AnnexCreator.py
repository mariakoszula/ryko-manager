from rykomanager.documentManager.DocumentCreator import DocumentCreator
from rykomanager.documentManager.DatabaseManager import DatabaseManager
from rykomanager.models import Contract
from rykomanager import app, config_parser, DateConverter

from os import path
from datetime import datetime


class AnnexCreator(DocumentCreator, DatabaseManager):
    def __init__(self, school_id, program_id, existing_annex: Contract = None):
        self.program_id = program_id
        self.program = DatabaseManager.get_program(program_id)
        self.school = DatabaseManager.get_school(school_id)
        if not existing_annex:
            self.contract = DatabaseManager.get_contract(school_id, self.program_id)
            self.contract_no = "{0}_{1}".format(self.contract.contract_no, DatabaseManager.get_next_annex_no(school_id, self.program_id ))
            self.contract_year = self.contract.contract_year
            self.contract_date = None
            self.validity_date = None
            self.fruitVeg_products = None
            self.dairy_products = None
        else:
            self.contract = existing_annex
            self.contract_no = existing_annex.contract_no
            self.contract_year = existing_annex.contract_year
            self.contract_date = existing_annex.contract_date
            self.validity_date = existing_annex.validity_date
            self.fruitVeg_products = existing_annex.fruitVeg_products
            self.dairy_products = existing_annex.dairy_products

        output_directory = self.school.generate_directory_name(config_parser.get('Directories', 'annex'));
        DocumentCreator.__init__(self, config_parser.get('DocTemplates', 'annex'), output_directory)
        DatabaseManager.__init__(self)

    def create(self, contract_date=None, validity_date=None, fruitVeg_products=None, dairy_products=None):
        if validity_date and DatabaseManager.is_annex(DateConverter.DateConverter.to_date(validity_date, pattern="%d.%m.%Y"),
                                                                            self.school.id):
            app.logger.error("[%s] Annex already exists [%s, %s]. Only modifying is possible", __class__.__name__,
                             self.school.nick, self.validity_date)
            return False

        self.contract_date = datetime.strptime(contract_date, "%d.%m.%Y")
        self.validity_date = datetime.strptime(validity_date, "%d.%m.%Y")
        self.fruitVeg_products = fruitVeg_products # @TODO if None get_the_latest_value
        self.dairy_products = dairy_products

        app.logger.info("[%s] Adding new annex: school_nick %s: city %s | current_date %s, | contract_no %s"
                        "| contract_year %s | validity_date %s | fruitVeg_products %s | dairy_products %s ",
                        __class__.__name__, self.school.nick, self.school.city, self.contract_date, self.contract_no,
                        self.contract_year, self.validity_date, self.fruitVeg_products, self.dairy_products)

        if self.update_row():
            self.generate()
        else:
            app.logger.error("[%s]  Something went wrong when creating annex", __class__.__name__)
        return True

    def generate(self):
        self.document.merge(
            city=self.school.city,
            current_date=self.contract_date.strftime("%d.%m.%Y"),
            contract_no=str(self.contract_no.split("_")[0]),
            contract_year=str(self.contract_year),
            semester_no=self.program.get_current_semester(),
            school_year=self.program.school_year,
            name=self.school.name,
            address=self.school.address,
            nip=self.school.nip,
            regon=self.school.regon,
            responsible_person=self.school.responsible_person,
            fruitveg_products=str(self.fruitVeg_products),
            dairy_products=str(self.dairy_products),
            validity_date=self.validity_date.strftime("%d.%m.%Y")
        )
        created_annex = DocumentCreator.generate(self, "Aneks_" + self.contract_date.strftime("%d_%m_%Y") + ".docx")
        new_annex_dst = path.join(config_parser.get('Directories', 'annex_all'),
                                                    "{0}_Aneks_{1}_{2}.docx".format(self.school.nick, self.contract_no, self.contract_year))
        DocumentCreator.copy_to_path(created_annex, new_annex_dst)

    def update_row(self):
        annex = Contract(contract_no=self.contract_no, contract_year=self.contract_year, contract_date=self.contract_date,
                         validity_date=self.validity_date, fruitVeg_products=self.fruitVeg_products, dairy_products=self.dairy_products, is_annex=True,
                         school_id=self.school.id, program_id=self.program_id)
        return DatabaseManager.add_row(annex)

