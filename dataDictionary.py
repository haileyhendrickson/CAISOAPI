FOR QUERYING:
url = 'http://oasis.caiso.com/oasisapi/SingleZip' ALWAYS THIS
startdate = yyyymmdd format, no dashes
starttime = hr:mn (00:00)
enddate = yyyymmdd format, no dashes
endtime = hr:mn (00:00)
queryname = specifies the kind of report wanted. EX: 'PRC_LMP' for hourly locational marginal prices
marketRunID = specifies the type of market (DAM or RUC)

CSV: Depends on the Query Name
PRC_INTVL_LMP
- 'INTERVALSTARTTIME_GMT': interval start  in GMT
- 'INTERVALENDTIME_GMT': interval end time in GMT
- 'OPR_DT': operation date
- 'OPR_HR': operation hour?
- 'NODE_ID_XML': node ID
- 'NODE_ID': node ID
- 'NODE': node ID
- 'MARKET_RUN_ID': ?
- 'LMP_TYPE': MCC= Congestion, MCE= Energy, MCL= Loss, LMP= LMP IDK?
- 'XML_DATA_ITEM': includes LMP type, and part of query name
- 'PNODE_RESMRID':  node ID
- 'GRP_TYPE': group type. OPTIONS?
- 'POS'
- 'MW'
- 'OPR_INTERVAL'
- 'GROUP'
