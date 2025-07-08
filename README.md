# CAISOAPI

A GUI-based Python tool to query and visualize data from the CAISO API. The program efficiently queries 4 different LMP reports from https://oasis.caiso.com. These include: Day Ahead Market (DAM), Five Minute Market (FMM), Hour Ahead Market (HASP), and the Real Time Market (RTM). This program queries the data (for any date range) and formats it appropriately.  

## 🔧 Features
- Select date ranges
- Download and extract zipped data
- View data visualizations (e.g., top 5% zoom charts)
- Export processed Excel files

## 📦 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/haileyhendrickson/CAISOAPI.git
   cd CAISOAPI

## Use
Download .exe file to local machine, open it, and enjoy!

## Running on a Local Machine:
- python -m venv venv  # create a new env
- source venv/Scripts/activate  # activate env
- pip install -r requirements.txt  # install dependencies


## Notes for use 
- Separate multiple nodes with a comma (e.g., NODE1,NODE2,NODE3).
- Each report query returns the raw data, monthly averages, hourly averages, and summary statistics.
- Please be patient; some reports, especially RTM, may take longer to process.
- Temporary partial files will appear during data retrieval but are deleted when processing completes.


## Version History -- Last updated: July 2025 (version 2.2) 
- v1.0: Initial release - basic report retrieval
- v2.0: Added summary and analysis pages
- v2.1: Tweaked analysis pages for improved insights
- v2.2: Added data visualizations
