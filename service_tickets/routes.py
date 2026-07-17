from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import request, jsonify
from models import db, ServiceTicket, Mechanic
from service_tickets.schemas import service_ticket_schema, service_tickets_schema
from service_tickets.bp import service_tickets_bp
from sqlalchemy import select

@service_tickets_bp.route('/', methods=['POST'])
def create_ticket():
    try:
        # 1. Load and validate data
        data = service_ticket_schema.load(request.json)
        
        # 2. Create and save to database
        new_ticket = ServiceTicket(**data)
        db.session.add(new_ticket)
        db.session.commit()
        
        return jsonify(service_ticket_schema.dump(new_ticket)), 201

    except Exception as e:
        # This will now catch database errors too!
        db.session.rollback() # Important: undo changes if error occurs
        details = str(getattr(e, "orig", e))
        if "UNIQUE constraint failed" in details:
            return jsonify({"error": "Service ticket could not be created", "details": details}), 409
        return jsonify({"error": str(e)}), 500



# GET '/': Retrieves all service tickets
@service_tickets_bp.route('/', methods=['GET'])
def get_tickets():
    query = select(ServiceTicket)
    tickets = db.session.execute(query).scalars().all()
    return jsonify(service_tickets_schema.dump(tickets)), 200

# PUT '/<ticket_id>/assign-mechanic/<mechanic_id>': Adds a relationship
@service_tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket:
        return jsonify({"error": "Service Ticket not found"}), 404
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    # Using relationship attributes to treat the relationship like a list
    if mechanic not in ticket.mechanics:
        ticket.mechanics.append(mechanic)
        db.session.commit()
        return jsonify({"message": f"Mechanic {mechanic_id} assigned to ticket {ticket_id}"}), 200
    else:
        return jsonify({"message": "Mechanic already assigned to this ticket"}), 200

# PUT '/<ticket_id>/remove-mechanic/<mechanic_id>': Removes the relationship
@service_tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket:
        return jsonify({"error": "Service Ticket not found"}), 404
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    if mechanic in ticket.mechanics:
        ticket.mechanics.remove(mechanic)
        db.session.commit()
        return jsonify({"message": f"Mechanic {mechanic_id} removed from ticket {ticket_id}"}), 200
    else:
        return jsonify({"error": "Mechanic not assigned to this ticket"}), 400