from app.myrequest import MyRequest
import os
import access


class Market:
    __base_url = None
    __api_key = None
    __app_id = None

    def __init__(self, app_id):
        self.__app_id = app_id

        api = {
            570: 'https://market.dota2.net/api/v2/',
            730: 'https://market.csgo.com/api/v2/'
        }

        self.__base_url = api[app_id]

    def set_api_key(self, api_key):
        self.__api_key = api_key

    def get_prices(self, currency='USD'):
        """
        :param currency: (USD,EUR,RUB)
        :return: json
        """
        api_method = f'prices/{currency}.json'
        return self.__api_request(api_method)

    def get_history_my_trades(self, date='01-04-2018', date_end=None):
        params = {
            'date': date
        }

        date_end and params.update(date_end)

        return self.__api_request('history', params_=params)

    def get_buy_orders(self, currency='USD'):
        """
        :param currency: (USD,EUR,RUB)
        :return: json
        """
        api_method = f'prices/class_instance/{currency}.json'
        return self.__api_request(api_method)

    def __api_request(self, api_method, params_=None):
        mr = MyRequest(os.path.join(os.getcwd(), 'logs'), f'market_{self.__app_id}.log')

        params = {
            'key': self.__api_key
        }

        params_ and params.update(params_)

        return mr.request(self.__base_url + api_method, params)

    @property
    def get_base_url(self):
        return self.__base_url

    @property
    def get_app_id(self):
        return self.__app_id

    @property
    def get_api_key(self):
        return self.__api_key

    @property
    def test(self):
        """
        :return: json
        """
        api_method = 'test'
        return self.__api_request(api_method)


if __name__ == '__main__':
    market = Market(570)
    market.set_api_key(access.m_api_key)
    print(market.test)
