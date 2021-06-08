import json,datetime,requests,time
from custom_print import custom_print

MARKET_OPEN_SECONDS=60*60*6+60*30   # 6:30 AM in seconds
SAMPLING_RATE_SECONDS=60

class Simulation():
    transaction_fee=5
    balance=0
    has_stock=False
    transaction_fees=0
    prices=[]
    params=None
    file=None
    load_mode=None
    price_index=0
    live_url=None

    def __init__(self,file,params,load_mode):
        self.file=file
        if(load_mode=="backtest"):
            custom_print("Running in backtest mode",0)
            self.load_prices()
        elif load_mode=="live":
            custom_print("Running in live mode",0)
            self.live_url=f"https://query1.finance.yahoo.com/v8/finance/chart/{self.file}?region=CA&lang=en-CA&includePrePost=false&interval=1m&useYfid=true&range=1m&corsDomain=ca.finance.yahoo.com&.tsrc=finance"
        elif load_mode=="live_test":
            self.live_url=f'http://127.0.0.1:5000/price'
        else:
            raise ValueError('Simulation: Unspecified load mode')

        self.params=params
        self.balance=self.params['starting_value']
        self.load_mode=load_mode
        
    def load_prices(self):
        # read data from file
        with open (f"data_include/{self.file}","r") as f:
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


    def fetch_latest_price(self):
        if self.load_mode=="backtest":
            if(self.price_index>=len(self.prices)):
                return "EOF"
            self.price_index=self.price_index+1
            return self.prices[self.price_index-1]
        else:
            r=requests.get(self.live_url)
            r_json=r.json()
            current_price=r_json['chart']['result'][0]['indicators']['quote'][0]['open'][0]
            timestamp=r_json['chart']['result'][0]['timestamp'][0]
            date_timestamp=datetime.datetime.fromtimestamp(timestamp)
            if(date_timestamp.hour>=12 and date_timestamp.minute==59):
                return "EOF"
            self.price_index=self.price_index+1
            if(self.load_mode=="live"):
                time.sleep(SAMPLING_RATE_SECONDS)
            else:
                pass
                #time.sleep(0.5)
            return current_price
            
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

    def get_timestamp(self,index):
        market_open=datetime.timedelta(seconds=MARKET_OPEN_SECONDS)
        delta_index=datetime.timedelta(seconds=index*SAMPLING_RATE_SECONDS)
        current_time=market_open+delta_index
        return str(current_time)

    # run the simulation once
    def run(self):
        print(self.params)
        current=None
        market_open=self.fetch_latest_price()
        price=market_open
        last_price=market_open

        trade_history=[]
        while(price is not "EOF"):
            last_price=price
            traded=False
            current_trade={}
            if self.has_stock:
                if(price/current-1>=self.params['min_growth'] or (price/current-1<=self.params['stop_loss'])):
                    self.sell(price)
                    traded=True
                    current_trade['type']="sell"
                    current_trade['timestamp']=self.get_timestamp(self.price_index)+f' {self.file}'
                    current_trade['price']=price
                    current=price
            else:
                if current is None: #market open
                    if(market_open/price-1>=self.params['min_drop_opening_purchase'] and self.price_index>=self.params['min_minutes_before_first_buy']):
                        bought=self.buy(price)
                        if not bought:
                            custom_print("Went bankrupt...exiting simulation\n",0)
                            break
                        current=price
                        traded=True
                        current_trade['type']="buy"
                        current_trade['timestamp']=self.get_timestamp(self.price_index)+f' {self.file}'
                        current_trade['price']=price                                          
                else:
                    if(current/price-1<=self.params['min_decay']):
                        bought=self.buy(price)
                        if not bought:
                            custom_print("Went bankrupt...exiting simulation\n",0)
                            break
                        current=price
                        traded=True
                        current_trade['type']="buy"
                        current_trade['timestamp']=self.get_timestamp(self.price_index)+f' {self.file}'
                        current_trade['price']=price
            if traded:
                trade_history.append(current_trade)
            price=self.fetch_latest_price()

        if(self.has_stock):
            custom_print("\nMarket is closing...selling the remaining shares\n",0)
            self.sell(last_price)
            trade_history.append({"type":"sell","timestamp":self.get_timestamp(len(self.prices)-1)+f' {self.file}',"price":last_price})

        return_yield=(self.balance/self.params['starting_value']-1)*100
        custom_print(f"Simulation complete. Balance is {self.balance}. Return is {return_yield}%, or ${self.balance-self.params['starting_value']}",0)
        custom_print(f"Total transaction fees: ${self.transaction_fees}. # Round trip trades: {int(self.transaction_fees/self.transaction_fee/2)}",0)

        return {"return_yield":return_yield,"trade_history":trade_history}