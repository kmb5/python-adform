import adform
import pandas as pd

CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
SCOPES = ['https://api.adform.com/scope/buyer.rtb.lineitem', 'https://api.adform.com/scope/buyer.campaigns.api.readonly']

def lineitem_report():
    print('\nStarting up & logging in to AdForm API...', end='')
    client = AdformClient(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scopes=SCOPES)
    if client.token:
        print('\nGetting Campaigns...', end='')
        spin.start()
        campaigns = client.get_all_campaigns()
        if type(campaigns) == int and campaigns in requests.status_codes._codes.keys():
            msg = requests.status_codes._codes.get(campaigns)[0]
            spin.stop()
            print(f'\bError, status code {campaigns}. Message: {msg}. Quitting.')
        else:
            all_camp_ids = [x.get('Campaign ID') for x in campaigns] # List comprehension which returns all the campaign IDs and only those (no campaign name, nothing else)
            spin.stop()

            print('\nGetting and filtering Orders...')
            orders = client.get_orders_per_campaigns(all_camp_ids) # Using the list of campaign IDs to get all the active and not deleted orders
            print('\nCreating report...', end='')
            spin.start()
            report = client.get_budgets_per_active_lineitem(orders) # Using the orders data structure to create the reports
            data_frame = pd.DataFrame(columns=['Line item name', 'Budget amount', 'Paused', 'Line item ID - PLACEMENT', 'Date'])    # Create an empty pandas dataframe (a table-like object in python) with the given columns
            for item in report:                                                                                                     # For each list in the report variable
                data_frame = data_frame.append(pd.DataFrame(item, index=[0]), sort=True)                                            # Create a sorted dataframe of the list (with index [0] otherwise it throws an error) and append it to the main dataframe (df variable)
            data_frame['Date'] = DATE_NOW_DMY                                                                                       # Overwrite the all rows of the Date column in the dataframe with the contents of the DATE_NOW_DMY variable

            writer = pd.ExcelWriter(f'Adform_lineitems_report__.xlsx')    # Instantiate an ExcelWriter object (from pandas) with the filename
            data_frame.to_excel(writer, 'Sheet1')                                       # Write the contents of the excel writer to the Sheet1 of the file
            writer.save()                                                               # Save the file
            spin.stop()

            print('\nAll done! Your report is saved.')
    else:
        print('Auth failed.')
        print(client.token)
