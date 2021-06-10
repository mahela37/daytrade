from datetime import datetime
from iexfinance.stocks import get_historical_intraday
import json

ticker="AMC"

def dump_file(date):
    result=get_historical_intraday(ticker, date,token='pk_1d48d9db381d4dc995cac4868533be43',output_format="json")
    filename=str(date).replace("-","_").split(" ")[0]+".json"
    with open(f'{ticker}/{filename}',"w") as f:
        f.write(json.dumps(result))

# dates=[
#     datetime(2021,5,5),
#     datetime(2021,5,6),
#     datetime(2021,5,7),
#     datetime(2021,5,8),
#     datetime(2021,5,9),
#     datetime(2021,5,10),
#     datetime(2021,5,11),
#     datetime(2021,5,12),
#     datetime(2021,5,13),
#     datetime(2021,5,14),
#     datetime(2021,5,15),
#     datetime(2021,5,16),
#     datetime(2021,5,17),
#     datetime(2021,5,18),
#     datetime(2021,5,19),
#     datetime(2021,5,20),
#     datetime(2021,5,21),
#     datetime(2021,5,22),
#     datetime(2021,5,23),
#     datetime(2021,5,24),
#     datetime(2021,5,25),
#     datetime(2021,5,26),
#     datetime(2021,5,27),
#     datetime(2021,5,28),
#     datetime(2021,5,29),
#     datetime(2021,5,30),
#     datetime(2021,5,31),
#     datetime(2021,6,1),
#     datetime(2021,6,2),
#     datetime(2021,6,3),
#     datetime(2021,6,4)
# ]
dates=[datetime(2021,6,9)]


size=len(dates)

for i,date in enumerate(dates):
    print(f"{i}/{size}")
    dump_file(date)
