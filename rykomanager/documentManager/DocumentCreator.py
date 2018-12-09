from rykomanager import app
import rykomanager.configuration as cfg

from mailmerge import MailMerge
from abc import ABC, abstractmethod
from os import path, makedirs
import subprocess


class DocumentCreator(ABC):

    def __init__(self, template_document, output_directory):
        if not path.exists(template_document):
            app.logger.error("[%s] template document: %s does not exists", __class__.__name__, template_document)
        self.document = DocumentCreator.start_doc_gen(template_document, output_directory)
        self.fields_to_merge = self.document.get_merge_fields()
        if cfg.devDebug:
            app.logger.info("[%s] merge fields: %s", __class__.__name__, self.fields_to_merge)

        self.template_document = template_document
        self.output_directory = output_directory
        super(DocumentCreator, self).__init__()

    @abstractmethod
    def generate(self, new_doc_name, gen_pdf=True):
        generated_file = path.join(self.output_directory, new_doc_name)

        res = DocumentCreator.end_doc_gen(self.document, generated_file, self.output_directory) #TODO: pdf are not genereting correctly for 5
        if gen_pdf and res:
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
            app.logger.error("[%s] Serious error when generating pdf from docx %s out_dir %s: err_msg: %s. Check libreoffice converter path: %s",
                                   __class__.__name__, docx_to_convert, output_dir , e, cfg.libreoffice_converter)

    @staticmethod
    def create_directory(output_directory):
        if not path.exists(output_directory):
            makedirs(output_directory)
            app.logger.info("[%s] Created new output directory: %s", __class__.__name__, output_directory)

    @staticmethod
    def start_doc_gen(doc_template, output_dir):
        DocumentCreator.create_directory(output_dir)
        return MailMerge(doc_template)

    @staticmethod
    def end_doc_gen(document, generated_file, output_dir):
        document.write(generated_file)
        app.logger.info("[%s] Created new output directory: %s", __class__.__name__, generated_file, )
        return True

    @abstractmethod
    def create(self):
        pass
