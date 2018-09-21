import pytest
from documentManager.DocumentCreator import DocumentCreator
from os import path
from documentManager.DatabaseManager import DatabaseManager
from models import Contract

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


def test_get_all_school_withContract_is25():
    assert(len(DatabaseManager.get_all_schools_with_contract("1")) == 25)


def test_get_all_schools_is26():
    assert(len(DatabaseManager.get_all_schools()) == 26)

def test_properlly_obtained_next_annex_id():
    assert(DatabaseManager.get_next_annex_no(1, 1) == 1)
    assert(DatabaseManager.get_next_annex_no(2, 1) == 2)