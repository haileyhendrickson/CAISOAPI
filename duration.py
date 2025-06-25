import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openpyxl
from openpyxl import Workbook
from openpyxl.chart import Reference, ScatterChart, Series

def duration_chart(filename):
    # cleaning to get chart columns
    df = pd.read_excel(filename)
    df = df.sort_values('LMP', ascending=False) # sorting by price/LMP high to low
    duration_counts = df['LMP'].value_counts() # counting how many there are of each LMP value
    total_count = df['LMP'].value_counts().sum() # counting how many values total
    df['duration_count'] = df['LMP'].map(duration_counts) # this represents how many there are of that specific value
    df['percent'] = df['duration_count']/total_count # percentage value
    chart_lmp = df[['LMP', 'percent']].drop_duplicates().copy() # making sure we aren't counting percents more than once (if a LMP value exists multiple times)
    chart_lmp['xval'] = chart_lmp['percent'].cumsum() # cumulative sum adds the rows value to all the previous rows values
    xval_map = dict(zip(chart_lmp['LMP'], chart_lmp['xval'])) # creating a map of new percentages?
    df['xval'] = df['LMP'].map(xval_map) # adding to OG DF
    df = df[['LMP', 'xval']] # limiting df to only the necessary columns

    # writting to a sheet and hiding it 
    with pd.ExcelWriter(f'{output_file_path}/{market_run_id} {timestamp}.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name='Hidden Duration Chart Data', index=False) # writing data to new sheet
    
    wb = openpyxl.load_workbook(filename) # finding workbook with filename
    ws = wb['Hidden Duration Chart Data'] # referencing
    ws.sheet_state = 'hidden' # hiding the sheet

    # referencing hidden sheet to create chart
    chart = ScatterChart()
    chart.title = 'LMP Duration Chart'
    chart.y_axis.title = 'LMP $/MWhr'
    chart.x_axis.title = 'Duration'
    chart.legend = None
    data_sheet = wb['Hidden Duration Chart Data']
    xvalues = Reference(data_sheet, min_col=2, min_row=2, max_row=total_count+1)  # Assuming headers in row 1
    yvalues = Reference(data_sheet, min_col=1, min_row=2, max_row=total_count+1)
    series = Series(yvalues, xvalues, title_from_data=False)
    chart.series.append(series)

    sheet = wb['Hours Below 0'] # adding chart to below 0 sheet
    sheet.add_chart(chart, 'B6')   
    wb.save(filename) # saving workbook to original file name

filename = 'HASP 06-25-2025 1007.xlsx'
output_file_path = 'C:/Users/hhendrickson/es/caiso'
market_run_id = 'HASP'
timestamp = '06-25-2025 1007'
duration_chart(filename)




# # chart code for excel! need to connect excel wb and ws somehow

# # chart code for python matplotlib
# plt.plot(df['xval'], df['LMP']) # how to create charts in excel through python?
# plt.title('LMP Duration Curve')
# plt.xlabel('Percent of time/ from {startdate} to {enddate}')
# plt.ylabel('LMP ($MW/hr)')
# plt.show()