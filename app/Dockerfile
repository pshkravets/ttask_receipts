FROM python

WORKDIR /app/receipts

COPY . .

RUN apt-get update\
    && pip install -r requirements.txt

RUN python app.py