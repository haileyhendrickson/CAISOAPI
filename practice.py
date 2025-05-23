
class ClassName:
    def __init__(self, query_name, market_run_id):
        self.query_name = query_name
        self.market_run_id = market_run_id
    
test = ClassName("PRC_LMP", "DAM")
   
print(test.query_name)
print(test.market_run_id)
