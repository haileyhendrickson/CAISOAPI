import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# hourly average sheet function
def hourly_average(filename): # creating a new sheet in the same excel file for hourly averages
    df = pd.read_excel(filename)
    if market_run_id == 'HASP': # doesn't have greenhouse gas
        df_avg = df.groupby(['NODE', 'Year', 'Month', 'Day', 'Hour (MST)'], as_index=False)[['Congestion', 'Energy', 'LMP', 'Loss']].mean().round(4) # grouping
        df_avg[['Congestion', 'Energy', 'Loss','LMP']] = df_avg[['Congestion', 'Energy', 'Loss','LMP']].round(4)
        df_avg = df_avg[['NODE', 'Year', 'Month', 'Day', 'Hour (MST)', 'Congestion', 'Energy', 'Loss', 'LMP']] # reordering column names
    else:
        df_avg = df.groupby(['NODE', 'Year', 'Month', 'Day', 'Hour (MST)'], as_index=False)[['Congestion', 'Energy', 'Greenhouse Gas', 'LMP', 'Loss']].mean().round(4) # grouping
        df_avg[['Congestion', 'Energy', 'Loss', 'Greenhouse Gas', 'LMP']] = df_avg[['Congestion', 'Energy', 'Loss', 'Greenhouse Gas' 'LMP']].round(4)            
        df_avg = df_avg[['NODE', 'Year', 'Month', 'Day', 'Hour (MST)', 'Congestion', 'Energy', 'Greenhouse Gas', 'Loss', 'LMP']] # reordering column names
    
    count = (df_avg['LMP'] < 0).sum() # counting how many hours LMP is below 0

    with pd.ExcelWriter(f'{output_file_path}/{filename}', engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        # writing hourly averages sheet
        df_avg.to_excel(writer, sheet_name='Hourly Average', index=False) # adding sheet to excel file
        # writing summary statistics sheet, using the hourly averages df
        row = 13
        pd.DataFrame([['Number of hours LMP is below 0:']]).to_excel(writer, sheet_name = 'Summary Statistics', startrow = row, header=False, index=False)
        row += 1
        pd.DataFrame([[count]]).to_excel(writer, sheet_name = 'Summary Statistics', startrow = row, header=False, index=False)
        row += 2 # adding a blank row in between
        pd.DataFrame([['Duration Curve']]).to_excel(writer, sheet_name = 'Summary Statistics', startrow = row, header=False, index=False)
        row += 1

    # heat map!
    pivot = df.pivot_table(index='Month', columns='Hour (MST)', values='LMP', aggfunc='mean')
    sns.heatmap(pivot, fmt=".1f", cmap="viridis")  # annot=True to show values      
    plt.title("Average LMP by Month and Hour")
    plt.xlabel("Hour")
    plt.ylabel("Month")
    plt.show()

output_file_path = 'C:/Users/hhendrickson/es/caiso'
market_run_id = 'HASP'
timestamp = '1340'
hourly_average('HASP 06-26-2025 1340.xlsx')