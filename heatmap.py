import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import openpyxl
from openpyxl.formatting.rule import ColorScaleRule


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
    pivot = df.pivot_table(index='Month', columns='Hour (MST)', values='LMP', aggfunc='mean') # creating a new table section df
    with pd.ExcelWriter(f'{output_file_path}/{filename}', engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        pivot.to_excel(writer, sheet_name='Hourly Average', startrow=2, startcol=12, index=False) # adding to hourly avg sheet

    heatmap_range = 'M4:AJ16' # range of heatmap to color
    color_scale_rule = ColorScaleRule(
        start_type='min', start_value=None, start_color='0000FF00', # red for minimum value
        end_type='max', end_value=None, end_color='00FF0000' # green for maximum value
    )
    wb = openpyxl.load_workbook(filename)
    sheet = wb['Hourly Average']
    sheet.conditional_formatting.add(heatmap_range, color_scale_rule)
    wb.save(filename)

output_file_path = 'C:/Users/hhendrickson/es/caiso'
market_run_id = 'HASP'
timestamp = '1340'
hourly_average('HASP 06-26-2025 1340.xlsx')