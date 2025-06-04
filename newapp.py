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

# all the functions
def backend(market_run_id, interval, startdate, enddate, sptie): # actually pulls data
    # API Calling Function
    def pull_request(startdate, enddate): # remove queryname later
        node=node_var.get()
        startdate = int(startdate.strftime('%Y%m%d')) # updating date format
        enddate = int(enddate.strftime('%Y%m%d'))
        url = "http://oasis.caiso.com/oasisapi/SingleZip"
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
        # print(response.url)

        try:
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

        elif 'INTERVAL_START_GMT' in df.columns: # if report type is PRC_RTM_LAP
            df = df.sort_values(['INTERVAL_START_GMT'])
            df['INTERVAL_START_GMT'] = df['INTERVAL_START_GMT'].str.replace(':00-00:00', '').str.replace('T', ' ')
            df['INTERVAL_END_GMT'] = df['INTERVAL_END_GMT'].str.replace(':00-00:00', '').str.replace('T', ' ')
            df['DATA_ITEM'] = df['DATA_ITEM'].replace({'LMP_PRC': 'LMP', 'LMP_CONG_PRC': 'Congestion', 'LMP_ENE_PRC':'Energy', 'LMP_LOSS_PRC': 'Loss', 'LMP_GHG_PRC': 'Greenhouse Gas'})
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
        ('RTM', 5, 'N'): ('PRC_INTVL_LMP', 3),
        ('HASP', 15, 'N'): ('PRC_HASP_LMP', 1),
        ('RTPD', 15, 'N'): ('PRC_RTPD_LMP', 2),
        ('', 'quarterly', 'N'): ('PRC_DS_REF', 3), # no specified market. runs fine like this
        ('RTM', 10, 'N'): ('PRC_CD_INTVL_LMP', 1), # default
        ('RTM', 10, 'Y'): ('PRC_CD_SPTIE_LMP', 3), # uses a different set of nodes
        ('RTM', 60, 'N'): ('PRC_RTM_LAP', 6)
    }
    
    queryname, version = map.get((market_run_id, interval, sptie), ('unknown', 'unknown')) # unknown is default val (means there is a error)

    startdate = datetime.strptime(startdate, '%m/%d/%y').date() # formats it to work with datetime package
    enddate = datetime.strptime(enddate, '%m/%d/%y').date()
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
        root.after(3000, root.destroy) # quits 3 seconds after finishing

    if difference.days <= 30:
        print(f'Pulling data for {startdate} to {enddate}.')
        pull_request(startdate, enddate)
        cleanFile('pull#0.csv')
        print('Done.')
        root.after(3000, root.destroy) # quits 3 seconds after finishing

# button functions
def submit(): # handles user inputs and checks for SPTIE
    market_run_id=market_type_var.get()
    interval=interval_var.get()

    if interval != 'quarterly':
        interval = int(interval) # changing to an int if not quarterly

    if (market_run_id == 'DAM' and interval == 60) or (market_run_id =='RTM' and interval == 10):
        sptie_label.grid(row=5, column=1)
        sptie_entry.grid(row=5,column=2)
    else:
        sptie_var.set('N') # default to no SPTIE if there isn't an option for SPTIE
        sptie_label.grid_remove()
        sptie_entry.grid_remove()
    

    sptie_choice = tk.Button(root, text='Pull Data', command=lambda: pullmydata(market_run_id, interval, startdate, enddate))
    sptie_choice.grid(row=6,column=2)

    market_type_var.set("") # not sure what these are here for
    interval_var.set("")

def pullmydata(market_run_id, interval, startdate, enddate): # final button to pull and create the file
    sptie=sptie_var.get()
    finished_label = tk.Label(root, text=f'Finished!')
    finished_label.grid(row=9,column=1)
    backend(market_run_id, interval, startdate, enddate, sptie) # need to add node


def findStartDate(): # need to alter so I can choose start and end date with same calendar
    global startdate
    startdate = cal.get_date()
    startdate_label.config(text=f'Start date: {startdate}')

def findEndDate(): # need to alter so I can choose start and end date with same calendar
    global enddate
    enddate = cal.get_date()
    enddate_label.config(text=f'End date: {enddate}')

def select_output_file(): # still not working:(
    global output_file_path
    directory = filedialog.askdirectory(title='Select output directory')
    if directory:
        output_file_path = directory
        output_file_label.config(text=directory)
    else:
        output_file_label.config(text='No directory selected yet')

# tkinter program
root=tk.Tk() # opening/initializing program
root.geometry("800x600")# setting the windows size

# declaring string variable for storing MRID and interval- defining as a string?
market_type_var=tk.StringVar() 
interval_var=tk.StringVar()
sptie_var=tk.StringVar()
node_var=tk.StringVar()

startdate = None # initializing
enddate = None

# widgets
MRID_label = tk.Label(root, text = 'Market Type:', font=('calibre',10, 'bold'))
MRID_entry = tk.Entry(root,textvariable = market_type_var, font=('calibre',10,'normal'))
MRIDoptions_label = tk.Label(root, text='DAM, RTM, HASP, or RTPD', font=('calibre',10))
 
intvl_label = tk.Label(root, text = 'Interval:', font = ('calibre',10,'bold'))
intvl_entry = tk.Entry(root, textvariable = interval_var, font = ('calibre',10,'normal'))
intvloptions_label = tk.Label(root, text='5, 10, 15, 60, quarterly', font=('calibre',10))

cal = Calendar(root, selectmode ='day',
            year=2024, month =1, # defaults
            day = 1)

chooseStartDate = Button(root, text='Choose Start Date', command=findStartDate)
chooseEndDate = Button(root, text='Choose End Date', command=findEndDate)

startdate_label = tk.Label(root, text= 'Start Date: ') 
enddate_label = tk.Label(root, text='End Date: ')

node_label = tk.Label(root, text='Node(s)')
node_entry = tk.Entry(root, textvariable = node_var, font=('calibre', 10))

# def show():
#     lbl.config(text=cb.get())

# # Dropdown options  
# a = ["node1", "node2", "node3", "node4", "node5"]

# # Combobox  
# cb = ttk.Combobox(root, values=a)
# cb.set("Select node(s)")
# lbl = Label(root, text=" ")
# lbl.grid(row=7,column=2)

sptie_label = tk.Label(root, text='Do you want SPTIE data? (Y/N): ', font=('calibre',10))
sptie_entry = tk.Entry(root,textvariable = sptie_var, font=('calibre',10))

sub_btn=tk.Button(root,text = 'Submit', command = submit) # submit is calling 'submit' function (gets user inputs)

output_file_button = tk.Button(root, text='Select Output File Path', command=select_output_file)
output_file_label = tk.Label(root, text='No file selected yet')

# grid 
cal.grid(row=0,column=0)
chooseStartDate.grid(row=1,column=0) 
chooseEndDate.grid(row=2,column=0)
MRID_label.grid(row=1, column=1)
intvl_label.grid(row=2,column=1)
MRID_entry.grid(row=1, column=2)
intvl_entry.grid(row=2, column=2)
node_label.grid(row=5, column=1)
node_entry.grid(row=5,column=2)
# cb.grid(row=6,column=1)
sub_btn.grid(row=6,column=2)
MRIDoptions_label.grid(row=1,column=3)
intvloptions_label.grid(row=2,column=3)
startdate_label.grid(row=3, column=1)
enddate_label.grid(row=4, column=1)
output_file_button.grid(row=4, column=0)
output_file_label.grid(row=5, column=0)


root.mainloop() # performing an infinite loop for the window to display