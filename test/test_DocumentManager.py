import pytest
from rykomanager.documentManager.DocumentCreator import DocumentCreator
from rykomanager.documentManager.RecordCreator import RecordCreator
from os import path
from rykomanager.documentManager.DatabaseManager import DatabaseManager
from rykomanager.models import Contract, ProductName, ProductType
from rykomanager.documentManager.ApplicationCreator import Fruit, Veg, Dairy, CommonData, FruitVegSummary, \
    DairySummary, ApplicationCreator


class DB(object):
    pass


@pytest.fixture(scope="session")
def db():
    assert 0, db


def test_pdf_is_properly_created():
    DocumentCreator.generate_pdf('helper_files\\aneks_test.docx', 'helper_files')
    assert (path.exists('helper_files\\aneks_test.pdf'))


def test_get_current_contract_value_for_school_id_3():
    contract = DatabaseManager.get_current_contract(3, 1)
    assert (isinstance(contract, Contract))
    assert (contract.dairy_products == 99 and contract.fruitVeg_products == 99)
    assert (contract.school.id == 3)


def test_get_all_school_withContract_is25():
    assert (len(DatabaseManager.get_all_schools_with_contract("1")) == 25)


def test_get_all_schools_is26():
    assert (len(DatabaseManager.get_all_schools()) == 29)


def test_properlly_obtained_next_annex_id():
    assert (DatabaseManager.get_next_annex_no(1, 1) == 1)
    assert (DatabaseManager.get_next_annex_no(2, 1) == 2)
    assert (DatabaseManager.get_next_annex_no(26, 1) == 2)


def test_extract_school_id():
    assert (RecordCreator.extract_school_id("records_schoolId_4") == 4)
    assert (RecordCreator.extract_school_id("records_schoolId_234") == 234)


def test_get_product():
    assert (DatabaseManager.get_product(1).name == ProductName.APPLE)


# def test_record_creator():
#     rc = RecordCreator(1, '2018-09-17', 1, 1)
#     rc.create()
#     assert(rc._get_kids_no() == 400)
#     rc_m = RecordCreator(1, '2018-09-17', 1, 10)
#     rc_m.create()
#     assert(rc_m._get_kids_no() == 422)
#     assert (path.exists("C:\\ryko-manager\\kowr_doc\\program_2018_2019_sem1\\szkoly\\SP 22\\WZ\\WZ_2018-09-17_jabłko.docx"))


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
#     assert(DatabaseManager.get_week_by_date('2018-09-17').week_no == 1)
#     assert (DatabaseManager.get_week_by_date('2018-09-26').week_no == 2)
#     assert (DatabaseManager.get_week_by_date('2018-10-19').week_no == 5)
#     assert (not DatabaseManager.get_week_by_date('2019-10-19'))
#
#
# def test_get_weekly_product():
#     schools_with_contract = DatabaseManager.get_all_schools_with_contract(session.get('program_id'))
#     assert(DatabaseManager.get_product_no(schools_with_contract[0].contracts[0].id, week_no=1) == 0)

def prepare_fruit_data(program_id, school, weeks):
    apple = DatabaseManager.get_product_amount(program_id, school, ProductName.APPLE, weeks)
    pear = DatabaseManager.get_product_amount(program_id, school, ProductName.PEAR, weeks)
    plum = DatabaseManager.get_product_amount(program_id, school, ProductName.PLUM, weeks)
    strawberry = DatabaseManager.get_product_amount(program_id, school, ProductName.STRAWBERRY, weeks)
    juice = DatabaseManager.get_product_amount(program_id, school, ProductName.JUICE, weeks)
    fruit_all = apple + pear + plum + strawberry + juice
    max_kids_perWeeks_fruitVeg = DatabaseManager.get_maxKids_perWeek(program_id, school, ProductType.FRUIT_VEG, weeks)
    return (fruit_all, max_kids_perWeeks_fruitVeg, dict([(ProductName.APPLE, apple), (ProductName.PEAR, pear),
                                                         (ProductName.STRAWBERRY, strawberry), (ProductName.PLUM, plum),
                                                         (ProductName.JUICE, juice)]))


def prepare_veg_data(program_id, school, weeks):
    carrot = DatabaseManager.get_product_amount(program_id, school, ProductName.CARROT, weeks)
    radish = DatabaseManager.get_product_amount(program_id, school, ProductName.RADISH, weeks)
    pepper = DatabaseManager.get_product_amount(program_id, school, ProductName.PEPPER, weeks)
    tomato = DatabaseManager.get_product_amount(program_id, school, ProductName.TOMATO, weeks)
    kohlrabi = DatabaseManager.get_product_amount(program_id, school, ProductName.KOHLRABI, weeks)
    veg_all = carrot + radish + pepper + tomato + kohlrabi
    max_kids_perWeeks_fruitVeg = DatabaseManager.get_maxKids_perWeek(program_id, school, ProductType.FRUIT_VEG, weeks)
    return (veg_all, max_kids_perWeeks_fruitVeg, dict([(ProductName.CARROT, carrot), (ProductName.RADISH, radish),
                                                       (ProductName.PEPPER, pepper), (ProductName.TOMATO, tomato),
                                                       (ProductName.KOHLRABI, kohlrabi)]))


def prepare_dairy_data(program_id, school, weeks):
    milk = DatabaseManager.get_product_amount(program_id, school, ProductName.MILK, weeks)
    yoghurt = DatabaseManager.get_product_amount(program_id, school, ProductName.YOGHURT, weeks)
    kefir = DatabaseManager.get_product_amount(program_id, school, ProductName.KEFIR, weeks)
    cheese = DatabaseManager.get_product_amount(program_id, school, ProductName.CHEESE, weeks)
    dairy_all = milk + yoghurt + kefir + cheese
    max_kids_perWeeks_milk = DatabaseManager.get_maxKids_perWeek(program_id, school, ProductType.DAIRY, weeks)
    return (dairy_all, max_kids_perWeeks_milk, dict([(ProductName.MILK, milk), (ProductName.YOGHURT, yoghurt),
                                                     (ProductName.KEFIR, kefir), (ProductName.CHEESE, cheese)]))


def prepare_weeks(program_id):
    data_to_merge = dict()
    data_to_merge['week_date_1'] = DatabaseManager.get_dates(program_id, 1)
    data_to_merge['week_date_2'] = DatabaseManager.get_dates(program_id, 2)
    data_to_merge['week_date_3'] = DatabaseManager.get_dates(program_id, 4)
    data_to_merge['week_date_4'] = DatabaseManager.get_dates(program_id, 13)
    data_to_merge['week_date_5'] = None
    data_to_merge['week_date_6'] = None
    data_to_merge['week_date_7'] = None
    data_to_merge['week_date_8'] = None
    data_to_merge['week_date_9'] = None
    data_to_merge['week_date_10'] = None
    data_to_merge['week_date_11'] = None
    data_to_merge['week_date_12'] = None
    return data_to_merge


def test_product_info():
    program_id = 1
    school_ids = [i for i in range(2, len(DatabaseManager.get_all_schools_with_contract(program_id)))]
    weeks = set([1, 2, 3, 4, 5, 6, 13])
    assert (DatabaseManager.get_program(program_id).school_year == '2018/2019')
    assert (DatabaseManager.get_program(program_id).semester_no == 1)
    assert (DatabaseManager.get_product_amount(program_id, school_ids[0], ProductName.MILK, weeks) == 5820)
    assert (DatabaseManager.get_product_amount(program_id, school_ids[0], ProductName.APPLE, weeks) == 582)
    assert (DatabaseManager.get_maxKids_perWeek(program_id, school_ids[0], ProductType.FRUIT_VEG, weeks) == 291)
    assert (DatabaseManager.get_maxKids_perWeek(program_id, school_ids[0], ProductType.DAIRY, weeks) == 291)
    assert ((len(DatabaseManager.get_records(program_id, school_ids[0], ProductType.FRUIT_VEG, weeks))) == 22)

    program_id = 5
    school_id = 1
    assert (DatabaseManager.get_product_amount(program_id, school_id, ProductName.APPLE, weeks) == 765)
    assert (DatabaseManager.get_product_amount(program_id, school_id, ProductName.MILK, weeks) == 1530)
    assert (DatabaseManager.get_maxKids_perWeek(program_id, school_id, ProductType.FRUIT_VEG, weeks) == 400)
    assert (DatabaseManager.get_maxKids_perWeek(program_id, school_id, ProductType.DAIRY, weeks) == 600)

    start_week = 1
    end_week = 12
    assert (DatabaseManager.get_dates(program_id, start_week) == "28.09-04.10\n2020")
    assert (DatabaseManager.get_dates(program_id, end_week) == "12.01-18.01\n2021")
    assert (DatabaseManager.get_maxKids_perWeek(program_id, school_id, ProductType.FRUIT_VEG,
                                                weeks=set([start_week])) == 310)
    assert (DatabaseManager.get_portion_perWeek(program_id, school_id, ProductType.DAIRY, 13) == 2)
    assert (DatabaseManager.get_portion_perWeek(program_id, school_id, ProductType.FRUIT_VEG, 13) == 3)
    assert (DatabaseManager.get_maxKids_perWeek(program_id, school_id, ProductType.FRUIT_VEG,
                                                weeks=set([end_week])) if end_week in weeks else "-" == "-")
    assert (DatabaseManager.get_portion_perWeek(program_id, school_id, ProductType.FRUIT_VEG,
                                                start_week) if start_week in weeks else "-" == 1)
    assert (DatabaseManager.get_portion_perWeek(program_id, school_id, ProductType.DAIRY,
                                                start_week) if start_week in weeks else "-" == 1)

    expected_weeks = prepare_weeks(program_id)
    cpi = CommonData(program_id, school_id, weeks)
    assert (cpi.get_week_numbers() == set([1, 2, 4, 13]))
    assert (cpi.length() == 4)
    cpi.prepare()
    for i in range(1, 13):
        assert (cpi.get()[f"week_date_{i}"] == expected_weeks[f"week_date_{i}"])

    fruits = Fruit(cpi)
    expected_data_fruits = prepare_fruit_data(program_id, school_id, weeks)
    assert (expected_data_fruits[0] == fruits.get_sum())
    assert (expected_data_fruits[2][ProductName.APPLE] == fruits.get_amount(ProductName.APPLE))
    assert (expected_data_fruits[2][ProductName.PEAR] == fruits.get_amount(ProductName.PEAR))
    assert (expected_data_fruits[2][ProductName.STRAWBERRY] == fruits.get_amount(ProductName.STRAWBERRY))
    assert (expected_data_fruits[2][ProductName.PLUM] == fruits.get_amount(ProductName.PLUM))
    assert (expected_data_fruits[2][ProductName.JUICE] == fruits.get_amount(ProductName.JUICE))
    vegs = Veg(cpi)
    expected_data_vegs = prepare_veg_data(program_id, school_id, weeks)
    assert (expected_data_vegs[0] == vegs.get_sum())
    assert (expected_data_vegs[2][ProductName.TOMATO] == vegs.get_amount(ProductName.TOMATO))
    assert (expected_data_vegs[2][ProductName.CARROT] == vegs.get_amount(ProductName.CARROT))
    assert (expected_data_vegs[2][ProductName.RADISH] == vegs.get_amount(ProductName.RADISH))
    assert (expected_data_vegs[2][ProductName.KOHLRABI] == vegs.get_amount(ProductName.KOHLRABI))
    assert (expected_data_vegs[2][ProductName.PEPPER] == vegs.get_amount(ProductName.PEPPER))

    dairy = Dairy(cpi)
    expected_data_dairy = prepare_dairy_data(program_id, school_id, weeks)
    assert (expected_data_dairy[0] == dairy.get_sum())
    assert (expected_data_dairy[2][ProductName.MILK] == dairy.get_amount(ProductName.MILK))
    assert (expected_data_dairy[2][ProductName.YOGHURT] == dairy.get_amount(ProductName.YOGHURT))
    assert (expected_data_dairy[2][ProductName.KEFIR] == dairy.get_amount(ProductName.KEFIR))
    assert (expected_data_dairy[2][ProductName.CHEESE] == dairy.get_amount(ProductName.CHEESE))

    fruit_veg_summary = FruitVegSummary(cpi)
    assert (expected_data_fruits[1] == fruit_veg_summary.get_kids())
    assert (expected_data_vegs[1] == fruit_veg_summary.get_kids())

    dairy_summary = DairySummary(cpi)
    assert (expected_data_dairy[1] == dairy_summary.get_kids())


def test_inconsistent_records():
    assert(len(DatabaseManager.get_any_inconsistent_records_with_annex(5, 1)) == 3)
    assert(len(DatabaseManager.get_any_inconsistent_records_with_annex(5, 2)) == 0)

