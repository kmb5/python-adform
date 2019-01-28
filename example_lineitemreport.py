from adform import AdformClient
import datetime
import pandas as pd

CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
SCOPES = ['https://api.adform.com/scope/buyer.rtb.lineitem', 'https://api.adform.com/scope/buyer.campaigns.api.readonly']
DATE_NOW_DMY = datetime.datetime.now().strftime('%d.%m.%y')

def lineitem_report():
    #Creates a .xlsx report of all active lineitems (name, budget, status, placement ID, date of export)
    print('\nStarting up & logging in to AdForm API...', end='')
    client = AdformClient(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scopes=SCOPES)
    campaigns = client.get_all_campaigns()
    if type(campaigns) == int and campaigns in requests.status_codes._codes.keys():
        #AdformClient.get_all_campaings() returns the status code if its not 200
        msg = requests.status_codes._codes.get(campaigns)[0]
        print(f'\bError, status code {campaigns}. Message: {msg}. Quitting.')
    else:
        all_camp_ids = [x.get('Campaign ID') for x in campaigns]
        print('\nGetting and filtering Orders...')
        orders = client.get_orders_per_campaigns(all_camp_ids)
        print('\nCreating report...', end='')
        report = client.get_budgets_per_active_lineitem(orders)
        data_frame = pd.DataFrame(columns=['Line item name', 'Budget amount', 'Paused', 'Line item Placement ID', 'Date'])
        for item in report:
            data_frame = data_frame.append(pd.DataFrame(item, index=[0]), sort=True)
        data_frame['Date'] = DATE_NOW_DMY
        writer = pd.ExcelWriter(f'Adform_lineitems_report__{DATE_NOW_DMY}.xlsx')
        data_frame.to_excel(writer, 'Sheet1')
        writer.save()
        print('\nAll done! Your report is saved.')
    else:
        print('Auth failed.')
        print(client.token)

if __name__== '__main__':
    lineitem_report()
    
