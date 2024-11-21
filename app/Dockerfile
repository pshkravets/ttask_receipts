FROM python

WORKDIR /app/receipts

COPY . .

RUN apt-get update\
    && pip install -r requirements.txt

ENV DB_HOST="db"
ENV POSTGRES_DB="receipt"
ENV POSTGRES_USER="user"
ENV POSTGRES_PASSWORD="qwe123"

CMD ["python", "app.py"]
