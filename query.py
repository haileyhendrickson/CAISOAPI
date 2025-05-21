import pandas as pd 
import requests
from zipfile import ZipFile, BadZipFile
from io import BytesIO

base_url = "http://oasis.caiso.com/oasisapi/SingleZip"

# Define your query parameters as a dictionary
params = {
    "resultformat": "6",
    "queryname": "PRC_LMP",
    "startdatetime": "20250101T07:00-0000",
    "enddatetime": "20250101T08:00-0000",
    "market_run_id": "DAM",
    "version": "1",
    "grp_type": "ALL_APNODES"  # Optional parameter (can vary by query)
}

try: # using this for now for error handling
    response = requests.get(base_url, params=params)
    with ZipFile(BytesIO(response.content)) as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                df = pd.read_csv(f)
                df.to_csv('test2.csv')
                # print(df.info())
                print(df.columns)
                # print(df['LMP_TYPE'].value_counts())
                # print(df['XML_DATA_ITEM'].value_counts)
except BadZipFile:
    print('Response is not a ZIP')
    print(response.content.decode(errors='replace'))
