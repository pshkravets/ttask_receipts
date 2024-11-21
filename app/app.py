from fastapi import FastAPI, APIRouter, Depends, status, HTTPException, Query
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi_filter import FilterDepends
from fastapi_pagination import add_pagination

from models import get_db, User, Receipt, Product
from utils import hash_password, create_access_token, require_auth
from html import receipt_to_html
from schemas import ReceiptCreateSchema
from filters import ReceiptFilter

app = FastAPI(debug=True)

add_pagination(app)

router = APIRouter()


@router.post('/registration/')
def registration(username: str, login: str, password: str, db: Session = Depends(get_db)):
    """
    :param username: required
    :param login: required, unique
    :param password: required

    :return:
        - '200 OK': user's login
        - '400 Bad Request': If user's login alredy exist's
    """
    if db.query(User).filter_by(login=login).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with this login already exists'
        )
    user = User(
        username=username,
        login=login,
        password=hash_password(password)
    )
    db.add(user)
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={'login': user.login}
    )


@router.get('/authorize/')
def authorize(login, password, db: Session = Depends(get_db)):
    """
    :param login: required, unique
    :param password: required

    :return:
        - '200 OK': access toke (JWT)
        - '400 Bad Request': wrong credentials
    """

    user = db.query(User).filter_by(login=login).first()
    if user and user.check_passwd(password):
        access_token = create_access_token(data={"sub": user.login})
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'token': access_token}
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Your login or password is incorrect'
    )


@router.post('/receipt/')
def create_receipt(receipt: ReceiptCreateSchema, user=Depends(require_auth), db: Session=Depends(get_db)):
    """
    :param user: JWT, required

    :return:
        - '200 OK': JSON information about receipt
    """
    products = []
    total = 0
    db_receipt = Receipt(
        type=receipt.payment.type,
        amount=receipt.payment.amount,
        created_at=datetime.now(),
        user_id=user.id
    )
    db.add(db_receipt)
    db.commit()
    db.refresh(db_receipt)
    for product in receipt.products:
        db_product = Product(
            name=product.name,
            price=product.price,
            quantity=product.quantity,
            receipt_id=db_receipt.id,
            total=product.price*product.quantity
        )
        products.append({
            'name': product.name,
            'price': product.price,
            'quantity': product.quantity,
            'total': product.price * product.quantity
        })
        db.add(db_product)
        total += product.price * product.quantity
    db_receipt.total = total
    db_receipt.rest = db_receipt.amount - total
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=db_receipt.to_dict()
    )


@router.get('/my_receipts/')
def receipts_list(
        user=Depends(require_auth),
        db: Session=Depends(get_db),
        filters: ReceiptFilter = FilterDepends(ReceiptFilter),
        limit: int = Query(100, ge=0),
        offset: int = Query(0, ge=0)
):
    """
    :param user: JWT, required
    :param filters:
        - total__gt: return all receipts which total cost is greater then total__gt, not required
        - total__lt: return all receipts which total cost is less then total__lt, not required
        - type: returns specified type of payment (cash, cashless), not required
        - created_at__gt: returns all receipts which were created after created_at__gt, not required
        - created_at__lt: returns all receipts which were created before created_at__lt, not required
    :param limit: set's pagination for receipts, not required
    :param offset: set's offset, not required

    :return:
        - '200 OK': return user's receipts
    """
    response = []
    query = filters.filter(db.query(Receipt).filter(Receipt.user_id==user.id)).limit(limit).offset(offset)

    for receipt in query:
        response.append(receipt.to_dict())

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response
        )


@router.get('/my_receipts/{receipt_id}')
def get_receipt(receipt_id, user=Depends(require_auth), db: Session=Depends(get_db)):
    """
    :param receipt_id: unique receipt's id, required
    :param user: JWT, required

    :return: specify receipts by it's id
    """
    receipt = db.query(Receipt).filter_by(id=receipt_id).first()
    if receipt:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=receipt.to_dict()
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Receipt with this id doesn\'t exist'
    )


@router.get('/receipt_text/{receipt_id}', response_class=HTMLResponse)
def get_receipt(receipt_id, chars_per_line=32, db: Session=Depends(get_db)):
    """
    :param receipt_id: unique receipt's id, required
    :param chars_per_line: amount of chars per line, not required

    :return: text of receipt
    """
    receipt = db.query(Receipt).filter_by(id=receipt_id).first()
    if receipt:
        content = receipt_to_html(receipt, int(chars_per_line))
        return content
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Receipt with this id doesn\'t exist'
    )


app.include_router(router)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)