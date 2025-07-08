# CAISOAPI PROGRAM

Internship project, creating a program to pull various price reports from the CAISO OASIS API (oasis.caiso.com). The purpose of the program is for simplified and more efficient data pulling for consultants and analysts at Energy Strategies.

CAISO API TOOL.exe is a program that efficiently queries 4 different LMP reports from https://oasis.caiso.com. These include: Day Ahead Market (DAM), Five Minute Market (FMM), Hour Ahead Market (HASP), and the Real Time Market (RTM). This program queries the data (for any date range) and formats it appropriately.  

Running on a Local Machine:
python -m venv venv  # create a new env
source venv/Scripts/activate  # activate env
pip install -r requirements.txt  # install dependencies


Installation 
- Download CAISO API TOOL.exe to your local machine and click to open.  After initial download, navigate to folder location for use. NOTE: The program will occasionally update (will be labeled with a version number). It only needs to be downloaded once each time it updates, then just navigate to its place in the folder to use it. 
- Input your desired report variables and submit. 
- The excel file with the report will automatically generate in your chosen file destination once finished. 

Notes for use 
- Separate multiple nodes with a comma. 
- Each requested report will include the actual report, the monthly average, the hourly average, and summary statistics.  
- Please be patient while the program is running. Some reports are slow (ex: RTM) 
- While the program is running, partial files will appear in the same folder as the program but will be deleted after it is finished running. 

Last updated: July 2025 (version 2.2) 

Version History 
- Version 1: Basic Program to call reports 
- Version 2: Added 3 new pages for summary and analysis 
- Version 2.1: tweaking of analysis pages 
- Version 2.2: added visualizations 

Files in GitHub:
- For GUI: use gui.py, or gui.exe if python libraries and extensions are not installed
- Backend(API) code: backend.py
- Detailed documentation: documentation.txt (includes daily log and processes)
- Data dictionary: Notes about each report type under the 'prices' tab at the CASIO OASIS site. 
- All other files are part of the creation process, including learning and testing new python skills.
