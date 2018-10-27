from rykomanager.documentManager.DocumentCreator import DocumentCreator
from rykomanager.documentManager.DatabaseManager import DatabaseManager
import rykomanager.configuration as cfg
from rykomanager.models import Summary, ProductName, ProductType, Application, Product
from rykomanager import app

from os import path


class ApplicationCreator(DocumentCreator, DatabaseManager):
    template_document_v = cfg.applicaton_docx_5
    template_document_va = cfg.application_docx_5a

    def __init__(self, school_id, summary_id):
        self.school_id = school_id
        self.school = DatabaseManager.get_school(school_id)
        self.summary = DatabaseManager.get_summary(summary_id)
        self.summary_id = summary_id

        weeks = (1,6) if self.summary.is_first else (7,12)
        self.apple = DatabaseManager.get_product_amount(self.school_id, ProductName.APPLE, weeks)
        self.pear = DatabaseManager.get_product_amount(self.school_id, ProductName.PEAR, weeks)
        self.plum = DatabaseManager.get_product_amount(self.school_id, ProductName.PLUM, weeks)
        self.strawberry = DatabaseManager.get_product_amount(self.school_id, ProductName.STRAWBERRY, weeks)
        self.carrot = DatabaseManager.get_product_amount(self.school_id, ProductName.CARROT, weeks)
        self.radish = DatabaseManager.get_product_amount(self.school_id, ProductName.RADISH, weeks)
        self.pepper = DatabaseManager.get_product_amount(self.school_id, ProductName.PEPPER, weeks)
        self.tomato = DatabaseManager.get_product_amount(self.school_id, ProductName.TOMATO, weeks)
        self.kohlrabi = DatabaseManager.get_product_amount(self.school_id, ProductName.KOHLRABI, weeks)
        self.milk = DatabaseManager.get_product_amount(self.school_id, ProductName.MILK, weeks)
        self.yoghurt = DatabaseManager.get_product_amount(self.school_id, ProductName.YOGHURT, weeks)
        self.kefir = DatabaseManager.get_product_amount(self.school_id, ProductName.KEFIR, weeks)
        self.cheese = DatabaseManager.get_product_amount(self.school_id, ProductName.CHEESE, weeks)
        self.fruit_all = self.apple + self.pear + self.plum + self.strawberry
        self.veg_all = self.carrot + self.radish + self.pepper + self.tomato + self.kohlrabi
        self.dairy_all = self.milk + self.yoghurt + self.kefir + self.cheese
        self.max_kids_perWeeks_fruitVeg = DatabaseManager.get_maxKids_perWeek(school_id, ProductType.FRUIT_VEG, weeks)
        self.max_kids_perWeeks_milk = DatabaseManager.get_maxKids_perWeek(school_id, ProductType.DAIRY, weeks)
        self.records_to_merge_vegFruit = []
        self.records_to_merge_milk = []
        self.sum_product_vegFruit = 0
        self.sum_product_milk = 0
        output_directory = path.join(cfg.output_dir_main, cfg.output_dir_school, self.school.nick,
                                     cfg.annex_folder_name)
        self.output_directory = output_directory
        DatabaseManager.__init__(self)

    def generate(self):
        if self.__prepare_data():
            self._generate_5()
            self._generate_5a()

    def _generate_5(self):
        DocumentCreator.__init__(self, ApplicationCreator.template_document_v, self.output_directory)
        self.document.merge(
            application_no=self.summary.get_application_no(),
            school_name=self.school.name,
            school_nip=self.school.nip,
            school_regon=self.school.regon,
            school_address=self.school.address,
            city=self.school.city,
            max_kids_fruitVeg=str(max(DatabaseManager.get_maxKids_perWeek(self.school.id, ProductType.FRUIT_VEG), DatabaseManager.get_contract(self.school.id).fruitVeg_products)),
            max_kids_milk=str(max(DatabaseManager.get_maxKids_perWeek(self.school.id, ProductType.DAIRY), DatabaseManager.get_contract(self.school.id).dairy_products)),
            week_date_1=DatabaseManager.get_dates(1) if self.summary.is_first else "-",
            week_date_2=DatabaseManager.get_dates(2) if self.summary.is_first else "-",
            week_date_3=DatabaseManager.get_dates(3) if self.summary.is_first else "-",
            week_date_4=DatabaseManager.get_dates(4) if self.summary.is_first else "-",
            week_date_5=DatabaseManager.get_dates(5) if self.summary.is_first else "-",
            week_date_6=DatabaseManager.get_dates(6) if self.summary.is_first else "-",
            week_date_7=DatabaseManager.get_dates(7) if not self.summary.is_first else "-",
            week_date_8=DatabaseManager.get_dates(8) if not self.summary.is_first else "-",
            week_date_9=DatabaseManager.get_dates(9) if not self.summary.is_first else "-",
            week_date_10=DatabaseManager.get_dates(10) if not self.summary.is_first else "-",
            week_date_11=DatabaseManager.get_dates(11) if not self.summary.is_first else "-",
            week_date_12=DatabaseManager.get_dates(12) if not self.summary.is_first else "-",
            fuitVeg_week1=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.FRUIT_VEG, (1,1)) if self.summary.is_first else "-"),
            fuitVeg_week2=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.FRUIT_VEG, (2,2)) if self.summary.is_first else "-"),
            fuitVeg_week3=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.FRUIT_VEG, (3,3)) if self.summary.is_first else "-"),
            fuitVeg_week4=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.FRUIT_VEG, (4,4)) if self.summary.is_first else "-"),
            fuitVeg_week5=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.FRUIT_VEG, (5,5)) if self.summary.is_first else "-"),
            fuitVeg_week6=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.FRUIT_VEG, (6,6)) if self.summary.is_first else "-"),
            fuitVeg_week7=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.FRUIT_VEG, (7,7)) if not self.summary.is_first else "-"),
            fuitVeg_week8=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.FRUIT_VEG, (8,8)) if not self.summary.is_first else "-"),
            fuitVeg_week9=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.FRUIT_VEG, (9,9)) if not self.summary.is_first else "-"),
            fuitVeg_week10=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.FRUIT_VEG, (10,10)) if not self.summary.is_first else "-"),
            fuitVeg_week11=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.FRUIT_VEG, (11,11)) if not self.summary.is_first else "-"),
            fuitVeg_week12=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.FRUIT_VEG, (12,12)) if not self.summary.is_first else "-"),
            milk_week1=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.DAIRY, (1,1)) if self.summary.is_first else "-"),
            milk_week2=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.DAIRY, (2,2)) if self.summary.is_first else "-"),
            milk_week3=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.DAIRY, (3,3)) if self.summary.is_first else "-"),
            milk_week4=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.DAIRY, (4,4)) if self.summary.is_first else "-"),
            milk_week5=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.DAIRY, (5,5)) if self.summary.is_first else "-"),
            milk_week6=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.DAIRY, (6,6)) if self.summary.is_first else "-"),
            milk_week7=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.DAIRY, (7,7)) if not self.summary.is_first else "-"),
            milk_week8=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.DAIRY, (8,8)) if not self.summary.is_first else "-"),
            milk_week9=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.DAIRY, (9,9)) if not self.summary.is_first else "-"),
            milk_week10=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.DAIRY, (10,10)) if not self.summary.is_first else "-"),
            milk_week11=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.DAIRY, (11,11)) if not self.summary.is_first else "-"),
            milk_week12=str(DatabaseManager.get_maxKids_perWeek(self.school_id, ProductType.DAIRY, (12,12)) if not self.summary.is_first else "-"),
            apple=str(self.apple),
            plum=str(self.plum),
            pear=str(self.pear),
            strawberry=str(self.strawberry),
            fruit_all=str(self.fruit_all),
            carrot=str(self.carrot),
            tomato=str(self.tomato),
            pepper=str(self.pepper),
            radish=str(self.radish),
            kohlrabi=str(self.kohlrabi),
            veg_all=str(self.veg_all),
            milk=str(self.milk),
            yoghurt=str(self.yoghurt),
            kefir=str(self.kefir),
            cheese=str(self.cheese),
            dairy_all=str(self.dairy_all)
        )
        DocumentCreator.generate(self, "Oswiadczenie_V_Wniosek_{}_{}.docx".format(self.summary.no, self.summary.year), False)

    def _generate_5a(self):
        DocumentCreator.__init__(self, ApplicationCreator.template_document_va, self.output_directory)

        self.document.merge_rows('date_vegFruit', self.records_to_merge_vegFruit)
        self.document.merge_rows('date_milk', self.records_to_merge_milk)
        self.document.merge(
            school_name=self.school.name,
            school_nip=self.school.nip,
            school_regon=self.school.regon,
            school_address=self.school.address,
            city=self.school.city,
            weeks=DatabaseManager.str_from_weeks(DatabaseManager.get_weeks(1), (1, 6)),
            sum_vegFruit=str(self.sum_product_vegFruit),
            sum_kids_vegFruit=str(self.sum_product_vegFruit),
            sum_milk=str(self.sum_product_milk),
            sum_kids_milk=str(self.sum_product_milk)
        )
        DocumentCreator.generate(self, "Ewidencja_VA_Wniosek_{}_{}.docx".format(self.summary.no, self.summary.year), False)

    def __prepare_data(self):
        for record in DatabaseManager.get_records(self.school_id, ProductType.FRUIT_VEG, (1, 6)):
            record_dict = dict()
            record_dict['date_vegFruit'] = DatabaseManager.str_from_date(record.date, "%d.%m.%Y")
            record_dict['kids_vegFruit'] = str(record.product_no)
            record_dict['vegFruit'] = Product.get_name_map(record.product)
            self.records_to_merge_vegFruit.append(record_dict)

        for record in DatabaseManager.get_records(self.school_id, ProductType.DAIRY, (1, 6)):
            record_dict = dict()
            record_dict['date_milk'] = DatabaseManager.str_from_date(record.date, "%d.%m.%Y")
            record_dict['kids_milk'] = str(record.product_no)
            record_dict['milk'] = Product.get_name_map(record.product)
            self.records_to_merge_milk.append(record_dict)

        self.sum_product_vegFruit = self.__sum_product(self.records_to_merge_vegFruit, 'kids_vegFruit')
        self.sum_product_milk = self.__sum_product(self.records_to_merge_milk, 'kids_milk')

        if self.sum_product_vegFruit != (self.fruit_all + self.veg_all):
            app.logger.error("Vale of fruitVeg product from 5 and 5A does not match! School: {0} 5: {1} "
                             " 5A: {2} -- ABORT generating".format(self.school.nick, self.fruit_all + self.veg_all, self.sum_product_vegFruit))
            return False
        if self.sum_product_milk != self.dairy_all:
            app.logger.error("Vale of dairy product from 5 and 5A does not match! School: {0} 5: {1} "
                             " 5A: {2} -- ABORT generating".format(self.school.nick, self.dairy_all, self.sum_product_milk))
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
        if not DatabaseManager.get_application(self.school_id, self.summary_id) and self.update_row():
            self.summary.apple += self.apple
            self.summary.pear += self.pear
            self.summary.plum += self.plum
            self.summary.strawberry += self.strawberry
            self.summary.carrot += self.carrot
            self.summary.radish += self.radish
            self.summary.pepper += self.pepper
            self.summary.tomato += self.tomato
            self.summary.milk += self.milk
            self.summary.yoghurt += self.yoghurt
            self.summary.kefir += self.kefir
            self.summary.cheese += self.cheese
            self.summary.kids_no += self.max_kids_perWeeks_fruitVeg
            self.summary.kids_no_milk += self.max_kids_perWeeks_milk
            if self.max_kids_perWeeks_fruitVeg != 0:
                self.summary.school_no = self.summary.school_no + 1
            if self.max_kids_perWeeks_milk != 0:
                self.summary.school_no_milk = self.summary.school_no_milk + 1
            self.summary.fruitVeg_income = (self.summary.apple + self.summary.pear + self.summary.plum + self.summary.strawberry
                                            + self.summary.carrot + self.summary.tomato + self.summary.radish + self.summary.kohlrabi) * DatabaseManager.get_fruit_price()
            self.summary.milk_income = (self.summary.milk + self.summary.yoghurt + self.summary.kefir + self.summary.cheese) * DatabaseManager.get_milk_price()
            DatabaseManager.modify_row()
            return True
        else:
            app.logger.error("Application for summary {0}/{1} for school {2} already exists".format(self.summary.no, self.summary.year, self.school.nick))
            return False

    def update_row(self):
        app = Application(summary_id=self.summary_id, school_id=self.school_id, apple=self.apple, pear=self.pear,
                          plum=self.plum, strawberry=self.strawberry, carrot=self.carrot, radish=self.radish, kohlrabi=self.kohlrabi,
                          tomato=self.tomato, pepper=self.pepper, milk=self.milk, yoghurt=self.yoghurt, cheese=self.cheese,
                          kefir=self.kefir, fruit_all=self.fruit_all, veg_all=self.veg_all, dairy_all=self.dairy_all,
                          max_kids_perWeeks_fruitVeg=self.max_kids_perWeeks_fruitVeg, max_kids_perWeeks_milk=self.max_kids_perWeeks_milk
                          )
        return DatabaseManager.add_row(app)
