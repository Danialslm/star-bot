from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship, backref

Base = declarative_base()


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)

    def __repr__(self):
        return f'<Admin id={self.id} chat_id={self.chat_id} name={self.name}>'


class Group(Base):
    __tablename__ = 'groups'

    chat_id = Column(Integer, primary_key=True)
    payer_id = Column(Integer, ForeignKey('admins.id'), nullable=False)
    payer = relationship('Admin', backref=backref('group', uselist=False))

    def __repr__(self):
        return f'<Group chat_id={self.chat_id} payer_id={self.payer_id}>'


CheckoutUc = Table(
    'checkout_uc',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('checkout_id', Integer, ForeignKey('checkouts.id'), nullable=False),
    Column('uc_id', Integer, ForeignKey('ucs.id'), nullable=False),
)


class UC(Base):
    __tablename__ = 'ucs'

    id = Column(Integer, primary_key=True)
    amount = Column(Integer, unique=True, nullable=False)
    price = Column(Integer, nullable=False)

    def __repr__(self):
        return f'<UC id={self.id} amount={self.amount} price={self.price}>'


class Checkout(Base):
    __tablename__ = 'checkouts'

    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey('admins.id'), nullable=False)
    admin = relationship('Admin', backref=backref('checkout', uselist=False))
    ucs = relationship('UC', secondary=CheckoutUc, backref='checkout')
