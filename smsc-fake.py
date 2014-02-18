import socket
import logging
import time

from smpp.esme import *

class SmscFake(ESME):

    def __init__(self, port=2775, credentials={}):
        logger = logging.getLogger('smsc')
        logging.basicConfig(filename='smsc.log', level=logging.INFO, format='%(asctime)s %(message)s')
        self.credentials = credentials
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('', port))
        self.server.listen(1)
        self.conn, self.addr = self.server.accept()
        print 'Connected by', self.addr
        while 1:
            pdu = self._ESME__recv()
            if not pdu: break
            print pdu
            #logger.info("Received message: %s", self.extract_from_pdu(pdu))
            self.conn.send(pack_pdu(self.__response(pdu)))
        self.conn.close()

    def extract_from_pdu(self, pdu):
	if 'header' in pdu and pdu['header']['command_id'] == 'submit_sm':
            output = []
            output.append("destination_addr=" + pdu['body']['mandatory_parameters']['destination_addr'])
            output.append("short_message='" + pdu['body']['mandatory_parameters']['short_message'] + "'")
            output.append("timestamp=" + str(int(time.time())))
            return " ".join(output)
        return pdu

    def __response(self, pdu):
        pdu_resp = {}
        resp_header = {}
        pdu_resp['header'] = resp_header
        resp_header['command_length'] = 0
        resp_header['command_id'] = 'generic_nack'
        resp_header['command_status'] = 'ESME_ROK'
        resp_header['sequence_number'] = pdu['header']['sequence_number']
        if pdu['header']['command_id'] in [
                'bind_transmitter',
                'bind_receiver',
                'bind_transceiver',
                'unbind',
                'submit_sm',
                'submit_multi',
                'deliver_sm',
                'data_sm',
                'query_sm',
                'cancel_sm',
                'replace_sm',
                'enquire_link',
                ]:
            resp_header['command_id'] = pdu['header']['command_id']+'_resp'
        if pdu['header']['command_id'] in [
                'bind_transmitter',
                'bind_receiver',
                'bind_transceiver',
                ]:
            resp_body = {}
            pdu_resp['body'] = resp_body
            resp_mandatory_parameters = {}
            resp_body['mandatory_parameters'] = resp_mandatory_parameters
            resp_mandatory_parameters['system_id'] = pdu['body']['mandatory_parameters']['system_id']
        if pdu['header']['command_id'] in [
                #'submit_sm', # message_id is optional in submit_sm
                'submit_multi',
                'deliver_sm',
                'data_sm',
                'query_sm',
                ]:
            resp_body = {}
            pdu_resp['body'] = resp_body
            resp_mandatory_parameters = {}
            resp_body['mandatory_parameters'] = resp_mandatory_parameters
            resp_mandatory_parameters['message_id'] = ''
            if pdu['header']['command_id'] == 'submit_multi':
                resp_mandatory_parameters['no_unsuccess'] = 0
            if pdu['header']['command_id'] == 'query_sm':
                resp_mandatory_parameters['final_date'] = ''
                resp_mandatory_parameters['message_state'] = 0
                resp_mandatory_parameters['error_code'] = 0
        return pdu_resp



if __name__ == '__main__':
    smsc = SmscFake(2777)

