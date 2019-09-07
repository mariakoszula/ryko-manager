from rykomanager.documentManager.DocumentCreator import DocumentCreator
from rykomanager.documentManager.DatabaseManager import DatabaseManager
import rykomanager.configuration as cfg
from rykomanager.models import Contract
from rykomanager import app
from rykomanager.DateConverter import DateConverter
from shutil import copyfile
from os import remove, path, makedirs


class ContractCreator(DocumentCreator, DatabaseManager):
    template_document = cfg.contract_docx
    main_contract_dir = path.join(cfg.output_dir_main,
                                  cfg.contract_dir_name)

    def __init__(self, school, program_id):
        if not path.exists(ContractCreator.main_contract_dir):
            makedirs(ContractCreator.main_contract_dir)

        self.program = DatabaseManager.get_program(program_id)
        self.school = school
        self.contract_no = None
        self.contract_year = None
        self.contract_date = None
        output_directory = path.join(cfg.output_dir_main, cfg.output_dir_school, self.school.nick, cfg.contract_dir_name)
        DocumentCreator.__init__(self, ContractCreator.template_document, output_directory)
        DatabaseManager.__init__(self)

    def create(self, contract_date=None):
        self.contract_date = DateConverter.to_date(contract_date, "%d.%m.%Y")

        contract = DatabaseManager.get_contract(self.school.id, self.program.id)
        if contract:
            self.contract_no = contract.contract_no
            self.contract_year = contract.contract_year

            app.logger.warning("[%s] Contract already exists [%s, %s]. Only update contract date and regenerate", __class__.__name__,
                             self.school.nick, self.program.id)
            contract.update(self.contract_date)
            self.generate()
        else:
            self.contract_no = str(DatabaseManager.get_next_contract_no(self.program.id))
            self.contract_year = DatabaseManager.get_contract_year(self.program.id)

            app.logger.info("[%s] Adding new contract: school_nick %s: city %s | current_date %s, | contract_no %s"
                        "| contract_year %s",
                        __class__.__name__, self.school.nick, self.school.city, self.contract_date, self.contract_no,
                        self.contract_year)

            if self.update_row():
                self.generate()
            else:
                app.logger.error("[%s]  Something went wrong when creating a contract", __class__.__name__)

    def generate(self):
        self.document.merge(
            city=self.school.city,
            date=DateConverter.to_string(self.contract_date, "%d.%m.%Y"),
            no=str(self.contract_no),
            year=str(self.contract_year),
            semester=self.prgoram.get_current_semester(),
            name=self.school.name,
            address=self.school.address,
            nip=self.school.nip,
            regon=self.school.regon,
            representant=self.school.responsible_person,
            email=self.school.email,
            program_start_date=DateConverter.to_string(self.program.start_date,"%d.%m.%Y"),
            program_end_date=DateConverter.to_string(self.program.end_date,"%d.%m.%Y"),
            nip_additional=self.school.representative_nip if self.school.representative_nip else "-",
            name_additional=self.school.representative if self.school.representative else "-",
            regon_additional=self.school.representative_regon if self.school.representative_regon else "-",
            giving_weeks=ContractCreator._preapre_str_from_weeks(DatabaseManager.get_weeks(self.program.id))

        )
        doc_contract_name = "Umowa_{0}_{1}.docx".format(self.contract_no, self.contract_year)
        created_doc_name = DocumentCreator.generate(self, doc_contract_name)

        doc_contract_name_copy = path.join(ContractCreator.main_contract_dir,
                                                    "{0}_Umowa_{1}_{2}.docx".format(self.school.nick, self.contract_no, self.contract_year))

        try:
            DocumentCreator.copy_to_path(created_doc_name, doc_contract_name_copy)
            # DocumentCreator.copy_to_path(created_doc_name.replace("docx", "pdf"), doc_contract_name_copy.replace("docx", "pdf")) #TODO problem with generating pdf numbering is wrong
        except:
            app.logger.error("Could not copy files [%s]", created_doc_name)
    @staticmethod
    def _preapre_str_from_weeks(weeks):
        return ",".join(["{0}-{1}".format(DateConverter.to_string(week.start_date, "%d.%m"),
                                          DateConverter.to_string(week.end_date, "%d.%m.%Y")) for week in weeks])

    def update_row(self):
        contract = Contract(contract_no=self.contract_no, contract_year=self.contract_year, contract_date=self.contract_date,
                         validity_date=self.contract_date, fruitVeg_products=0, dairy_products=0, is_annex=False,
                         school_id=self.school.id, program_id=self.program.id)
        return DatabaseManager.add_row(contract)

    @staticmethod
    def modify_row(self):
        pass

