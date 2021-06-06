import json
import os
from json2html import *

MIN_PRINT_LEVEL=1

# reduce clutter by defining print levels
def custom_print(data,level):
    if(level>=MIN_PRINT_LEVEL):
        print(data)

class Simulation():
    transaction_fee=5
    balance=0
    has_stock=False
    transaction_fees=0
    prices=[]
    params=None

    def __init__(self,file,params):
        self.load_prices(file)
        self.params=params
        self.balance=self.params['starting_value']

    def load_prices(self,file):
        # read data from file
        with open (f"data_include/{file}","r") as f:
            intraday=json.load(f)
        prices_raw=[]
        for entry in intraday:
            prices_raw.append(entry['average'])
        size=len(prices_raw)
        i=0

        # sometimes the entries return "None". Pad them with the previous value.  
        while(i<size):
            if(prices_raw[i])==None:
                prices_raw[i]=prices_raw[i-1]
            i=i+1
        self.prices=prices_raw

    def buy(self,price):
        if(self.balance-(price*self.params['num_shares'])-self.transaction_fee)>0:
            self.balance=self.balance-(price*self.params['num_shares'])-self.transaction_fee
            self.transaction_fees=self.transaction_fees+self.transaction_fee
            self.has_stock=True
            custom_print(f"bought {self.params['num_shares']} shares at {price}. Balance is {self.balance}",0)
            return True
        else:
            custom_print(f"not enough balance: {self.balance}",0)
            return False

    def sell(self,price):
        self.balance=self.balance+(price*self.params['num_shares'])-self.transaction_fee
        self.transaction_fees=self.transaction_fees+self.transaction_fee
        self.has_stock=False
        custom_print(f"sold {self.params['num_shares']} shares at {price}. Balance is {self.balance}",0)

    # run the simulation once
    def run(self):
        current=self.prices[0]
        last_price=self.prices[0]
        self.buy(current)

        for i,price in enumerate(self.prices):
            last_price=price
            if self.has_stock:
                if(price/current-1>=self.params['min_growth']):
                    self.sell(price)
                    current=price
            else:
                if(current/price-1<=self.params['min_decay']):
                    bought=self.buy(price)
                    if not bought:
                        custom_print("Went bankrupt...exiting simulation\n",0)
                        break
                    current=price

        if(self.has_stock):
            custom_print("\nMarket is closing...selling the remaining shares\n",0)
            self.sell(last_price)

        return_yield=(self.balance/self.params['starting_value']-1)*100
        custom_print(f"Simulation complete. Balance is {self.balance}. Return is {return_yield}%, or ${self.balance-self.params['starting_value']}",0)
        custom_print(f"Total transaction fees: ${self.transaction_fees}. # Round trip trades: {int(self.transaction_fees/self.transaction_fee/2)}",0)

        return return_yield

# tunes a black box given parameters and the output to optimize.
class Tuner():
    params=None
    files=None

    def __init__(self,params):
        self.params=params
        self.files=os.listdir(f"data_include")

    # given a list of parameters with start,end and increment defined, generate all permutations of the parameters.
    def generate_scenarios(self):
        params=self.params
        def generate_range(start,end,increment):
            result=[]
            while start<=end:
                result.append(start)
                start=start+increment
            return result

        steps=[]
        for entry in params:
            steps.append(generate_range(params[entry]['start'],params[entry]['end'],params[entry]['step']))

        import itertools
        scenario_matrix=list(itertools.product(*steps))

        scenarios=[]
        param_list=[param for param in params]
        for scenario in scenario_matrix:
            scenario_temp={}
            for i,param in enumerate(param_list):
                scenario_temp[param]=scenario[i]
            scenarios.append(scenario_temp)

        return scenarios
    
    # run simulations for all the days, given a parameter set
    def run_dataset(self,instance_params):
        results=[]
        for file in self.files:
            simulation=Simulation(file,instance_params)
            return_yield=simulation.run()
            results.append({"params":instance_params,"output":return_yield})
        return results

    # run simulations where eatch parameter set is tested against all the days
    def run_tuner(self):
        scenarios=self.generate_scenarios()
        custom_print(f"generated {len(scenarios)} scenarios",1)
        custom_print(scenarios,0)

        passing_scenarios=[]
        num_scenarios=len(scenarios)
        print_step=int(num_scenarios/100)
        for i,scenario in enumerate(scenarios):
            if(i%print_step==0):
                custom_print(f"Running scenario {i} of {len(scenarios)}",1)
            result=self.run_dataset(scenario)
            result_valid=True

            for entry in result:
                if(entry["output"]<=0):
                    result_valid=False
                    break
            if(result_valid):
                passing_scenarios.append(result)
        return passing_scenarios


params={
    "min_growth":{"start":0.01,"end":0.05,"step":0.01},
    "min_decay":{"start":-0.05,"end":-0.01,"step":0.01},
    "starting_value":{"start":1000,"end":5000,"step":500},
    "num_shares":{"start":30,"end":60,"step":5}
}

tuner=Tuner(params)
result=tuner.run_tuner()

scenarios=[]
for scenario in result:
    average_yield=0
    i=0
    for day in scenario:
        i=i+1
        average_yield=(average_yield+day["output"])/(i) 
    params=scenario[0]['params']
    scenarios.append({"params":params,"average_yield":average_yield})

sorted_result= sorted(scenarios, key=lambda k: k['average_yield'],reverse=True)
custom_print(sorted_result,0)
custom_print(f"\n{len(sorted_result)} passing parameters found",2)

out_file_name="out_daytrade.html"
with open(out_file_name,"w") as f:
    sorted_result_json=json.dumps(sorted_result)
    sorted_result_html=json2html.convert(json = sorted_result_json)
    f.write(json.dumps(sorted_result_html))

custom_print(f"Wrote output to file at {out_file_name}",2)

