from rykomanager import app, config_parser

from mailmerge import MailMerge
from abc import ABC, abstractmethod
import subprocess
import win32api
from shutil import copy
from os import path, makedirs, remove, rename


class DocumentCreator(ABC):
    wdFormatPDF = 17
    pdf_converter = path.normpath(config_parser.get('Common', 'libreoffice_converter_path'))

    def __init__(self, template_document, output_directory):
        if not path.exists(template_document):
            app.logger.error("[%s] template document: %s does not exists", __class__.__name__, template_document)
        self.document = DocumentCreator.start_doc_gen(template_document, output_directory)
        self.fields_to_merge = self.document.get_merge_fields()

        if config_parser.get('Common', 'debug_on'):
            app.logger.info("[%s] merge fields: %s", __class__.__name__, self.fields_to_merge)

        self.template_document = template_document
        self.output_directory = output_directory
        super(DocumentCreator, self).__init__()

    @abstractmethod
    def generate(self, new_doc_name, gen_pdf=True): #@TODO fix this method for generating pdfs
        generated_file = path.join(self.output_directory, new_doc_name)

        res = DocumentCreator.end_doc_gen(self.document, generated_file, self.output_directory, gen_pdf) #TODO: pdf are not genereting correctly for 5
        if res:
            return generated_file
        # elif res:
        #     DocumentCreator.print_pdf(generated_file)
        #     return generated_file
        return None #@TODO create exception here and return the ProperException

    @staticmethod
    def copy_to_path(source, dest):
        old_file_name = path.basename(source)
        new_file_name = path.basename(dest)
        new_dst = path.dirname(dest)
        if not path.exists(new_dst):
            makedirs(new_dst)
        if source:
            if path.exists(path.join(dest)):
                remove(path.join(dest))
            copy(source, new_dst)
            rename(path.join(new_dst, old_file_name), path.join(new_dst, new_file_name))

    def generate_many(self):
        pass

    def generate_rows(self):
        pass

    @staticmethod
    def generate_pdf(docx_to_convert, output_dir):
        try:
            docx_to_convert = path.normpath(docx_to_convert)
            output_dir = path.normpath(output_dir)
            app.logger.info(f"Generate pdf for {docx_to_convert} using {DocumentCreator.pdf_converter} save in {output_dir}")
            args = [DocumentCreator.pdf_converter, '--headless', '--convert-to', 'pdf', '--outdir', output_dir, docx_to_convert]
            subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=3000)
        except Exception as e:
            app.logger.error("[%s] Serious error when generating pdf from docx %s out_dir %s: err_msg: %s. Check libreoffice converter path: %s",
                                   __class__.__name__, docx_to_convert, output_dir , e, DocumentCreator.pdf_converter,)

    @staticmethod
    def print_pdf(filename):
        pass
        #win32api.ShellExecute(0, 'open', 'gsprint.exe',
        #                      '-printer "\\\\' + self.server + '\\' + self.printer_name + '" ' + file, '.', 0)

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
    def end_doc_gen(document, generated_file, output_dir, gen_pdf=True):
        document.write(generated_file)
        app.logger.info("[%s] Created new output directory: %s", __class__.__name__, generated_file, )
        if gen_pdf:
            DocumentCreator.generate_pdf(generated_file, output_dir)
        return True

    @abstractmethod
    def create(self):
        pass
