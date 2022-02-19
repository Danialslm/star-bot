from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship, backref

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    chat_id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f'<User chat_id={self.chat_id} full_name={self.full_name}>'


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    admin_name = Column(String, nullable=False)
    user_chat_id = Column(Integer, ForeignKey('users.chat_id'))
    user = relationship('User', backref=backref('admin', uselist=False))

    def __repr__(self):
        return f'<Admin id={self.id} user={self.user}>'


class Group(Base):
    __tablename__ = 'groups'

    chat_id = Column(Integer, primary_key=True)
    payer_chat_id = Column(Integer, ForeignKey('users.chat_id'), nullable=False)
    payer = relationship('User', backref=backref('group', uselist=False))

    def __repr__(self):
        return f'<Group chat_id={self.chat_id} payer={self.payer}>'


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
