from app.myrequest import MyRequest
import pyotp
import os
import access


class Bitskins:
    __api_key = None
    __secret = None
    __app_id = None
    __base_url = 'https://bitskins.com/api/v1/'

    def __init__(self, app_id):
        self.__app_id = app_id

    def __api_request(self, api_method, params_=None):
        my_token = pyotp.TOTP(self.__secret)
        code = my_token.now()

        params = {
            'api_key': self.__api_key,
            'code': code,
            'app_id': self.__app_id
        }

        params_ and params.update(params_)

        mr = MyRequest(os.path.join(os.getcwd(), 'logs'), f'bitskins_{self.__app_id}.log')
        return mr.request(self.__base_url + api_method, params)

    def get_market_buy_orders(self, params=None):
        return self.__api_request('get_market_buy_orders', params)

    def summarize_buy_orders(self, params=None):
        return self.__api_request('summarize_buy_orders', params)

    def get_sell_history(self, params=None):
        return self.__api_request('get_sell_history', params)

    def get_buy_history(self, params=None):
        return self.__api_request('get_buy_history', params)

    def get_item_history(self, params=None):
        return self.__api_request('get_item_history', params)

    def get_sales_info(self, params=None):
        return self.__api_request('get_sales_info', params)

    def get_all_item_prices(self, params=None):
        return self.__api_request('get_all_item_prices', params)

    def get_price_data_for_items_on_sale(self, params=None):
        return self.__api_request('get_price_data_for_items_on_sale', params)

    @property
    def get_api_key(self):
        return self.__api_key

    def set_api_key(self, api_key):
        self.__api_key = api_key

    @property
    def get_secret(self):
        return self.__secret

    def set_secret(self, secret):
        self.__secret = secret

    @property
    def get_base_url(self):
        return self.__base_url

    def set_base_url(self, base_url):
        self.__base_url = base_url


if __name__ == '__main__':
    bitskins = Bitskins(730)
    bitskins.set_api_key(access.b_api_key)
    bitskins.set_secret(access.b_secret)
    bitskins.get_market_buy_orders()
