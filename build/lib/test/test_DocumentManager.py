import pytest
from documentManager.DocumentCreator import DocumentCreator
from documentManager.RecordCreator import RecordCreator
from os import path
from documentManager.DatabaseManager import DatabaseManager
from models import Contract, ProductName
import configuration as cfg


class DB(object):
    pass


@pytest.fixture(scope="session")
def db():
    assert 0, db


def test_pdf_is_properly_created():
    DocumentCreator.generate_pdf('C:\\ryko-manager\\test\\helper_files\\aneks_test.docx', 'C:\\ryko-manager\\test\\helper_files')
    assert(path.exists('C:\\ryko-manager\\test\\helper_files\\aneks_test.pdf'))

#@TODO add some failure case for generation


def test_get_current_contract_value_for_school_id_3():
    contract = DatabaseManager.get_current_contract(3, 1)
    assert (isinstance(contract, Contract))
    assert (contract.dairy_products == 99 and contract.fruitVeg_products == 99)
    assert (contract.self.school.id == 3)


def test_get_all_school_withContract_is25():
    assert(len(DatabaseManager.get_all_schools_with_contract("1")) == 25)


def test_get_all_schools_is26():
    assert(len(DatabaseManager.get_all_schools()) == 26)


def test_properlly_obtained_next_annex_id():
    assert(DatabaseManager.get_next_annex_no(1, 1) == 1)
    assert(DatabaseManager.get_next_annex_no(2, 1) == 2)
    assert (DatabaseManager.get_next_annex_no(26, 1) == 2)


def test_extract_school_id():
    assert(RecordCreator.extract_school_id("records_schoolId_4") == 4)
    assert(RecordCreator.extract_school_id("records_schoolId_234") == 234)


# def test_record_creator():
#     rc = RecordCreator(1, '2018-09-17', 1, 1)
#     rc.create()
#     assert(rc._get_kids_no() == 400)
#     rc_m = RecordCreator(1, '2018-09-17', 1, 10)
#     rc_m.create()
#     assert(rc_m._get_kids_no() == 422)
#     assert (path.exists("C:\\ryko-manager\\kowr_doc\\program_2018_2019_sem1\\szkoly\\SP 22\\WZ\\WZ_2018-09-17_jabłko.docx"))


def test_get_product():
    assert(DatabaseManager.get_product(1, 1).name == ProductName.APPLE)


# def test_generate_many_record():
#     rc = RecordCreator(1, '2018-09-17', 1, 1)
#     rc2 = RecordCreator(1, '2018-09-17', 1, 10)
#     rc3 = RecordCreator(1, '2018-09-17', 2, 2)
#     rc4 = RecordCreator(1, '2018-09-17', 2, 11)
#     rc.create()
#     rc2.create()
#     rc3.create()
#     rc4.create()
#     RecordCreator.generate_many('2018-09-17', [rc, rc2, rc3, rc4])
#     assert (path.exists("C:\\ryko-manager\\kowr_doc\\program_2018_2019_sem1\\WZ\\2018-09-17.docx"))
#
# def test_get_week_by_date():
    assert(DatabaseManager.get_week_by_date('2018-09-17').week_no == 1)
    assert (DatabaseManager.get_week_by_date('2018-09-26').week_no == 2)
    assert (DatabaseManager.get_week_by_date('2018-10-19').week_no == 5)
    assert (not DatabaseManager.get_week_by_date('2019-10-19'))


def test_get_weekly_product():
    schools_with_contract = DatabaseManager.get_all_schools_with_contract(session.get('program_id'))
    assert(DatabaseManager.get_product_no(schools_with_contract[0].contracts[0].id, week_no=1) == 0)