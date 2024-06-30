import sqlite3


class DBHelper:

    def __init__(self, dbname="stats.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS registry (user text, counter integer)"
        self.conn.execute(tblstmt)
        self.conn.commit()

    def add_user(self, user):
        stmt = "INSERT INTO registry (user, counter) VALUES (?, ?)"
        args = (user, 0)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def update_counter(self, user):
        stmt = f"UPDATE registry SET counter=counter+1 WHERE user = '{user}'"
        self.conn.execute(stmt)
        self.conn.commit()

    def get_counter(self, user):
        stmt = f"SELECT counter FROM registry WHERE user='{user}'" 
        res = [x[0] for x in self.conn.execute(stmt)]
        if len(res) == 0:
            return 0
        else:
            return res[0]