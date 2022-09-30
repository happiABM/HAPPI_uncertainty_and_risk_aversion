#build a Class for the system
#record data on the system level

import numpy as np
from cls_Power_Plant import PowerPlant,CoalPlant,GccPlant
# from func_demand_supply import func_demand_supply
from func_demand_supply_new import func_demand_supply
from cls_Fuel import natural_gas,biogas
from params import slice_hours,eps,p0
from collections import Counter

#from itertools import combinations

class El_System():
    def __init__(self
                ,capacity_mix=None
                ,electricity_price=None
                ,carbon_price_record=None
                ,demand_record = None
                ,CO2_emission = None
                ):
        self.capacity_mix = {pp: 0 for pp in PowerPlant.__subclasses__()} # capacity mix of the generation plants
        self.electricity_price = []
        self.demand_record = []
        self.CO2_emission = []
        self.produce_lst = []



    @classmethod
    def evaluate_tech_profitability(cls,tech,scenario):
        pass
    #return profitability_distribution

    @classmethod
    def clear_the_market(cls,electricity_demand,supply_lst,cost_order,slice_hours):
        return zip(*map(func_demand_supply
                        ,electricity_demand
                        ,supply_lst
                        ,[cost_order]*len(electricity_demand)
                        ,slice_hours
                        ,[eps]*len(electricity_demand)
                        ,[p0]*len(electricity_demand)
                        ))
        #return el_price,el_production,slice_revuene,prod_fossil1,prod_fossil2
    

    def record_average_el_price(self,el_price,el_production,slice_hours):
        self.electricity_price.append(sum(np.array(el_price)*np.array(el_production)*np.array(slice_hours))/sum(np.array(el_production)*np.array(slice_hours))) #total_price/total_production
    

    def record_CO2_emission(self,tech_order,produce_data,slice_hours,carbon_price):
        fossil1 = tech_order[-2]#either CoalPlant or GccPlant
        fossil2 = tech_order[-1]#either CoalPlant or GccPlant

        produce_fossil1 = []
        produce_fossil2 = []

        for produce in produce_data:
            produce_fossil1.append(produce[-2])
            produce_fossil2.append(produce[-1])
        
        
        if natural_gas.fuel_cost+carbon_price>=biogas.fuel_cost:
            GccPlant.fuel_type = biogas
        else:
            GccPlant.fuel_type = natural_gas
        
        emission_from_fossil1 =  sum(np.array(produce_fossil1) *np.array(slice_hours)) * fossil1.fuel_type.emission_intensity
        emission_from_fossil2 =  sum(np.array(produce_fossil2) *np.array(slice_hours)) * fossil2.fuel_type.emission_intensity
        
        #print('fossil1.fuel_type',fossil1.fuel_type.emission_intensity)
        
        self.CO2_emission.append(emission_from_fossil1+ emission_from_fossil2)



    def record_production (self, el_price,tech_order,produce_data,slice_hours):
        produce_data = zip(*produce_data)
        el_price = list(np.around(np.array(el_price),2))
        for tech, produce in zip(tech_order,produce_data):
            tech_produce = np.array(produce) * np.array(slice_hours)
            tech.produce_quantity.append(tech_produce.sum())
            # price_produce = zip(el_price, tech_produce)
            c = Counter()
            for price, produce in zip(el_price, tech_produce):
                c[price] += produce
            tech.price_produce.append(Counter(c).most_common())##.most_common(): save the data as a tuple
        

       