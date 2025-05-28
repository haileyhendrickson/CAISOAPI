import pandas as pd 
import requests
from zipfile import ZipFile
from io import BytesIO
from datetime import date, timedelta, time

# API Calling Function
def pull_request(startdate, enddate): # remove queryname later
    url = "http://oasis.caiso.com/oasisapi/SingleZip"
    startdate = int(startdate.strftime('%Y%m%d'))
    enddate = int(enddate.strftime('%Y%m%d'))
    params = {
    "resultformat": 6, # should always be this- creates a CSV
    "queryname": queryname, # locational marginal prices
    "startdatetime": f'{startdate}T07:00-0000', 
    "enddatetime": f'{enddate}T07:00-0000', 
    "market_run_id": market_run_id,
    "version": version,  
    "node": 'AMARGOSA_1_SN001'
    }
    try:
        response = requests.get(url, params=params)
        # print(response.url)
        with ZipFile(BytesIO(response.content)) as z:
            for filename in z.namelist():
                with z.open(filename) as f:
                    df = pd.read_csv(f)
                    df.to_csv(f'pull#{counter}.csv')
                    if difference.days != 30:
                        pass # adding this in so there aren't appending issues with small pulls
                        files.append(f'pull#{counter}.csv')
    except Exception as e: 
        print(f"Error message: {e}")
    

# cleaning function!
def cleanFile(filename):
    df = pd.read_csv(filename) # reading in file
    df = df.drop(columns = ['NODE_ID_XML', 'NODE_ID', 'PNODE_RESMRID', 'OPR_DT', 'MARKET_RUN_ID', 'Unnamed: 0']) # dropping redundant columns
    df = df.sort_values(['LMP_TYPE', 'INTERVALSTARTTIME_GMT'])
    df['LMP_TYPE'] = df['LMP_TYPE'].replace({'LMP': 'LMP', 'MCC': 'Congestion', 'MCE':'Energy', 'MCL': 'Loss', 'MGHG': 'Greenhouse Gas'})
    df['INTERVALSTARTTIME_GMT'] = df['INTERVALSTARTTIME_GMT'].str.replace('00-00:00', '').str.replace('T', ' ') # getting rid of seconds
    df['INTERVALENDTIME_GMT'] = df['INTERVALENDTIME_GMT'].str.replace('-00:00','').str.replace('T',' ') # getting rid of seconds
    df.to_csv(filename) # should replace file with cleaned version

# user inputs map
map = {
    ('DAM', 60): ('PRC_LMP', 1), # default
    # ('DAM', 60): ('PRC_SPTIE_LMP', 4), # what is the difference with this one?
    ('RTM', 5): ('PRC_INTVL_LMP', 1),
    ('HASP', 15): ('PRC_HASP_LMP', 1),
    ('RTPD', 15): ('PRC_RTPD_LMP', 2),
    ('N/A', 'quarterly'): ('PRC_DS_REF', 1), # no specified market. runs fine like this
    ('RTM', 10): ('PRC_CD_INTVL_LMP', 1), # default
    # ('RTM', 10): ('PRC_CD_SPTIE_LMP', 3), # what is the difference with this one?
    ('RTM', 60): ('PRC_RTM_LAP', 6)
}
market_run_id = input('Market Type (DAM, RTM, HASP, RTPD): ')
interval = input('Interval (5, 10, 15, 60, quarterly): ')
if interval != 'quarterly':
    interval = int(interval) # changing to an int if not quarterly
queryname, version = map.get((market_run_id, interval), ('unknown', 'unknown')) # unknown is default val (means there is a error)
node = input('Specify a node. Separate multiple nodes with a comma: ').replace(' ', '')


# user inputs for date yyyy-mm-dd
startdate = input('Start date (yyyy-mm-dd): ')
enddate = input('End date (yyyy-mm-dd): ')
startdate = date.fromisoformat(startdate) # formats it to work with datetime package
enddate = date.fromisoformat(enddate)
difference = enddate - startdate # counts days in between
days = difference.days # making a counter for my loop bc .days is readonly

files = [] # creating an empty list for my files
df_list = []
counter = 0 # initializing, probably delete later
if difference.days > 30:
    while days > 0: # until we reach the end date
        if days < 30: # when we get below 30 days left
            pull_request(startdate, enddate)
            print(f'Pulling data for {startdate} to {enddate}.') 
            break # ending loop once I get to the end date
        nextdate = startdate + timedelta(days=30) # creating a chunk
        print(f'Pulling data for {startdate} to {nextdate}.') 
        pull_request(startdate, nextdate)
        days -= 30 # updating this counter
        counter += 1 
        startdate = nextdate # update start date to be next date
    for file in files:
        cleanFile(file) # I have no stinky idea where to put this
        df_list.append(pd.read_csv(file))

    df_combined = pd.concat(df_list, ignore_index=True)
    df_combined.to_csv(f'combinedFileFor{startdate}To{enddate}.csv', index=False)
if difference.days <= 30:
    print(f'Pulling data for {startdate} to {enddate}.')
    pull_request(startdate, enddate)
    print('Done.')
