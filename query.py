import pandas as pd 
import requests
from zipfile import ZipFile, BadZipFile
from io import BytesIO
from datetime import datetime, date, timedelta

# User inputs/ setting parameters
# map = {
#     'PRC_LMP': ('DAM', 1, 60), # default
#     'PRC_SPTIE_LMP': ('DAM', 4, 60),
#     'PRC_INTVL_LMP': ('RTM', 1, 5),
#     'PRC_HASP_LMP': ('HASP', 1, 15),
#     'PRC_RTPD_LMP': ('RTPD', 2, 15),
#     'PRC_DS_REF': ('N/A', 1, 'quarterly'), # no specified market. runs fine like this
#     'PRC_CD_INTVL_LMP': ('RTM', 1, 10), # default
#     'PRC_CD_SPTIE_LMP': ('RTM', 3, 10), 
#     'PRC_RTM_LAP': ('RTM', 6, 60),
# }

map = {
    ('DAM', 60): ('PRC_LMP', 1), # default
    ('DAM', 60): ('PRC_SPTIE_LMP', 4), # what is the difference with this one?
    ('RTM', 5): ('PRC_INTVL_LMP', 1),
    ('HASP', 15): ('PRC_HASP_LMP', 1),
    ('RTPD', 15): ('PRC_RTPD_LMP', 2),
    ('N/A', 'quarterly'): ('PRC_DS_REF', 1), # no specified market. runs fine like this
    ('RTM', 10): ('PRC_CD_INTVL_LMP', 1), # default
    ('RTM', 10): ('PRC_CD_SPTIE_LMP', 3), # what is the difference with this one?
    ('RTM', 60): ('PRC_RTM_LAP', 6)
}
market_run_id = input('Market Type (DAM, RTM, HASP, RTPD): ')
interval = input('Interval (5, 10, 15, 60, quarterly): ')
if interval != 'quarterly':
    interval = int(interval) # changing to an int if not quarterly
queryname, version = map.get((market_run_id, interval), ('unknown', 'unknown')) # unknown is default val (means there is a error)


# queryname = input('Select Report Type: ')
# market_run_id, version = map[queryname] # setting parameters for market and version based on dictionary

startdate = '20250527' # input('Enter a start date (YYYY/MM/DD): ').replace('/', '')
enddate = '20250528' # input('Enter an end date (YYYY/MM/DD): ').replace('/', '')
startdatetime = startdate+'T07:00-0000'
enddatetime = enddate+'T08:00-0000'

url = "http://oasis.caiso.com/oasisapi/SingleZip"

node = '0096WD_7_N001' # input('Specify a node. Separate multiple nodes with a comma: ').replace(' ', '')
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
