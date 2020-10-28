from rykomanager.documentManager.DocumentCreator import DocumentCreator
from rykomanager.documentManager.DatabaseManager import DatabaseManager
from rykomanager.models import RecordState, ProductType, Record
from rykomanager import app, config_parser
from rykomanager.DateConverter import DateConverter
import re
from os import path, listdir, makedirs
import datetime
from rykomanager.name_strings import ALL_RECORDS_DOC_NAME


class RecordCreator(DocumentCreator, DatabaseManager):
    template_document = config_parser.get('DocTemplates', 'record')

    def __init__(self, program_id, current_date, school_id, product_id, generation_date=""):
        self.program_id = program_id
        self.date = DateConverter.to_date(current_date)
        self.state = RecordState.NOT_DELIVERED
        self.contract = DatabaseManager.get_current_contract(school_id, self.program_id, current_date)
        self.product = DatabaseManager.get_product(product_id)
        self.doc_data = dict()
        self.generation_date = DateConverter.to_date(generation_date) if generation_date else datetime.date.today()
        output_directory = self.contract.school.generate_directory_name(config_parser.get('Directories', 'record'))
        DocumentCreator.__init__(self, RecordCreator.template_document, output_directory)
        DatabaseManager.__init__(self)
        self._prepare_data_for_doc()

    @classmethod
    def from_record(cls, record):
        if not isinstance(record, Record):
            raise Exception("Not Record instance")
        return cls(record.contract.program.id, record.date, record.contract.school.id, record.product_id,
                   record.generation_date)

    def create(self):
        app.logger.info("[%s] Adding new record: date %s, school %s: product %s",
                        __class__.__name__, self.date, self.contract.school.nick, self.product.name)
        if self.update_row():
            self.generate()

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
        DocumentCreator.generate(self, "WZ_{0}_{1}.docx".format(DateConverter.to_string(self.date),
                                                                self.product.get_type_mapping()), gen_pdf=True)

    @staticmethod
    def regenerate_documentation(daily_records):
        if not daily_records:
            return
        record_list = list()
        for daily_record in daily_records:
            record_list.append(RecordCreator.from_record(daily_record))
        RecordCreator.generate_many(record_list, ALL_RECORDS_DOC_NAME)

    @staticmethod
    def generate_many(records_to_merge, file_prefix=None):
        if not records_to_merge:
            return

        out_dir = config_parser.get('Directories', 'record_all')
        doc = DocumentCreator.start_doc_gen(RecordCreator.template_document, out_dir)
        records_to_merge_list = [record.doc_data for record in records_to_merge
                                 if (isinstance(record, RecordCreator) and record.doc_data)]
        if not records_to_merge_list:
            return

        date = records_to_merge[0].date
        if not isinstance(date, datetime.date):
            date = DateConverter.to_date(date)

        gen_date = records_to_merge[0].generation_date
        if not isinstance(gen_date, datetime.date):
            gen_date = DateConverter.to_date(gen_date)

        assert (gen_date and date)  # @TODO remove later
        if not gen_date or not date:
            return

        out_dir = path.join(out_dir, DateConverter.to_string(gen_date, '%Y_%m_%d'), DateConverter.to_string(date))
        if not path.exists(out_dir):
            makedirs(out_dir)

        out_file_name = ALL_RECORDS_DOC_NAME
        if file_prefix and file_prefix != ALL_RECORDS_DOC_NAME:
            counter = 1
            for filename in listdir(out_dir):
                if file_prefix in filename:
                    counter += 1
            out_file_name = "{}_{}{}".format(out_file_name, file_prefix, counter)

        out_doc = path.join(out_dir, "{}.docx".format(out_file_name))
        doc.merge_pages(records_to_merge_list)
        app.logger.info("[%s] Created merge docx of records in dir: [%s]", RecordCreator.__qualname__, out_doc)
        DocumentCreator.end_doc_gen(doc, out_doc, out_dir, gen_pdf=True)

    def _prepare_data_for_doc(self):
        self.doc_data['city'] = self.contract.school.city
        self.doc_data['current_date'] = DateConverter.to_string(self.date)
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
                        contract_id=self.contract.id, week_id=DatabaseManager.get_week_by_date(self.date).id,
                        generation_date=self.generation_date)

        return DatabaseManager.add_row(record)

    def modify_row(self):
        pass

    @staticmethod
    def extract_school_id(string_with_school_id):
        pattern = r'records_schoolId_(\d+)'
        return int(re.findall(pattern, string_with_school_id)[0])
