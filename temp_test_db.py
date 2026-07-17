import sys
import traceback

print("--- Running connection checks ---")

try:
    from mechanics import _build_database_uri
    print("Imported mechanics._build_database_uri successfully.")
except Exception as e:
    print("Failed to import mechanics._build_database_uri:")
    traceback.print_exc()
    _build_database_uri = None

try:
    from models import db
    print("Imported models.db successfully.")
except Exception as e:
    print("Failed to import models.db:")
    traceback.print_exc()
    db = None

try:
    from mechanics import create_app
    print("Imported mechanics.create_app successfully.")
except Exception as e:
    print("Failed to import mechanics.create_app:")
    traceback.print_exc()
    create_app = None

try:
    from sqlalchemy import text
    print("Imported sqlalchemy.text successfully.")
except Exception as e:
    print("Failed to import sqlalchemy.text:")
    traceback.print_exc()
    text = None

# Mask URI and attempt connections
uri = None
if _build_database_uri:
    try:
        uri = _build_database_uri()
        import urllib.parse
        try:
            parsed = urllib.parse.urlsplit(uri)
            if parsed.password:
                netloc = parsed.username or ''
                netloc += ':***'
                if parsed.hostname:
                    netloc += '@' + parsed.hostname
                    if parsed.port:
                        netloc += f':{parsed.port}'
                masked_uri = urllib.parse.urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))
            else:
                masked_uri = uri
        except Exception as ex:
            masked_uri = f"Error masking URI: {ex}"
        print(f"Masked URI: {masked_uri}")
    except Exception as e:
        print("Failed to build URI:")
        traceback.print_exc()

if uri:
    try:
        import mysql.connector
        from urllib.parse import urlsplit
        parsed = urlsplit(uri)
        user = parsed.username
        password = parsed.password
        # In connection string like mysql+pymysql://, username/password can be URL-encoded, but mysql.connector might want them decoded or raw
        import urllib.parse
        if user:
            user = urllib.parse.unquote(user)
        if password:
            password = urllib.parse.unquote(password)
        host = parsed.hostname
        port = parsed.port or 3306
        database = parsed.path.lstrip('/')
        
        print(f"Attempting mysql.connector direct connection to {host}:{port}/{database} user={user}...")
        conn = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database,
            connection_timeout=5
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        res = cursor.fetchone()
        print(f"mysql.connector success! result: {res}")
        cursor.close()
        conn.close()
    except Exception as e:
        print("mysql.connector failed:")
        traceback.print_exc()

if create_app and db and text:
    try:
        print("Creating app via create_app()...")
        app = create_app()
        print("App created successfully. Entering app context...")
        with app.app_context():
            print("Executing SQLAlchemy SELECT 1...")
            result = db.session.execute(text("SELECT 1")).scalar()
            print(f"SQLAlchemy context success! result: {result}")
    except Exception as e:
        print("SQLAlchemy app context execution failed:")
        traceback.print_exc()
