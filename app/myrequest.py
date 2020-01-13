import requests
import logging
import os


class MyRequest:
    def __init__(self, path_to_logs, filename_logs):
        """

        :param path_to_logs: example 'mydir/logs'
        :param filename_logs: example 'test.log'
        """
        if not os.path.isdir(path_to_logs):
            raise Exception(f'Dir {path_to_logs}, not exist!')

        filename = os.path.join(path_to_logs, filename_logs)

        logging.basicConfig(format='%(asctime)s | %(message)s', filename=filename, level=logging.INFO)

    @staticmethod
    def request(path, params=None):
        """
        Return json type response

        :param path:
        :param params:
        :return: json
        """
        response = requests.get(path, params=params or {})

        if not 200 <= response.status_code < 400:
            logging.error(f'Error, get {response.url}, status code: {response.status_code}')
            raise Exception(f'Error, get {response.url}, status code: {response.status_code}')

        if not response.text:
            logging.error(f'Error, response content empty !')
            raise Exception('Error, response content empty !')

        logging.info(f'Finish get {response.url}')
        print(f'Finish get {response.url}')

        return response.json()
