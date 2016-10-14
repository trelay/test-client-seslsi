#!/usr/bin/env python
import sys
import requests
from requests.exceptions import *
from HTMLLogger import HTMLLogger
from jsonconv import json2html
import json
#from errors import *

#TODO:
#url='http://127.0.0.1:5000/test-operator-ses/sas/.dev.sg3/cli'


class RUN_SEQUENCE(object):
    def __init__(self, logger):
        self.logger = logger

    def run(self, test, url):
        self.__send_requests(test, url)

    def __send_requests(self, test, url):
        msg = "Starting test %s" % str(test)
        self.logger.info(msg)

        try:
            response_obj = requests.post(url, json=test)
        except ConnectionError, err:
            msg="Can't connect to Server: check if server is running"
            self.logger.error(msg)
            return
        except RequestException, err:
            msg = "Error happens: " + str(err)
            self.logger.error(msg)
            return

        status_code = response_obj.status_code
        if status_code == 200:
            #Perhaps not use response_obj.json()
            response_t = response_obj.text.encode('ascii', 'ignore')
            response = json.loads(response_t)
    
            if response['status']['result']=="success":
                response_table = json2html.convert(json = response['response'])
                #Prevent HTMLLogger from transfering to unicode
                msg = "Get response from Server, response:%s" % response_table
                self.logger.table(msg)
            else:
                for error in response['status']['errors']:
                    msg = '''error-type: %(error-type)s, message: %(message)s''' % error
                    self.logger.error('''error-type: %(error-type)s, message: %(message)s''')
        else:
            msg = "Error code:{0}, please check the url:{1} you requested".format(status_code, url)
            self.logger.error(msg)
        
                
def RUN_TEST(logger, test_sequence_json):
    msg = "START TEST WITH TEST NAME: %s" % test_sequence_json['name']
    url = test_sequence_json['url']
    logger.info(msg)
    for test in test_sequence_json['sequence']:
        run_sequence = RUN_SEQUENCE(logger)
        run_sequence.run(test, url)
        

if __name__ == "__main__":

    logger=HTMLLogger(name="SES Client", html_filename="log.html", console_log=True)

    try:
        json_f = sys.argv[1]
        with open(json_f,'r') as f:
            test_sequence = f.read()
    except EnvironmentError:
        msg = "Can't find the file you specified."
        logger.error(msg)
        sys.exit(msg)

    try:
        test_sequence_json = json.loads(test_sequence)
    except Exception, err:
        msg = "Test Sequence is not in correct format: "+ err.__str__()
        logger.error(msg)
        sys.exit(err.__str__())
    RUN_TEST(logger, test_sequence_json)
    sys.exit(0)
    
