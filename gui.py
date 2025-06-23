import tkinter as tk
from tkinter import filedialog, ttk
from tkinter import *
from tkcalendar import Calendar
from customtkinter import *
import pandas as pd 
import requests
from zipfile import ZipFile
from io import BytesIO
from datetime import date, timedelta, time, datetime
import time
import sys


# all backend code
def backend(market_run_id, startdate, enddate): # Pulls, cleans, and formats data into the excel file.
    node=node_var.get()
    node = node.replace(' ', '')
    # API Calling Function
    def pull_request(startdate, enddate): # calls each 30 day chunk and adds it to a list of files
        startdate = int(startdate.strftime('%Y%m%d')) # updating date format
        enddate = int(enddate.strftime('%Y%m%d'))
        url = "http://oasis.caiso.com/oasisapi/SingleZip"
        params = {
            "resultformat": 6, # should always be this- creates a CSV
            "queryname": queryname, # locational marginal prices
            "startdatetime": f'{startdate}T00:00-0000', 
            "enddatetime": f'{enddate}T00:00-0000', 
            "market_run_id": market_run_id,
            "version": version,  
            "node": node,
            }

        response = requests.get(url, params=params)
        try: # reading the file
            with ZipFile(BytesIO(response.content)) as z:
                for filename in z.namelist():
                    with z.open(filename) as f:
                        df = pd.read_csv(f) 
                        df.to_csv(f'pull#{counter}.csv') # creating chunk
                        if '<?xml version="1.0" encoding="UTF-8"?>' in df.columns:
                            pass
                        else: # only appending files that pull- error handling 
                            files.append(f'pull#{counter}.csv') # creating a list of all files I need to combine
        except Exception as e: # if there are errors- usually doesn't come to this. can probably delete
            print(f"Error message: {e}")

    # cleaning function!
    def cleanFile(filename):
        df = pd.read_csv(filename) # reading in file
        all_drop = ['NODE_ID_XML', 'NODE_ID', 'PNODE_RESMRID', 'OPR_DT', 'OPR_HR', 'OPR_INTERVAL', 'XML_DATA_ITEM', 'POS', 'GROUP', 'GRP_TYPE', 'MARKET_RUN_ID', 'Unnamed: 0', 'INTERVAL_START_TIME'] # dropping unneeded columns
        valid_columns = [col for col in all_drop if col in df.columns]
        df = df.drop(columns=valid_columns) # dropping conditionally- if they are in the df, they are dropped. prevents errors. 
        df = df.sort_values(['INTERVALSTARTTIME_GMT']) # sorting by time/date
        df['INTERVALSTARTTIME_GMT'] = df['INTERVALSTARTTIME_GMT'].str.replace('-00:00', '').str.replace('T', ' ') # getting rid of seconds
        df['INTERVALENDTIME_GMT'] = df['INTERVALENDTIME_GMT'].str.replace('-00:00','').str.replace('T',' ') # getting rid of seconds
        # conditional cleaning
        if 'LMP_TYPE' in df.columns: # making LMP_TYPE more readable
                df['LMP_TYPE'] = df['LMP_TYPE'].replace({'LMP': 'LMP', 'MCC': 'Congestion', 'MCE':'Energy', 'MCL': 'Loss', 'MGHG': 'Greenhouse Gas'})
        if 'MW' in df.columns: # rounding DAM and HASP
            df['MW'] = df['MW'].round(4)
        if 'VALUE' in df.columns:# rounding RTM
            df['VALUE'] = df['VALUE'].round(4)
        if 'PRC' in df.columns:# rounding FMM
            df['PRC'] = df['PRC'].round(4)
        # splitting date into smaller columns for readability and grouping
        df[['Year', 'Month','Day']] = df['INTERVALSTARTTIME_GMT'].str.split('-',expand=True)
        df[['Day', 'Time']] = df['Day'].str.split(' ',expand=True)
        df[['Hour (GMT)','Minute', 'Seconds']] = df['Time'].str.split(':',expand=True)
        df = df.drop(columns=['Time', 'Seconds']) # ditching time and seconds
        df.to_csv(filename) # replacing file with cleaned version

    # missing values function
    def fill_missing_values(filename):
        df = pd.read_excel(filename)
        # finding and creating rows for missing intervals
        df['INTERVALSTARTTIME_GMT'] = pd.to_datetime(df['INTERVALSTARTTIME_GMT']).dt.floor('15min') # makes it some sort of set so I can subtact it later
        full_range = pd.date_range(start=df['INTERVALSTARTTIME_GMT'].min(), end=df['INTERVALSTARTTIME_GMT'].max(), freq='15min') # finding all intervals I should have
        full_df = pd.DataFrame({'INTERVALSTARTTIME_GMT': full_range}) # df for all intervals I need
        if 'Greenhouse Gas' in full_df.columns: # conditional logic for HASP
            result = full_df.merge( # combining data with full intervals, putting in nulls for vals in rows that had missing intervals 
                df[['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Hour (GMT)', 'Minute','Congestion', 'Energy', 'Loss', 'Greenhouse Gas', 'LMP']],  # Include original data columns
                on='INTERVALSTARTTIME_GMT',
                how='outer'
            )
        else:
            result = full_df.merge( # combining data with full intervals, putting in nulls for vals in rows that had missing intervals 
                df[['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Hour (GMT)', 'Minute','Congestion', 'Energy', 'Loss', 'LMP']],  # Include original data columns
                on='INTERVALSTARTTIME_GMT',
                how='outer'
            )
        # filling in missing values
        interval_end = result['INTERVALSTARTTIME_GMT'] + pd.Timedelta(minutes=15) # finding starttime and adding 15 minutes
        result['INTERVALENDTIME_GMT']=result['INTERVALENDTIME_GMT'].fillna(interval_end) # filling in empty values
        result = result.sort_values(['INTERVALSTARTTIME_GMT', 'NODE']) # making sure it is sorted by node so I can backfill
        result['NODE'] = result['NODE'].bfill() # backfilling node
        result['INTERVALSTARTTIME_GMT'] = result['INTERVALSTARTTIME_GMT'].astype(str) # changing start time from date to string so I can split it
        for row in result: # filtering through all rows
            if result['INTERVALENDTIME_GMT'].isnull: # if it has missing values, fill them in!
                result[['Year', 'Month','Day']] = result['INTERVALSTARTTIME_GMT'].str.split('-',expand=True) # splitting interval to make yr, mnth, hr, etc
                result[['Day', 'Time']] = result['Day'].str.split(' ',expand=True)
                result[['Hour (GMT)','Minute', 'Seconds']] = result['Time'].str.split(':',expand=True)
        result = result.drop(columns=['Time', 'Seconds'])
        # filling in LMP values
        result = result.sort_values(['Hour (GMT)', 'Minute'])
        if 'Greenhouse Gas' in result.columns: # conditional logic for HASP
            LMP_list = ['Congestion', 'Energy', 'Loss', 'Greenhouse Gas', 'LMP']    
        else:
            LMP_list = ['Congestion', 'Energy', 'Loss', 'LMP']
        for column in LMP_list: # making a for loop for efficiency purposes    
            result[column] = result[column].bfill() # can backfill here because of the new sorting- takes previous day's same hour and minute intvl price.
        result = result.sort_values('INTERVALSTARTTIME_GMT') # setting to original sorting
        # reordering columns 
        if 'Greenhouse Gas' in result.columns: 
            result = result[['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Day', 'Hour (GMT)', 'Minute','Congestion', 'Energy', 'Loss', 'Greenhouse Gas', 'LMP' ]]
        else:
            result = result[['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Day', 'Hour (GMT)', 'Minute','Congestion', 'Energy', 'Loss', 'LMP' ]]
        result.to_excel(filename) # should replace file with the filled version

    # monthly average sheet function
    def monthly_average(filename):
        df = pd.read_excel(filename)
        if market_run_id == 'HASP': # doesn't have greenhouse gas
            df_avg = df.groupby(['NODE', 'Year', 'Month', 'Hour (GMT)'], as_index=False)[['Congestion', 'Energy', 'LMP', 'Loss']].mean() # grouping
            df_avg = df_avg[['NODE', 'Year', 'Month', 'Hour (GMT)', 'Congestion', 'Energy', 'Loss', 'LMP']] # reordering column names
        else:
            df_avg = df.groupby(['NODE', 'Year', 'Month', 'Hour (GMT)'], as_index=False)[['Congestion', 'Energy', 'Greenhouse Gas', 'LMP', 'Loss']].mean() # grouping
            df_avg = df_avg[['NODE', 'Year', 'Month', 'Hour (GMT)', 'Congestion', 'Energy', 'Greenhouse Gas', 'Loss', 'LMP']] # reordering column names
        with pd.ExcelWriter(f'{output_file_path}/{market_run_id} {timestamp}.xlsx', engine='openpyxl', mode='a') as writer: # adding sheet to excel file
            df_avg.to_excel(writer, sheet_name='Monthly Average', index=False)       

    # hourly average sheet function
    def hourly_average(filename): # creating a new sheet in the same excel file for hourly averages
        df = pd.read_excel(filename)
        if market_run_id == 'HASP': # doesn't have greenhouse gas
            df_avg = df.groupby(['NODE', 'Year', 'Month', 'Day', 'Hour (GMT)'], as_index=False)[['Congestion', 'Energy', 'LMP', 'Loss']].mean() # grouping
            df_avg = df_avg[['NODE', 'Year', 'Month', 'Day', 'Hour (GMT)', 'Congestion', 'Energy', 'Loss', 'LMP']] # reordering column names
        else:
            df_avg = df.groupby(['NODE', 'Year', 'Month', 'Day', 'Hour (GMT)'], as_index=False)[['Congestion', 'Energy', 'Greenhouse Gas', 'LMP', 'Loss']].mean() # grouping
            df_avg = df_avg[['NODE', 'Year', 'Month', 'Day', 'Hour (GMT)', 'Congestion', 'Energy', 'Greenhouse Gas', 'Loss', 'LMP']] # reordering column names
        
        count = (df_avg['LMP'] <= 0).sum()
        # chart logic here

        # writing hourly averages sheet
        with pd.ExcelWriter(f'{output_file_path}/{market_run_id} {timestamp}.xlsx', engine='openpyxl', mode='a') as writer: # adding sheet to excel file
            df_avg.to_excel(writer, sheet_name='Hourly Average', index=False) 
        # writing below 0 sheet
            row = 0
            pd.DataFrame([['Count of times LMP is below 0']]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, index=False)
            row +=1 # not adding a blank row
            pd.DataFrame([[count]]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row += 2 # adding a blank row in between
            pd.DataFrame([['Duration Curve']]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row +=1
            # df.to_excel(writer, sheet_name='Days Below 0', startrow=row, header=False, index=False) # write chart with this on

    # summary statistics sheet function
    def summary_statistics(filename): 
        df = pd.read_excel(filename)
        top5LMP = df.sort_values(by='LMP', ascending=False).head(5) # prints top 5 rows based on LMP
        min5LMP = df.sort_values(by='LMP', ascending=True).head(5) # bottom 5 rows based on LMP
        top5cong = df.sort_values(by='Congestion', ascending=False).head(5) # prints top 5 rows based on congestion
        min5cong = df.sort_values(by='Congestion', ascending=True).head(5) # bottom 5 rows based on congestion
        top5eng = df.sort_values(by='Energy', ascending=False).head(5) # prints top 5 rows based on energy
        min5eng = df.sort_values(by='Energy', ascending=True).head(5) # bottom 5 rows based on energy
        top5loss = df.sort_values(by='Loss', ascending=False).head(5) # prints top 5 rows based on loss
        min5loss = df.sort_values(by='Loss', ascending=True).head(5) # bottom 5 rows based on loss
        if 'Greenhouse Gas' in df.columns(): # conditional logic to handle GHG columns
            top5ghg = df.sort_values(by='Greenhouse Gas', ascending=False).head(5) # prints top 5 rows based on loss
            min5ghg = df.sort_values(by='Greenhouse Gas', ascending=True).head(5) # bottom 5 rows based on loss
        
        with pd.ExcelWriter(f'{output_file_path}/{market_run_id} {timestamp}.xlsx', engine='openpyxl', mode='a') as writer: # adding sheet to excel file
            # summary statistics for 4 elements of LMP
            row = 0
            pd.DataFrame([['Summary Statistics']]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row += 1
            if 'Greenhouse Gas' in df.columns():
                pd.DataFrame([[df.describe('Congestion', 'Energy', 'Loss', 'Greenhouse Gas', 'LMP')]]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            else:
                pd.DataFrame([[df.describe('Congestion', 'Energy', 'Loss', 'LMP')]]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row += 2 # adding a space in between

            # min, max 5 rows for each of the 4 LMP factors 
            pd.DataFrame([['LMP 5 highest prices']]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row+=1
            pd.DataFrame([[top5LMP]]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row+=1
            pd.DataFrame([['LMP 5 lowest prices']]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row+=1
            pd.DataFrame([[min5LMP]]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row+=2 # break
            pd.DataFrame([['Congestion 5 highest prices']]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row+=1
            pd.DataFrame([[top5cong]]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row+=1
            pd.DataFrame([['Congestion 5 lowest prices']]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row+=1
            pd.DataFrame([[min5cong]]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row+=2 # break
            pd.DataFrame([['Energy 5 highest prices']]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row+=1
            pd.DataFrame([[top5eng]]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row+=1
            pd.DataFrame([['Energy 5 lowest prices']]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row+=1
            pd.DataFrame([[min5eng]]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row+=2 # break
            pd.DataFrame([['Loss 5 highest prices']]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row+=1
            pd.DataFrame([[top5loss]]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row+=1
            pd.DataFrame([['Loss 5 lowest prices']]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row+=1
            pd.DataFrame([[min5loss]]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
            row+=2 # break
            if 'Greenhouse Gas' in df.columns(): # only add these if GHG is a column 
                pd.DataFrame([['Greenhouse Gas 5 highest prices']]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
                row+=1
                pd.DataFrame([[top5ghg]]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
                row+=1
                pd.DataFrame([['Greenhouse Gas 5 lowest prices']]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
                row+=1
                pd.DataFrame([[min5ghg]]).to_excel(writer, sheet_name = 'Days Below 0', startrow = row, header=False, index=False)
                row+=2 # break
        # maybe include a macro for readability formatting


    # user inputs map
    map = { # market name, market_run_id, query_name, version - needed for parameters
        ('DAM'): ('DAM', 'PRC_LMP', 1), 
        ('RTM'): ('RTM', 'PRC_INTVL_LMP', 3),
        ('HASP'): ('HASP', 'PRC_HASP_LMP', 1),
        ('FFM'): ('RTPD', 'PRC_RTPD_LMP', 2,), 
    }
    
    market_run_id, queryname, version = map.get((market_run_id), ('unknown')) # getting variables from map based on user input
    startdate = datetime.strptime(startdate, '%m/%d/%y').date() # formats it to work with datetime package
    enddate = datetime.strptime(enddate, '%m/%d/%y').date()
    difference = enddate - startdate # counts days in between
    days = difference.days # making a counter for my loop bc .days is readonly

    # logic for using the API, cleaning, and formatting as an xlsx file.
    files = [] # creating an empty list for my csv files 
    df_list = [] # empty list that stores the actual rows of the files later (for concatenation)
    counter = 0 # initializing, used to label different files
    timestamp = datetime.now() # using for filename
    timestamp = timestamp.strftime('%m-%d-%Y %H%M')

    if difference.days > 30: # logic that breaks the whole date range into chunks of 30 days to comply with the API
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
    
        # combining files and cleaning them up a little
        df_combined = pd.concat(df_list, ignore_index=True) # combining 30 day chunks
        cond_drop = ['Unnamed: 0.1', 'Unnamed: 0'] # dropping these if they exist
        conditional_drop = [col for col in cond_drop if col in df_combined.columns]
        df_combined = df_combined.drop(columns=conditional_drop)
        df_combined = df_combined.drop_duplicates() # dropping duplicate 

        # pivoting table and reordering columns (for first sheet)
        if 'MW' in df_combined.columns: # this one will do nothing for the DAM pull, except maybe make a duplicate page
            df_combined = pd.pivot_table(df_combined, values='MW', index=['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Day', 'Hour (GMT)', 'Minute'], columns='LMP_TYPE') # breaking out LMP_TYPE columns, keeping the other indexed columns
            df_combined = df_combined.reset_index() # resetting index to work with column names
            if 'Greenhouse Gas' in df_combined.columns: # DAM 
                df_combined = df_combined[['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Day', 'Hour (GMT)', 'Minute', 'Congestion', 'Energy', 'Greenhouse Gas', 'Loss', 'LMP']]
            else: # HASP 
                df_combined = df_combined[['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Day', 'Hour (GMT)', 'Minute', 'Congestion', 'Energy', 'Loss', 'LMP']]
        if 'VALUE' in df_combined.columns: # RTM , I think
            df_combined = pd.pivot_table(df_combined, values='VALUE', index=['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Day', 'Hour (GMT)', 'Minute'], columns='LMP_TYPE')
            df_combined = df_combined.reset_index()
            df_combined = df_combined[['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Day', 'Hour (GMT)', 'Minute', 'Congestion', 'Energy', 'Greenhouse Gas', 'Loss', 'LMP']]
        if 'PRC' in df_combined.columns: # FFM , I think
            df_combined = pd.pivot_table(df_combined, values='PRC', index=['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Day', 'Hour (GMT)', 'Minute'], columns='LMP_TYPE')
            df_combined = df_combined.reset_index()
            df_combined = df_combined[['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Day', 'Hour (GMT)', 'Minute', 'Congestion', 'Energy', 'Greenhouse Gas', 'Loss', 'LMP']]
        
        # pushing to excel file, deleting csv chunks
        df_combined.to_excel(f'{output_file_path}/{market_run_id} {timestamp}.xlsx', sheet_name=f'{market_run_id}', index=False) # writing initial report to an xlsx file
        fill_missing_values(f'{output_file_path}/{market_run_id} {timestamp}.xlsx')        
        monthly_average(f'{output_file_path}/{market_run_id} {timestamp}.xlsx') # writing and adding monthly average sheet to file        
        hourly_average(f'{output_file_path}/{market_run_id} {timestamp}.xlsx') # writing and adding hourly average sheet to file
        summary_statistics(f'{output_file_path}/{market_run_id} {timestamp}.xlsx')

        # deleting all of the csv 30 day chunk files from the folder
        if getattr(sys, 'frozen', False): # finding file path to wherever GUI is stored
            application_path = os.path.dirname(sys.executable)
        for csv in files: # deleting extra files
            filepath = os.path.join(application_path, csv) # creating path to CSV file that will populate in the GUI folder
            os.remove(filepath) # deleting files

        status_lbl.configure(text='Finished!') # updating status label 
        root.update()            

    if difference.days <= 30: # logic for user requests that are less than 30 days (doesn't need chunking)
        print(f'Pulling data for {startdate} to {enddate}.')
        pull_request(startdate, enddate)
        cleanFile('pull#0.csv')
        df = pd.read_csv('pull#0.csv')
        if 'MW' in df.columns: # this one will do nothing for the DAM pull
            df = pd.pivot_table(df, values='MW', index=['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Day', 'Hour (GMT)', 'Minute'], columns='LMP_TYPE') # breaking out LMP_TYPE columns, keeping the other indexed columns
        if 'VALUE' in df.columns:
            df = pd.pivot_table(df, values='VALUE', index=['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Day', 'Hour (GMT)', 'Minute'], columns='LMP_TYPE')
        if 'PRC' in df.columns:
            df = pd.pivot_table(df, values='PRC', index=['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Day', 'Hour (GMT)', 'Minute'], columns='LMP_TYPE')
        df = df.reset_index()
        df.to_excel(f'{output_file_path}/{market_run_id} {timestamp}.xlsx', index=False) # writing initial report to an xlsx file
        fill_missing_values(f'{output_file_path}/{market_run_id} {timestamp}.xlsx')
        monthly_average(f'{output_file_path}/{market_run_id} {timestamp}.xlsx') # writing and adding monthly average sheet to file        
        hourly_average(f'{output_file_path}/{market_run_id} {timestamp}.xlsx') # writing and adding hourly average sheet to file
        summary_statistics(f'{output_file_path}/{market_run_id} {timestamp}.xlsx')

        # deleting csv from folder
        if getattr(sys, 'frozen', False): # finding file path to wherever GUI is stored
            application_path = os.path.dirname(sys.executable)
        filepath = os.path.join(application_path, csv) # creating path to CSV file that will populate in the GUI folder
        os.remove(filepath) # deleting files

        status_lbl.configure(text='Finished!')
        root.update() # updating status label

   
# button/widget functions
def submit(): # after user gives all inputs, runs all of the backend code
    status_lbl.configure(text='Running...')
    root.update() # updating status label
    market_run_id=MRIDDropdown.get() # grabbing market_run_id based on user input
    backend(market_run_id, startdate, enddate) # calling backend code

def findStartDate(): # for selecting the start date
    global startdate
    startdate = cal.get_date()
    startdate_label.configure(text=f'Start date: {startdate}')

def findEndDate(): # for selecting the end date
    global enddate
    enddate = cal.get_date()
    enddate_label.configure(text=f'End date: {enddate}')

def select_output_file(): # for selecting excel output file path
    global output_file_path
    directory = filedialog.askdirectory(title='Select output directory')
    if directory:
        output_file_path = directory
        output_file_label.configure(text=directory) # displaying file path
    else:
        output_file_label.configure(text='No directory selected yet') # if they tried to submit without a filepath

def update_report_lbl(choice): # displays the report name, based on the user chosen market type
    if choice == 'DAM':
        reportname = 'Locational Marginal Prices'
    if choice == 'RTM':
        reportname = 'Interval Locational Marginal Prices'
    if choice == 'HASP':
        reportname = 'Hour Ahead Locational Marginal Prices'
    if choice == 'FFM':
        reportname = 'FMM Locational Marginal Prices'
    report_lbl.configure(text=f'{reportname}')
    root.update()


# tkinter program
root = CTk() # initializing window
root.geometry('800x600') # setting size
set_appearance_mode('light') # can also be light

node_var=tk.StringVar()

startdate = None # initializing
enddate = None

# widgets
MRID_label = CTkLabel(root, text = 'Market Type:', font=('Arial',15), text_color='#04033A')
MRIDDropdown = CTkComboBox(master=root, values=['DAM', 'RTM', 'HASP', 'FFM'], command=update_report_lbl)

report_lbl = CTkLabel(root, text = 'Locational Marginal Prices', font=('Arial',15), text_color='#04033A')

cal = Calendar(root, selectmode ='day',
            year=2024, month =1, # defaults
            day = 1, font=('Arial', 15))

chooseStartDate = CTkButton(root, text='Choose Start Date', command=findStartDate, corner_radius=26,fg_color='#162157', hover_color='#6D7DCF')
chooseEndDate = CTkButton(root, text='Choose End Date', command=findEndDate, corner_radius=26,fg_color='#162157', hover_color='#6D7DCF')

startdate_label = CTkLabel(root, text= 'Start Date: ', font=('Arial',15), text_color='#04033A') 
enddate_label = CTkLabel(root, text='End Date: ', font=('Arial',15), text_color='#04033A')

node_label = CTkLabel(root, text='Node(s):', font=('Arial',15), text_color='#04033A')
node_entry = CTkEntry(root, textvariable = node_var, font=('Arial',15), text_color='#04033A')

sub_btn=CTkButton(master=root,text = 'Submit', command = submit, corner_radius=32,fg_color='#162157', hover_color='#6D7DCF') 

output_file_button = CTkButton(root, text='Select Output File Path', command=select_output_file, corner_radius=32,fg_color='#162157', hover_color='#6D7DCF')
output_file_label = CTkLabel(root, text='No path selected', font=('Arial',10), text_color='#04033A')

status_lbl = CTkLabel(root, text='', font=('Arial',15), text_color='#04033A')

title_lbl = CTkLabel(root, text='CAISO OASIS DATA', font=('Arial',20, 'bold'), text_color='#04033A')

# grid- where all the widgets are displayed on the GUI
cal.grid(row=6,column=0)
chooseStartDate.grid(row=4,column=0) 
chooseEndDate.grid(row=5,column=0)
MRID_label.grid(row=1, column=1)
MRIDDropdown.grid(row=1, column=2)
node_label.grid(row=3, column=1)
node_entry.grid(row=3,column=2)
sub_btn.grid(row=6,column=2)
startdate_label.grid(row=4, column=1)
enddate_label.grid(row=5, column=1)
output_file_button.grid(row=1, column=0)
output_file_label.grid(row=2, column=0)
title_lbl.grid(row=0, column=2)
report_lbl.grid(row=2,column=2)
status_lbl.grid(row=7,column=2) 

root.mainloop() # performing an infinite loop for the window to display