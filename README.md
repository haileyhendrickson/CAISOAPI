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
- download .exe file to local machine, open it, and enjoy!

## Running on a Local Machine:
- python -m venv venv  # create a new env
- source venv/Scripts/activate  # activate env
- pip install -r requirements.txt  # install dependencies


## Notes for use 
- Separate multiple nodes with a comma. 
- Each requested report will include the actual report, the monthly average, the hourly average, and summary statistics.  
- Please be patient while the program is running. Some reports are slow (ex: RTM) 
- While the program is running, partial files will appear in the same folder as the program but will be deleted after it is finished running. 

Last updated: July 2025 (version 2.2) 

## Version History 
- Version 1: Basic Program to call reports 
- Version 2: Added 3 new pages for summary and analysis 
- Version 2.1: tweaking of analysis pages 
- Version 2.2: added visualizations 
