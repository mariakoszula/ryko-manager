from rykomanager.documentManager.DocumentCreator import DocumentCreator
from rykomanager.documentManager.DatabaseManager import DatabaseManager
from rykomanager.models import ProductName, ProductType, Application, Summary, School
from rykomanager import app, config_parser
from shutil import copyfile
from os import path, makedirs, remove
from rykomanager.DateConverter import DateConverter


class ApplicationCreator(DocumentCreator, DatabaseManager):
    template_document_v = config_parser.get('DocTemplates', 'application')
    template_document_va = config_parser.get('DocTemplates', 'application_5a')
    main_app_dir = config_parser.get('Directories', 'application_all')

    def __init__(self, program_id, school, summary, date):
        self.main_app_dir = path.join(ApplicationCreator.main_app_dir, str(summary.no))
        if not path.exists(self.main_app_dir):
            makedirs(self.main_app_dir)
        self.program_id = program_id
        self.all_weeks = set([week.week_no for week in DatabaseManager.get_weeks(program_id)])
        self.school: School = school
        self.summary: Summary = summary
        self.__prepare_fruit_data()
        self.__prepare_dairy_data()
        self.sign_date = DateConverter.to_date(date)
        self.output_directory = self.school.generate_directory_name(config_parser.get('Directories', 'application'))
        DatabaseManager.__init__(self)

    def __prepare_fruit_data(self):
        self.apple = DatabaseManager.get_product_amount(self.program_id, self.school.id, ProductName.APPLE,
                                                        self.summary.weeks)
        self.pear = DatabaseManager.get_product_amount(self.program_id, self.school.id, ProductName.PEAR,
                                                       self.summary.weeks)
        self.plum = DatabaseManager.get_product_amount(self.program_id, self.school.id, ProductName.PLUM,
                                                       self.summary.weeks)
        self.strawberry = DatabaseManager.get_product_amount(self.program_id, self.school.id, ProductName.STRAWBERRY,
                                                             self.summary.weeks)
        self.juice = DatabaseManager.get_product_amount(self.program_id, self.school.id, ProductName.JUICE,
                                                        self.summary.weeks)
        self.carrot = DatabaseManager.get_product_amount(self.program_id, self.school.id, ProductName.CARROT,
                                                         self.summary.weeks)
        self.radish = DatabaseManager.get_product_amount(self.program_id, self.school.id, ProductName.RADISH,
                                                         self.summary.weeks)
        self.pepper = DatabaseManager.get_product_amount(self.program_id, self.school.id, ProductName.PEPPER,
                                                         self.summary.weeks)
        self.tomato = DatabaseManager.get_product_amount(self.program_id, self.school.id, ProductName.TOMATO,
                                                         self.summary.weeks)
        self.kohlrabi = DatabaseManager.get_product_amount(self.program_id, self.school.id, ProductName.KOHLRABI,
                                                               self.summary.weeks)
        self.fruit_all = self.apple + self.pear + self.plum + self.strawberry + self.juice
        self.veg_all = self.carrot + self.radish + self.pepper + self.tomato + self.kohlrabi
        self.max_kids_perWeeks_fruitVeg = DatabaseManager.get_maxKids_perWeek(self.program_id, self.school.id,
                                                                          ProductType.FRUIT_VEG, self.summary.weeks)
        self.records_to_merge_vegFruit = []
        self.sum_product_vegFruit = 0

    def __prepare_dairy_data(self):
        self.milk = DatabaseManager.get_product_amount(self.program_id, self.school.id, ProductName.MILK,
                                                       self.summary.weeks)
        self.yoghurt = DatabaseManager.get_product_amount(self.program_id, self.school.id, ProductName.YOGHURT,
                                                          self.summary.weeks)
        self.kefir = DatabaseManager.get_product_amount(self.program_id, self.school.id, ProductName.KEFIR,
                                                        self.summary.weeks)
        self.cheese = DatabaseManager.get_product_amount(self.program_id, self.school.id, ProductName.CHEESE,
                                                         self.summary.weeks)
        self.dairy_all = self.milk + self.yoghurt + self.kefir + self.cheese
        self.max_kids_perWeeks_milk = DatabaseManager.get_maxKids_perWeek(self.program_id, self.school.id,
                                                                          ProductType.DAIRY, self.summary.weeks)
        self.records_to_merge_milk = []
        self.sum_product_milk = 0


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
            max_kids_fruitVeg=str(max(DatabaseManager.get_maxKids_perWeek(self.program_id, self.school.id, ProductType.FRUIT_VEG, self.all_weeks), DatabaseManager.get_contract(self.school.id, self.program_id).fruitVeg_products)),
            max_kids_milk=str(max(DatabaseManager.get_maxKids_perWeek(self.program_id, self.school.id, ProductType.DAIRY, self.all_weeks), DatabaseManager.get_contract(self.school.id, self.program_id).dairy_products)),
            week_date_1=str(DatabaseManager.get_dates(self.program_id, 1)),
            week_date_2=str(DatabaseManager.get_dates(self.program_id, 2)),
            week_date_3=str(DatabaseManager.get_dates(self.program_id, 3)),
            week_date_4=str(DatabaseManager.get_dates(self.program_id, 4)),
            week_date_5=str(DatabaseManager.get_dates(self.program_id, 5)),
            week_date_6=str(DatabaseManager.get_dates(self.program_id, 6)),
            week_date_7=str("-"),
            week_date_8=str("-"),
            week_date_9=str("-"),
            week_date_10=str("-"),
            week_date_11=str("-"),
            week_date_12=str("-"),
            fuitVeg_week1=str(DatabaseManager.get_maxKids_perWeek(self.program_id, self.school.id, ProductType.FRUIT_VEG, set([1]))),
            fuitVeg_week2=str(DatabaseManager.get_maxKids_perWeek(self.program_id, self.school.id, ProductType.FRUIT_VEG, set([2]))),
            fuitVeg_week3=str(DatabaseManager.get_maxKids_perWeek(self.program_id, self.school.id, ProductType.FRUIT_VEG, set([3]))),
            fuitVeg_week4=str(DatabaseManager.get_maxKids_perWeek(self.program_id, self.school.id, ProductType.FRUIT_VEG, set([4]))),
            fuitVeg_week5=str(DatabaseManager.get_maxKids_perWeek(self.program_id, self.school.id, ProductType.FRUIT_VEG, set([5]))),
            fuitVeg_week6=str(DatabaseManager.get_maxKids_perWeek(self.program_id, self.school.id, ProductType.FRUIT_VEG, set([6]))),
            fuitVeg_week7="-",
            fuitVeg_week8="-",
            fuitVeg_week9="-",
            fuitVeg_week10="-",
            fuitVeg_week11="-",
            fuitVeg_week12="-",
            portion_no_fruitVeg_1 = str(DatabaseManager.get_portion_perWeek(self.program_id, self.school.id, ProductType.FRUIT_VEG, 1)),
            portion_no_fruitVeg_2=str(DatabaseManager.get_portion_perWeek(self.program_id, self.school.id, ProductType.FRUIT_VEG, 2))  ,
            portion_no_fruitVeg_3=str(DatabaseManager.get_portion_perWeek(self.program_id, self.school.id, ProductType.FRUIT_VEG, 3))  ,
            portion_no_fruitVeg_4=str(DatabaseManager.get_portion_perWeek(self.program_id, self.school.id, ProductType.FRUIT_VEG, 4))  ,
            portion_no_fruitVeg_5=str(DatabaseManager.get_portion_perWeek(self.program_id, self.school.id, ProductType.FRUIT_VEG, 5))  ,
            portion_no_fruitVeg_6=str(DatabaseManager.get_portion_perWeek(self.program_id, self.school.id, ProductType.FRUIT_VEG, 6))  ,
            portion_no_fruitVeg_7="-",
            portion_no_fruitVeg_8="-",
            portion_no_fruitVeg_9="-",
            portion_no_fruitVeg_10="-",
            portion_no_fruitVeg_11="-",
            portion_no_fruitVeg_12="-",
            milk_week1=str(DatabaseManager.get_maxKids_perWeek(self.program_id, self.school.id, ProductType.DAIRY, (1,1))),
            milk_week2=str(DatabaseManager.get_maxKids_perWeek(self.program_id, self.school.id, ProductType.DAIRY, (2,2))),
            milk_week3=str(DatabaseManager.get_maxKids_perWeek(self.program_id, self.school.id, ProductType.DAIRY, (3,3))),
            milk_week4=str(DatabaseManager.get_maxKids_perWeek(self.program_id, self.school.id, ProductType.DAIRY, (4,4))),
            milk_week5=str(DatabaseManager.get_maxKids_perWeek(self.program_id, self.school.id, ProductType.DAIRY, (5,5))),
            milk_week6=str(DatabaseManager.get_maxKids_perWeek(self.program_id, self.school.id, ProductType.DAIRY, (6,6))),
            milk_week7=str("-"),
            milk_week8=str("-"),
            milk_week9=str("-"),
            milk_week10=str("-"),
            milk_week11=str("-"),
            milk_week12=str("-"),
            portion_no_milk_1=str(
                DatabaseManager.get_portion_perWeek(self.program_id, self.school.id, ProductType.DAIRY, 1)),
            portion_no_milk_2=str(
                DatabaseManager.get_portion_perWeek(self.program_id, self.school.id, ProductType.DAIRY, 2)),
            portion_no_milk_3=str(
                DatabaseManager.get_portion_perWeek(self.program_id, self.school.id, ProductType.DAIRY, 3)),
            portion_no_milk_4=str(
                DatabaseManager.get_portion_perWeek(self.program_id, self.school.id, ProductType.DAIRY, 4)),
            portion_no_milk_5=str(
                DatabaseManager.get_portion_perWeek(self.program_id, self.school.id, ProductType.DAIRY, 5)),
            portion_no_milk_6=str(
                DatabaseManager.get_portion_perWeek(self.program_id, self.school.id, ProductType.DAIRY, 6)),
            portion_no_milk_7= "-",
            portion_no_milk_8="-",
            portion_no_milk_9="-",
            portion_no_milk_10="-",
            portion_no_milk_11="-",
            portion_no_milk_12="-",
            apple=str(self.apple),
            plum=str(self.plum),
            pear=str(self.pear),
            strawberry=str(self.strawberry),
            juice=str(self.juice),
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
            dairy_all=str(self.dairy_all),
            date_day=DateConverter.two_digits(self.sign_date.day),
            date_month=DateConverter.two_digits(self.sign_date.month),
            date_year=str(self.sign_date.year)
        )
        doc_5_name = "Oswiadczenie_V_Wniosek_{}_{}.docx".format(self.summary.no, self.summary.year)
        doc_5_name_copy = path.join(self.main_app_dir,
                                                    "{0}_OswiadczenieV_{1}_{2}.docx".format(self.school.nick, self.summary.no, self.summary.year))
        DocumentCreator.generate(self, doc_5_name, False)
        if path.exists(doc_5_name_copy):
            remove(doc_5_name_copy)
        copyfile(path.join(self.output_directory, doc_5_name), doc_5_name_copy)


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
            weeks=DatabaseManager.str_from_weeks(DatabaseManager.get_weeks(self.program_id), self.summary.weeks),
            sum_vegFruit=str(self.sum_product_vegFruit),
            sum_kids_vegFruit=str(self.sum_product_vegFruit),
            sum_milk=str(self.sum_product_milk),
            sum_kids_milk=str(self.sum_product_milk),
            date_day=DateConverter.two_digits(self.sign_date.day),
            date_month=DateConverter.two_digits(self.sign_date.month),
            date_year=str(self.sign_date.year)
        )
        doc_5a_name = "Ewidencja_VA_Wniosek_{}_{}.docx".format(self.summary.no, self.summary.year)
        doc_5a_name_copy = path.join(self.main_app_dir,
                                                    "{0}_EwidencjaVa_{1}_{2}.docx".format(self.school.nick, self.summary.no, self.summary.year))
        DocumentCreator.generate(self, doc_5a_name, False)
        if path.exists(doc_5a_name_copy):
            remove(doc_5a_name_copy)
        copyfile(path.join(self.output_directory, doc_5a_name), doc_5a_name_copy)

    def __prepare_data(self):
        for record in DatabaseManager.get_records(self.program_id, self.school.id, ProductType.FRUIT_VEG, self.summary.weeks):
            record_dict = dict()
            record_dict['date_vegFruit'] = DateConverter.to_string(record.date, "%d.%m.%Y")
            record_dict['kids_vegFruit'] = str(record.product_no)
            record_dict['vegFruit'] = record.Product.get_name_mapping()
            self.records_to_merge_vegFruit.append(record_dict)

        for record in DatabaseManager.get_records(self.program_id, self.school.id, ProductType.DAIRY, self.summary.weeks):
            record_dict = dict()
            record_dict['date_milk'] = DateConverter.to_string(record.date, "%d.%m.%Y")
            record_dict['kids_milk'] = str(record.product_no)
            record_dict['milk'] = record.Product.get_name_mapping()
            self.records_to_merge_milk.append(record_dict)

        self.sum_product_vegFruit = self.__sum_product(self.records_to_merge_vegFruit, 'kids_vegFruit')
        self.sum_product_milk = self.__sum_product(self.records_to_merge_milk, 'kids_milk')

        if self.sum_product_vegFruit != (self.fruit_all + self.veg_all):
            app.logger.error("Value of fruitVeg product from 5 and 5A does not match! School: {0} 5: {1} "
                             " 5A: {2} -- ABORT generating".format(self.school.nick, self.fruit_all + self.veg_all, self.sum_product_vegFruit))
            return False
        if self.sum_product_milk != self.dairy_all:
            app.logger.error("Value of dairy product from 5 and 5A does not match! School: {0} 5: {1} "
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
        application = DatabaseManager.get_application(self.school.id, self.summary.id)
        if len(application) > 1:
            app.logger.error(
                "Application serious error: should never be returned more than one item in this list")
            return False
        if not application and self.create_new():
            app.logger.info(
                "Application for summary {0}/{1} for school {2} added".format(self.summary.no, self.summary.year,
                                                                                    self.school.nick))
            self.__increase_in_summary()
            return True
        else:
            if DatabaseManager.remove_application(application[0].id):
                app.logger.info("Application {3} for summary {0}/{1} for school {2} removed".format(self.summary.no, self.summary.year, self.school.nick,
                                                                                                 application[0].id))
            return self.create()

    def __update_summary(self):
        self.summary.fruitVeg_income = self.summary.get_fruit_veg_income()
        self.summary.milk_income = self.summary.get_dairy_income()
        app.logger.info("Update summary {2} fruitVeg_income: {0}, milk_income: {1}".format(self.summary.fruitVeg_income, self.summary.milk_income, self.school.nick))
        DatabaseManager.modify()

    def __increase_in_summary(self):
        self.summary.apple += self.apple
        self.summary.pear += self.pear
        self.summary.plum += self.plum
        self.summary.strawberry += self.strawberry
        self.summary.juice += self.juice
        self.summary.carrot += self.carrot
        self.summary.radish += self.radish
        self.summary.pepper += self.pepper
        self.summary.tomato += self.tomato
        self.summary.kohlrabi += self.kohlrabi
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
        self.__update_summary()

    def __decrease_in_summary(self):
        self.summary.apple -= self.apple
        self.summary.pear -= self.pear
        self.summary.plum -= self.plum
        self.summary.strawberry -= self.strawberry
        self.summary.juice -= self.juice
        self.summary.carrot -= self.carrot
        self.summary.radish -= self.radish
        self.summary.pepper -= self.pepper
        self.summary.tomato -= self.tomato
        self.summary.kohlrabi -= self.kohlrabi
        self.summary.milk -= self.milk
        self.summary.yoghurt -= self.yoghurt
        self.summary.kefir -= self.kefir
        self.summary.cheese -= self.cheese
        self.summary.kids_no -= self.max_kids_perWeeks_fruitVeg
        self.summary.kids_no_milk -= self.max_kids_perWeeks_milk
        if self.max_kids_perWeeks_fruitVeg != 0:
            self.summary.school_no = self.summary.school_no - 1
        if self.max_kids_perWeeks_milk != 0:
            self.summary.school_no_milk = self.summary.school_no_milk - 1
        self.__update_summary()
        self.__init__(self.school.id, self.summary.id)

    def create_new(self):
        application = Application(summary_id=self.summary.id, school_id=self.school.id, apple=self.apple, pear=self.pear,
                          plum=self.plum, strawberry=self.strawberry, juice=self.juice, carrot=self.carrot, radish=self.radish, kohlrabi=self.kohlrabi,
                          tomato=self.tomato, pepper=self.pepper, milk=self.milk, yoghurt=self.yoghurt, cheese=self.cheese,
                          kefir=self.kefir, fruit_all=self.fruit_all, veg_all=self.veg_all, dairy_all=self.dairy_all,
                          max_kids_perWeeks_fruitVeg=self.max_kids_perWeeks_fruitVeg, max_kids_perWeeks_milk=self.max_kids_perWeeks_milk
                          )
        return DatabaseManager.add_row(application)
