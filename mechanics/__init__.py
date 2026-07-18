import os
from pathlib import Path
import sys
from flask import Flask, Blueprint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models import db


def _load_env_file() -> None:
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if not os.path.exists(env_path):
        return

    with open(env_path, 'r', encoding='utf-8') as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue

            key, value = line.split('=', 1)
            # Make the repository .env authoritative so stale shell or editor
            # variables do not keep old database credentials alive.
            os.environ[key.strip()] = value.strip().strip('"').strip("'")


_load_env_file()


def _read_env_file_values() -> dict[str, str]:
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if not os.path.exists(env_path):
        return {}

    values: dict[str, str] = {}
    with open(env_path, 'r', encoding='utf-8') as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue

            key, value = line.split('=', 1)
            values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def _normalized_env_value(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None

    normalized = value.strip()
    if not normalized:
        return None

    placeholder_values = {'your_password', 'your_new_password', 'change_me'}
    if normalized.lower() in placeholder_values:
        return None

    return normalized


def _build_database_uri() -> str:
    # Prefer a full SQLAlchemy URL when provided.
    env_file_values = _read_env_file_values()

    database_url = env_file_values.get('DATABASE_URL') or _normalized_env_value('DATABASE_URL')
    if database_url:
        return database_url

    mysql_values = {
        'user': env_file_values.get('MYSQL_USER') or _normalized_env_value('MYSQL_USER'),
        'password': env_file_values.get('MYSQL_PASSWORD') or _normalized_env_value('MYSQL_PASSWORD'),
        'host': env_file_values.get('MYSQL_HOST') or _normalized_env_value('MYSQL_HOST'),
        'port': env_file_values.get('MYSQL_PORT') or _normalized_env_value('MYSQL_PORT'),
        'db': env_file_values.get('MYSQL_DB') or _normalized_env_value('MYSQL_DB'),
    }

    has_complete_mysql_config = all(
        mysql_values[name]
        for name in ('user', 'password', 'host', 'port', 'db')
    )

    if not has_complete_mysql_config:
        return 'sqlite:///garage.db'

    return (
        f"mysql+mysqlconnector://{mysql_values['user'] or 'root'}:{mysql_values['password'] or ''}"
        f"@{mysql_values['host'] or 'localhost'}:{mysql_values['port'] or '3306'}/{mysql_values['db'] or 'mechanic_library_db'}"
    )

def create_app():
    app = Flask(__name__)

    # Active DB config uses MySQL via env vars (or DATABASE_URL).
    app.config['SQLALCHEMY_DATABASE_URI'] = _build_database_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database and marshmallow with the app
    db.init_app(app)
    db.app = app  # Associate the db with the Flask app

    # Import and register Blueprints
    from mechanics.routes import mechanics_bp
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')

    from service_tickets.routes import service_tickets_bp
    app.register_blueprint(service_tickets_bp, url_prefix='/service-tickets')

    from customers.routes import customers_bp
    app.register_blueprint(customers_bp, url_prefix='/customers')

    # Create the database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app

mechanics_bp = Blueprint('mechanics_bp', __name__)

try:
    from . import routes
except ImportError:
    import routes

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
