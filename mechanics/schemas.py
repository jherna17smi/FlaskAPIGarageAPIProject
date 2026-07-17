from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models import Mechanic
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema  # pyright: ignore[reportMissingImports]

class MechanicSchema(SQLAlchemyAutoSchema):
    id = fields.Int(dump_only=True)

    class Meta:
        model = Mechanic
        # Routes instantiate models manually, so deserialize into dicts.
        load_instance = False

# Create instances for single and multiple mechanic serialization
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
