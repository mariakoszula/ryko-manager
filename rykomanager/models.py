from rykomanager import db
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

    db.UniqueConstraint('week_no', 'program_id')
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
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(ProductName), nullable=False)
    type = db.Column(db.Enum(ProductType), nullable=False)
    min_amount = db.Column(db.Integer, nullable=False)

    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    program = db.relationship('Program', backref=db.backref('week', lazy=True))

    #@TODO remove language dependency
    def get_name_mapping(self):
        if self.name == ProductName.APPLE:
            return "jabłko"
        if self.name == ProductName.PEAR:
            return "gruszka"
        if self.name == ProductName.PLUM:
            return "śliwka"
        if self.name == ProductName.STRAWBERRY:
            return "truskawka"
        if self.name == ProductName.CARROT:
            return "marchew"
        if self.name == ProductName.RADISH:
            return "rzodkiewka"
        if self.name == ProductName.PEPPER:
            return "papryka"
        if self.name == ProductName.TOMATO:
            return "pomidor"
        if self.name == ProductName.KOHLRABI:
            return "kalarepa"
        if self.name == ProductName.MILK:
            return "mleko"
        if self.name == ProductName.YOGHURT:
            return "jogurt"
        if self.name == ProductName.KEFIR:
            return "kefir"
        if self.name == ProductName.CHEESE:
            return "ser twarogowy"

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


class RecordState(enum.Enum):
    NOT_DELIVERED = 1
    DELIVERED = 2


class Record(db.Model):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
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


db.create_all()