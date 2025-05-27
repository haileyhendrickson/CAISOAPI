import pandas as pd 
import requests
from zipfile import ZipFile, BadZipFile
from io import BytesIO
from datetime import datetime, date, timedelta

# User inputs/ setting parameters
map = {
    'PRC_LMP': ('DAM', 1), 
    'PRC_SPTIE_LMP': ('DAM', 4),
    'PRC_INTVL_LMP': ('RTM', 1),
    'PRC_HASP_LMP': ('HASP', 1),
    'PRC_RTPD_LMP': ('RTPD', 2),
    'PRC_DS_REF': ('', 1), # no specified market. runs fine like this
    'PRC_CD_INTVL_LMP': ('RTM' ,1),
    'PRC_RTM_LAP': ('RTM', 6),
}

queryname = input('Select Report Type: ')
market_run_id, version = map[queryname] # setting parameters for market and version based on dictionary

startdate = input('Enter a start date (YYYY/MM/DD): ').replace('/', '')
enddate = input('Enter an end date (YYYY/MM/DD): ').replace('/', '')
startdatetime = startdate+'T07:00-0000'
enddatetime = enddate+'T08:00-0000'

url = "http://oasis.caiso.com/oasisapi/SingleZip"

node = input('Specify a node. Separate multiple nodes with a comma: ').replace(' ', '')
params = {
"resultformat": 6, # should always be this- creates a CSV
"queryname": queryname, # determines what kind of data pull we want
"startdatetime": startdatetime,
"enddatetime": enddatetime,
"market_run_id": market_run_id,
"version": version, 
"node": node
}

# calling API
try: # using this for now for error handling -- doesn't work right. when there is an error it prints to the CSV
    response = requests.get(url, params=params)
    # print(response.url)
    with ZipFile(BytesIO(response.content)) as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                df = pd.read_csv(f)
                df.to_csv('test2.csv')
                # print(df.info())
                # print(df.columns)
                # print(df['LMP_TYPE'].value_counts())
                # print(df['XML_DATA_ITEM'].value_counts)
                print("Done.")
except Exception as e: # probably need to change this for better error handling
    print(f"Error message: {e}")
    # print(response.content.decode(errors='replace'))
