import pandas as pd
import numpy as np

df = pd.read_excel('RTM 06-17-2025 1546.xlsx')

print(df['LMP'].isnull().sum())
print(df['Loss'].isnull().sum())
print(df['Congestion'].isnull().sum())
print(df['Energy'].isnull().sum())
print(df['Greenhouse Gas'].isnull().sum())
print(df.head())

# I can't find any null values in DAM or RTM, 2024 or 2023. 