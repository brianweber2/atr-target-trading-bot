class TDAmeritradeAPI(object):
	'''
	This class defines all of the API calls available to TD Ameritrade's trading
	API. In each request an access token is required.
	'''

	def __init__(self, client_id, redirect_uri, access_token=None, at_expires_in=0,
							 refresh_token=None, rt_expires_in=0, strategy=None):
		self.access_token = access_token
		self.at_expires_in = at_expires_in
		self.client_id = client_id
		self.redirect_uri = redirect_uri
		self.refresh_token = refresh_token
		self.rt_expires_in = rt_expires_in
		self.strategy = strategy
		self.token_type = 'Bearer'
		self.api = 'https://api.tdameritrade.com/v1/'

	def get_access_token(self):
		'''
		Retrieve new access_token after the current one has expired.
		'''
		pass

	def get_account(self, account_id):
		pass

	def get_accounts(self):
		pass

	def get_positions(self):
		pass

	def get_order(self, account_id, order_id):
		pass

	def cancel_order(self, account_id, order_id):
		pass

	def place_order(self, account_id):
		pass

	def replace_order(self, account_id, order_id):
		pass

	def create_saved_order(self, account_id):
		pass

	def delete_saved_order(self, account_id, saved_order_id):
		pass

	def get_save_order(self, account_id, saved_order_id):
		pass

	def replace_saved_order(self, account_id, saved_order_id):
		pass

	def get_hours_for_market(self, market):
		pass

	def get_hours_for_markets(self):
		pass

	def get_index_movers(self, index):
		pass

	def get_option_chain(self):
		pass

	def get_price_history(self, symbol):
		pass

	def get_quote(self, symbol):
		pass

	def get_quotes(self, symbols):
		pass

	def get_transaction_history(self, account_id, transaction_id):
		pass

	def get_transactions_history(self, account_id):
		pass

	def get_preferences(self, account_id):
		pass

	def get_streamer_subscription_keys(self):
		pass

	def get_user_principals(self):
		pass

	def update_preferences(self, account_id):
		pass
