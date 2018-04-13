
import xmltodict
import datetime
import pytz
import sys
import os

from dateutil import parser
from collections import OrderedDict
from utils import Utils
from dao import DAO
from constants import *


class ProcessXML:

    __dirbase_xml = None

    def __init__(self):
        self.__dirbase_xml = 'viaturas_recover'

    def __read_xml_convert_dict(self, xml_filename):
        """
        function that read the xml file and convert to dict
        """
        xml_ordered_dict = OrderedDict()
        with open(xml_filename) as xml:
            xml_ordered_dict = xmltodict.parse(xml.read())

        return xml_ordered_dict['S:Envelope']['S:Body'][
            'ns2:get_vehicle_historyResponse'
        ]['return']['historyEntries']['historyEntry']

    def __remove_new_fields_by_reference(self, record_dict):
        """
        Function that remove the fileds that not exists in the database,
        bacause, in the request on viaturas script the webservice not return
        these fields. 
        """
        del record_dict['gps']
        del record_dict['seqId']
        del record_dict['eType']
        del record_dict['pTime']
        del record_dict['rCode']
        del record_dict['rType']
        del record_dict['tType']
        if 'info' in record_dict.keys():
            del record_dict['info']

        # import pdb; pdb.set_trace()

    def __get_data_by_thirty_minute(self, xml_ordered_dict_in_list):
        """
        Function that get register by half and half an hour
        """
        date_bigger = datetime.datetime.utcnow()
        date_bigger = date_bigger.replace(tzinfo=pytz.UTC)
        thirty_minutes_timedelta = datetime.timedelta(minutes=30)
        xml_ordered_dict_int_list_result = []

        """
         - The current date readed will be always smaller than the after date
           readed because the xml file is readed of top to bottom.
         - The if of this loop will check if the date_bigger is bigger that
           the date_smaller plus thirty minutes. thereby will added in
           the xml_ordered_dict_int_list_result the dates with interval of
           the 30 minutes in between dates.
        """
        for register in xml_ordered_dict_in_list:
            date_smaller = parser.parse(register['sTime'])
            if date_bigger > (date_smaller + thirty_minutes_timedelta):
                xml_ordered_dict_int_list_result.append(register)

            date_bigger = date_smaller

        return xml_ordered_dict_int_list_result

    def success_messages(self, record_inserted):
        """
        Function tha display success message
        """
        print('{} Inserted in the table {}.{} in server 10.1.8.58'.format(
            record_inserted, SCHEMA_58, TABLE_VEICULOS_ALL_58)
        )
        print('{} Inserted in the table {}.{} in server 10.1.8.58'.format(
            record_inserted, SCHEMA_58, TABLE_VEICULOS_58)
        )
        print('{} Inserted in the table {}.{} in server 10.1.8.45'.format(
            record_inserted, SCHEMA_45, TABLE_VEICULOS_ALL_45)
        )
        print('{} Inserted in the table {}.{} in server 10.1.8.45'.format(
            record_inserted, SCHEMA_45, TABLE_VEICULOS_HIST_45)
        )

    def __execute_inserts(self, xml_divided_by_thirty_minute, dao_45, dao_58, filename):
        """
        Function that perform all the inserts
        """
        for reg in xml_divided_by_thirty_minute:
            self.__remove_new_fields_by_reference(reg)
            # Inserting in veiculos in 58
            sql_inst_veiculos_all_58 = Utils.get_doned_sql(
                reg, SCHEMA_58, TABLE_VEICULOS_ALL_58
            )
            dao_58.insert_veiculos_all(sql_inst_veiculos_all_58)

            dao_58.insert_in_veiculos_and_veiculos_hist(
                reg, SCHEMA_58, TABLE_VEICULOS_58, filename
            )
            # Inserting in veiculos in 45
            sql_inst_veiculos_all_45 = Utils.get_doned_sql(
                reg, SCHEMA_45, TABLE_VEICULOS_ALL_45
            )
            dao_45.insert_veiculos_all(sql_inst_veiculos_all_45)

            dao_45.insert_in_veiculos_and_veiculos_hist(
                reg, SCHEMA_45, TABLE_VEICULOS_HIST_45, filename
            )
        return 1

    def __create_file_with_xml_without_latlng(self, list_xml_with_filename):
        """
        Function tha create file to indentify the files without lat lng
        """
        # file = open('error.txt', 'w+')

        for filename, xml_data in list_xml_with_filename.items():
            for reg in xml_data:
                if 'lat' not in reg.keys() or 'lng' not in reg.keys():
                    # file.write(filename)
                    index_remove = list_xml_with_filename[filename].index(reg)
                    del list_xml_with_filename[filename][index_remove]

        # file.close()

    def __get_xml_all_files(self):
        """
        Function that read all xml file in the directory __dirbase_xml
        and call the function to read one xml file and to create date interval
        together date. The fila will be created a result that have as key the
        xml filename and your value will all xml data divided by 30 minutes.
        """
        xml_all_filename = os.listdir(self.__dirbase_xml)
        result = {}
        for xml_filename in xml_all_filename:
            path_xml_filename = os.path.join(self.__dirbase_xml, xml_filename)
            xml_data_dict = self.__read_xml_convert_dict(path_xml_filename)
            xml_data_by_thirty_minute = self.__get_data_by_thirty_minute(
                xml_data_dict
            )
            result[xml_filename] = xml_data_by_thirty_minute
            print('{} Readed'.format(xml_filename))
        return result

    def main(self):
        xml_data_all_files = self.__get_xml_all_files()
        dao_58 = DAO(HOST_58, DATABASE_58, USER_58, PASSWD_58)
        dao_45 = DAO(HOST_45, DATABASE_45, USER_45, PASSWD_45)
        record_inserted = 0
        self.__create_file_with_xml_without_latlng(xml_data_all_files)

        # Making inserts
        try:
            for filename, xml_data in xml_data_all_files.items():
                record_inserted += self.__execute_inserts(
                    xml_data, dao_45, dao_58, filename
                )
                print('The XML from {} was inserted with Successfully'.format(
                    filename)
                )

        except Exception as exc:
            dao_58.conn.rollback()
            dao_45.conn.rollback()
            sys.exit('{}\n Rollback successfully'.format(exc))
        else:
            dao_58.conn.commit()
            dao_45.conn.commit()
            self.success_messages(record_inserted)


if __name__ == '__main__':
    pxml = ProcessXML()
    pxml.main()
