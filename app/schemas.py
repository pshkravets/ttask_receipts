from pydantic import BaseModel
from typing import List
from datetime import datetime


class PaymentSchema(BaseModel):
    type: str
    amount: float

    class Config:
        orm_mode = True

class ProductBaseSchema(BaseModel):
    name: str
    price: float
    quantity: int

    class Config:
        orm_mode = True

class ProductCreateSchema(ProductBaseSchema):
    pass


class ProductSchema(ProductBaseSchema):
    id: int
    total: float



class ReceiptBaseSchema(BaseModel):
    products: List[ProductCreateSchema]
    # payment: PaymentSchema

    class Config:
        orm_mode = True


class ReceiptCreateSchema(ReceiptBaseSchema):
    payment: PaymentSchema


class ReceiptSchema(ReceiptBaseSchema):
    id: int
    products: List[ProductSchema]
    total: float
    rest: float
    created_at: datetime
    type: str
    amount: float


class PersonalReceipts(BaseModel):
    receipts: List[ReceiptSchema]