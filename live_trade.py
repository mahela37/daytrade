from simulation import Simulation

params={
    "min_growth":0.02,
    "min_decay":-0.02,
    "starting_value":5000,
    "num_shares":100,
    "stop_loss":-0.4,
    "min_drop_opening_purchase":0.05,
    "min_minutes_before_first_buy":20
}

simulation=Simulation("AMC",params,"live")
result=simulation.run()
print(result)