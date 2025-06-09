# # space for practicing with classes, strEnum, and dictionaries


# # dictionary stuff
# market_run_map = {
#     'PRC_LMP': ('DAM', 1),
#     'PRC_SPTIE_LMP': 'DAM',
#     'PRC_INTVL_LMP': 'RTM',
#     'PRC_HASP_LMP': 'HASP',
#     'PRC_RTPD_LMP': 'RTPD',
#     'PRC_DS_REF': '', # this one doesn't have a specified market
#     'PRC_CD_INTVL_LMP': 'RTM',
#     'PRC_RTM_LAP': 'RTM',
# }
# # queryname = input('Select Report Type: ')
# people = { # list as a dictionary value
#     "PRC_LMP": ("DAM", 1),
#     "PRC_RTM_LAP": ("RTM", 6)
# }
# # Access both pieces of info
# # market_run_id, version = people[queryname] # setting parameters for market and version based on dictionary

# # combining files in a list
# import pandas as pd
# startdate = '2024-01-01'
# enddate = '2024-12-31'
# files = ['pull#1.csv', 'pull#2.csv', 'pull#3.csv', 'pull#4.csv', 'pull#5.csv', 'pull#6.csv', 'pull#7.csv', 'pull#8.csv', 'pull#9.csv', 'pull#10.csv', 'pull#11.csv', 'pull#12.csv', 'pull#13.csv', 'pull#13.csv']

# df_list = [pd.read_csv(file) for file in files]
# df_combined = pd.concat(df_list, ignore_index=True)
# df_combined.to_csv(f'combinedFileFor{startdate}To{enddate}.csv', index=False)

# # df_combined = pd.DataFrame()
# # for file in files:
# #     df = pd.read_csv(file)
# #     df_combined = df_combined(df, ignore_index=True)
# # df_combined.to_csv(f'PullFor{startdate}To{enddate}.csv', index=False)



# # datetime stuff

# from datetime import datetime, date, timedelta

# startdate = input('Enter a start date (YYYY/MM/DD): ').replace('/', '') # user input
# enddate = input('Enter an end date (YYYY/MM/DD): ').replace('/', '')
# startdate = date.fromisoformat(startdate) # formats it to work with datetime package
# enddate = date.fromisoformat(enddate)
# difference = enddate - startdate # counts days in between
# print(difference.days)

# if difference.days > 30:
#     while difference.days > 0: # until we reach the end date
#         if difference.days < 30: # when we get below 30 days left
#             pass
#             # end date needs to be original end date
#         nextdate = startdate + timedelta(days=30) # creating a chunk
#         difference.days -= 30 # updating this counter
#         # pull a file from start date to +30 days: startdate = startdate (reformat), enddate = startdate+30days (reformat)
#         startdate = nextdate # update start date to be next date
#         # if there's less than 31 days left, fix that 
# # if not, run like normal


    


# nextdate = startdate + timedelta(days=31) # adding days

# # very last bit of code, to format it back to how I need
# nextdate = nextdate.strftime('%Y%m%d') # formats it without dashes for API use



# # # class stuff
# # class ClassName:
# #     def __init__(self, query_name, market_run_id):
# #         self.query_name = query_name
# #         self.market_run_id = market_run_id
    
# # test = ClassName("PRC_LMP", "DAM")
   
# # print(test.query_name)
# # print(test.market_run_id)


# # making dual condition if statments
# name = input('name: ')
# age = int(input('age: '))
# if name == 'Hailey' and age == 22:   
#     print('true')
# else:
#     print('false')

# # cleaning
# import pandas as pd
# def cleanFile(filename):
#     # dropping redundant and uneccesary columns
#     df = pd.read_csv(filename) # reading in file

#     if 'EFF_QTR_START_DT_GMT' in df.columns: # if the report type is reference prices
#         # drop duplicate rows 
#         df = df.sort_values(['EFF_QTR_START_DT_GMT']) # sort by EFF_QTR_START_DT_GMT
#         # cleaning times
#         df['EFF_QTR_START_DT_GMT'] = df['EFF_QTR_START_DT_GMT'].str.replace(':00-00:00', '').str.replace('T', ' ')
#         df['EFF_QTR_END_DT_GMT'] = df['EFF_QTR_END_DT_GMT'].str.replace(':00-00:00','').str.replace('T',' ')
#         df['EFF_QTR_START_DT'] = df['EFF_QTR_START_DT'].str.replace(':00-00:00', '').str.replace('T', ' ') 
#         df['EFF_QTR_END_DT'] = df['EFF_QTR_END_DT'].str.replace(':00-00:00','').str.replace('T',' ') 

#     else: # all other report types
#         all_drop = ['NODE_ID_XML', 'NODE_ID', 'PNODE_RESMRID', 'OPR_DT', 'MARKET_RUN_ID', 'Unnamed: 0']
#         valid_columns = [col for col in all_drop if col in df.columns]
#         df = df.drop(columns=valid_columns)
#         # sorting by time/date
#         df = df.sort_values(['INTERVALSTARTTIME_GMT'])
#         # cleaning times
#         df['INTERVALSTARTTIME_GMT'] = df['INTERVALSTARTTIME_GMT'].str.replace(':00-00:00', '').str.replace('T', ' ') # getting rid of seconds
#         df['INTERVALENDTIME_GMT'] = df['INTERVALENDTIME_GMT'].str.replace(':00-00:00','').str.replace('T',' ') # getting rid of seconds
#         # conditional cleaning
#         if 'LMP_TYPE' in df.columns:
#                 df['LMP_TYPE'] = df['LMP_TYPE'].replace({'LMP': 'LMP', 'MCC': 'Congestion', 'MCE':'Energy', 'MCL': 'Loss', 'MGHG': 'Greenhouse Gas'})

#     df.to_csv(filename) # should replace file with cleaned version

# # cleaning for reference prices (no market)
# # drop duplicate rows 
# # sort by EFF_QTR_START_DT_GMT
# df = df.sort_values(['EFF_QTR_START_DT_GMT'])
#     # cleaning times
# df['EFF_QTR_START_DT_GMT'] = df['EFF_QTR_START_DT_GMT'].str.replace(':00-00:00', '').str.replace('T', ' ') # getting rid of seconds
# df['EFF_QTR_END_DT_GMT'] = df['EFF_QTR_END_DT_GMT'].str.replace(':00-00:00','').str.replace('T',' ') # getting rid of seconds
# df['EFF_QTR_START_DT'] = df['EFF_QTR_START_DT'].str.replace(':00-00:00', '').str.replace('T', ' ') # getting rid of seconds
# df['EFF_QTR_END_DT'] = df['EFF_QTR_END_DT'].str.replace(':00-00:00','').str.replace('T',' ') # getting rid of seconds

# import pandas as pd
# import numpy 
# df = pd.read_csv('pull#2.csv')
# print(df.columns)

# import datetime
# timestamp = datetime.datetime.now()
# timestamp = timestamp.strftime('%m-%d-%Y %H:%M')
# print(timestamp)

