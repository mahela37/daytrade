import json,datetime
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

    def __init__(self,file,params):
        self.file=file
        self.load_prices()
        self.params=params
        self.balance=self.params['starting_value']

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
        current=None
        market_open=self.prices[0]
        last_price=self.prices[0]

        trade_history=[]
        for i,price in enumerate(self.prices):
            last_price=price
            traded=False
            current_trade={}
            if self.has_stock:
                if(price/current-1>=self.params['min_growth'] or (price/current-1<=self.params['stop_loss'])):
                    self.sell(price)
                    traded=True
                    current_trade['type']="sell"
                    current_trade['timestamp']=self.get_timestamp(i)+f' {self.file}'
                    current_trade['price']=price
                    current=price
            else:
                if current is None: #market open
                    if(market_open/price-1>=self.params['min_drop_opening_purchase'] and i>=self.params['min_minutes_before_first_buy']):
                        bought=self.buy(price)
                        if not bought:
                            custom_print("Went bankrupt...exiting simulation\n",0)
                            break
                        current=price
                        traded=True
                        current_trade['type']="buy"
                        current_trade['timestamp']=self.get_timestamp(i)+f' {self.file}'
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
                        current_trade['timestamp']=self.get_timestamp(i)+f' {self.file}'
                        current_trade['price']=price
            if traded:
                trade_history.append(current_trade)

        if(self.has_stock):
            custom_print("\nMarket is closing...selling the remaining shares\n",0)
            self.sell(last_price)
            trade_history.append({"type":"sell","timestamp":self.get_timestamp(len(self.prices)-1)+f' {self.file}',"price":last_price})

        return_yield=(self.balance/self.params['starting_value']-1)*100
        custom_print(f"Simulation complete. Balance is {self.balance}. Return is {return_yield}%, or ${self.balance-self.params['starting_value']}",0)
        custom_print(f"Total transaction fees: ${self.transaction_fees}. # Round trip trades: {int(self.transaction_fees/self.transaction_fee/2)}",0)

        return {"return_yield":return_yield,"trade_history":trade_history}