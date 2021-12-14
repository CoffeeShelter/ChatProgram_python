import pandas as pd
import pymysql
from pymysql.err import MySQLError

class DBManager:
    def __init__(self):
        self.conn = None
        self.curs = None

    # DB 연결
    def connect(self, user, password, host):
        try:
            conn = pymysql.connect(
                host=host,
                user=user,
                password=password,
                charset="utf8mb4"
            )
            self.conn = conn
            self.curs = conn.cursor(pymysql.cursors.DictCursor)

            self.createDB("CHATTING")

            return conn
        
        except MySQLError as e:
            _, msg = e.args
            print("[DB ERROR] : {}".format(msg))
            return None

    # 상품, 건강기능식품, 인증마크 테이블 생성 (테이블이 이미 만들어져 있을 시 생성하지 않음)
    def createDB(self, dbName):
        sql = "CREATE DATABASE IF NOT EXISTS {}".format(dbName)
        self.curs.execute(sql)
        self.conn.select_db(dbName)

        sql = "CREATE TABLE IF NOT EXISTS USER_ \
            ( \
                ID VARCHAR(200) NOT NULL, \
                PWD VARCHAR(200) NOT NULL, \
                NAME_ VARCHAR(300) NOT NULL, \
                EMAIL VARCHAR(20) NOT NULL, \
                DATE_ DATETIME DEFAULT CURRENT_TIMESTAMP, \
                PRIMARY KEY(ID) \
            )"
        self.curs.execute(sql)

    def search_by_id(self, id):
        sql = "SELECT * FROM USER_ WHERE ID=%s"
        self.curs.execute(sql, id)
        return self.curs