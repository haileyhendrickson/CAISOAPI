import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

df = pd.read_excel('HASP 06-18-2025 1102.xlsx')

df['INTERVALSTARTTIME_GMT'] = pd.to_datetime(df['INTERVALSTARTTIME_GMT']).dt.floor('15T') # makes it some sort of set so I can subtact it later
full_range = pd.date_range(df['INTERVALSTARTTIME_GMT'].min(), df['INTERVALSTARTTIME_GMT'].max(), freq='15T') # finding all intervals I shoudl have

missing = set(full_range) - set(df['INTERVALSTARTTIME_GMT']) # taking out values I do have, finding missing rows
print(sorted(missing)) # found the mising values!! 

# set new int start time that incoudes these missing values, and backfill
newdf = df.reindex(full_range)

print(full_range)
# print(df.isnull().sum())

