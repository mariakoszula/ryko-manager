from mailmerge import MailMerge
from abc import ABC, abstractmethod


class DocumentCreator(ABC):

    def __init__(self, template_document, output_directory):
        self.template_document = template_document;
        self.output_directory = output_directory
        super().__init__()

    def generate(self):
        pass

    def generate_many(self):
        pass

    def generate_rows(self):
        pass

    def __validate_no_of_params(self):
        pass

    @staticmethod
    def generate_pdf(self, dox_to_convert):
        pass

    @abstractmethod
    def create(self):
        pass