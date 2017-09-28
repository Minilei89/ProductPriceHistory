from mssql_db import MSSQL_Database
from scrape_microcenter import ScrapeMicrocenter
from gc import collect
class Price_History(MSSQL_Database):
    def __init__(self, server, user,password, database, autocommit=True):
        temp = MSSQL_Database(server=server, user=user, password=password,
                            database='tempdb', autocommit=autocommit)
        temp.create_db(database)
        temp.close_conn()
        MSSQL_Database.__init__(self, server=server, user=user,
                                password=password, database=database,
                                autocommit=autocommit)

    def insert_table(self, table_name, **kwargs):
        Sku = kwargs["Sku"]
        with self._conn.cursor() as cursor:
            command = """
            SELECT TOP(1) ProductPrice
            FROM {table_name}
            WHERE Sku = '{Sku}'
            ORDER BY Time Desc
            """.format(table_name=table_name,Sku=Sku)
            cursor.execute(command)
            price = cursor.fetchone()
        if not price or (str(price[0]) != kwargs['ProductPrice'] and price):
            if kwargs['ProductPrice'] != 'NULL':
                MSSQL_Database.insert_table(self, table_name, **kwargs)
