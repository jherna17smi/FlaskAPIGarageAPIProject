from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models import ServiceTicket
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema  # pyright: ignore[reportMissingImports]

class ServiceTicketSchema(SQLAlchemyAutoSchema):
    id = fields.Int(dump_only=True)

    class Meta:
        model = ServiceTicket
        # include_fk = True ensures that foreign keys are included in the JSON
        include_fk = True
        # Routes instantiate models manually, so deserialize into dicts.
        load_instance = False

# Create instances for single and multiple ticket serialization
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
