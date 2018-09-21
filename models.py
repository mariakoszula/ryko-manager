from setup import db
import enum


class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nick = db.Column(db.String(60), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), unique=True, nullable=False)
    city = db.Column(db.String(30), unique=True, nullable=False)
    nip = db.Column(db.String(80), unique=True)
    regon = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    phone = db.Column(db.String(80), unique=True)
    responsible_person = db.Column(db.String(60), nullable=False)
    representative = db.Column(db.String(120))
    representative_nip = db.Column(db.String(80))
    representative_regon = db.Column(db.String(80))
    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return '<School: %r>' % self.name


class Semester(enum.Enum):
    one = 1
    two = 2


class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    semester_no = db.Column(db.Enum(Semester), nullable=False)
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
    __table_args__ = {'extend_existing': True}


class Contract(db.Model):
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

    __table_args__ = {'extend_existing': True}


class Week(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week_no = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    program = db.relationship('Program', backref=db.backref('weeks', lazy=True))

    __table_args__ = {'extend_existing': True}


class ProductType(enum.Enum):
    FRUIT_VEG = 1
    DAIRY = 2


class ProductName(enum.Enum):
    APPLE = 1
    PEAR = 2
    STRAWBERRY = 3
    PLUM = 4
    END_FRUITS = 10

    CARROT = 11
    RADISH = 12
    PEPPER = 13
    TOMATO = 14
    KOHLRABI = 15
    END_VEG = 20

    MILK = 21
    YOGHURT = 22
    KEFIR = 23
    CHEESE = 24
    END_DIARY = 25


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(ProductName), nullable=False)
    type = db.Column(db.Enum(ProductType), nullable=False)
    min_amount = db.Column(db.Integer, nullable=False)

    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    program = db.relationship('Program', backref=db.backref('week', lazy=True))

    __table_args__ = {'extend_existing': True}


class RecordState(enum.Enum):
    NOT_DELIVERED = 1
    DELIVERED = 2


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    state = db.Column(db.Enum(RecordState), nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product',
                             backref=db.backref('records', lazy=True))

    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=False)
    contract = db.relationship('Contract',
                             backref=db.backref('records', lazy=True, order_by='Contract.validity_date.desc()'))

    __table_args__ = {'extend_existing': True}

db.create_all()