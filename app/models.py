from bcrypt import checkpw
from sqlalchemy import Column, Integer, String, Enum, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from database import Base, engine, get_db


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    login = Column(String, unique=True)
    password = Column(String)
    receipts = relationship('Receipt', back_populates='user')

    def check_passwd(self, passwd):
        return checkpw(bytes(passwd, 'utf-8'), bytes(self.password, 'utf-8'))


class Receipt(Base):
    __tablename__ = 'receipts'

    id = Column(Integer, primary_key=True)
    type = Column(Enum('cash', 'cashless', name='payment_type'), nullable=False)
    amount = Column(Float, nullable=False)
    total = Column(Float)
    products = relationship('Product', back_populates='receipt')
    created_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='receipts')
    rest = Column(Float)

    def to_dict(self):
        return {
            'id': self.id,
            'products': [product.to_dict() for product in self.products],
            'payment': {
                'type': self.type,
                'amount': self.amount
            },
            'total': self.total,
            'rest': self.rest,
            'created_at': self.created_at.isoformat(),
        }


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer)
    receipt_id = Column(Integer, ForeignKey('receipts.id'))
    receipt = relationship('Receipt', back_populates='products')
    total = Column(Float)

    def to_dict(self):
        return {
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'total': self.total,
        }


Base.metadata.create_all(bind=engine)
