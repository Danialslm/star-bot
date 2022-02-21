from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    group = Column(String, nullable=False)

    def __repr__(self):
        return f'<Admin id={self.id} chat_id={self.chat_id} name={self.name}>'


class SoldUc(Base):
    __tablename__ = 'sold_ucs'

    id = Column(Integer, primary_key=True)
    admin_chat_id = Column(Integer, nullable=False)
    uc_amount = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)


class UC(Base):
    __tablename__ = 'ucs'

    id = Column(Integer, primary_key=True)
    amount = Column(Integer, unique=True, nullable=False)
    price = Column(Integer, nullable=False)

    def __repr__(self):
        return f'<UC id={self.id} amount={self.amount} price={self.price}>'
