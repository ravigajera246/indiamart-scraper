# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 17:33:06 2020

@author: shrey.arora
"""


from googleapiclient import discovery
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from bs4 import BeautifulSoup
import urllib.request
import pandas as pd


def get_google_sheet(spreadsheet_id, range_name):
    """ Retrieve sheet data using OAuth credentials and Google Python API. """
    scopes = 'https://www.googleapis.com/auth/spreadsheets'
   # scope_write = 'https://www.googleapis.com/auth/spreadsheets'
    # Setup the Sheets API
    store = file.Storage('credentials.json')
    creds = store.get()
    #creds_write = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scopes)
    if not creds or creds.invalid: ## for reading the gsheet
        flow = client.flow_from_clientsecrets('client_secret.json', scopes)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    #if not creds_write or creds_write.invalid:
       # client_write = gspread.authorize(creds_write)
       # gsheet_op_1 = client_write.open("Onboarding AM scoring").sheet2
    # Call the Sheets API
    gsheet = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()

    return gsheet

def gsheet2df(gsheet):
    """ Converts Google sheet data to a Pandas DataFrame.
    Note: This script assumes that your data contains a header file on the first row!
    Also note that the Google API returns 'none' from empty cells - in order for the code
    below to work, you'll need to make sure your sheet doesn't contain empty cells,
    or update the code to account for such instances.
    """
    #print( len(gsheet.get('values', [])[0]))
    header = gsheet.get('values', [])[0]  #['Key_signup','Timestamp','#Cards','Price_per_card','Status','Dispatch_Date','Product_Go_through','User_details','KYC','NEFT','Actual_Onboarding_Date','Payment_Status','Payment_Date','AM','Sign_Up_Month','Sign_Up_Year','date_assigned','signup_gap_today','Fleet_Size','fleet_Category']    #gsheet.get('values', [])[0]   # Assumes first line is header!
    values = gsheet.get('values', [])[1:]  # Everything else is data.
    if not values:
        print('No data found.')
    else:
        all_data = []
        for col_id, col_name in enumerate(header):
            column_data = []
            for row in values:
                column_data.append(row[col_id])
            ds = pd.Series(data=column_data, name=col_name)
            all_data.append(ds)
        df = pd.concat(all_data, axis=1)
        return df

def write2gsheet(data_values,sheet_name):
    scopes = 'https://www.googleapis.com/auth/spreadsheets'
   # scope_write = 'https://www.googleapis.com/auth/spreadsheets'
    # Setup the Sheets API
    store = file.Storage('credentials.json')
    creds = store.get()
    #creds_write = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scopes)
    if not creds or creds.invalid: ## for reading the gsheet
        flow = client.flow_from_clientsecrets('client_secret.json', scopes)
        creds = tools.run_flow(flow, store)
    service = discovery.build('sheets', 'v4', credentials=creds)
    value_input_option = 'USER_ENTERED'
    values = data_values
    body = {
    'values': values
    }
    sheet_id = '1AgVFOpCe7XVGdrO6NB_Bhlr8kNk-62or3D44wvpMgBM'
    sheet_range = sheet_name
    service.spreadsheets().values().append(spreadsheetId=sheet_id, range=sheet_range,valueInputOption=value_input_option, body=body).execute()

def cleargsheet(range_name):
    scopes = 'https://www.googleapis.com/auth/spreadsheets'
   # scope_write = 'https://www.googleapis.com/auth/spreadsheets'
    # Setup the Sheets API
    store = file.Storage('credentials.json')
    creds = store.get()
    #creds_write = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scopes)
    if not creds or creds.invalid: ## for reading the gsheet
        flow = client.flow_from_clientsecrets('client_secret.json', scopes)
        creds = tools.run_flow(flow, store)
    service = discovery.build('sheets', 'v4', credentials=creds)
    clear_values_request_body = {
    # TODO: Add desired entries to the request body.
    }  

    service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=range_name, body=clear_values_request_body).execute()



cities = ['delhi','noida','gurugram','chandigarh','mumbai']
niches = ['food','restaurants','school','doctors','clinics','fashion','brands']
values = pd.DataFrame()

for city in cities:
    print(city)
    
    for niche in niches:
        print(niche)
        ##city = cities[0]
        ##niche =niches[0]
        
        
        url = "https://dir.indiamart.com/search.mp?ss=%s&cq=%s&cq_src=city-mcat&prdsrc=1&search_type=c"%(niche,city)
        try:
            page = urllib.request.urlopen(url)
        except:
            print("An error occured.")
        
        soup = BeautifulSoup(page, 'html.parser')
        #print(soup)
        products = soup.find_all('span', attrs={'data-click': "^Prod0Name"})
        company_names = soup.find_all('h4',attrs={'data-click': "^CompanyName"})
        phone_numbers = soup.find_all('span', attrs={'class': "pns_h duet"})
        address = soup.find_all('p', attrs={'class': "sm clg"})
        place = city 
        industry = niche
        
        prods = []
        for p in products:
            prods.append(p.getText().split(',')[0])
        
        
        
        comp_names = []
        for c in company_names:
            comp_names.append(c.getText().split(",")[0])
            
        phone_num = []
        for pn in phone_numbers:
            phone_num.append(pn.getText().split(",")[0])
            
        addresses = []
        for ad in address:
            addresses.append(ad.getText().split("\n")[0] + ad.getText().split("\n")[1][16:-1])
           
        
          
        for i in range(0,len(prods)):
            row_data = {'product':prods[i],'company':comp_names[i],'Contact':phone_num[i],'address':addresses[i],'city':place,'industry':niche}
            values = values.append(row_data,ignore_index=True)

