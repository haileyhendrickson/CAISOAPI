import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

df = pd.read_excel('HASP 06-18-2025 1102.xlsx')

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


