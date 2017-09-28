import pymssql
from scrape_microcenter import ScrapeMicrocenter
from time import time

class MSSQL_Database:
    def __init__(self, server, user, password, database, autocommit=True):
        self._server = server
        self._user = user
        self._password = password
        self._database = database
        self._autocommit = autocommit
        self._conn = pymssql.connect(server=server, port=1433, user=user,
                                     password=password, database=database,
                                     autocommit=autocommit)
        self._tablecol = {}

    def mssql_dec(func):
        def execute(self, *args, **kwargs):
            with self._conn.cursor() as cursor:
                command = func(self, *args, **kwargs)
                cursor.execute(command)
                print(command)
        return execute

    def time_dec(func):
        def wrapper(self, *args, **kwargs):
            init_t = time()
            ret = func(self, *args, **kwargs)
            final_t = time()
            print(func, args, kwargs, final_t-init_t)
            return ret
        return wrapper

    @time_dec
    @mssql_dec
    def create_db(self, db_name):
        command = """
        IF NOT EXISTS(SELECT * FROM master.dbo.sysdatabases WHERE NAME = '{db_name}')
            BEGIN
                CREATE DATABASE [{db_name}]
            END;""".format(db_name=db_name)
        return command

    @time_dec
    @mssql_dec
    def create_table(self, table_name, **kwargs):
        self._tablecol = kwargs
        command ="""
    IF OBJECT_ID('{name}', 'U') IS NULL
        CREATE TABLE {name} (
            ID int IDENTITY(1,1) PRIMARY KEY,\n""".format(name=table_name)
        if kwargs is not None:
            for col, col_type in kwargs.items():
                if col_type.upper() == 'VARCHAR':
                    command += "\t\t{col} {col_type}(255),\n".format(
                        col=col, col_type=col_type)
                else:
                    command += "\t\t{col} {col_type},\n".format(
                    col=col, col_type=col_type)
        command += "\t\t);"
        return command

    @time_dec
    @mssql_dec
    def insert_table(self, table_name, **kwargs):
        assert kwargs is not None,"Product not passed. Check to see argument is passed"
        command = "INSERT INTO {table_name} (".format(table_name=table_name)
        for col_name in kwargs:
            command += "{}, ".format(col_name)
        command = command[0:-2]
        command += ")\nVALUES ("
        for col_name in kwargs:
            kwargs[col_name] = kwargs[col_name].replace("\'", "\'\'")
            if self._tablecol[col_name] in ('varchar', 'datetime'):
                command += "'{}', ".format(kwargs[col_name])
            else:
                command += "{}, ".format(kwargs[col_name])
        command = command[0:-2]
        command += ");"
        print(command)
        return command

    @time_dec
    def get_tablecol(self):
        return self._tablecol

    @time_dec
    def commit_command(self):
        self._conn.commit()

    @time_dec
    def close_conn(self):
        self._conn.close()
