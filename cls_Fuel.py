#HAPPI code Version_July 2021, author: Jinxi
##class Fuels
import random

class Fuel():
    def __init__(self,fuel_type,cost_fuel,emission_intensity):
        self.fuel_type = fuel_type
        self.fuel_cost = cost_fuel #euro/kWh el
        self.emission_intensity = emission_intensity*10**(-6) # tCO2/kWh electricity

coal = Fuel('coal',2.0*10**(-2),1000)# gCO2/kWh electricity
#coalCCS = Fuel('coalCCS',2.0,500)# 
natural_gas= Fuel('natural_gas',4.6*10**(-2),432)
#natural_gasCCS = Fuel('natural_gasCCS',natural_gas.fuel_cost*0.467/0.4+0.457,51)
biogas = Fuel('biogas',8.0*10**(-2),0)
uranium = Fuel('uranium',1.0*10**(-2),0)
air = Fuel('air',0,0)
sun = Fuel('sun',0,0)
H2 = Fuel('H2',2,0)


#print(coal.cost_fuel)
# real_gas_price = []
# real_coal_price = []
# def func_fuel_price(similation_period,scenario):
#     if scenario == 'stochastic':
#         for year in range (similation_period+1):
#             real_gas_price.append(natural_gas.fuel_cost+ random.randint(-0.5*natural_gas.fuel_cost, natural_gas.fuel_cost))
#             real_coal_price.append(coal.fuel_cost+ random.randint(-0.5*coal.fuel_cost, coal.fuel_cost))
#     return real_gas_price, real_coal_price
     