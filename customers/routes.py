from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import request, jsonify
from sqlalchemy import select

from api_helpers import validation_error_response, commit_session
from customers.bp import customers_bp
from customers.schemas import customer_schema, customers_schema
from models import db, Customer


@customers_bp.route('/', methods=['POST'])
def create_customer():
    try:
        data = customer_schema.load(request.json)
    except Exception as error:
        return validation_error_response(error)

    customer = Customer(**data)
    db.session.add(customer)

    commit_error = commit_session(db, "Customer could not be created")
    if commit_error:
        return commit_error

    return jsonify(customer_schema.dump(customer)), 201


@customers_bp.route('/', methods=['GET'])
def list_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()
    return jsonify(customers_schema.dump(customers)), 200


@customers_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify(customer_schema.dump(customer)), 200


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    try:
        data = customer_schema.load(request.json, partial=True)
    except Exception as error:
        return validation_error_response(error)

    for key, value in data.items():
        setattr(customer, key, value)

    commit_error = commit_session(db, "Customer could not be updated")
    if commit_error:
        return commit_error

    return jsonify(customer_schema.dump(customer)), 200


@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    db.session.delete(customer)

    commit_error = commit_session(db, "Customer could not be deleted")
    if commit_error:
        return commit_error

    return jsonify({"message": f"Customer {customer_id} deleted successfully"}), 200
