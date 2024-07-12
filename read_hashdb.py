import pandas as pd, os
from sqlalchemy import create_engine, select, Table, MetaData
from dotenv import load_dotenv
import pymysql
from fastapi import FastAPI, HTTPException
import uvicorn
from contextlib import asynccontextmanager
from pydantic import BaseModel
from passlib.hash import bcrypt
from datetime import datetime

app = FastAPI()

class ba(BaseModel):
    user: str
    pw: str

load_dotenv()
db_user = os.getenv('MYSQL_BA_USER')
db_pw = os.getenv('MYSQL_BA_PW')
db = os.getenv('MYSQL_BA_DB')
db_table_main = os.getenv('MYSQL_BA_TABLE_MAIN')
db_host= os.getenv('MYSQL_HOST')
engine = create_engine(f'mysql+pymysql://{db_user}:{db_pw}@127.0.0.1:3306/{db}')


def df_readdb(engine,query):
    df=pd.read_sql_query(query,engine)
    return df

def db2dict(table):
    try:
        conn = pymysql.connect(host=db_host,user=db_user,password=db_pw,database=db)
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT * FROM {table}')
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            result = []
            for row in rows:
                row_dict = {}
                for idx, col in enumerate(columns):
                    row_dict[col] = row[idx]
                result.append(row_dict)
        return result
    except Exception as e:
        return f"Error {e}"
    finally:
        conn.close()
    
def insertdb2user(data):
    try:
        conn = pymysql.connect(host=db_host,user=db_user,password=db_pw,database=db)
        with conn.cursor() as cursor:
            affected_rows=cursor.execute(f'INSERT INTO {db_table_main} (create_time, user, hash, mod_time) VALUES (%s,%s,%s,%s)', data )
        conn.commit()
        return affected_rows
    except Exception as e:
        return f"Error {e}"
    finally:
        conn.close()

def delfromdb(table,con):
    try:
        conn = pymysql.connect(host=db_host,user=db_user,password=db_pw,database=db)
        with conn.cursor() as cursor:
            affected_rows=cursor.execute(f'DELETE FROM {table} WHERE {con}')
        conn.commit()
        return affected_rows
    except Exception as e:
        return f"Error {e}"
    finally:
        conn.close()

@app.get('/api/v1/getuser')
async def getuserv1():
    query=f"SELECT * from {db_table_main}"
    df=pd.read_sql_query(query,engine)
    return df.to_dict()

@app.post('/api/v1/setuser')
async def setuserv1(ba: ba):
    rowlist=db2dict(db_table_main)
    if isinstance(rowlist, str):
        return rowlist
    for row in rowlist:
        if ba.user==row["user"]:
            return "Error: User already used"
    bcrypt_hash = bcrypt.hash(ba.pw) #generate hash from pw
    data=(datetime.now(), ba.user, bcrypt_hash, datetime.now())#setup data for insert
    aff_rows=insertdb2user(data)
    if isinstance(aff_rows, str) or aff_rows<1:
        return aff_rows
    return f"User: {ba.user} added"

@app.post('/api/v1/deluser')
async def setuserv1(ba: ba):
    rowlist=db2dict(db_table_main)
    if isinstance(rowlist, str):
        return rowlist
    id=None
    for row in rowlist:
        if ba.user==row["user"]:
            id=row["id"]
            break
    if not id:
        return "Error: User not found"
    con = f"id= {id}"
    aff_rows=delfromdb(db_table_main,con)
    if isinstance(aff_rows, str) or aff_rows<1:
        return aff_rows
    return f"User: {ba.user} deleted"

if __name__=="__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
