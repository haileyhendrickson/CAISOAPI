from enum import StrEnum

# "PRC_DS_REF": needs to be implemented since it doesn't have a market value
MARKET_RUN_ID = { # making a dictionary for finding market ID
    "PRC_LMP": "DAM",
    "PRC_SPTIE": "DAM",
    "PRC_INTVL_LMP": "RTM",
    "PRC_HASP_LMP": "HASP",
    "PRC_RTPD_LMP": "PRC_RTPD_LMP",
    "PRC_CD_INTVL_LMP": "RTM",
    "PRC_RTM_LAP": "RTM"
}

print()

# def test_market(query_name):
#     query_name = MARKET_RUN_ID(query_name)
#     print(query_name)

# test_market("PRC_LMP")

from enum import Enum

class Color(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

print(Color.RED)       # Outputs: Color.RED
print(Color.RED.value) # Outputs: 'red'
print(Color.RED == "red")  # True
