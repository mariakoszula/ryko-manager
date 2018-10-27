from rykomanager.documentManager.DocumentCreator import DocumentCreator
from rykomanager.documentManager.DatabaseManager import DatabaseManager
import rykomanager.configuration as cfg
from rykomanager.models import Summary
from rykomanager import app

from os import path


class SummaryCreator(DocumentCreator, DatabaseManager):
    template_document = cfg.summary_docx

    def __init__(self, week_start_id, week_no, is_first):
        self.week_start_id = week_start_id
        self.week_no = week_no
        self.is_first = is_first
        self.year = SummaryCreator._get_current_year()
        self.no = DatabaseManager.get_next_summary_no(self.year)
        self.summary = None
        output_directory = path.join(cfg.output_dir_main)
        self.fruit_all = 0
        self.veg_all = 0
        self.dairy_all = 0
        DocumentCreator.__init__(self, SummaryCreator.template_document, output_directory)
        DatabaseManager.__init__(self)

    @staticmethod
    def _get_current_year():
        return 2018

    def __base_check(self):
        calculated_fruitVeg_price = (self.fruit_all + self.veg_all) * DatabaseManager.get_fruit_price()
        calculated_dairy_price = self.dairy_all * DatabaseManager.get_milk_price()

        if not calculated_fruitVeg_price == self.summary.fruitVeg_income:
            app.logger.error("Summary ABORT: the price for fruitVeg does not match calculated_fruitVeg_price: {} expected: {} fruitVeg: {}".format(
                calculated_fruitVeg_price, DatabaseManager.get_fruit_price(), (self.fruit_all + self.veg_all)))
            return False

        if not calculated_dairy_price == self.summary.milk_income:
            app.logger.error("Summary ABORT: the price for dairy does not match calculated_dairy_price: {} expected: {} milk: {}".format(
                calculated_dairy_price, DatabaseManager.get_milk_price(), self.dairy_all))
            return False
        return True

    def generate(self):
        if not self.summary:
            app.logger.error("Summary does not exists")
            return

        self.fruit_all = sum([self.summary.apple, self.summary.pear, self.summary.plum, self.summary.strawberry])
        self.veg_all = sum([self.summary.carrot, self.summary.tomato, self.summary.radish, self.summary.kohlrabi])
        self.dairy_all = self.summary.milk + self.summary.yoghurt + self.summary.kefir + self.summary.cheese

        if not self.__base_check():
            app.logger.error("Summary Base Check failed")
            return

        week_range = (1, 6) if self.summary.is_first else (7, 12)
        self.document.merge(
                application_no=self.summary.get_application_no(),
                city="Zielona Góra",
                kids_no_fruitVeg=str(self.summary.kids_no),
                kids_no_milk=str(self.summary.kids_no_milk),
                weeks=DatabaseManager.str_from_weeks(DatabaseManager.get_weeks(program_id=1), week_range),
                is_first="X" if self.summary.is_first else "",
                is_not_first="X" if not self.summary.is_first else "",
                apple=str(self.summary.apple),
                plum=str(self.summary.plum),
                pear=str(self.summary.pear),
                strawberry=str(self.summary.strawberry),
                fruit_all=str(self.fruit_all),
                carrot=str(self.summary.carrot),
                tomato=str(self.summary.tomato),
                pepper=str(self.summary.pepper),
                radish=str(self.summary.radish),
                kohlrabi=str(self.summary.kohlrabi),
                veg_all=str(self.veg_all),
                milk=str(self.summary.milk),
                yoghurt=str(self.summary.yoghurt),
                kefir=str(self.summary.kefir),
                cheese=str(self.summary.cheese),
                dairy_all=str(self.dairy_all),
                fruitVeg_income="{0:.2f}".format(round(self.summary.fruitVeg_income, 2)),
                dairy_income="{0:.2f}".format(round(self.summary.milk_income, 2)),
                school_no_fruitVeg=str(self.summary.school_no),
                school_no_milk=str(self.summary.school_no_milk),
                school_no=str(max(self.summary.school_no, self.summary.school_no_milk))
        )
        DocumentCreator.generate(self, "Wniosek_{}_{}.docx".format(self.summary.no, self.summary.year), False)

    def create(self):
        self.summary = DatabaseManager.is_summary(self.no, self.year)[0] if DatabaseManager.is_summary(self.no, self.year) else None
        if not self.summary:
            self.update_row()

    def update_row(self):
        summary = Summary(no=self.no, year=self.year, is_first=True, program_id=cfg.current_program_id)
        if DatabaseManager.add_row(summary):
            self.summary = DatabaseManager.is_summary(self.no, self.year)[0]


    def modify_row(self):
        pass
