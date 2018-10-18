from rykomanager.documentManager.DocumentCreator import DocumentCreator
from rykomanager.documentManager.DatabaseManager import DatabaseManager
from rykomanager.models import RecordState, ProductType, Record
import rykomanager.configuration as cfg
from rykomanager import app

import re
from os import path
import datetime


class RecordCreator(DocumentCreator, DatabaseManager):
    template_document = cfg.record_docx

    def __init__(self, program_id, date, school_id, product_id):
        self.program_id = program_id
        self.date = DatabaseManager.date_from_str(date)
        self.state = RecordState.NOT_DELIVERED
        self.contract = DatabaseManager.get_current_contract(school_id, self.program_id, date)
        self.product = DatabaseManager.get_product(self.program_id, product_id)
        self.doc_data = dict()
        output_directory = path.join(cfg.output_dir_main, cfg.output_dir_school,
                                     self.contract.school.nick, cfg.record_folder_name)
        DocumentCreator.__init__(self, RecordCreator.template_document, output_directory)
        DatabaseManager.__init__(self)

    def create(self):
        app.logger.info("[%s] Adding new record: date %s, school %s: product %s",
                        __class__.__name__, self.date, self.contract.school.nick, self.product.name)
        self._prepare_data_for_doc()
        self.generate()
        self.update_row()

    def generate(self):
        self.document.merge(
            city=self.doc_data['city'],
            current_date=self.doc_data['current_date'],
            name=self.doc_data['name'],
            address=self.doc_data['address'],
            nip=self.doc_data['nip'],
            regon=self.doc_data['regon'],
            email=self.doc_data['email'],
            kids_no=self.doc_data['kids_no'],
            product_name=self.doc_data['product_name'],
            record_title=self.doc_data['record_title']
        )
        DocumentCreator.generate(self, "WZ_{0}_{1}.docx".format(DatabaseManager.str_from_date(self.date),
                                                                self.product.get_name_mapping()))

    @staticmethod
    def generate_many(date, records_to_merge):
        out_dir = path.join(cfg.output_dir_main, cfg.record_folder_name)
        doc = DocumentCreator.start_doc_gen(RecordCreator.template_document, out_dir)
        if not isinstance(date, datetime.datetime):
            date = DatabaseManager.date_from_str(date)
        out_doc = path.join(out_dir, "{}.docx".format(DatabaseManager.str_from_date(date)))
        records_to_merge_list = [record.doc_data for record in records_to_merge
                                 if (isinstance(record, RecordCreator) and record.doc_data)]

        doc.merge_pages(records_to_merge_list)

        app.logger.info("[%s] Created merge docx of records in dir: [%s]", RecordCreator.__qualname__, out_doc)
        DocumentCreator.end_doc_gen(doc, out_doc, out_dir)

    def _prepare_data_for_doc(self):
        self.doc_data['city'] = self.contract.school.city
        self.doc_data['current_date'] = DatabaseManager.str_from_date(self.date)
        self.doc_data['name'] = self.contract.school.name
        self.doc_data['address'] = self.contract.school.address
        self.doc_data['nip'] = self.contract.school.nip
        self.doc_data['regon'] = self.contract.school.regon
        self.doc_data['email'] = self.contract.school.email
        self.doc_data['kids_no'] = str(self._get_kids_no())
        self.doc_data['product_name'] = self.product.get_name_mapping()
        self.doc_data['record_title'] = self.product.get_record_title_mapping()

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
        record = Record(date=self.date, state=RecordState.NOT_DELIVERED, product_id=self.product.id,
                        contract_id=self.contract.id, week_id=DatabaseManager.get_week_by_date(self.date).id)
        DatabaseManager.add_row(record)

    def modify_row(self):
        pass

    @staticmethod
    def extract_school_id(string_with_school_id):
        pattern = r'records_schoolId_(\d+)'
        return int(re.findall(pattern, string_with_school_id)[0])


