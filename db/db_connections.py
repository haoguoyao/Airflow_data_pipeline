import mysql.connector
import sys,os

# print(os.path.abspath(os.path.join('.')))
# root_path = os.path.abspath(os.path.join('.'))
# if root_path not in sys.path:
#     sys.path.append(root_path)
# sys.path.append(".")
import db.db_settings as db_settings

# Database configuration (update this with your database credentials)
db_config = {
    'user': db_settings.user,
    'password': db_settings.password,
    'host': db_settings.host,
    'database': 'coco',
    'raise_on_warnings': True,
    'pool_name': 'mypool',
    'pool_size': 2
}
cnx_pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)

# Function to get a connection from the pool
def get_db_connection():
    return cnx_pool.get_connection()
