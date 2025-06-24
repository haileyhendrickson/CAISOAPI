import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_excel('HASP 06-23-2025 1314.xlsx')

# y axis = df['LMP']
# x axis = what percent of the day/year that takes up

# QUESTION: do we want an avg daily/monthly curve, or avg yearly, or total of the pull? Maybe create a macro of dates?
    # play around with it for now

df = df.sort_values('LMP', ascending=False) # sorting by price high to low
print(df.info())
duration_counts = df['LMP'].value_counts()
total_count = df['LMP'].value_counts().sum()
df['duration_count'] = df['LMP'].map(duration_counts) # duration is going to be the % of time it exists in the df, plus what has already occured
print(total_count)
df['percent'] = df['duration_count']/total_count # percentage value
df['xval'] = np.nan
total_percent = 0 # initializing this
while total_percent <= 1:
    for row in df.itertuples(): # need to use row here somewhere 
            current_percent = row.percent
            total_percent += current_percent
            df.at[row.Index, 'xval'] = total_percent

print(df.head())
df.to_csv('test.csv')

plt.plot(df['xval'], df['LMP'])
plt.show()