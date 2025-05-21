import pandas as pd 
import requests
from zipfile import ZipFile, BadZipFile
from io import BytesIO

# User inputs/ setting parameters
queryname = input('Select Report Type: ') # how to make a dropdown later?
if queryname == 'PRC_LMP':
    market_run_id = 'DAM'
if queryname == 'PRC_SPTIE_LMP':
    market_run_id = 'DAM'
if queryname == 'PRC_INTVL_LMP':
    market_run_id = 'RTM'
if queryname == 'PRC_HASP_LMP':
    market_run_id = 'HASP'
if queryname == 'PRC_RTPD_LMP':
    market_run_id = 'PRC_RTPD_LMP'
if queryname == 'PRC_DS_REF':
    market_run_id = '' # NO MARKET ID FOR THIS ONE   
if queryname == 'PRC_CD_INTVL_LMP':
    market_run_id = 'RTM'
if queryname == 'PRC_RTM_LAP':
    market_run_id = 'RTM'

startdate = input('Enter a start date (YYYY/MM/DD): ').replace('/', '')
enddate = input('Enter an end date (YYYY/MM/DD): ').replace('/', '')
timeSelect = input('Do you want to start at a specific time? ') # add in time settings later
if timeSelect == 'Y':
    starttime = input('Enter Start time (hr:mn): ')
    starttime = f'{starttime}-0000'
    endtime = input('Enter End time (hr:mn): ')
    endtime = f'{endtime}-0000'
if timeSelect == 'N':
    starttime = '00:00-0000'
    endtime = '00:00-0000'
startdatetime = startdate+'T'+starttime
enddatetime = enddate+'T'+endtime

base_url = "http://oasis.caiso.com/oasisapi/SingleZip"

node = input('Specify a node. Separate multiple nodes with a comma. Leave blank for all nodes: ')
if node == '': # means they want all nodes
    params = {
    "resultformat": 6, # should always be this- creates a CSV
    "queryname": queryname, # determines what kind of data pull we want
    "startdatetime": startdatetime,
    "enddatetime": enddatetime,
    "market_run_id": market_run_id,
    "version": "1", # version 1 is the oldest and the safest I think
    "grp_type": "ALL_APNODES"
}
if node != '':
    node = node.replace(' ', '') # removing any spaces
    params = {
    "resultformat": 6, # should always be this- creates a CSV
    "queryname": queryname, # determines what kind of data pull we want
    "startdatetime": startdatetime,
    "enddatetime": enddatetime,
    "market_run_id": market_run_id,
    "version": "1", # version 1 is the oldest and the safest I think
    "node": node
}

# calling API
try: # using this for now for error handling
    response = requests.get(base_url, params=params)
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
except BadZipFile:
    print('Response is not a ZIP')
    print(response.content.decode(errors='replace'))
