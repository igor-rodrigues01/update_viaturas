#!-*-coding:utf-8-*-
import psycopg2
import sys
from utils import Utils


class DAO:

    conn = None
    __cursor = None

    def __init__(self, host, db, user, passwd):
        self.conn = self.connection(host, db, user, passwd)
        self.__cursor = self.conn.cursor()

    def connection(self, host, db, user, passwd):
        """
        Function that make the connection in postgres
        """
        try:
            return psycopg2.connect(
                host=host, database=db, user=user, password=passwd
            )
        except Exception as ex:
            sys.exit('Falha na conexão {}'.format(ex))

    def insert_veiculos_all(self, sql):
        self.__cursor.execute(sql)

    def insert_in_veiculos_and_veiculos_hist(self, record, schema, table, filename):
        fields_and_values = Utils.data_prepare_to_veiculos(filename, record)
        fields = fields_and_values[0]
        values = fields_and_values[1]
        values = (
            values[1], values[0], values[2], values[3], values[4], values[5]
        )
        sql = Utils.create_sql(schema=schema, table_name=table)
        fields_and_data = fields + values
        sql_with_value = sql % fields_and_data
        self.__cursor.execute(sql_with_value)

    def close(cls):
        """
        Function that close the connection
        """
        cls.conn.close()
