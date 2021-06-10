from simulation import Simulation

params={
    "min_growth":0.03,
    "min_decay":-0.04,
    "starting_value":3000,
    "num_shares":50,
    "stop_loss":-0.4,
    "min_drop_opening_purchase":0,
    "min_minutes_before_first_sell":20
}

simulation=Simulation("AMC",params,"live")
result=simulation.run()
print(result)