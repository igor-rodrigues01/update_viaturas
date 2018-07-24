from http.client import HTTPConnection
from xmltodict import parse
from io import StringIO


class CreateXMLFromWebserviceData:

    def __init__(self, webservice_url='www.linker.net.br'):
        self._ws_connection = HTTPConnection(webservice_url)
        self._ws_message_all_vehicle = """<soapenv:Envelope
                xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                xmlns:lin="http://linkerapi.portalorion.zatix.com.br/">
                <soapenv:Header/><soapenv:Body><lin:get_vehicle_list/>
                </soapenv:Body></soapenv:Envelope>"""


        self.__headers = {
            'authorization': "Basic bWFyY2Vsby5hZ3VpYXI6Y2VuaW1hX29tbmlsaW5r",
            'content-type': "text/xml",
            'cache-control': "no-cache"
        }

    def __get_data_from_webservice(self, message):
        try:
            self._ws_connection.request(
                "POST", "/linker_api?wsdl=",
                message,
                self.__headers
            )
            response = self._ws_connection.getresponse()

        except Exception as ex:
            print(ex)

        data = response.read()
        return data.decode("utf-8")

    def __make_message_to_get_one_vehicle(self, plate):
        message = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                xmlns:lin="http://linkerapi.portalorion.zatix.com.br/">
                <soapenv:Header/>
                <soapenv:Body>
                <lin:get_vehicle_history>
                <plate>{}</plate>
                <showOrder>BELOW</showOrder>
                <numberOfRecords>600</numberOfRecords>
                </lin:get_vehicle_history>
                </soapenv:Body>
                </soapenv:Envelope>""".format(plate)
        return message

    def __get_historic_of_one_vehicle(self, plates_list):
        for plate in plates_list:
            message = self.__make_message_to_get_one_vehicle(plate)
            ws_returned_xml = self.__get_data_from_webservice(message)
            file_xml = open('viaturas_recover/{}-historic.xml'.format(plate), 'w');
            file_xml.write(ws_returned_xml)
            file_xml.close()

    def __convert_xml_str_to_dict(self, xml_str):
        xml_file_in_memory = StringIO(xml_str)
        dict_xml = parse(xml_file_in_memory.read())
        return dict_xml

    def __get_all_plates(self):
        plates_list = []
        ws_returned_xml = self.__get_data_from_webservice(self._ws_message_all_vehicle)
        dict_xml = self.__convert_xml_str_to_dict(ws_returned_xml)
        vehicles = dict_xml['S:Envelope']['S:Body']['ns2:get_vehicle_listResponse']\
            ['return']['vehicles']['vehicle']

        for vehicle in vehicles:
            for key, value in vehicle.items():
                if key == 'plate':
                    plates_list.append(value)
        return plates_list

    def main(self):
        plates_list = self.__get_all_plates()
        self.__get_historic_of_one_vehicle(plates_list)


if __name__ == '__main__':
    CreateXMLFromWebserviceData().main()
