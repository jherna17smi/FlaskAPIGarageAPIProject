from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if __name__ == '__main__':
    from mechanics import create_app

    app = create_app()
    app.run(debug=True)
    raise SystemExit

from flask import request, jsonify
from models import db, Mechanic
from sqlalchemy import select

try:
    from .schemas import mechanic_schema, mechanics_schema
    from . import mechanics_bp
except ImportError:
    from schemas import mechanic_schema, mechanics_schema
    from __main__ import mechanics_bp


def validation_error_response(error):
    return jsonify(getattr(error, "messages", {"error": str(error)})), 400

# POST '/' : Creates a new Mechanic
@mechanics_bp.route('/', methods=['POST'])
def create_mechanic():
    try:
        # Deserialize and validate incoming JSON data
        data = mechanic_schema.load(request.json)
    except Exception as e:
        return validation_error_response(e)

    new_mechanic = Mechanic(**data)
    db.session.add(new_mechanic)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        details = str(getattr(e, "orig", e))
        if "UNIQUE constraint failed" in details:
            return jsonify({"error": "Mechanic could not be created", "details": details}), 409
        return jsonify({"error": "Mechanic could not be created", "details": details}), 500
    return jsonify(mechanic_schema.dump(new_mechanic)), 201

# GET '/': Retrieves all Mechanics
@mechanics_bp.route('/', methods=['GET'])
def get_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    return jsonify(mechanics_schema.dump(mechanics)), 200

# PUT '/<int:id>': Updates a specific Mechanic based on the id
@mechanics_bp.route('/<int:id>', methods=['PUT'])
def update_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    try:
        # Use partial=True to allow updating only specific fields
        data = mechanic_schema.load(request.json, partial=True)
    except Exception as e:
        return validation_error_response(e)

    for key, value in data.items():
        setattr(mechanic, key, value)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        details = str(getattr(e, "orig", e))
        if "UNIQUE constraint failed" in details:
            return jsonify({"error": "Mechanic could not be updated", "details": details}), 409
        return jsonify({"error": "Mechanic could not be updated", "details": details}), 500
    return jsonify(mechanic_schema.dump(mechanic))

# DELETE '/<int:id>': Deletes a specific Mechanic based on the id
@mechanics_bp.route('/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Mechanic {id} deleted successfully"}), 200
