from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema  # pyright: ignore[reportMissingImports]
from models import Customer


class CustomerSchema(SQLAlchemyAutoSchema):
    id = fields.Int(dump_only=True)

    class Meta:
        model = Customer
        load_instance = False


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
