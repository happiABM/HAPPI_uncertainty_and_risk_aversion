#HAPPI code Version_July 2021, author: Jinxi
#tax_profile: a growing or a constant scenario, with or without price volatility.

import random
#from params import similation_period
def func_tax (similation_period,tax_scenario,initial_tax,start_year = 10,max_tax=100):
    #with or without price volatility.
    tax = initial_tax #initial tax
    tax_profile =[]
    if tax_scenario == 'grow':
        growth_rate = 2
        end_year = start_year + int(max_tax/growth_rate)
         
        for year in range(similation_period+40) :
            if year <= start_year or year > end_year:
                increaseRate = 0
            if start_year < year <= end_year:
                increaseRate = growth_rate #euro /tCO2 year
            tax += increaseRate
            tax_profile.append(tax)# Euro/tCO2 .
        
        return tax_profile 
    
    if tax_scenario == 'constant':
        tax_profile = [initial_tax]*(similation_period+40)
        return tax_profile

    if tax_scenario =='no_tax':
        tax_profile = [0]* (similation_period+40)
        return tax_profile

    if tax_scenario =='jump':
        year_interval = 10 #make a jump every 10 years
        jump_level = 20 #euro/ton CO2
        
        for year in range(0,similation_period+40,year_interval) :
            tax_profile+=([initial_tax] * year_interval) #euro 
            if initial_tax < 100:
                initial_tax += jump_level
            else:
                continue
        return tax_profile
    
    if tax_scenario =='jump+grow':
        return tax_profile

    if tax_scenario == 'constant + variation':
        for year in range(similation_period+40+1):
            tax_profile.append(random.randint(initial_tax/2, initial_tax*2))
        return tax_profile

    if tax_scenario == 'grow + variation':
        for year in range(similation_period+40) :
            if year <= 10 or year > 80:
                increaseRate = 0
            if 10 < year <= 80:
                increaseRate = 1 #euro /tCO2 year
            tax += (increaseRate + random.randint(-2,2))
            tax_profile.append(tax)# Euro/tCO2 .
        return tax_profile

        




# scenario = 'grow'
# #scenario = 'grow'
# initial_tax = 0
# #real_tax_profile = list(map(func_tax,range (similation_period+40)))
#real_tax_profile = func_tax(similation_period=80,tax_scenario='jump',initial_tax=30)
