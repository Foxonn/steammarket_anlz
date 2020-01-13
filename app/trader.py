from app.bitskins import Bitskins
from app.market import Market
import pandas as pd
from urllib.parse import quote
import access

pd.set_option('max_colwidth', 800)


class Trader:
    __bitskins = None
    __market = None

    def __init__(self, app_id, **kwargs):
        """
        :param app_id:
        :param kwargs: {'bitskins_api_key', 'bitskins_secret', 'market_api_key'}
        """
        bitskins = Bitskins(app_id)
        bitskins.set_api_key(kwargs['bitskins_api_key'])
        bitskins.set_secret(kwargs['bitskins_secret'])

        self.__bitskins = bitskins

        market = Market(app_id)
        market.set_api_key(kwargs['market_api_key'])

        self.__market = market

    def b_get_buy_history(self, params=None):
        purchasers = self.__bitskins.get_buy_history(params)

        if not purchasers['data']:
            raise Exception('Data not found!')

        if not purchasers['data']['items']:
            raise Exception('Items not found!')

        df = pd.DataFrame(purchasers['data']['items'])

        return df

    def b_get_item_history(self, params=None):
        purchasers = self.__bitskins.get_item_history(params)

        if not purchasers['data']:
            raise Exception('Data not found!')

        if not purchasers['data']['items']:
            raise Exception('Items not found!')

        df = pd.DataFrame(purchasers['data']['items'])

        return df

    def b_get_all_item_prices(self, params=None):
        data = self.__bitskins.get_all_item_prices(params=params)
        df = pd.DataFrame(data['prices'])
        df = df[['market_hash_name', 'price']]
        return df

    def m_find_sell_market(self):
        data = self.__market.get_prices()

        df = pd.DataFrame(data['items'])

        dtypes = {
            'market_hash_name': 'object',
            'price': 'float32',
        }

        df = df.astype(dtypes)

        df = df[['market_hash_name', 'price']]
        df['price'] = df['price'].apply(lambda x: round(x, 2))

        return df

    def m_get_buy_orders(self, currency='USD'):
        data = self.__market.get_buy_orders(currency)

        items = []

        for item in data['items']:
            _ = data['items'][item]
            _.update({'ids': item})

            items.append(_)

        df = pd.DataFrame(items)

        df = df[(df['buy_order'].apply(lambda x: x is not None)) & (df['popularity_7d'].apply(lambda x: x is not None))]
        df = df[['market_hash_name', 'buy_order', 'ids', 'popularity_7d']]
        df = df.drop_duplicates('market_hash_name', keep='last')
        df = df.astype({'buy_order': 'float32'})
        df = df.astype({'popularity_7d': 'int16'})
        df = df[(df['buy_order'] < 2) & (df['buy_order'] > 0.3) & (df['popularity_7d'] > 30)]

        return df

    def b_get_market_buy_orders(self, params=None):
        data = self.__bitskins.get_market_buy_orders(params=params)

        orders = [order for order in data['data']['orders']]

        df = pd.DataFrame(orders)

        dtypes = {
            'buy_order_id': 'int32',
            'place_in_queue': 'int16',
            'price': 'float32',
            'suggested_price': 'float32',
            'market_hash_name': 'object',
            'is_mine': 'object',
            'created_at': 'datetime64[ns]',
        }

        df = df.astype(dtypes)

        df = df[['buy_order_id', 'price', 'market_hash_name']]

        df = df.sort_values(by='price', ascending=False)
        df = df.drop_duplicates('market_hash_name')

        return df

    def b_get_price_data_for_items_on_sale(self, params=None):
        data = self.__bitskins.get_price_data_for_items_on_sale(params=params)

        df = pd.DataFrame(data['data']['items'])
        df.updated_at = pd.to_datetime(df.updated_at, unit='s')
        df = df[['market_hash_name', 'lowest_price']]
        df = df.astype({'lowest_price': 'float32'})
        df = df[df['lowest_price'] > 0]

        return df

    def b_get_sales_info(self, params=None):
        json = self.__bitskins.get_sales_info(params=params)

        df = pd.DataFrame(json['data']['sales'])
        df.sold_at = pd.to_datetime(df.sold_at, unit='s')
        df = df.set_index('sold_at')

        return df

    def b_find_orders(self, min_price, max_price):
        purchasers = self.__bitskins.summarize_buy_orders()

        if not purchasers['data']:
            raise Exception('Data not found!')

        if not purchasers['data']['items']:
            raise Exception('Items not found!')

        dtypes = {
            'number_of_buy_orders': 'int16',
            'market_hash_name': 'object',
            'max_price': 'float16',
            'my_buy_orders': 'object',
        }

        items = [purchasers['data']['items'][item] for item in purchasers['data']['items']]

        df = pd.DataFrame(items)

        df = df[['number_of_buy_orders', 'market_hash_name', 'max_price', 'my_buy_orders']]

        df = df.astype(dtypes)

        df = df[df['max_price'] < max_price]
        df = df[df['max_price'] > min_price]
        df = df[df['my_buy_orders'].apply(lambda x: x is not None)]
        df['max_price'] = df['max_price'].apply(lambda x: round(x, 2))

        df = df.sort_values(by='number_of_buy_orders', ascending=False)

        return df

    def table_seller_m_to_buyer_b(self):
        b_buyer = self.b_get_market_buy_orders()
        m_seller = self.m_find_sell_market()

        df = b_buyer.merge(m_seller, left_on='market_hash_name', right_on='market_hash_name', suffixes=('_b', '_m'))
        df = df[df['price_b'] > df['price_m']]

        df['proof'] = 100 / (df['price_m'] / (df['price_b'] - df['price_m']))
        df = df.astype({'proof': 'float32'})
        df['proof'] = df['proof'].apply(lambda x: round(x, 2))
        df = df.sort_values(by='proof', ascending=False)

        return df

    def table_seller_b_to_buyer_m(self):
        m_buyer = self.m_get_buy_orders()
        b_seller = self.b_get_price_data_for_items_on_sale()

        df = m_buyer.merge(b_seller, on='market_hash_name')
        df = df[df['buy_order'] > df['lowest_price']]
        df['proof'] = 100 / (df['lowest_price'] / (df['buy_order'] - df['lowest_price']))
        df = df.astype({'proof': 'float32'})
        df['proof'] = df['proof'].apply(lambda x: round(x, 2))
        df = df.sort_values(by='proof', ascending=False)
        df['link'] = 'https://market.csgo.com/item/' + df.ids.apply(
            lambda x: str(x).replace('_', '-')) + '_' + df.market_hash_name.apply(
            lambda x: quote(str(x)))
        df = df.set_index('market_hash_name')
        df = df[['proof', 'buy_order', 'lowest_price', 'link']]

        return df


params = {
    'bitskins_api_key': access.b_api_key,
    'bitskins_secret': access.b_secret,
    'market_api_key': access.m_api_key,
}

trader = Trader(730, **params)
print(trader.table_seller_b_to_buyer_m().to_string())
# print(trader.table_seller_m_to_buyer_b().to_string())
