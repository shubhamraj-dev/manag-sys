import sqlite3
from datetime import datetime


class Schema:
    def __init__(self):
        self.conn = sqlite3.connect('pms.db')
        self.create_user_table()
        self.create_leaves_table()
        self.create_user_details_table()
        self.create_working_data()

    def create_user_table(self):

        query = """
        CREATE TABLE IF NOT EXISTS "User" (
          id INTEGER PRIMARY KEY,
          name TEXT,
          email TEXT,
          password TEXT,
          type INTEGER
          );
          """
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()
        cursor.close()

    def create_leaves_table(self):
        query = """
                CREATE TABLE IF NOT EXISTS "leaves" (
                  email TEXT,
                  date DATE,
                  type INTEGER
                  );
                  """
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()
        cursor.close()

    def create_user_details_table(self):
        query = """
                        CREATE TABLE IF NOT EXISTS "user_details" (
                          email TEXT PRIMARY KEY,
                          name TEXT,
                          salary_per_hr INTEGER,
                          joining_date DATE,
                          job_title TEXT,
                          pay_in_overtime INTEGER,
                          max_casual_leaves INTEGER,
                          max_sick_leaves INTEGER
                          );
                          """
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()
        cursor.close()

    def create_working_data(self):
        query = """
                CREATE TABLE IF NOT EXISTS "working_data" (
                  email TEXT,
                  year TEXT,
                  month TEXT,
                  sick_leaves INTEGER,
                  casual_leaves INTEGER,
                  working_hours INTEGER
                  );
                  """
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()
        cursor.close()


class TableUser:

    def __init__(self):
        self.conn = sqlite3.connect("pms.db")

    def create(self, name, email, password, type):
        query = """
        insert into User (name,email,password,type) values(?, ?, ?,?)
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (name, email, password, type))
        self.conn.commit()
        query = """
                insert into working_data (email,year,month,sick_leaves,casual_leaves,working_hours) values(?, ?, ?,?,? , ? )
                """
        bun = datetime.now()
        cursor.execute(query, (email, bun.year, bun.month, 0, 0, 0))
        self.conn.commit()
        print("Record inserted successfully into SqliteDb_developers table ", cursor.rowcount)
        cursor.close()
        return True

    def reads(self, email):
        query = "select * from User where email = (?)"
        cursor = self.conn.cursor()
        cursor.execute(query, (email,))
        records = cursor.fetchone()
        # print(records)
        # print(records[0], records[1])
        cursor.close()
        return records
