import pandas as pd
startdate = '2024-01-01'
enddate = '2024-12-31'
files = ['pull#1.csv', 'pull#2.csv', 'pull#3.csv', 'pull#4.csv', 'pull#5.csv', 'pull#6.csv', 'pull#7.csv', 'pull#8.csv', 'pull#9.csv', 'pull#10.csv', 'pull#11.csv', 'pull#12.csv', 'pull#13.csv', 'pull#13.csv']

df_list = [pd.read_csv(file) for file in files]
df_combined = pd.concat(df_list, ignore_index=True)
df_combined.to_csv(f'combinedFileFor{startdate}To{enddate}.csv', index=False)

# df_combined = pd.DataFrame()
# for file in files:
#     df = pd.read_csv(file)
#     df_combined = df_combined(df, ignore_index=True)
# df_combined.to_csv(f'PullFor{startdate}To{enddate}.csv', index=False)
