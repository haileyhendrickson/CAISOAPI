# space for practicing with classes, strEnum, and dictionaries


# dictionary stuff
market_run_map = {
    'PRC_LMP': ('DAM', 1),
    'PRC_SPTIE_LMP': 'DAM',
    'PRC_INTVL_LMP': 'RTM',
    'PRC_HASP_LMP': 'HASP',
    'PRC_RTPD_LMP': 'RTPD',
    'PRC_DS_REF': '', # this one doesn't have a specified market
    'PRC_CD_INTVL_LMP': 'RTM',
    'PRC_RTM_LAP': 'RTM',
}
# queryname = input('Select Report Type: ')
people = { # list as a dictionary value
    "PRC_LMP": ("DAM", 1),
    "PRC_RTM_LAP": ("RTM", 6)
}
# Access both pieces of info
# market_run_id, version = people[queryname] # setting parameters for market and version based on dictionary


# datetime stuff

from datetime import datetime, date, timedelta

startdate = input('Enter a start date (YYYY/MM/DD): ').replace('/', '') # user input
enddate = input('Enter an end date (YYYY/MM/DD): ').replace('/', '')
startdate = date.fromisoformat(startdate) # formats it to work with datetime package
enddate = date.fromisoformat(enddate)
difference = enddate - startdate # counts days in between
print(difference.days)

if difference.days > 30:
    while difference.days > 0: # until we reach the end date
        if difference.days < 30: # when we get below 30 days left
            pass
            # end date needs to be original end date
        nextdate = startdate + timedelta(days=30) # creating a chunk
        difference.days -= 30 # updating this counter
        # pull a file from start date to +30 days: startdate = startdate (reformat), enddate = startdate+30days (reformat)
        startdate = nextdate # update start date to be next date
        # if there's less than 31 days left, fix that 
# if not, run like normal


    


nextdate = startdate + timedelta(days=31) # adding days

# very last bit of code, to format it back to how I need
nextdate = nextdate.strftime('%Y%m%d') # formats it without dashes for API use



# # class stuff
# class ClassName:
#     def __init__(self, query_name, market_run_id):
#         self.query_name = query_name
#         self.market_run_id = market_run_id
    
# test = ClassName("PRC_LMP", "DAM")
   
# print(test.query_name)
# print(test.market_run_id)
