from mailmerge import MailMerge
from abc import ABC, abstractmethod
from os import path, makedirs
import setup
import configuration as cfg
import subprocess


class DocumentCreator(ABC):

    def __init__(self, template_document, output_directory):
        if not path.exists(template_document):
            setup.app.logger.error("[%s] template document: %s does not exists", __class__.__name__, template_document)
        self.document = MailMerge(template_document)
        self.fields_to_merge = self.document.get_merge_fields()
        setup.app.logger.info("[%s] merge fields: %s", __class__.__name__, self.fields_to_merge)
        DocumentCreator.create_directory(output_directory)

        self.template_document = template_document
        self.output_directory = output_directory
        super(DocumentCreator, self).__init__()

    @abstractmethod
    def generate(self, new_doc_name):
        generated_file = path.join(self.output_directory, new_doc_name)
        self.document.write(generated_file)
        DocumentCreator.generate_pdf(generated_file, self.output_directory)

    def generate_many(self):
        pass

    def generate_rows(self):
        pass

    @staticmethod
    def generate_pdf(docx_to_convert, output_dir):
        try:
            args = [cfg.libreoffice_converter, '--headless', '--convert-to', 'pdf', '--outdir', output_dir, docx_to_convert]
            subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=3000)
        except Exception as e:
            setup.app.logger.error("[%s] Serious error when generating pdf from docx %s out_dir %s: err_msg: %s",
                                   __class__.__name__, output_dir, docx_to_convert, e)

    @staticmethod
    def create_directory(output_directory):
        if not path.exists(output_directory):
            makedirs(output_directory)
            setup.app.logger.info("[%s] Created new output directory: %s", __class__.__name__, output_directory)

    @abstractmethod
    def create(self):
        pass
