import pandas as pd 
import requests
from zipfile import ZipFile
from io import BytesIO
from datetime import date, timedelta, time
import time

# API Calling Function
def pull_request(startdate, enddate): # remove queryname later
    url = "http://oasis.caiso.com/oasisapi/SingleZip"
    startdate = int(startdate.strftime('%Y%m%d'))
    enddate = int(enddate.strftime('%Y%m%d'))
    if market_run_id == '': # reference prices is different- no market
            params = {
        "resultformat": 6, # should always be this- creates a CSV
        "queryname": queryname, # locational marginal prices
        "startdatetime": f'{startdate}T08:00-0000', 
        "enddatetime": f'{enddate}T08:00-0000', 
        "version": version,  
        "node_id": node # reference prices uses this parameter
        }
    else: 
        params = {
            "resultformat": 6, # should always be this- creates a CSV
            "queryname": queryname, # locational marginal prices
            "startdatetime": f'{startdate}T08:00-0000', 
            "enddatetime": f'{enddate}T08:00-0000', 
            "market_run_id": market_run_id,
            "version": version,  
            "node": node,
            }

    response = requests.get(url, params=params)
    try:
        # print(response.url)
        with ZipFile(BytesIO(response.content)) as z:
            for filename in z.namelist():
                with z.open(filename) as f:
                    df = pd.read_csv(f)
                    df.to_csv(f'pull#{counter}.csv')
                    # if difference.days != 30:
                    #     pass # adding this in so there aren't appending issues with small pulls
                    if '<?xml version="1.0" encoding="UTF-8"?>' in df.columns:
                        pass
                    else: # only appending files that pull- error handling for contingency dispatch
                        files.append(f'pull#{counter}.csv') 
    except Exception as e: 
        print(f"Error message: {e}")
    

# cleaning function!
def cleanFile(filename):
    df = pd.read_csv(filename) # reading in file

    if 'EFF_QTR_START_DT_GMT' in df.columns: # if the report type is reference prices
        df = df.sort_values(['EFF_QTR_START_DT_GMT']) # sort by EFF_QTR_START_DT_GMT
        df['EFF_QTR_START_DT_GMT'] = df['EFF_QTR_START_DT_GMT'].str.replace(':00-00:00', '').str.replace('T', ' ')
        df['EFF_QTR_END_DT_GMT'] = df['EFF_QTR_END_DT_GMT'].str.replace(':00-00:00','').str.replace('T',' ')
        df['EFF_QTR_START_DT'] = df['EFF_QTR_START_DT'].str.replace(':00-00:00', '').str.replace('T', ' ') 
        df['EFF_QTR_END_DT'] = df['EFF_QTR_END_DT'].str.replace(':00-00:00','').str.replace('T',' ') 

    if 'INTERVAL_START_GMT' in df.columns: # if report type is PRC_RTM_LAP
        df = df.sort_values(['INTERVAL_START_GMT'])
        df['INTERVAL_START_GMT'] = df['INTERVAL_START_GMT'].str.replace(':00-00:00', '').str.replace('T', ' ')
        df['INTERVAL_END_GMT'] = df['INTERVAL_END_GMT'].str.replace(':00-00:00', '').str.replace('T', ' ')
        df['DATA_ITEM'] = df['LMP_TYPE'].replace({'LMP_PRC': 'LMP', 'LMP_CONG_PRC': 'Congestion', 'LMP_ENE_PRC':'Energy', 'LMP_LOSS_PRC': 'Loss', 'LMP_GHG_PRC': 'Greenhouse Gas'})
        df = df.drop(columns=['OPR_DATE'])
        df = df.rename(columns={'RESOURCE_NAME': 'NODE'})

    else: # all other report types
        all_drop = ['NODE_ID_XML', 'NODE_ID', 'PNODE_RESMRID', 'OPR_DT', 'MARKET_RUN_ID', 'Unnamed: 0', 'INTERVAL_START_TIME']
        valid_columns = [col for col in all_drop if col in df.columns]
        df = df.drop(columns=valid_columns)
        df = df.sort_values(['INTERVALSTARTTIME_GMT']) # sorting by time/date
        df['INTERVALSTARTTIME_GMT'] = df['INTERVALSTARTTIME_GMT'].str.replace('-00:00', '').str.replace('T', ' ') # getting rid of seconds
        df['INTERVALENDTIME_GMT'] = df['INTERVALENDTIME_GMT'].str.replace('-00:00','').str.replace('T',' ') # getting rid of seconds
        # conditional cleaning
        if 'LMP_TYPE' in df.columns:
                df['LMP_TYPE'] = df['LMP_TYPE'].replace({'LMP': 'LMP', 'MCC': 'Congestion', 'MCE':'Energy', 'MCL': 'Loss', 'MGHG': 'Greenhouse Gas'})

    df.to_csv(filename) # should replace file with cleaned version

# user inputs map
map = {
    ('DAM', 60, 'N'): ('PRC_LMP', 1), # default
    ('DAM', 60, 'Y'): ('PRC_SPTIE_LMP', 4), # uses a different set of nodes
    ('RTM', 5, 'N'): ('PRC_INTVL_LMP', 1),
    ('HASP', 15, 'N'): ('PRC_HASP_LMP', 1),
    ('RTPD', 15, 'N'): ('PRC_RTPD_LMP', 2),
    ('', 'quarterly', 'N'): ('PRC_DS_REF', 3), # no specified market. runs fine like this
    ('RTM', 10, 'N'): ('PRC_CD_INTVL_LMP', 1), # default
    ('RTM', 10, 'Y'): ('PRC_CD_SPTIE_LMP', 3), # uses a different set of nodes
    ('RTM', 60, 'N'): ('PRC_RTM_LAP', 6)
}
market_run_id = input('Market Type (DAM, RTM, HASP, RTPD): ')
interval = input('Interval (5, 10, 15, 60, quarterly): ')
if interval != 'quarterly':
    interval = int(interval) # changing to an int if not quarterly
if (market_run_id == 'DAM' and interval == 60) or (market_run_id =='RTM' and interval == 10):
    SPTIE = input('Do you want SPTIE data? (Y/N): ') # differentiating between similar report types
else:
    SPTIE = 'N' # default to no SPTIE if there isn't an option for SPTIE
queryname, version = map.get((market_run_id, interval, SPTIE), ('unknown', 'unknown')) # unknown is default val (means there is a error)
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
            print(f'Pulling data for {startdate} to {enddate}.') 
            pull_request(startdate, enddate)
            break # ending loop once I get to the end date
        nextdate = startdate + timedelta(days=30) # creating a chunk
        print(f'Pulling data for {startdate} to {nextdate}.') 
        pull_request(startdate, nextdate)
        days -= 30 # updating this counter
        counter += 1 
        startdate = nextdate # update start date to be next date
        time.sleep(10) # avoiding query limits
    for file in files: # if tabbed over, it cleans each pull before combining, but is bad at error handling
        cleanFile(file) 
        df_list.append(pd.read_csv(file))

    df_combined = pd.concat(df_list, ignore_index=True)
    # mild cleaning for combined file
    cond_drop = ['Unnamed: 0.1', 'Unnamed: 0']
    conditional_drop = [col for col in cond_drop if col in df_combined.columns]
    df_combined = df_combined.drop(columns=conditional_drop)
    df_combined = df_combined.drop_duplicates() # dropping duplicate rows
    df_combined.to_csv(f'combinedFileFor{startdate}To{enddate}.csv', index=False)

if difference.days <= 30:
    print(f'Pulling data for {startdate} to {enddate}.')
    pull_request(startdate, enddate)
    # clean the file!!
    print('Done.')




