import pandas as pd, os
from sqlalchemy import create_engine
from dotenv import load_dotenv
import pymysql
import getpass

if __name__=="__main__":
    db_root_user=input("DB root user: ")
    db_root_pw=getpass.getpass("pw: ")

    load_dotenv()

        # Connect to MariaDB
    conn = pymysql.connect(
        host='localhost',
        user=db_root_user,
        password=db_root_pw,
        #database='your_database'
    )

    # Add User
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('MYSQL_BA_DB')};")
    
    # Add DB
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE USER IF NOT EXISTS '{os.getenv('MYSQL_BA_USER')}'@'%' IDENTIFIED BY '{os.getenv('MYSQL_BA_PW')}'")

    # Grant permissions
    with conn.cursor() as cursor:
        cursor.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {os.getenv('MYSQL_BA_DB')}.* TO '{os.getenv('MYSQL_BA_USER')}'@'%'")
    
    conn.close()
    
