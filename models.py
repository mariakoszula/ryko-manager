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

    def __init__(self, name):
        self.name = name

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

    def __init__(self):
        pass


class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_no = db.Column(db.Integer, nullable=False)
    contract_year = db.Column(db.Integer, nullable=False)
    contract_date = db.Column(db.DateTime, nullable=False)
    validity_date = db.Column(db.DateTime, nullable=False)
    fruitVeg_products = db.Column(db.Integer, nullable=False)
    dairy_products = db.Column(db.Integer, nullable=False)
    is_annex = db.Column(db.Boolean, nullable=False, default=0)

    school_id = db.Column(db.Integer,  db.ForeignKey('school.id'), nullable=False)
    school = db.relationship('School', backref=db.backref('contracts', lazy=True))
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    program = db.relationship('Program', backref=db.backref('contracts', lazy=True))

    db.UniqueConstraint('contract_no', 'contract_year')
    __table_args__ = {'extend_existing': True}

    def __init__(self):
        pass


db.create_all()