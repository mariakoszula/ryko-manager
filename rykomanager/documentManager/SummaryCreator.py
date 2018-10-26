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

        output_directory = path.join(cfg.output_dir_main)
        DocumentCreator.__init__(self, SummaryCreator.template_document, output_directory)
        DatabaseManager.__init__(self)

    @staticmethod
    def _get_current_year():
        return 2018

    def generate(self, new_doc_name):
        pass

    def create(self):
        if not DatabaseManager.is_summary(self.no, self.year):
            self.update_row()

    def update_row(self):
        summary = Summary(no=self.no, year=self.year, is_first=True, program_id=cfg.current_program_id)
        DatabaseManager.add_row(summary)

    def modify_row(self):
        pass
