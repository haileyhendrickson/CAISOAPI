import pandas as pd 
import requests
from zipfile import ZipFile, BadZipFile
from io import BytesIO
from datetime import datetime, date, timedelta

startdate = '2024/01/01' # jan 1 2024
enddate = '2024/12/31' # dec 31 2024

url = "http://oasis.caiso.com/oasisapi/SingleZip"
params = {
"resultformat": 6, # should always be this- creates a CSV
"queryname": 'PRC_LMP', # locational marginal prices
"startdatetime": f'{startdate}T07:00-0000', 
"enddatetime": f'{enddate}T07:00-0000', 
"market_run_id": 'DAM', # day ahead market
"version": 1,  
"node": '0096WD_7_N001'
}

startdate = date.fromisoformat(startdate, ) # formats it to work with datetime package
enddate = date.fromisoformat(enddate)

print(f'start: {startdate}, end: {enddate}')

'''
difference = enddate - startdate # counts days in between
print(difference.days) # delete later

if difference.days > 30:
    while difference.days > 0: # until we reach the end date
        if difference.days < 30: # when we get below 30 days left
            pass
            # end date needs to be original end date
        nextdate = startdate + timedelta(days=30) # creating a chunk
        difference.days -= 30 # updating this counter
        # pull a file from start date to +30 days: startdate = startdate (reformat), enddate = startdate+30days (reformat)
        startdate = nextdate # update start date to be next date
        # if there's less than 31 days left, fix that 
# if not, run like normal
'''

# calling API
try:
    response = requests.get(url, params=params)
    # print(response.url)
    with ZipFile(BytesIO(response.content)) as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                df = pd.read_csv(f)
                df.to_csv('test2.csv')
                print("Done.")
except Exception as e: # doesn't print the error for some reason
    print(f"Error message: {e}")
