from documentManager import DocumentCreator
from documentManager import DatabaseManager
import configuration as cfg


class AnnexCreator(DocumentCreator, DatabaseManager):
    template_document = cfg.annex_docx
    output_dir = cfg.annex_ouput_dir

    def __init__(self):
        super.__init__(AnnexCreator.template_document, AnnexCreator.output_dir)

    def create(self):
        pass

