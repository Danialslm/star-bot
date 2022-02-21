from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    group = Column(String, nullable=False)
    sold_ucs = relationship('UC', secondary='sold_ucs', backref='admin', cascade='all,delete')

    def __repr__(self):
        return f'<Admin id={self.id} chat_id={self.chat_id} name={self.name}>'


class SoldUc(Base):
    __tablename__ = 'sold_ucs'

    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey('admins.id'), nullable=False)
    uc_id = Column(Integer, ForeignKey('ucs.id'), nullable=False)
    quantity = Column(Integer, default=0)


class UC(Base):
    __tablename__ = 'ucs'

    id = Column(Integer, primary_key=True)
    amount = Column(Integer, unique=True, nullable=False)
    price = Column(Integer, nullable=False)

    def __repr__(self):
        return f'<UC id={self.id} amount={self.amount} price={self.price}>'
