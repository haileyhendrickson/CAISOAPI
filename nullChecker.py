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
result = full_df.merge( # combining data with full intervals, putting in nulls for vals in rows that had missing intervals 
    df[['INTERVALSTARTTIME_GMT', 'INTERVALENDTIME_GMT', 'NODE', 'Year', 'Month', 'Hour (GMT)', 'Minute','Congestion', 'Energy', 'Loss', 'LMP']],  # Include original data columns
    on='INTERVALSTARTTIME_GMT',
    how='outer'
)

result.to_csv('test.csv')
print('file created.')

# filling in missing values
interval_end = result['INTERVALSTARTTIME_GMT'] + pd.Timedelta(minutes=15) # finding starttime and adding 15 minutes
result['INTERVALENDTIME_GMT']=result['INTERVALENDTIME_GMT'].fillna(interval_end) # filling in empty values
result.sort_values(['INTERVALSTARTTIME_GMT', 'NODE']) # not sure I actually need this. sorting so I can backfill node
result['NODE'] = result['NODE'].bfill() # backfilling node bc they should be grouped together
result['INTERVALSTARTTIME_GMT'] = result['INTERVALSTARTTIME_GMT'].astype(str)
for row in result: # filtering through all rows
    if result['INTERVALENDTIME_GMT'].isnull: # if it has missing values
        result[['Year', 'Month','Day']] = result['INTERVALSTARTTIME_GMT'].str.split('-',expand=True) # splitting interval to make yr, mnth, hr, etc
        result[['Day', 'Time']] = result['Day'].str.split(' ',expand=True)
        result[['Hour (GMT)','Minute', 'Seconds']] = result['Time'].str.split(':',expand=True)

result = result.drop(columns=['Time', 'Seconds'])

result.to_csv('test.csv') # testing purposes
print('string/date columns cleaned.')

# filling in LMP values
LMP_list = ['Congestion', 'Energy', 'Loss', 'LMP']
for value in df[LMP_list]: # making a for loop for efficiency purposes
    # find previous day's value, set to object
    df[LMP_list] = df[LMP_list].fillna() # put value in fillna()