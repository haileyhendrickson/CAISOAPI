import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# # duration chart!
# df = pd.read_excel('HASP 06-18-2025 1102.xlsx')

# df = df.sort_values('LMP') # sorting by LMP, might not be needed
# n = len(df) # number of values
# percentage = (np.arange(1, n+1)/(n+1)) * 100 # determining percentage the value is equaled or exceeded

# # plotting
# plt.plot(percentage, df)
# plt.grid(True)
# plt.show()


market_run_id = 'HASP'
output_file_path = 'C:/Users/hhendrickson/es/caiso'
timestamp = '06-23-2025 1314'


def summary_statistics(filename): 
    df = pd.read_excel(filename)
    if 'Greenhouse Gas' in df.columns: # conditional logic for finding applicable column
        cols = ['Congestion', 'Energy', 'Loss', 'Greenhouse Gas', 'LMP']
    else:
        cols = ['Congestion', 'Energy', 'Loss', 'LMP']
        desc=df[cols].describe() # finding what I want to display

    top5LMP = df.sort_values(by='LMP', ascending=False).head(5) # prints top 5 rows based on LMP
    min5LMP = df.sort_values(by='LMP', ascending=True).head(5) # bottom 5 rows based on LMP

    with pd.ExcelWriter(f'{output_file_path}/{market_run_id} {timestamp}.xlsx', engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer: # adding sheet to excel file
        # summary statistics for 4 elements of LMP
        row = 1
        pd.DataFrame([['Summary Statistics']]).to_excel(writer, sheet_name = 'Summary Statistics', startrow = row, header=True, index=False) # title
        row += 1
        desc.to_excel(writer, sheet_name = 'Summary Statistics', startrow=row) # writing summary statistics to df
        row += 2 # adding a space in between

        # min, max 5 rows for each of the 4 LMP factors 
        pd.DataFrame([['LMP 5 highest prices']]).to_excel(writer, sheet_name = 'Summary Statistics', startrow = row, header=False, index=False)
        row+=1
        pd.DataFrame([[top5LMP]]).to_excel(writer, sheet_name = 'Summary Statistics', startrow = row, header=False, index=False)
        row+=6
        pd.DataFrame([['LMP 5 lowest prices']]).to_excel(writer, sheet_name = 'Summary Statistics', startrow = row, header=False, index=False)
        row+=1
        pd.DataFrame([[min5LMP]]).to_excel(writer, sheet_name = 'Summary Statistics', startrow = row, header=False, index=False)
        row+=6 # break


summary_statistics('HASP 06-23-2025 1314.xlsx')