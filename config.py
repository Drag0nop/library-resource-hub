import os

MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'kn@g@rk0ti')
MYSQL_DB = os.getenv('MYSQL_DB', 'library_db')
SECRET_KEY = os.getenv('SECRET_KEY', 'change_this_to_a_secret')
