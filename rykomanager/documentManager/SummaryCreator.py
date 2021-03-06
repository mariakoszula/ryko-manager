from rykomanager.documentManager.DocumentCreator import DocumentCreator
from rykomanager.documentManager.DatabaseManager import DatabaseManager
from rykomanager.models import ProductName
from rykomanager.models import Summary
from rykomanager import app, config_parser
from typing import Set
import datetime


class SummaryCreator(DocumentCreator, DatabaseManager):
    def __init__(self, program_id, weeks: Set[int], no=None):
        self.summary: Summary = None
        self.program_id = program_id
        self.weeks = weeks
        if no:
            self.summary = DatabaseManager.get_summary(self.program_id, no)
            self.summary.weeks = weeks
            DatabaseManager.modify()
        self.school_no = 0
        output_directory = config_parser.get('Directories', 'current_program')
        DocumentCreator.__init__(self, config_parser.get('DocTemplates', 'summary'), output_directory)
        DatabaseManager.__init__(self)

    @staticmethod
    def _get_current_year():
        now = datetime.datetime.now()
        return now.year

    def __base_check(self):
        assert(self.summary.get_from_fruit_list(ProductName.APPLE).amount == self.summary.apple)
        assert (self.summary.get_fruit_veg_income() == self.summary.fruitVeg_income)
        assert (self.summary.get_dairy_income() == self.summary.milk_income)
        assert(self.summary.get_from_diary_list(ProductName.MILK).amount == self.summary.milk)
        assert(self.summary.get_from_diary_list(ProductName.KEFIR).amount == self.summary.kefir)
        calculated_fruitVeg_price = self.summary.get_fruit_veg_income()
        calculated_dairy_price = self.summary.get_dairy_income()

        if not calculated_fruitVeg_price == self.summary.fruitVeg_income:
            app.logger.error("Summary ABORT: the price for fruitVeg does not match calculated_fruitVeg_price: {} expected: {}  fruitVeg amoung: {}"
                             " income: {} ".format(
                calculated_fruitVeg_price, DatabaseManager.get_fruit_price(), calculated_fruitVeg_price, self.summary.fruitVeg_income))
            return False

        if not calculated_dairy_price == self.summary.milk_income:
            app.logger.error("Summary ABORT: the price for dairy does not match calculated_dairy_price: {} expected: {} milk: {}".format(
                calculated_dairy_price, DatabaseManager.get_milk_price(), self.summary.milk_income))
            return False
        return True

    def generate(self):
        if not self.summary:
            app.logger.error("Summary does not exists")
            return

        if not self.__base_check():
            app.logger.error("Summary Base Check failed")
            return

        assert(int(self.summary.get_veg_income() + self.summary.get_fruit_income()) == int(self.summary.get_fruit_veg_income()))
        #TODO refactor based on idea in Application Creator
        self.document.merge(
                application_no=self.summary.get_application_no(),
                city="Zielona Góra",
                wn=str(self.summary.number_of_weeks),
                kids_no_fruitVeg=str(self.summary.kids_no),
                kids_no_milk=str(self.summary.kids_no_milk),
                weeks=DatabaseManager.str_from_weeks(DatabaseManager.get_weeks(self.program_id), self.summary.weeks),
                apple=str(self.summary.get_from_fruit_list(ProductName.APPLE).amount),
                applewn=str(self.summary.get_from_fruit_list(ProductName.APPLE).calculate_netto()),
                applevat=str(self.summary.get_from_fruit_list(ProductName.APPLE).calculate_vat()),
                applewb=str(self.summary.get_from_fruit_list(ProductName.APPLE).calculate_brutto()),
                plum=str(self.summary.get_from_fruit_list(ProductName.PLUM).amount),
                plumwn=str(self.summary.get_from_fruit_list(ProductName.PLUM).calculate_netto()),
                plumvat=str(self.summary.get_from_fruit_list(ProductName.PLUM).calculate_vat()),
                plumwb=str(self.summary.get_from_fruit_list(ProductName.PLUM).calculate_brutto()),
                pear=str(self.summary.get_from_fruit_list(ProductName.PEAR).amount),
                pearwn=str(self.summary.get_from_fruit_list(ProductName.PEAR).calculate_netto()),
                pearvat=str(self.summary.get_from_fruit_list(ProductName.PEAR).calculate_vat()),
                pearwb=str(self.summary.get_from_fruit_list(ProductName.PEAR).calculate_brutto()),
                strawberry=str(self.summary.get_from_fruit_list(ProductName.STRAWBERRY).amount),
                strawberrywn=str(self.summary.get_from_fruit_list(ProductName.STRAWBERRY).calculate_netto()),
                strawberryvat=str(self.summary.get_from_fruit_list(ProductName.STRAWBERRY).calculate_vat()),
                strawberrywb=str(self.summary.get_from_fruit_list(ProductName.STRAWBERRY).calculate_brutto()),
                juice=str(self.summary.get_from_fruit_list(ProductName.JUICE).amount),
                juicewn=str(self.summary.get_from_fruit_list(ProductName.JUICE).calculate_netto()),
                juicevat=str(self.summary.get_from_fruit_list(ProductName.JUICE).calculate_vat()),
                juicewb=str(self.summary.get_from_fruit_list(ProductName.JUICE).calculate_brutto()),
                fruitall=str(self.summary.get_fruit_amount()),
                fruitalln="{0:.2f}".format(self.summary.get_fruit_netto()),
                fruitallvat="{0:.2f}".format(self.summary.get_fruit_vat()),
                fruitallwb="{0:.2f}".format(self.summary.get_fruit_income()),
                carrot=str(self.summary.get_from_fruit_list(ProductName.CARROT).amount),
                carrotwn=str(self.summary.get_from_fruit_list(ProductName.CARROT).calculate_netto()),
                carrotvat=str(self.summary.get_from_fruit_list(ProductName.CARROT).calculate_vat()),
                carrotwb=str(self.summary.get_from_fruit_list(ProductName.CARROT).calculate_brutto()),
                tomato=str(self.summary.get_from_fruit_list(ProductName.TOMATO).amount),
                tomatown=str(self.summary.get_from_fruit_list(ProductName.TOMATO).calculate_netto()),
                tomatovat=str(self.summary.get_from_fruit_list(ProductName.TOMATO).calculate_vat()),
                tomatowb=str(self.summary.get_from_fruit_list(ProductName.TOMATO).calculate_brutto()),
                pepper=str(self.summary.get_from_fruit_list(ProductName.PEPPER).amount),
                pepperwn=str(self.summary.get_from_fruit_list(ProductName.PEPPER).calculate_netto()),
                peppervat=str(self.summary.get_from_fruit_list(ProductName.PEPPER).calculate_vat()),
                pepperwb=str(self.summary.get_from_fruit_list(ProductName.PEPPER).calculate_brutto()),
                radish=str(self.summary.get_from_fruit_list(ProductName.RADISH).amount),
                radishwn=str(self.summary.get_from_fruit_list(ProductName.RADISH).calculate_netto()),
                radishvat=str(self.summary.get_from_fruit_list(ProductName.RADISH).calculate_vat()),
                radishwb=str(self.summary.get_from_fruit_list(ProductName.RADISH).calculate_brutto()),
                kohlrabi=str(self.summary.get_from_fruit_list(ProductName.KOHLRABI).amount),
                kohlrabiwn=str(self.summary.get_from_fruit_list(ProductName.KOHLRABI).calculate_netto()),
                kohlrabivat=str(self.summary.get_from_fruit_list(ProductName.KOHLRABI).calculate_vat()),
                kohlrabiwb=str(self.summary.get_from_fruit_list(ProductName.KOHLRABI).calculate_brutto()),
                veg_all=str(self.summary.get_veg_amount()),
                veg_alln="{0:.2f}".format(self.summary.get_veg_netto()),
                veg_allvat="{0:.2f}".format(self.summary.get_veg_vat()),
                veg_allwb="{0:.2f}".format(self.summary.get_veg_income()),

                fruitVeg_income="{0:.2f}".format(self.summary.fruitVeg_income),

                milk=str(self.summary.get_from_diary_list(ProductName.MILK).amount),
                milkwn=str(self.summary.get_from_diary_list(ProductName.MILK).calculate_netto()),
                milkvat=str(self.summary.get_from_diary_list(ProductName.MILK).calculate_vat()),
                milkwb=str(self.summary.get_from_diary_list(ProductName.MILK).calculate_brutto()),
                yoghurt=str(self.summary.get_from_diary_list(ProductName.YOGHURT).amount),
                yoghurtwn=str(self.summary.get_from_diary_list(ProductName.YOGHURT).calculate_netto()),
                yoghurtvat=str(self.summary.get_from_diary_list(ProductName.YOGHURT).calculate_vat()),
                yoghurtwb=str(self.summary.get_from_diary_list(ProductName.YOGHURT).calculate_brutto()),
                kefir=str(self.summary.get_from_diary_list(ProductName.KEFIR).amount),
                kefirwn=str(self.summary.get_from_diary_list(ProductName.KEFIR).calculate_netto()),
                kefirvat=str(self.summary.get_from_diary_list(ProductName.KEFIR).calculate_vat()),
                kefirwb=str(self.summary.get_from_diary_list(ProductName.KEFIR).calculate_brutto()),
                cheese=str(self.summary.get_from_diary_list(ProductName.CHEESE).amount),
                cheesewn=str(self.summary.get_from_diary_list(ProductName.CHEESE).calculate_netto()),
                cheesevat=str(self.summary.get_from_diary_list(ProductName.CHEESE).calculate_vat()),
                cheesewb=str(self.summary.get_from_diary_list(ProductName.CHEESE).calculate_brutto()),

                dairy_all=str(self.summary.get_dairy_amount()),
                dairy_wn="{0:.2f}".format(self.summary.get_dairy_netto()),
                dairy_vat="{0:.2f}".format(self.summary.get_dairy_vat()),
                dairy_wb="{0:.2f}".format(self.summary.get_dairy_income()),
                dairy_income="{0:.2f}".format(self.summary.milk_income),

                school_no_fruitVeg=str(self.summary.school_no),
                school_no_milk=str(self.summary.school_no_milk),
                app_school_no=str(self.school_no)
        )
        DocumentCreator.generate(self, f"Wniosek_{self.summary.no}.docx", False)

    def create(self):
        if not self.summary:
            self.create_new()
        else:
            self.clear()
        self.summary
        return self.summary

    @staticmethod
    def get_next_number(program_id):
        summaries = DatabaseManager.get_summaries(program_id)
        return 1 + (max([summary.no for summary in summaries]) if summaries else 0)

    def create_new(self):
        number = SummaryCreator.get_next_number(self.program_id)
        summary = Summary(no=number,
                          year=SummaryCreator._get_current_year(),
                          program_id=self.program_id,
                          weeks=self.weeks)
        if DatabaseManager.add_row(summary):
            self.summary = DatabaseManager.get_summary(self.program_id, number)

    def get_id(self):
        return self.summary.id

    def modify(self):
        pass

    def clear(self):
        # TODO refactor
        self.summary.apple = 0
        self.summary.pear = 0
        self.summary.plum = 0
        self.summary.strawberry = 0
        self.summary.juice = 0
        self.summary.carrot = 0
        self.summary.radish = 0
        self.summary.pepper = 0
        self.summary.tomato = 0
        self.summary.kohlrabi = 0
        self.summary.milk = 0
        self.summary.yoghurt = 0
        self.summary.kefir = 0
        self.summary.cheese = 0
        self.summary.kids_no = 0
        self.summary.kids_no_milk = 0
        self.summary.school_no = 0
        self.summary.school_no_milk = 0
        self.summary.fruitVeg_income = 0
        self.summary.milk_income = 0
        DatabaseManager.modify()
