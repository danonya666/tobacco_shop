import psycopg2
import secret
def isint(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
class PgDal:
    def __init__(self):
        self.conn = psycopg2.connect(dbname='tobacco', user='postgres',
                                     password=secret.password, host='localhost', port=8090)
        self.cursor = self.conn.cursor()
        self.conn.autocommit = True

    def select_logins(self):
        self.cursor.execute('SELECT * FROM login')
        return self.list_cursor()

    def print_all(self):
        for row in self.cursor:
            print(row)

    def list_cursor(self):
        result = []
        for row in self.cursor:
            result.append(row)
        return result

    def all_shipments(self):
        self.cursor.execute('SELECT * FROM shipment')
        return self.list_cursor()

    def subj_name_from_key(self, key):
        self.cursor.execute(f'Select "name" from subject where key = {key}')
        return self.list_cursor()

    def logistic_name_from_key(self, key):
        self.cursor.execute(f'Select "name" from logistics where key = {key}')
        return self.list_cursor()

    def product_key_from_name(self, name):
        print(f"select key from product where name = '{name}'")
        self.cursor.execute(f"select key from product where name = '{name}'")
        print(self.cursor)
        return self.list_cursor()

    def logistics_key_from_name(self, name):
        self.cursor.execute(f"select key from logistics where name = '{name}'")
        print('qq1')
        return self.list_cursor()

    def subject_key_from_name(self, name):
        self.cursor.execute(f"select key from subject where name = '{name}'")
        print('qq2')
        return self.list_cursor()

    def add_shipment(self, am, pr, log, subj):
        if pr != [] and log != [] and subj != [] and isint(am):
            self.cursor.execute(f"insert into shipment (amount, product_key, logistics_key, subject_key) values ({am}, '{pr[0][0]}', '{log[0][0]}', '{subj[0][0]}')")
            return 1
        else:
            return -1


if __name__ == '__main__':
    pg = PgDal()
    pg.select_logins()
