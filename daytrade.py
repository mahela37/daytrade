import json,datetime
from json2html import *
from custom_print import custom_print
from tuner import Tuner


params_simulation={
    "min_growth":{"start":0.04,"end":0.04,"step":0.01},
    "min_decay":{"start":-0.04,"end":-0.02,"step":0.01},
    "starting_value":{"start":6000,"end":6000,"step":1000},
    "num_shares":{"start":50,"end":100,"step":5},
    "stop_loss":{"start":-0.4,"end":-0.03,"step":0.02},
    "min_drop_opening_purchase":{"start":0.05,"end":0.2,"step":0.03},
    "min_minutes_before_first_buy":{"start":40,"end":40,"step":10}
}

tuner=Tuner(params_simulation)
result=tuner.run_tuner()

scenarios=[]

for scenario in result:
    trade_histories=[]
    yields=[]
    average_yield=0
    i=0
    for day in scenario:
        i=i+1
        average_yield=(average_yield+day["output"])/(i) 
        trade_histories.append(day['trade_history'])
        yields.append(day['output'])
    params=scenario[0]['params']
    scenarios.append({"params":params,"average_yield":average_yield,"trade_history":trade_histories,"yield":yields})

sorted_result= sorted(scenarios, key=lambda k: k['average_yield'],reverse=True)
custom_print(sorted_result,0)
custom_print(f"\n{len(sorted_result)} passing parameters found",2)

current_datetime=str(datetime.datetime.now()).split(".")[0].replace("-","_").replace(":","_").replace(" ","_")
out_file_name=f"output_files/out_daytrade_{current_datetime}.html"
with open(out_file_name,"w") as f:
    out_html=json2html.convert(json = json.dumps({"params":params_simulation,"summary":sorted_result[0:10]}))
    f.write(json.dumps(out_html))

custom_print(f"Wrote output to file at {out_file_name}",2)

