#HAPPI code Version_July 2021, author: Jinxi
#the main module

import os 
# import itertools
import time
import numpy as np
import random
import pandas as pd
import csv

###=======================###
from cls_Consumer import Consumer
from cls_Fuel import coal,natural_gas,biogas
from Initialization import Happi,real_carbon_price_profile,case_lst
from params import slice_hours,similation_period,extra_year
from cls_Power_Plant import PowerPlant,CoalPlant,GccPlant,NuclearPlant,WindPlant,SolarPlant
tech_lst = PowerPlant.__subclasses__()
from cls_Power_Company import Power_Company
    
###=======================###


financial_module = 'off'
cheapest_plant = min(tech_lst, key=lambda i: i.overnight_cost)

# 1) The consumer needs electricity.
electricity_demand = Consumer.express_demand('electricity') #consumer is characterise by price elasticity
coal_cost = coal.fuel_cost
natural_gas_cost = natural_gas.fuel_cost
##==========set up expected carbon price ranges that the agent expected======##
delta_lst = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]

caseName = 'new/VaR=0_delta=0.0/'
delta = 0#.25
mean = 1.5
possible_range = [mean-3*delta,mean-2*delta,mean-1*delta,mean, mean+1*delta, mean+2*delta,mean+3*delta ]
#possible_range = [0.75,1.0,1.25,1.5,1.75,2.0,2.25] #expected carbon price
#possible_range = [1.5] #expected carbon price
#possible_range = [1.5]

##==============########=======================##
#print(possible_range)
print(case_lst)
case =  case_lst[0]
evaluate_method = case[0][0]
risk_adjust_method = case[0][1]
print(risk_adjust_method)
for company in Power_Company.lst:
    company.risk_averse_level = case[1]
#print(company.risk_averse_level)


##==============start the simulation===============###
for year in range (0,100):
#for year in range (0,imilation_period):
    print('\n','year: ', year)
    carbon_price = real_carbon_price_profile [year]
    # coal_cost = coal.cost
    # natural_gas_cost = natural_gas.cost

    # 2) The power companies produce electricity.
    tech_order,cost_order = Power_Company.bid_el_price(carbon_price,coal_cost,natural_gas_cost)
    # supply_lst = Power_Company.offer_capacity(tech_order)
    supply_lst = [tech.available_capacity() for tech in tech_order]
    supply_lst = (list(zip(*supply_lst))) #supply profile for each 64 slices.
    #the market clears demand and supply, return electricity price and production of each slice
    
    el_price,el_production,slice_revuene,dispatch_lst = Happi.clear_the_market(electricity_demand,supply_lst,cost_order,slice_hours)
    Happi.record_average_el_price(el_price,el_production,slice_hours)
    Happi.record_CO2_emission(tech_order,dispatch_lst,slice_hours,carbon_price)
    Happi.record_production (el_price,tech_order,dispatch_lst,slice_hours)
    #print(f'Happi.electricity_price {Happi.electricity_price[year]:.4f}')

    ##===========================companies update financial status===========######
    annual_tech_revuene = np.sum(slice_revuene,axis=0) #per technology
    PowerPlant.get_revenue_per_plant(annual_tech_revuene,tech_order,Real_lifeMode ='True')
    for company in Power_Company.lst: #each company updates cash on its bank account
            revenue = company.calculate_revenue()#calculate revenue.
            #print('revenue: ',round(revenue/10**6,2))
            company.update_cash(revenue)
            company.pay_back_debt(year)
            company.record_financial_variable(revenue,year) #record net income,debt,cash,equity.

            if financial_module == "on":
                if company.equity < 0:#check_bankruptcy
                    print('you are bankrupt '+company.name)
                    company.status = 'inactive' #no further investment will be allowed.

            #if company.status == 'active':
                #company.pay_dividend() #company pays out dividend to shareholders

            continue
    ##=============================================================######

    ##===========================check system status===========######
    ## lifespan of plants minus 1, and return the plants has 0 lifespan.
    decommission_lst = PowerPlant.lifespan_minus_1(PowerPlant)
    #print(' decommission_lst ',decommission_lst)
    ## how variable(carbon price) has chaneged in the past years
    possible_carbon_price = Power_Company.forecast_carbon_price (real_carbon_price_profile[:year+1],possible_range)
    #print(possible_carbon_price)

    while True: #as long as the decommission_lst is not empty.
        # print('check1')
        if not decommission_lst:
            # print('NO decommission')
            break #if the decomission is empty, then break.
        else:#otherwise, decommsion another plant.#remove one plant at a time.
            PowerPlant.decommission_one_plant(decommission_lst)
            #print('\n','decommission')
            random.shuffle(Power_Company.lst) #randomize the order of companies for investment.


            ##===========================new investment decisions===========######
            while True:
                #random.shuffle(Power_Company.lst) #randomize the order of companies for investment.
                count_NO = 0 #counting the number of "No investment"
                # for tech in tech_lst:
                #     Power_Company.estimate_profits(tech,possible_carbon_price,electricity_demand)#estimate profits for different scenarios.

                for company in Power_Company.lst:
                    if financial_module == "on":
                        if (company.status == 'inactive' 
                        or company.cash <= company.fraction_f * cheapest_plant.overnight_cost
                        ):
                        ##if a company is 'inactive' or cannot afford the cheapest plant.
                            count_NO += 1
                            continue#then skip the eveluation process
                    
                    #                                     ) for tech in tech_lst]#estimate profits for different scenarios.
                    # company.evaluate_portfolio_profits (year
                    #                                     ,tech_lst
                    #                                     ,possible_carbon_price
                    #                                     ,electricity_demand
                    #                                     ,risk_adjust_method = 'mean-deviation' #'mean-deviation','loss-aversion',
                    #                                     ,financial_module = 'off'
                    #                                     )
                    # invesment_decision = company.evaluate_options(tech_lst,year,financial_module ='off')
                    if evaluate_method == 'individual_assessment':

                        invesment_decision = company.estimate_single_profits (year
                                                                            ,company.tech_preference
                                                                            ,possible_carbon_price
                                                                            ,financial_module
                                                                            ,risk_adjust_method 
                                                                            )
                    elif evaluate_method == 'single_portfolio_assessment':#both
                        invesment_decision = company.evaluate_portfolio_and_single_profits(year
                                                                                        ,company.tech_preference
                                                                                        ,possible_carbon_price
                                                                                        ,financial_module
                                                                                        ,risk_adjust_method
                                                                                        )
                    
                    elif evaluate_method == 'portfolio_assessment':
                        invesment_decision = company.evaluate_only_portfolio_profits(year
                                                                                    ,tech_lst
                                                                                    # ,company.tech_preference
                                                                                    ,possible_carbon_price
                                                                                    ,financial_module
                                                                                    ,risk_adjust_method
                                                                                    )

                    #print('investment decision: ',invesment_decision )
                    
                    if invesment_decision != None:
                        new_plant = invesment_decision(owner=company)#The power companies 'construct' the newly invested plant and update the capacity mix
                        new_plant.record_annual_investment(year)#record how many new plants are invested per year
                        print('\n',"the newly invested plant is a", type(new_plant).__name__)
                        company.portfolio[type(new_plant)] += 1 #add the new_plant to the corresponding compamy's portfolio.
                        #print(company.portfolio)
                        company.update_repayment_schedule_and_financial_status(year,new_plant) ##update installment and principle_payment.
                        # if new_plant == WindPlant:
                        #     print(np.round(np.array(company.NPV_single_assessment[CoalPlant])/10**6,2))
                        #print(new_plant.criteria)
                        #print(round(company.cash/10**6,2))
                        continue

                    else:# invesment_decision == None:
                        count_NO += 1
                        continue

                if count_NO == len(Power_Company.lst): #no companies wants to make more investment.
                    break
                else: continue

            continue
    PowerPlant.record_data(tech_lst) #record capacity mix and overnight cost.
    #if technology_learning == "on":
        #PowerPlant.technology_learning(year)

    for company in Power_Company.lst:
        company.record_portfolio(tech_lst) #each company records own capacity,for later plotting
        # if year > 3:
        #     company.update_risk_averse_level(real_carbon_price_profile[:year]) #each agent adaptes its risk_averse_level
        #else:
        #company.risk_level_lst.append(company.risk_averse_level)
        #     # if company.name == 'A6':
        #     #     print(company.equity)
        #     #     print(company.risk_averse_level)

    continue # year +=1 #go to next year

####================#######end######==================######
# print("END of the simulation")


for pp in tech_lst:
    print(int(pp.quantity)) #print out the final capacity mix.
    #print(pp.average_pofitability_lst)

#=============export and save final results===============#
# Answer = input('Do you want to continue with saving data to CSV? Type yes or no: ')
# if Answer == ('yes') or Answer == ('y'):
#     print ('saving the data')
savepath = 'C:/Users/jinxi/Box/ABM_model/PaperIV_carbon_price_uncertianty/model_output/'

# caseName = evaluate_method+'_'+ risk_adjust_method +'='+str(company.risk_averse_level)+'_10agent/'






if not os.path.exists(savepath+str(caseName)):
    os.mkdir(savepath+caseName)

##====save system capacity====#####
save_varaible = 'system_installed_capacity'
with open(savepath+caseName+save_varaible+'.csv','w', newline='') as f:
    writer = csv.writer(f)
    for tech in tech_lst:
        writer.writerow([tech.__name__[0:-5]]+tech.capacity_record)

save_varaible = 'electricity_production'
with open(savepath+caseName+save_varaible+'.csv','w', newline='') as f:
    writer = csv.writer(f)
    for tech in tech_lst:
        writer.writerow([tech.__name__[0:-5]]+tech.produce_quantity)

save_varaible = 'production_price'
with open(savepath+caseName+save_varaible+'.csv','w', newline='') as f:
    writer = csv.writer(f)
    for tech in tech_lst:
        writer.writerow([tech.__name__[0:-5]]+tech.price_produce)


save_varaible = 'overnight_cost'
with open(savepath+caseName+save_varaible+'.csv','w', newline='') as f:
    writer = csv.writer(f)
    for tech in tech_lst:
        writer.writerow([tech.__name__[0:-5]]+tech.cost_record)
save_varaible ='electricity_price'
with open(savepath+caseName+save_varaible+'.csv','w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(Happi.electricity_price)

save_varaible ='CO2_emission'
with open(savepath+caseName+save_varaible+'.csv','w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(Happi.CO2_emission)    

save_varaible = 'annual_investment'
with open(savepath+caseName+save_varaible+'.csv','w', newline='') as f:
    writer = csv.writer(f)
    for tech in tech_lst:
        writer.writerow([tech.__name__[0:-5]]+tech.annual_investment)

save_varaible = 'annual_revenue_records'
with open(savepath+caseName+save_varaible+'.csv','w', newline='') as f:
    writer = csv.writer(f)
    for tech in tech_lst:
        writer.writerow([tech.__name__[0:-5]]+tech.annual_revenue_records)

save_varaible = 'estimated_NPV'
with open(savepath+caseName+save_varaible+'.csv','w', newline='') as f:
    writer = csv.writer(f)
    for tech in tech_lst:
        writer.writerow([tech.__name__[0:-5]]+ tech.estimated_NPV_records)

save_varaible = 'average_pofitability'
with open(savepath+caseName+save_varaible+'.csv','w', newline='') as f:
    writer = csv.writer(f)
    for tech in tech_lst:
        writer.writerow([tech.__name__[0:-5]]+ [dict(tech.average_pofitability_lst)])

##========every assessment of investment that were materialized.====##
save_varaible = 'investment_assessment'
if risk_adjust_method == 'mean-variance' or risk_adjust_method == 'mean-deviation':
    col=['year'
        ,'plant_type'
        ,'selection_criteria'
        ,'ep_no_invest'
        ,'dev_no_invest'
        ,'ep_self_invest'
        ,'dev_self_invest'
        ]
elif risk_adjust_method == 'loss-aversion':
    col=['year'
        ,'plant_type'
        ,'selection_criteria'
        ,'ep_no_invest'
        ,'ep_self_invest'
        ,'positive_caseNames'
        ,
        ]

df = pd.DataFrame(Power_Company.investment_assessment_lst, columns=col)
df.to_csv(savepath+caseName+save_varaible+'.csv')  

##===save data for every assessment under criteria 2.=====##
save_varaible = 'assessment_recods'
if risk_adjust_method == 'mean-variance' or risk_adjust_method == 'mean-deviation':
    col=['year'
        ,'company name'
        ,'plant_type'
        ,'selection_criteria'
        ,'ep_no_invest'
        ,'ep_self_invest'
        ,'sum_ep_no_invest'
        ,'sum_ep_self_invest'
        ,'var_no_invest'
        ,'var_self_invest'
        ,'portfolio_pofitability'
        ,'weighted_el_price'
        ]

elif risk_adjust_method == 'loss-aversion':
    col=['year'
        ,'company name'
        ,'plant_type'
        ,'selection_criteria'
        ,'ep_no_invest'
        ,'ep_self_invest'
        ,'difference'
        ,'sum_ep_self_invest'
        ,'positive_cases'
        ,'portfolio_pofitability'
        ,'weighted_el_price'
        ]

#print(col)
df = pd.DataFrame(Power_Company.assessment_recods, columns=col)
df.to_csv(savepath+caseName+save_varaible+'.csv')  


##====save Power_Company's data====#####
# for company in Power_Company.lst:
#     with open(savepath+caseName+'company_capacity/'+company.name+'.csv','w', newline='') as f:
#             writer = csv.writer(f)
#             for tech in tech_lst:
#                 writer.writerow([tech.__name__[0:-5]]+company.portfolio_lst[tech])

#     if financial_module == 'on':
#         with open(savepath+caseName+'debt/'+company.name+'.csv','w', newline='') as f:
#             writer = csv.writer(f)
#             writer.writerow(company.debt_lst)

#         with open(savepath+caseName+'cash/'+company.name+'.csv','w', newline='') as f:
#             writer = csv.writer(f)
#             writer.writerow(company.cash_lst)

#         with open(savepath+caseName+'ROE/net_income_'+company.name+'.csv','w', newline='') as f:
#             writer = csv.writer(f)
#             writer.writerow(company.net_income_lst)

#         with open(savepath+caseName+'ROE/equity_'+company.name+'.csv','w', newline='') as f:
#             writer = csv.writer(f)
#             writer.writerow(company.equity_lst)

# ##=========company's risk levels===========##
# with open(savepath+caseName+'risk_aversion_level.csv','w', newline='') as f:
#         writer = csv.writer(f)
#         for company in Power_Company.lst:
#             writer.writerow([company.name]+company.risk_level_lst)



print("END of saving data")
    #gc.collect()
    #     #=============END of the data saving process===============#
    # if Answer == ('no'or 'n'):
    #     print('Data is not saved')
    #     print('End of the simulation')