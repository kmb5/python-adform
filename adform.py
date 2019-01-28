#! /usr/local/bin/python3

import json
import requests

# ---- CONSTANTS ---- #

CLIENT_ID = 'YOUR_CLIENT_ID_HERE'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET_HERE'
BASE_URL = 'https://api.adform.com/'

# ---- CONSTANTS ---- #

# ---- MAIN ADFORM CLIENT CLASS AND ITS METHODS ---- #

class AdformClient():
    def __init__(self, client_id, client_secret, scope, base_url=BASE_URL):
        self.client_id = client_id
        self.client_secret = client_secret
        if type(scopes) == list:
            self.scope = ' '.join(scope)
        else:
            self.scope = scope
        self.base_url = base_url
        self._authorize()

    def _authorize(self):
        # Called by __init__ - gets token for given scope (valid for 1 hours)
        # Authorization is done by client credentials method, supplying a Client ID and a Client secret
        # The token is extracted from the response and added to the AdformClient object.
        # If there is an error (eg. secret is wrong), the token will be 'Auth_error' instead of the actual token.
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload_dict = {'grant_type':'client_credentials', 'client_id':self.client_id, 'client_secret':self.client_secret, 'scope':self.scope}
        response = requests.post('https://id.adform.com/sts/connect/token', headers=headers, data=payload_dict)
        self.token = json.loads(response.text).get('access_token', 'Auth_error')
        self.header = {'Authorization': 'Bearer ' + self.token}
        
    def _get_lineitem_ids(self, list_of_orders, paused='false', deleted='false'):
        # Needs AdformClient instance with buyer.rtb.lineitem scope
        # Internal method called by get_budgets_per_active_lineitem
        # By default it returns a list of all the ACTIVE AND NOT DELETED lineitems
        # Eg.: [1231324, 12123124, 879873456, 345234464]
        url = 'v1/buyer/rtb/lineitems/'
        order_ids = []
        for campaign_dict in list_of_orders:
            for order in campaign_dict.get('Orders'):
                order_ids.append(str(order.get('Order ID')))
        joined_ids = ','.join(order_ids) # The API accepts the order IDs separated by strings (and not part of a list)
        response = requests.get(self.base_url + url, headers=self.header, params={'orderIds': joined_ids, 'paused': paused, 'deleted': deleted})
        if response.status_code == 200:
            return [lineitem_dict.get('id') for lineitem_dict in json.loads(response.text)]
        return response.status_code

    def budget_report(self, line_item_id):
        # Needs AdformClient instance with buyer.rtb.lineitem scope
        # Returns a dictionary based on the format outlined in https://api.adform.com/v1/help/buyer/rtb/lineitems#!/LineItems/LineItems_GetList
        # If there is an error with the request (eg. timeout, etc.) it returns the status code of the error instead of a dictionary.
        url = 'v1/buyer/rtb/lineitems/'
        response = requests.get(self.base_url + url + line_item_id, headers=self.header)
        if response.status_code == 200:
            return json.loads(response.text)
        return response.status_code

    def get_orders_per_campaigns(self, campaign_ids, active=['true']):
        # Doesn't need any specific scope, works with any
        # Returns a data structure, where each campaign ID has a list of dictionaries attached to it containing order details
        # Eg. [{'Campaign ID': 1234, 'Orders': [{'Order ID': 0001, 'Order Name': 'SampleName', 'Order Budget': 988, 'Active': True}, {'Order ID': 0002}, ...]}, {'Campaign ID': 5678, 'Orders': [{...}, {...}, ...]}
        url = 'v1/buyer/orders/'
        all_orders = []
        for status in active: # By default it only gets the active orders, if you want paused as well add 'false' to the list when calling this method
            for campaign_id in tqdm(campaign_ids):
                response = requests.get(self.base_url + url, headers=self.header, params={'campaignId': campaign_id, 'active': status})
                if response.status_code == 200:
                    orders_of_camp = [{'Order ID': order_dict.get('id'), 'Order Name': order_dict.get('name'), 'Order Budget': order_dict.get('budget'), 'Active': order_dict.get('active')} for order_dict in json.loads(response.text)]
                    all_orders.append({'Campaign ID': campaign_id, 'Orders': orders_of_camp})
        return all_orders

    def get_budgets_per_active_lineitem(self, list_of_orders):
        # Needs AdformClient instance with buyer.rtb.lineitem scope
        # Returns a list of dictionaries for each lineitem containing the line item name, the budget amount, the status (as boolean True or False, see below) and the placement ID
        # Eg. [{'Line item name': Test1, 'Budget amount': 87, 'Paused': False, 'Line item ID - PLACEMENT': 9283742}, {'Line item name': Test2, 'Budget amount': 0, 'Paused': True, 'Line item ID - PLACEMENT': 987654}, {...}]
        results = []
        for lineitem_id in self._get_lineitem_ids(list_of_orders=list_of_orders):
            report = self.budget_report(line_item_id=str(lineitem_id))
            results.append(
                {
                    'Line item name': report.get('name'),
                    'Budget amount': report.get('budget', {}).get('money', {}).get('amount'),
                    'Paused': report.get('paused'),
                    'Line item Placement ID': report.get('placementId')
                })
        return results

    def get_campaigns_filter_by_name(self, keyword, status=('Active', 'Paused')):
        # Needs AdformClient instance with buyer.campaigns.api or buyer.campaigns.api.readonly scope
        # Returns a list of dictionaries for each campaign FILTERED BY A GIVEN KEYWORD containing the campaign ID, campaign name, campaign type and status
        # Eg. [[{'Campaign ID': 23425, 'Campaign Name': 'Test1', 'Status': 'Active'}, {'Campaign ID': 57889, 'Campaign Name': 'Test2', 'Status': 'Paused'}, {...}]
        url = 'v1/buyer/campaigns/'
        response = requests.get(self.base_url + url, headers=self.header)
        if response.status_code == 200:
            return [{'Campaign ID': campaign_dict.get('id'), 'Campaign Name': campaign_dict.get('name'), 'Campaign Type': campaign_dict.get('type'), 'Status': campaign_dict.get('status')} for campaign_dict in json.loads(response.text) if keyword in campaign_dict['name'] and campaign_dict['status'] in status]
        return response.status_code

    def get_campaigns_filter_by_status(self, status=('Active', 'Paused')):
        # Needs AdformClient instance with buyer.campaigns.api or buyer.campaigns.api.readonly scope
        # Returns a list of dictionaries for each campaign FILTERED BY A GIVEN STATUS (that must be a Tuple) containing the campaign ID, campaign name, campaign type and status
        # Eg. [[{'Campaign ID': 23425, 'Campaign Name': 'Test1', 'Status': 'Active'}, {'Campaign ID': 57889, 'Campaign Name': 'Test2', 'Status': 'Paused'}, {...}]
        url = 'v1/buyer/campaigns/'
        response = requests.get(self.base_url + url, headers=self.header)
        if response.status_code == 200:
            return [{'Campaign ID': campaign_dict.get('id'), 'Campaign Name': campaign_dict.get('name'), 'Campaign Type': campaign_dict.get('type'), 'Status': campaign_dict.get('status')} for campaign_dict in json.loads(response.text) if campaign_dict['status'] in status]
        return response.status_code

    def get_all_campaigns(self):
        # Needs AdformClient instance with buyer.campaigns.api or buyer.campaigns.api.readonly scope
        # Returns a list of dictionaries for EACH AND EVERY campaign containing the campaign ID, campaign name, campaign type and status
        # Eg. [[{'Campaign ID': 23425, 'Campaign Name': 'Test1', 'Status': 'Active'}, {'Campaign ID': 57889, 'Campaign Name': 'Test2', 'Status': 'Paused'}, {...}]
        url = 'v1/buyer/campaigns/'
        response = requests.get(self.base_url + url, headers=self.header)
        if response.status_code == 200:
            return [{'Campaign ID': campaign_dict.get('id'), 'Campaign Name': campaign_dict.get('name'), 'Campaign Type': campaign_dict.get('type'), 'Status': campaign_dict.get('status')} for campaign_dict in json.loads(response.text)]
        return response.status_code

# ---- MAIN ADFORM CLIENT CLASS AND ITS METHODS ---- #
