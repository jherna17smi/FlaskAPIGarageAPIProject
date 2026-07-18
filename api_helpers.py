from flask import jsonify


def validation_error_response(error):
    return jsonify(getattr(error, "messages", {"error": str(error)})), 400


def commit_session(db, default_error_message: str):
    try:
        db.session.commit()
        return None
    except Exception as error:
        db.session.rollback()
        details = str(getattr(error, "orig", error))
        if "UNIQUE constraint failed" in details or "Duplicate entry" in details:
            return jsonify({"error": default_error_message, "details": details}), 409
        return jsonify({"error": default_error_message, "details": details}), 500
