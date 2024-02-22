import mysql.connector
import sys,os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import db.db_settings as db_settings

# Database configuration (update this with your database credentials)
db_config = {
    'user': db_settings.user,
    'password': db_settings.password,
    'host': db_settings.host,
    'database': db_settings.dbname,
    'raise_on_warnings': True,
    'pool_name': 'mypool',
    'pool_size': 2
}
cnx_pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)

# Function to get a connection from the pool
def get_db_connection():
    return cnx_pool.get_connection()

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
