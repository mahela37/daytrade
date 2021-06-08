from simulation import Simulation

params={
    "min_growth":0.04,
    "min_decay":-0.04,
    "starting_value":6000,
    "num_shares":100,
    "stop_loss":-0.4,
    "min_drop_opening_purchase":0.05,
    "min_minutes_before_first_buy":40
}

simulation=Simulation("AMC",params,"live_test")
result=simulation.run()
print(result)