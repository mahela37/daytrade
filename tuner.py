# tunes a black box given parameters and the output to optimize.
import os
from custom_print import custom_print
from simulation import Simulation

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
            simulation_results=simulation.run()
            return_yield=simulation_results['return_yield']
            trade_history=simulation_results['trade_history']
            results.append({"params":instance_params,"output":return_yield,"trade_history":trade_history})
        return results

    # run simulations where eatch parameter set is tested against all the days
    def run_tuner(self):
        scenarios=self.generate_scenarios()
        custom_print(f"generated {len(scenarios)} scenarios",1)
        custom_print(scenarios,0)

        passing_scenarios=[]
        num_scenarios=len(scenarios)
        for i,scenario in enumerate(scenarios):
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