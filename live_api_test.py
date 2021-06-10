import json,datetime
from flask import Flask
app = Flask(__name__)


MARKET_OPEN_SECONDS=60*60*6+60*30   # 6:30 AM in seconds
SAMPLING_RATE_SECONDS=60

# read data from file
with open (f"AMC/2021_06_04.json","r") as f:
    intraday=json.load(f)
prices_raw=[]
for entry in intraday:
    prices_raw.append(entry['average'])
size=len(prices_raw)
i=0

# sometimes the entries return "None". Pad them with the previous value.  
prices=[]
while(i<size):
    if(prices_raw[i])==None:
        prices_raw[i]=prices_raw[i-1]
    i=i+1

prices=prices_raw
counter=0
seconds=1623159000


@app.route('/price')
def hello_world():
    global prices
    global counter
    global seconds
    return_data={'chart':{"result":[{"meta":{"regularMarketPrice":prices[counter],"regularMarketTime":seconds}}]}}
    seconds=seconds+60
    counter=counter+1
    return json.dumps(return_data)

if __name__=="__main__":
    app.run()