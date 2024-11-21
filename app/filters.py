from typing import Optional
from datetime import datetime
from fastapi_filter.contrib.sqlalchemy import Filter

from models import Receipt


class ReceiptFilter(Filter):
    total__gt: Optional[float] = None
    total__lt: Optional[float] = None
    type: Optional[str] = None
    created_at__gt: Optional[datetime] = None
    created_at__lt: Optional[datetime] = None

    class Constants(Filter.Constants):
        model = Receipt