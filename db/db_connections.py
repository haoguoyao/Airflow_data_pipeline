
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import db.db_settings as db_settings



def get_db_engine():
    # Connect to your MySQL database
    # Format: mysql+mysqlconnector://<user>:<password>@<host>/<dbname>
    engine = create_engine('mysql+mysqlconnector://{}:{}@{}/{}'.format(db_settings.user,db_settings.password,db_settings.host,db_settings.dbname))
    return engine
def get_db_session():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
