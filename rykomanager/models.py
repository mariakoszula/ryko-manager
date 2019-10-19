from rykomanager import db
import enum
from rykomanager.DateConverter import  DateConverter
from typing import List
class ProductType(enum.Enum):
    NONE = 0
    FRUIT_VEG = 1
    DAIRY = 2


class ProductName(enum.Enum):
    APPLE = 1
    PEAR = 2
    STRAWBERRY = 3
    PLUM = 4
    JUICE = 5

    CARROT = 11
    RADISH = 12
    PEPPER = 13
    TOMATO = 14
    KOHLRABI = 15

    MILK = 21
    YOGHURT = 22
    KEFIR = 23
    CHEESE = 24


fruit_veg_mapping = {  ProductName.APPLE: "jabłko",
                       ProductName.PEAR: "gruszka",
                       ProductName.PLUM: "śliwka",
                       ProductName.STRAWBERRY: "truskawka",
                       ProductName.JUICE: "sok owocowy",
                       ProductName.CARROT: "marchew",
                       ProductName.RADISH: "rzodkiewka",
                       ProductName.PEPPER: "papryka",
                       ProductName.TOMATO: "pomidor",
                       ProductName.KOHLRABI: "kalarepa" }

dairy_mapping = {   ProductName.CHEESE: "ser twarogowy",
                    ProductName.KEFIR: "kefir",
                    ProductName.YOGHURT: "jogurt",
                    ProductName.MILK: "mleko" }


class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nick = db.Column(db.String(60), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), unique=True, nullable=False)
    city = db.Column(db.String(30), unique=True, nullable=False)
    nip = db.Column(db.String(80))
    regon = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    phone = db.Column(db.String(80), unique=True, nullable=False)
    responsible_person = db.Column(db.String(60), nullable=False)
    representative = db.Column(db.String(120))
    representative_nip = db.Column(db.String(80))
    representative_regon = db.Column(db.String(80))
    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return '<School: %r>' % self.name


class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    semester_no = db.Column(db.Integer, nullable=False)
    school_year = db.Column(db.String(20), nullable=False)
    fruitVeg_price = db.Column(db.Float)
    dairy_price = db.Column(db.Float)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    dairy_min_per_week = db.Column(db.Integer)
    fruitVeg_min_per_week = db.Column(db.Integer)
    dairy_amount = db.Column(db.Integer)
    fruitVeg_amount = db.Column(db.Integer)
    db.UniqueConstraint('school_year', 'semester_no')
    __table_args__ = {'extend_existing': True, }

    def convert_start_date_to_string(self):
        return DateConverter.to_string(self.start_date)

    def convert_start_end_to_string(self):
        return DateConverter.to_string(self.end_date)

    def contract_no(self):
        cno = 0
        for contract in self.contracts:
            if not contract.is_annex:
                cno = cno + 1
        return cno

    def contract_date(self):
        if self.contracts:
            return DateConverter.to_string(self.contracts[0].contract_date)
        else:
            return "rrrr-mm-dd"

    def get_current_semester(self):
        if self.semester_no == 1:
            return "I"
        elif self.semester_no == 2:
            return "II"
        return "INVALID"

    @staticmethod
    def get_products_types():
        return [(ProductType.FRUIT_VEG, "owocowo-warzywny"), (ProductType.DAIRY, "nabiał")]

    @staticmethod
    def get_products_names(product_type):
        if int(product_type) == ProductType.FRUIT_VEG.value:
            return fruit_veg_mapping
        if int(product_type) == ProductType.DAIRY.value:
            return dairy_mapping
        return {}


class Contract(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    contract_no = db.Column(db.String(80), nullable=False)
    contract_year = db.Column(db.Integer, nullable=False)
    contract_date = db.Column(db.DateTime, nullable=False)
    validity_date = db.Column(db.DateTime, nullable=False)
    fruitVeg_products = db.Column(db.Integer, nullable=False)
    dairy_products = db.Column(db.Integer, nullable=False)
    is_annex = db.Column(db.Boolean, nullable=False, default=0)

    school_id = db.Column(db.Integer,  db.ForeignKey('school.id'), nullable=False)
    school = db.relationship('School', backref=db.backref('contracts', lazy=True, order_by='Contract.validity_date.desc()'))
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    program = db.relationship('Program', backref=db.backref('contracts', lazy=True))

    def update(self, contract_date, validity_date=None, fruitVeg_products=None, dairy_products=None):
        self.contract_date = DateConverter.to_date(contract_date)
        if validity_date:
            self.validity_date = validity_date
        if fruitVeg_products:
            self.fruitVeg_products = fruitVeg_products
        if dairy_products:
            self.dairy_products = dairy_products
        db.session.commit()

    def convert_date_to_string(self):
        return DateConverter.to_string(self.contract_date)

    def convert_validity_date_to_string(self):
        return DateConverter.to_string(self.validity_date)

    __table_args__ = (
        db.UniqueConstraint('validity_date', 'school_id'),
        )


class Week(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week_no = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    program = db.relationship('Program', backref=db.backref('weeks', lazy=True))

    def convert_start_date_to_string(self):
        return DateConverter.to_string(self.start_date)

    def convert_start_end_to_string(self):
        return DateConverter.to_string(self.end_date)

    db.UniqueConstraint('week_no', 'program_id')
    __table_args__ = {'extend_existing': True}


class Product(db.Model):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(ProductName), nullable=False)
    type = db.Column(db.Enum(ProductType), nullable=False)
    min_amount = db.Column(db.Integer, nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    program = db.relationship('Program', backref=db.backref('products', lazy=True))

    #@TODO remove language dependency
    def get_name_mapping(self):
        name = fruit_veg_mapping.get(self.name, None)
        if name:
            return name
        else:
            name = dairy_mapping.get(self.name, "")
        return name

    def get_record_title_mapping(self):
        if self.type == ProductType.DAIRY:
            return "Mleko i przetwory mleczne"
        if self.type == ProductType.FRUIT_VEG:
            return "Warzywa i owoce "

    def get_type_mapping(self):
        if self.type == ProductType.DAIRY:
            return "nb"
        if self.type == ProductType.FRUIT_VEG:
            return "wo"

    def is_dairy(self):
        return self.type == ProductType.DAIRY

    def is_fruit_veg(self):
        return self.type == ProductType.FRUIT_VEG

class RecordState(enum.Enum):
    NOT_DELIVERED = 1
    DELIVERED = 2


class Record(db.Model):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    generation_date = db.Column(db.DateTime)
    state = db.Column(db.Enum(RecordState), nullable=False, default=RecordState.NOT_DELIVERED)

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product',
                             backref=db.backref('records', lazy=True))

    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=False)
    contract = db.relationship('Contract',
                             backref=db.backref('records', lazy=True, order_by='Contract.validity_date.desc()',
                             cascade="all, delete-orphan"))

    week_id = db.Column(db.Integer, db.ForeignKey('week.id'), nullable=False)
    week = db.relationship('Week',
                             backref=db.backref('records', lazy=True))


    def __str__(self):
        return f"Week no {self.week.week_no} school {self.contract.school.nick} productType {self.product.type}"

    __table_args__ = (
        db.UniqueConstraint('date', 'product_id', 'contract_id'),
        )

    def set_to_delivered(self):
        self.state = RecordState.DELIVERED
        db.session.commit()

    def update_product(self, product_id):
        self.product_id = product_id
        db.session.commit()

    def is_dairy(self):
        return self.product.type == ProductType.DAIRY

    def is_fruitVeg(self):
        return self.product.type == ProductType.FRUIT_VEG


class ProductHandler:
    def __init__(self, amount: int = 0, vat: int = 0, prize: float = 0):
        self.amount = amount
        self.vat = vat
        self.prize = prize

    def calculate_netto(self):
        return round(self.amount * self.prize, 2)

    def calculate_vat(self):
        return round((self.calculate_netto() * self.vat)/100, 2)

    def calculate_brutto(self):
         return round(self.calculate_netto() + self.calculate_vat(),2)


class Summary(db.Model):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    no = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    kids_no = db.Column(db.Integer, default=0)
    school_no = db.Column(db.Integer, default=0)
    apple = db.Column(db.Integer, default=0)
    pear = db.Column(db.Integer, default=0)
    plum = db.Column(db.Integer, default=0)
    strawberry = db.Column(db.Integer, default=0)
    juice = db.Column(db.Integer, default=0)
    carrot = db.Column(db.Integer, default=0)
    radish = db.Column(db.Integer, default=0)
    pepper = db.Column(db.Integer, default=0)
    tomato = db.Column(db.Integer, default=0)
    kohlrabi = db.Column(db.Integer, default=0)
    school_no_milk = db.Column(db.Integer, default=0)
    kids_no_milk = db.Column(db.Integer, default=0)
    milk = db.Column(db.Integer, default=0)
    yoghurt = db.Column(db.Integer, default=0)
    kefir = db.Column(db.Integer, default=0)
    cheese = db.Column(db.Integer, default=0)
    fruitVeg_income = db.Column(db.Float, default=0)
    milk_income = db.Column(db.Float, default=0)
    is_first = db.Column(db.Boolean, nullable=False)

    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    program = db.relationship('Program',
                             backref=db.backref('summary', lazy=True))

    def __fruit_list(self):
        return [ProductHandler(self.apple, 5, float(self.program.fruitVeg_price)), ProductHandler(self.plum, 5, float(self.program.fruitVeg_price)),
                ProductHandler(self.pear, 5, float(self.program.fruitVeg_price)),  ProductHandler(self.strawberry, 5, float(self.program.fruitVeg_price)),
                ProductHandler(self.juice, 5, float(self.program.fruitVeg_price)), ProductHandler(self.carrot, 8, float(self.program.fruitVeg_price)),
                ProductHandler(self.tomato, 5, float(self.program.fruitVeg_price)), ProductHandler(self.radish, 8, float(self.program.fruitVeg_price)),
                ProductHandler(self.kohlrabi, 8, float(self.program.fruitVeg_price)), ProductHandler(self.pepper, 8, float(self.program.fruitVeg_price))]

    def __dairy_list(self):
        return [ProductHandler(self.milk, 5, float(self.program.dairy_price)), ProductHandler(self.yoghurt, 5, float(self.program.dairy_price)),
                ProductHandler(self.kefir, 5, float(self.program.dairy_price)), ProductHandler(self.cheese, 5, float(self.program.dairy_price))]

    def get_from_fruit_list(self, product: ProductName):
        if product == ProductName.APPLE:
            return self.__fruit_list()[0]
        if product == ProductName.PLUM:
            return self.__fruit_list()[1]
        if product == ProductName.PEAR:
            return self.__fruit_list()[2]
        if product == ProductName.STRAWBERRY:
            return self.__fruit_list()[3]
        if product == ProductName.JUICE:
            return self.__fruit_list()[4]
        if product == ProductName.CARROT:
            return self.__fruit_list()[5]
        if product == ProductName.TOMATO:
            return self.__fruit_list()[6]
        if product == ProductName.RADISH:
            return self.__fruit_list()[7]
        if product == ProductName.KOHLRABI:
            return self.__fruit_list()[8]
        if product == ProductName.PEPPER:
            return self.__fruit_list()[9]

    def get_from_diary_list(self, product: ProductName):
        if product == ProductName.MILK:
            return self.__fruit_list()[0]
        if product == ProductName.YOGHURT:
            return self.__fruit_list()[1]
        if product == ProductName.KEFIR:
            return self.__fruit_list()[2]
        if product == ProductName.CHEESE:
            return self.__fruit_list()[3]

    @staticmethod
    def calculate_income(products_list: List[ProductHandler]):
        return sum([product.calculate_brutto() for product in products_list])

    @staticmethod
    def calculate_netto(products_list: List[ProductHandler]):
        return sum([product.calculate_netto() for product in products_list])

    @staticmethod
    def calculate_vat(products_list: List[ProductHandler]):
        return sum([product.calculate_vat() for product in products_list])

    def get_fruit_vat(self):
        return Summary.calculate_vat(self.__fruit_list())

    def get_fruit_netto(self):
        return Summary.calculate_netto(self.__fruit_list())

    def get_fruit_veg_income(self):
        return self.calculate_income(self.__fruit_list())

    def get_dairy_vat(self):
        return Summary.calculate_vat(self.__dairy_list())

    def get_dairy_netto(self):
        return Summary.calculate_netto(self.__dairy_list())

    def get_dairy_income(self):
        return self.calculate_income(self.__dairy_list())

    def __str__(self):
        return f"[{self.id}]Summary {self.get_application_no()} program {self.program_id}"

    def get_application_no(self):
        return "{0}/{1}/{2}".format(self.program.semester_no, self.no, self.program.school_year)

    __table_args__ = (
                        db.UniqueConstraint('no', 'year', 'program_id'),)


class Application(db.Model):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    apple = db.Column(db.Integer, default=0)
    pear = db.Column(db.Integer, default=0)
    plum = db.Column(db.Integer, default=0)
    strawberry = db.Column(db.Integer, default=0)
    carrot = db.Column(db.Integer, default=0)
    radish = db.Column(db.Integer, default=0)
    pepper = db.Column(db.Integer, default=0)
    tomato = db.Column(db.Integer, default=0)
    kohlrabi = db.Column(db.Integer, default=0)
    milk = db.Column(db.Integer, default=0)
    yoghurt = db.Column(db.Integer, default=0)
    kefir = db.Column(db.Integer, default=0)
    cheese = db.Column(db.Integer, default=0)
    fruit_all = db.Column(db.Integer, default=0)
    veg_all = db.Column(db.Integer, default=0)
    dairy_all = db.Column(db.Integer, default=0)
    max_kids_perWeeks_fruitVeg = db.Column(db.Integer, default=0)
    max_kids_perWeeks_milk = db.Column(db.Integer, default=0)
    juice = db.Column(db.Integer, default=0)

    summary_id = db.Column(db.Integer,  db.ForeignKey('summary.id'), nullable=False)
    summary = db.relationship('Summary', backref=db.backref('application', lazy=True, order_by='Contract.validity_date.desc()'))

    school_id = db.Column(db.Integer,  db.ForeignKey('school.id'), nullable=False)
    school = db.relationship('School', backref=db.backref('application', lazy=True, order_by='Contract.validity_date.desc()'))

    __table_args__ = (
                        db.UniqueConstraint('summary_id', 'school_id'),)


db.create_all()