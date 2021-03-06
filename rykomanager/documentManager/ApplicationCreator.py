from rykomanager.documentManager.DocumentCreator import DocumentCreator
from rykomanager.documentManager.DatabaseManager import DatabaseManager
from rykomanager.models import ProductName, ProductType, Application, Summary, School
from rykomanager import app, config_parser
from shutil import copyfile
from os import path, makedirs, remove
from rykomanager.DateConverter import DateConverter
from typing import Dict, Set


class DataContainer(object):
    def __init__(self):
        self.dict_data: Dict = dict()

    def prepare(self):
        raise NotImplementedError

    def get(self):
        return self.dict_data


class DefaultData(DataContainer):
    def __init__(self, school, sign_date):
        super().__init__()
        self.school = school
        self.sign_date = DateConverter.to_date(sign_date)

    def prepare(self):
        self.dict_data['school_name'] = self.school.name
        self.dict_data['school_nip'] = self.school.nip
        self.dict_data['school_regon'] = self.school.regon
        self.dict_data['school_address'] = self.school.address
        self.dict_data['city'] = self.school.city
        self.dict_data['date_day'] = DateConverter.two_digits(self.sign_date.day)
        self.dict_data['date_month'] = DateConverter.two_digits(self.sign_date.month)
        self.dict_data['date_year'] = str(self.sign_date.year)


class Week(object):
    def __init__(self, number, date):
        self.no: int = number
        self.date: str = date


class CommonData(DataContainer):
    def __init__(self, program_id, school_id, given_weeks: Set):
        super().__init__()
        self.program_id = program_id
        self.school_id = school_id
        self.weeks = CommonData.__get_active_week(self.program_id, self.school_id, given_weeks)

    @staticmethod
    def __get_active_week(program_id, school_id, given_weeks):
        weeks = dict()
        no = 1
        for week_no in given_weeks:
            if DatabaseManager.is_any_record(program_id, school_id, week_no):
                weeks[no] = Week(number=week_no, date=DatabaseManager.get_dates(program_id, week_no))
                no += 1
        return weeks

    def get_week_numbers(self):
        return set([week.no for week in self.weeks.values()])

    def length(self):
        return len(self.weeks.values())

    def prepare(self):
        self.prepare_per_week("week_date_", lambda week: week.date)

    def prepare_per_week(self, base_name, fun):
        for week in range(1, int(config_parser.get('Program', 'weeks')) + 1):
            self.dict_data[f"{base_name}{week}"] = fun(self.weeks[week]) if week in self.weeks.keys() else None


class ProductSummary(DataContainer):
    def __init__(self, common_app_info: CommonData):
        super().__init__()
        self.common_app_info = common_app_info
        self.min_product_no = 0
        self.max_product_no = 0

    def raise_if_not_set(self, product_id: ProductName = None):
        if self.min_product_no == 0 and self.max_product_no == 0:
            raise ValueError
        if product_id \
                and (product_id.value < self.min_product_no.value or product_id.value >= self.max_product_no.value):
            raise ValueError(f"{product_id} is out of range ({self.min_product_no}, {self.max_product_no})")

    def get_sum(self):
        self.raise_if_not_set()
        return sum([self.get_amount(ProductName(i)) for i in range(self.min_product_no.value + 1,
                                                                   self.max_product_no.value)])

    def get_amount(self, product_name: ProductName):
        self.raise_if_not_set(product_name)
        return DatabaseManager.get_product_amount(self.common_app_info.program_id,
                                                  self.common_app_info.school_id,
                                                  product_name,
                                                  self.common_app_info.get_week_numbers())

    def __prepare_one(self, product_name: ProductName):
        self.dict_data[product_name.name.lower()] = self.get_amount(product_name)

    def prepare(self):
        self.raise_if_not_set()
        for product_id in range(self.min_product_no.value + 1, self.max_product_no.value):
            self.__prepare_one(ProductName(product_id))
        self.dict_data[f"{self.__class__.__name__.lower()}_all"] = self.get_sum()


class Fruit(ProductSummary):
    def __init__(self, common_app_info: CommonData):
        super().__init__(common_app_info)
        self.min_product_no = ProductName.MIN_FRUIT_PRODUCT_NO
        self.max_product_no = ProductName.MAX_FRUIT_PRODUCT_NO


class Veg(ProductSummary):
    def __init__(self, common_app_info: CommonData):
        super().__init__(common_app_info)
        self.min_product_no = ProductName.MIN_VEG_PRODUCT_NO
        self.max_product_no = ProductName.MAX_VEG_PRODUCT_NO


class Dairy(ProductSummary):
    def __init__(self, common_app_info: CommonData):
        super().__init__(common_app_info)
        self.min_product_no = ProductName.MIN_DAIRY_PRODUCT_NO
        self.max_product_no = ProductName.MAX_DAIRY_PRODUCT_NO


class ProductTypeSummary(DataContainer):
    def __init__(self, common_app_info: CommonData):
        super().__init__()
        self.common_app_info = common_app_info
        self.product_type = ProductType.NONE
        self.base_name = None
        self.contract_kids_no = 0

    def __raise_if_not_set(self):
        if self.product_type == ProductType.NONE or not self.base_name:
            raise ValueError("Need to specify product type and base_name")

    def get_kids(self, week=0):
        self.__raise_if_not_set()
        weeks = week if week else self.common_app_info.get_week_numbers()
        return DatabaseManager.get_maxKids_perWeek(self.common_app_info.program_id, self.common_app_info.school_id,
                                                   self.product_type, weeks)

    def prepare(self):
        self.__raise_if_not_set()
        self.common_app_info.prepare_per_week(f"{self.base_name}_week",
                                              lambda week: DatabaseManager.get_maxKids_perWeek(
                                                  self.common_app_info.program_id,
                                                  self.common_app_info.school_id,
                                                  self.product_type,
                                                  set([week.no])))
        self.common_app_info.prepare_per_week(f"portion_no_{self.base_name}_",
                                              lambda week: DatabaseManager.get_portion_perWeek(
                                                  self.common_app_info.program_id,
                                                  self.common_app_info.school_id,
                                                  self.product_type,
                                                  week.no))
        all_weeks = set([week.week_no for week in DatabaseManager.get_weeks(self.common_app_info.program_id)])
        max_kids_from_weeks = DatabaseManager.get_maxKids_perWeek(self.common_app_info.program_id,
                                                                  self.common_app_info.school_id,
                                                                  self.product_type, all_weeks)
        self.dict_data[f"max_kids_{self.base_name}"] = max(max_kids_from_weeks, self.contract_kids_no)


class FruitVegSummary(ProductTypeSummary):
    def __init__(self, common_app_info: CommonData):
        super().__init__(common_app_info)
        self.product_type = ProductType.FRUIT_VEG
        self.base_name = "fruitVeg"
        self.contract_kids_no = DatabaseManager.get_contract(self.common_app_info.school_id,
                                                             self.common_app_info.program_id).fruitVeg_products


class DairySummary(ProductTypeSummary):
    def __init__(self, common_app_info: CommonData):
        super().__init__(common_app_info)
        self.product_type = ProductType.DAIRY
        self.base_name = "milk"
        self.contract_kids_no = DatabaseManager.get_contract(self.common_app_info.school_id,
                                                             self.common_app_info.program_id).dairy_products


class ApplicationCreator(DocumentCreator, DatabaseManager):
    def __init__(self, program_id, school, summary, date):
        self.template_document_v = config_parser.get('DocTemplates', 'application')
        self.template_document_va = config_parser.get('DocTemplates', 'application_5a')
        self.main_app_dir = path.join(config_parser.get('Directories', 'application_all'), str(summary.no))
        if not path.exists(self.main_app_dir):
            makedirs(self.main_app_dir)
        self.program_id = program_id
        self.school: School = school

        self.summary: Summary = summary

        self.default_data: DefaultData = DefaultData(self.school, date)
        self.common_data: CommonData = CommonData(self.program_id, self.school.id,
                                                  self.summary.weeks)

        self.fruits = Fruit(self.common_data)
        self.vegs = Veg(self.common_data)
        self.dairy = Dairy(self.common_data)

        self.frutiVeg = FruitVegSummary(self.common_data)
        self.dairySummary = DairySummary(self.common_data)

        self.tmp_data_to_rename = list(
            [self.default_data, self.common_data, self.fruits, self.vegs, self.dairy, self.frutiVeg, self.dairySummary])

        self.output_directory = self.school.generate_directory_name(config_parser.get('Directories', 'application'))

        self.product_data = dict()
        if not self.__prepare_data():
            raise Exception("Cannot prepare data")
        DatabaseManager.__init__(self)

    def __prepare_fruit_data(self):
        self.records_to_merge_vegFruit = []
        self.sum_product_vegFruit = 0

    def __prepare_dairy_data(self):
        self.records_to_merge_milk = []
        self.sum_product_milk = 0

    def generate(self):
        # TODO refactor to reuse generate
        self._generate_5()
        self._generate_5a()

    @staticmethod
    def convert_to_str(value):
        if value is None: return "-"
        return str(value)

    def _generate_5(self):
        DocumentCreator.__init__(self, self.template_document_v, self.output_directory)
        data_to_merge = dict()
        data_to_merge['application_no'] = self.summary.get_application_no()

        data_to_merge.update({k: ApplicationCreator.convert_to_str(v) for k, v in self.default_data.get().items()})
        data_to_merge.update({k: ApplicationCreator.convert_to_str(v) for k, v in self.common_data.get().items()})
        data_to_merge.update({k: ApplicationCreator.convert_to_str(v) for k, v in self.frutiVeg.get().items()})
        data_to_merge.update({k: ApplicationCreator.convert_to_str(v) for k, v in self.dairySummary.get().items()})
        data_to_merge.update({k: ApplicationCreator.convert_to_str(v) for k, v in self.product_data.items()})

        self.document.merge(**data_to_merge)

        doc_5_name = "Oswiadczenie_V_Wniosek_{}_{}.docx".format(self.summary.no, self.summary.year)
        doc_5_name_copy = path.join(self.main_app_dir,
                                    "{0}_OswiadczenieV_{1}_{2}.docx".format(self.school.nick, self.summary.no,
                                                                            self.summary.year))
        DocumentCreator.generate(self, doc_5_name, False)
        if path.exists(doc_5_name_copy):
            remove(doc_5_name_copy)
        copyfile(path.join(self.output_directory, doc_5_name), doc_5_name_copy)

    def _generate_5a(self):
        DocumentCreator.__init__(self, self.template_document_va, self.output_directory)

        self.document.merge_rows('date_vegFruit', self.records_to_merge_vegFruit)
        self.document.merge_rows('date_milk', self.records_to_merge_milk)
        data_to_merge = dict()
        data_to_merge.update(self.default_data.get())
        data_to_merge['weeks'] = DatabaseManager.str_from_weeks(DatabaseManager.get_weeks(self.program_id),
                                                                self.summary.weeks)
        data_to_merge['sum_vegFruit'] = str(self.sum_product_vegFruit)
        data_to_merge['sum_kids_vegFruit'] = str(self.sum_product_vegFruit)
        data_to_merge['sum_milk'] = str(self.sum_product_milk)
        data_to_merge['sum_kids_milk'] = str(self.sum_product_milk)

        self.document.merge(**data_to_merge)

        doc_5a_name = "Ewidencja_VA_Wniosek_{}_{}.docx".format(self.summary.no, self.summary.year)
        doc_5a_name_copy = path.join(self.main_app_dir,
                                     "{0}_EwidencjaVa_{1}_{2}.docx".format(self.school.nick, self.summary.no,
                                                                           self.summary.year))
        DocumentCreator.generate(self, doc_5a_name, False)
        if path.exists(doc_5a_name_copy):
            remove(doc_5a_name_copy)
        copyfile(path.join(self.output_directory, doc_5a_name), doc_5a_name_copy)

    def __prepare_data(self):
        inconsistent_records = DatabaseManager.get_any_inconsistent_records_with_annex(self.program_id, self.school.id)
        if inconsistent_records:
            #TODO change this excpetion to some meaningfull one
           raise TypeError(' | '.join([f"{record.date.year}-{record.date.month}-{record.date.day} {record.product.get_name_mapping()}" for record in inconsistent_records]))

        for data in self.tmp_data_to_rename:
            data.prepare()

        self.product_data.update(self.fruits.get())
        self.product_data.update(self.vegs.get())
        self.product_data.update(self.dairy.get())

        self.product_data['max_kids_perWeeks_fruitVeg'] = self.frutiVeg.get_kids()
        self.product_data['max_kids_perWeeks_milk'] = self.dairySummary.get_kids()

        self.__prepare_fruit_data()
        self.__prepare_dairy_data()
        for record in DatabaseManager.get_records(self.program_id, self.school.id, ProductType.FRUIT_VEG,
                                                  self.summary.weeks):
            record_dict = dict()
            record_dict['date_vegFruit'] = DateConverter.to_string(record.date, "%d.%m.%Y")
            record_dict['kids_vegFruit'] = str(record.product_no)
            record_dict['vegFruit'] = record.Product.get_name_mapping()
            self.records_to_merge_vegFruit.append(record_dict)

        for record in DatabaseManager.get_records(self.program_id, self.school.id, ProductType.DAIRY,
                                                  self.summary.weeks):
            record_dict = dict()
            record_dict['date_milk'] = DateConverter.to_string(record.date, "%d.%m.%Y")
            record_dict['kids_milk'] = str(record.product_no)
            record_dict['milk'] = record.Product.get_name_mapping()
            self.records_to_merge_milk.append(record_dict)

        self.sum_product_vegFruit = self.__sum_product(self.records_to_merge_vegFruit, 'kids_vegFruit')
        self.sum_product_milk = self.__sum_product(self.records_to_merge_milk, 'kids_milk')

        fruit_veg = self.product_data['veg_all'] + self.product_data['fruit_all']
        if self.sum_product_vegFruit != fruit_veg:
            app.logger.error("Value of fruitVeg product from 5 and 5A does not match! School: {0} 5: {1} "
                             " 5A: {2} -- ABORT generating".format(self.school.nick, fruit_veg,
                                                                   self.sum_product_vegFruit))
            return False

        if self.sum_product_milk != self.product_data['dairy_all']:
            app.logger.error("Value of dairy product from 5 and 5A does not match! School: {0} 5: {1} "
                             " 5A: {2} -- ABORT generating".format(self.school.nick, self.product_data['dairy_all'],
                                                                   self.sum_product_milk))
            return False
        return True

    def __sum_product(self, records, type):
        sum = 0
        for recrod in records:
            for (key, value) in recrod.items():
                if key == type:
                    sum += int(value)
        return sum

    def create(self):
        application = DatabaseManager.get_application(self.school.id, self.summary.id)
        if len(application) > 1:
            app.logger.error(
                "Application serious error: should never be returned more than one item in this list")
            return False
        if not application and self.create_new():
            app.logger.info(
                "Application for summary {0}/{1} for school {2} added".format(self.summary.no, self.summary.year,
                                                                              self.school.nick))
            self.__increase_in_summary() # change this to use observer when new Application is added
            return True
        else:
            if DatabaseManager.remove_application(application[0].id):
                app.logger.info("Application {3} for summary {0}/{1} for school {2} removed".format(self.summary.no,
                                                                                                    self.summary.year,
                                                                                                    self.school.nick,
                                                                                                    application[0].id))
            return self.create()

    def __update_summary(self):
        self.summary.fruitVeg_income = self.summary.get_fruit_veg_income()
        self.summary.milk_income = self.summary.get_dairy_income()
        app.logger.info("Update summary {2} fruitVeg_income: {0}, milk_income: {1}".format(self.summary.fruitVeg_income,
                                                                                           self.summary.milk_income,
                                                                                           self.school.nick))
        DatabaseManager.modify()

    def __increase_in_summary(self):
        # TODO refactor idea: Summary should be obsevator of ApplicationCreator and perform informaton update
        # overload _add_ method in Summary self + application - add products; self - application remove products
        # increase/descrease number of schools setup weeks number not in model in SummraryCreator as only needed of document generation

        try:
            self.summary.set_number_of_weeks(self.common_data.get_week_numbers())
        except ValueError:
            raise
        self.summary.apple += self.product_data['apple']
        self.summary.pear += self.product_data['pear']
        self.summary.plum += self.product_data['plum']
        self.summary.strawberry += self.product_data['strawberry']
        self.summary.juice += self.product_data['juice']
        self.summary.carrot += self.product_data['carrot']
        self.summary.radish += self.product_data['radish']
        self.summary.pepper += self.product_data['pepper']
        self.summary.tomato += self.product_data['tomato']
        self.summary.kohlrabi += self.product_data['kohlrabi']
        self.summary.milk += self.product_data['milk']
        self.summary.yoghurt += self.product_data['yoghurt']
        self.summary.kefir += self.product_data['kefir']
        self.summary.cheese += self.product_data['cheese']

        self.summary.kids_no += self.product_data['max_kids_perWeeks_fruitVeg']
        if self.product_data['max_kids_perWeeks_fruitVeg'] != 0:
            self.summary.school_no = self.summary.school_no + 1

        self.summary.kids_no_milk += self.product_data['max_kids_perWeeks_milk']
        if self.product_data['max_kids_perWeeks_milk'] != 0:
            self.summary.school_no_milk = self.summary.school_no_milk + 1
        self.__update_summary()

    def __decrease_in_summary(self):
        # TODO refactor, check if needed
        self.summary.apple -= self.product_data['apple']
        self.summary.pear -= self.product_data['pear']
        self.summary.plum -= self.product_data['plum']
        self.summary.strawberry -= self.product_data['strawberry']
        self.summary.juice -= self.product_data['juice']
        self.summary.carrot -= self.product_data['carrot']
        self.summary.radish -= self.product_data['radish']
        self.summary.pepper -= self.product_data['pepper']
        self.summary.tomato -= self.product_data['tomato']
        self.summary.kohlrabi -= self.product_data['kohlrabi']
        self.summary.milk -= self.product_data['milk']
        self.summary.yoghurt -= self.product_data['yoghurt']
        self.summary.kefir -= self.product_data['kefir']
        self.summary.cheese -= self.product_data['cheese']
        self.summary.kids_no -= self.product_data['max_kids_perWeeks_fruitVeg']
        if self.product_data['max_kids_perWeeks_fruitVeg'] != 0:
            self.summary.school_no = self.summary.school_no - 1

        self.summary.kids_no_milk -= self.product_data['max_kids_perWeeks_milk']
        if self.product_data['max_kids_perWeeks_milk'] != 0:
            self.summary.school_no_milk = self.summary.school_no_milk - 1

        self.__update_summary()
        self.__init__(self.school.id, self.summary.id)

    def create_new(self):
        application_data = dict()
        application_data['summary_id'] = self.summary.id
        application_data['school_id'] = self.school.id
        application_data.update(self.product_data)
        application = Application(**application_data)
        return DatabaseManager.add_row(application)
