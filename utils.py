#!-*-coding:utf-8-*-
import re
from constants import (
    TABLE_VEICULOS_58, TABLE_VEICULOS_HIST_45,
    TABLE_VEICULOS_ALL_45, TABLE_VEICULOS_ALL_58
)


class Utils:

    @classmethod
    def __create_str_with_space(cls, space_quantity):
        """
        Funcao que cria uma string com espacos para serem preechidos.
        Esta funcao sera usada na formatacao da string que recebera o
        sql para a insercao e ela necessaria devido a variacao de dados
        retornados do webservice.
        """
        str_with_space = ''

        for space in range(space_quantity):
            if space == 0:
                str_with_space += '%s'
            else:
                str_with_space += ',%s'
        return str_with_space

    @classmethod
    def create_sql(cls, schema, items=5, table_name=TABLE_VEICULOS_ALL_45):
        """
        Funcao que cria e formata o sql baseado em uma tabela.
        """
        if table_name == TABLE_VEICULOS_ALL_58 or table_name == TABLE_VEICULOS_ALL_45:
            space_fields_and_datas = cls.__create_str_with_space(len(items))
            sql = 'insert into '+schema+'.'+table_name+'('+space_fields_and_datas+')'\
                ' values('+space_fields_and_datas+');'
        else:
            sql = 'insert into '+schema+'.'+table_name+'(%s,%s,%s,%s,%s)'\
                ' values(ST_SetSRID(ST_MakePoint(%s,%s),4326),%s,%s,%s,%s);'

        return sql

    @classmethod
    def data_prepare_to_veiculos(cls, filename, item_dict):
        """
        Funcao que prepara e formata os dados para a insercao
        na tabela veiculos.
        """
        fields = ('position', 'date', 'velocity', 'turned_on', 'plate',)
        values = ()
        exists_key = lambda key:True if key in item_dict.keys() else False

        if exists_key('lat') and exists_key('lng'):
            values += ("'"+item_dict['lat']+"'", "'"+item_dict['lng']+"'")
        else:
            import pdb; pdb.set_trace()
            values += ('',)

        if exists_key('sTime'):
            values += ("'"+item_dict['sTime']+"'",)
        else:
            values += ('',)

        if exists_key('speed'):
            values += (item_dict['speed'],)
        else:
            values += (0,)

        if exists_key('ign'):
            if item_dict['ign'] == 'Y':
                values += (True,)
            else:
                values += (False,)
        else:
            values += ('',)

        if exists_key('plate'):
            values += ("'"+item_dict['plate']+"'",)
        else:
            values = ('',)

        return (fields, values)

    @classmethod
    def get_doned_sql(cls, item_dict, schema, table_name):
        """
        Funcao que realiza a insercao de apenas um registro
        na tabela veiculos_all.
        """
        fields = ()
        data = ()
        sql = None
        sql_with_value = None
        fields_and_data = None

        sql = cls.create_sql(schema, item_dict, table_name=table_name)
        for key, value in item_dict.items():
            fields += (key,)
            data += ("'"+re.sub(r"'", "''", value)+"'",)

        fields_and_data = fields + data
        sql_with_value = sql % fields_and_data
        return sql_with_value
