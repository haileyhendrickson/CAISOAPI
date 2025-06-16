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
# import datetime

# all the functions
def backend(market_run_id, startdate, enddate): # actually pulls data
    # API Calling Function
    node=node_var.get()
    def pull_request(startdate, enddate): # remove queryname later
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
        # print(response.url) # for testing purposes
        try:
            with ZipFile(BytesIO(response.content)) as z:
                for filename in z.namelist():
                    with z.open(filename) as f:
                        df = pd.read_csv(f)
                        df.to_csv(f'pull#{counter}.csv')
                        if '<?xml version="1.0" encoding="UTF-8"?>' in df.columns:
                            pass
                        else: # only appending files that pull- error handling 
                            files.append(f'pull#{counter}.csv') 
        except Exception as e: 
            print(f"Error message: {e}")

    # cleaning function!
    def cleanFile(filename):
        df = pd.read_csv(filename) # reading in file
        all_drop = ['NODE_ID_XML', 'NODE_ID', 'PNODE_RESMRID', 'OPR_DT', 'OPR_HR', 'OPR_INTERVAL', 'XML_DATA_ITEM', 'POS', 'GROUP', 'GRP_TYPE', 'MARKET_RUN_ID', 'Unnamed: 0', 'INTERVAL_START_TIME']
        valid_columns = [col for col in all_drop if col in df.columns]
        df = df.drop(columns=valid_columns)
        df = df.sort_values(['INTERVALSTARTTIME_GMT']) # sorting by time/date
        df['INTERVALSTARTTIME_GMT'] = df['INTERVALSTARTTIME_GMT'].str.replace('-00:00', '').str.replace('T', ' ') # getting rid of seconds
        df['INTERVALENDTIME_GMT'] = df['INTERVALENDTIME_GMT'].str.replace('-00:00','').str.replace('T',' ') # getting rid of seconds
        # conditional cleaning
        if 'LMP_TYPE' in df.columns:
                df['LMP_TYPE'] = df['LMP_TYPE'].replace({'LMP': 'LMP', 'MCC': 'Congestion', 'MCE':'Energy', 'MCL': 'Loss', 'MGHG': 'Greenhouse Gas'})
        if 'MW' in df.columns:
            df['MW'] = df['MW'].round(4)
        if 'VALUE' in df.columns:
            df['VALUE'] = df['VALUE'].round(4)
        if 'PRC' in df.columns:
            df['PRC'] = df['PRC'].round(4)
        df[['Year', 'Month','Day']] = df['INTERVALSTARTTIME_GMT'].str.split('-',expand=True)
        df[['Day', 'Time']] = df['Day'].str.split(' ',expand=True)
        df[['Hour (GMT)','Minute', 'Seconds']] = df['Time'].str.split(':',expand=True)
        df = df.drop(columns=['Time', 'Seconds'])
        df.to_csv(filename) # should replace file with cleaned version

    # hourly average function
    def hourly_average(filename): # creating a new file for hourly averages
        df = pd.read_excel(filename)
        if market_run_id == 'HASP': # doesn't have greenhouse gas
            df_avg = df.groupby(['NODE', 'Year', 'Month', 'Day', 'Hour (GMT)'], as_index=False)[['Congestion', 'Energy', 'LMP', 'Loss']].mean()
        else:
            df_avg = df.groupby(['NODE', 'Year', 'Month', 'Day', 'Hour (GMT)'], as_index=False)[['Congestion', 'Energy', 'Greenhouse Gas', 'LMP', 'Loss']].mean()

        with pd.ExcelWriter(f'{output_file_path}/{market_run_id} {timestamp}.xlsx', engine='openpyxl', mode='a') as writer:
            df_avg.to_excel(writer, sheet_name='Hourly Average', index=False)

    # user inputs map
    map = {
        ('DAM'): ('DAM', 'PRC_LMP', 1), 
        ('RTM'): ('RTM', 'PRC_INTVL_LMP', 3),
        ('HASP'): ('HASP', 'PRC_HASP_LMP', 1),
        ('FFM'): ('RTPD', 'PRC_RTPD_LMP', 2,), 
    }
    
    market_run_id, queryname, version = map.get((market_run_id), ('unknown')) 

    startdate = datetime.strptime(startdate, '%m/%d/%y').date() # formats it to work with datetime package
    enddate = datetime.strptime(enddate, '%m/%d/%y').date()
    difference = enddate - startdate # counts days in between
    days = difference.days # making a counter for my loop bc .days is readonly

    # logic that breaks the whole date range into chunks of 30 days to comply with the API
    files = [] # creating an empty list for my files
    df_list = []
    counter = 0 # initializing, used to label different files
    timestamp = datetime.now()
    timestamp = timestamp.strftime('%m-%d-%Y %H%M')
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
        
        df_combined = pd.concat(df_list, ignore_index=True) # combining 30 day chunks
        # mild cleaning for combined file
        cond_drop = ['Unnamed: 0.1', 'Unnamed: 0']
        conditional_drop = [col for col in cond_drop if col in df_combined.columns]
        df_combined = df_combined.drop(columns=conditional_drop)
        df_combined = df_combined.drop_duplicates() # dropping duplicate 
        if 'MW' in df_combined.columns: # this one will do nothing for the DAM pull, except maybe make a duplicate page
            df_combined = pd.pivot_table(df_combined, values='MW', index=['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Day', 'Hour', 'Minute'], columns='LMP_TYPE')
        if 'VALUE' in df_combined.columns:
            df_combined = pd.pivot_table(df_combined, values='VALUE', index=['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Day', 'Hour', 'Minute'], columns='LMP_TYPE')
        if 'PRC' in df_combined.columns:
            df_combined = pd.pivot_table(df_combined, values='PRC', index=['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Day', 'Hour', 'Minute'], columns='LMP_TYPE')
        df_combined = df_combined.reset_index()
        df_combined.to_excel(f'{output_file_path}/{market_run_id} {timestamp}.xlsx', index=False)
        hourly_average(f'{output_file_path}/{market_run_id} {timestamp}.xlsx')
        status_lbl.configure(text='Finished!')
        root.update()

    if difference.days <= 30:
        print(f'Pulling data for {startdate} to {enddate}.')
        pull_request(startdate, enddate)
        cleanFile('pull#0.csv')
        df = pd.read_csv('pull#0.csv')
        if 'MW' in df.columns: # this one will do nothing for the DAM pull
            df = pd.pivot_table(df, values='MW', index=['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Day', 'Hour', 'Minute'], columns='LMP_TYPE')
        if 'VALUE' in df.columns:
            df = pd.pivot_table(df, values='VALUE', index=['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Day', 'Hour', 'Minute'], columns='LMP_TYPE')
        if 'PRC' in df.columns:
            df = pd.pivot_table(df, values='PRC', index=['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Day', 'Hour', 'Minute'], columns='LMP_TYPE')
        df = df.reset_index()
        df.to_excel(f'{output_file_path}/{market_run_id} {timestamp}.xlsx', index=False)    
        hourly_average(f'{output_file_path}/{market_run_id} {timestamp}.xlsx')    
        status_lbl.configure(text='Finished!')
        root.update()

   
# button functions
def submit(): # runs all of the backend code
    status_lbl.configure(text='Running...')
    root.update() # updating status label
    market_run_id=MRIDDropdown.get()
    
    backend(market_run_id, startdate, enddate)

def findStartDate(): # for selecting the start date
    global startdate
    startdate = cal.get_date()
    startdate_label.configure(text=f'Start date: {startdate}')

def findEndDate(): # for selecting the end date
    global enddate
    enddate = cal.get_date()
    enddate_label.configure(text=f'End date: {enddate}')

def select_output_file(): # for selecting output file path
    global output_file_path
    directory = filedialog.askdirectory(title='Select output directory')
    if directory:
        output_file_path = directory
        output_file_label.configure(text=directory)
    else:
        output_file_label.configure(text='No directory selected yet')

def update_report_lbl(choice):
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

# grid 
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