#HAPPI, author Jinxi, July 2021.
#CLASS Power_Company
#more description comeang soon..

#from typing import no_type_check
import numpy as np
import itertools
import numpy_financial as npf
from statistics import pstdev,pvariance
from cls_Power_Plant import PowerPlant,CoalPlant,GccPlant,\
    NuclearPlant,WindPlant,SolarPlant#,tech_lst#Ngcc_ccsPlant,
from cls_Fuel import coal,natural_gas,biogas
#from tax_profile import real_tax_profile
from func_NPV_CRF import func_NPV#,func_CRF
from func_revenue import func_revenue
from func_merit_order import func_merit_order
from params import slice_hours,similation_period,extra_year
from cls_Consumer import Consumer
electricity_demand = Consumer().express_demand('electricity')

class Power_Company():
    lst = [] #store all instances.
    foresight = 10 #(default) foresight for carbon tax.
    #init_portfolio = {pp.__name__ : [0] for pp in tech_lst}#initially owned plant
    ##====== financial variables======##:
    initial_cash = 400*10**6#several thousand million Euro
    fraction_f = 0.3 #0% financing fraction from own bank accout.
    interests_rate = 0.04 # 4% bank interest rate for loans
    saveBuffer = 1500*10**6 #money saved in the bank account before paying dividend.
    dividend_fraction = 0.0 #50% of the "free" cash are paid out as dividend.
    hr_homo = 0.06
    hf_homo = 1
    investment_assessment_lst = [] ##for plotting
    assessment_recods = []

    def __init__(self
                ,name
                ,risk_averse_level
                ,tech_preference = [CoalPlant,GccPlant,NuclearPlant,WindPlant,SolarPlant]
                ,hr=hr_homo
                ,hf=hf_homo
                ,cash=initial_cash
                ,debt=0
                ,status='active'
                ,principle_payment = None
                ,portfolio_lst= None
                ,net_income_lst= None
                ,equity_lst = None
                ,debt_lst = None
                ,cash_lst = None
                ,risk_level_lst = None
                ,NPV_single_assessment = {pp : [] for pp in PowerPlant.__subclasses__()}
                ,portfolio_revenue_no_investment = []
                ,portfolio_revenue_self_invest = {pp : [] for pp in PowerPlant.__subclasses__()}
                ,portfolio_revenue_others_invest = {pp : [] for pp in PowerPlant.__subclasses__()}
                ):
        ##define varaibles
        self.name = name
        self.risk_averse_level = risk_averse_level
        self.tech_preference = tech_preference
        self.hr = hr#hurdle rate
        self.hf = hf #future cabon tax expectation
        self.portfolio = {pp: 0 for pp in PowerPlant.__subclasses__()} # initial plant portfolio
        self.portfolio_lst = {pp : [0] for pp in PowerPlant.__subclasses__()}
        #financial variables:
        self.cash = cash
        self.debt = debt
        self.status = status
        self.principle_payment = np.array([0]*(similation_period+extra_year+1), dtype=float)
        self.net_income_lst = [] #record annaul net income for (expost) ROE calculation
        self.equity_lst = [] #record annaul net income for (expost) ROE calculation
        self.debt_lst = [] #record annaul current amount of debt
        self.cash_lst = [] #record annaul current amount of cash in the bank account
        self.risk_level_lst = []
        ##new investment assessment
        self.NPV_single_assessment = NPV_single_assessment
        self.portfolio_revenue_no_investment = portfolio_revenue_no_investment
        self.portfolio_revenue_self_invest = portfolio_revenue_self_invest
        self.portfolio_revenue_others_invest = portfolio_revenue_others_invest
        
        Power_Company.lst.append(self)#append all company instances

        #self.installment = np.array([0]*(similation_period+40), dtype=float)
        #self.interest_payment = np.array([0]*(similation_period+40), dtype=float)

    @property
    def equity(self):
        #print('the value of my plants', self.my_plant_value()/10**7)
        return self.cash + self.my_plant_value() - self.debt

####===================produce_electricity===========####
    @classmethod
    def bid_el_price (cls,carbon_price,coal_cost,natural_gas_cost):#bid at the marginal costs/running cost of the technology
        CoalPlant.running_cost = coal_cost + carbon_price * coal.emission_intensity
        GccPlant.running_cost = min (natural_gas_cost+carbon_price*natural_gas.emission_intensity,biogas.fuel_cost+carbon_price*natural_gas.emission_intensity)
        if CoalPlant.running_cost > GccPlant.running_cost:
            tech_order = [SolarPlant,WindPlant,NuclearPlant,GccPlant,CoalPlant]
        else:
            tech_order = [SolarPlant,WindPlant,NuclearPlant,CoalPlant,GccPlant]
        
        cost_order = [tech.running_cost for tech in tech_order]

        return tech_order,cost_order


##==============update financial status==================##
    @classmethod
    def offer_capacity(cls,tech_order):
        supply_tech = [tech.available_capacity() for tech in tech_order]
        return supply_tech


    def calculate_revenue(self):
        portfolio_revenue = 0
        for tech, value in self.portfolio.items():
            portfolio_revenue += value * tech.revuene_per_plant
            #print('portfolio_revenue',self.portfolio[tech])
        return portfolio_revenue    


        # pp_quantity_own = [self.portfolio[pp] for pp in tech_order]
        # revenue = sum(x*y for x,y in zip(pp_quantity_own,revuene_per_plant))
        

    def check_affordability(self,invesment_cadidate,year):
        remaining = (self.cash 
                    - invesment_cadidate.overnight_cost * self.fraction_f
                    - self.debt * self.interests_rate
                    - self.principle_payment[year+1]
                    )
        if remaining > 0:
            return invesment_cadidate
        else:
            return None   

    def update_cash(self,amount):
        self.cash += amount
        
    def update_debt(self,amount):
        self.debt += amount
    
    def pay_back_debt(self,year):
        interest_cost = self.debt * self.interests_rate
        #if self.name == 'hr0.045hf0': print('interest cost = ', round(interest_cost/10**7,2))

        if self.cash < interest_cost:
            self.status == 'inactive' #no further investment allowed
            self.cash = 0
            self.principle_payment[year+1] += self.principle_payment[year]
             #pay interest costs.
        else:
            self.cash -= interest_cost ##pay back interest costs
            #print('interest cost paid:',round(interest_cost/10**6,2))
            if self.cash - self.principle_payment[year] < 0:
                self.status == 'inactive'
                self.debt -= self.cash
                self.principle_payment[year+1] += (self.principle_payment[year]- self.cash)
                self.cash = 0
            
            else:
                self.status == 'active'
                self.cash -= self.principle_payment[year]
                self.debt -= self.principle_payment[year]
                #print('principle cost paid:',round(self.principle_payment[year]/10**6,2))

            #return interest_cost + self.principle_payment[year]
        
            #if self.name == 'hr0.045hf0': 
                #print('principle next year before hand', round(self.principle_payment[year+1]/10**7,2))
            #if self.name == 'hr0.045hf0':
                #print('principle unpaid', round((self.principle_payment[year]- self.cash)/10**7,2))
                #print('principle next year after unpaid', round(self.principle_payment[year+1]/10**7,2))
       


    def record_financial_variable(self,revenue,year):
        self.net_income_lst.append(revenue - self.debt * self.interests_rate - self.principle_payment[year])
        self.equity_lst.append(self.equity)
        self.debt_lst.append(self.debt)
        self.cash_lst.append(self.cash)

        # print('equity',round(self.equity/10**6,2))
        # print('debt',round(self.debt/10**6,2))
        # print('cash',round(self.cash/10**6,2))
                 



    def update_repayment_schedule_and_financial_status(self,year,new_plant):
        financed_by_own_capital = new_plant.overnight_cost * self.fraction_f
        financed_by_debt = new_plant.overnight_cost  *  (1-self.fraction_f)
        self.update_cash(-1 * financed_by_own_capital)#pay downpayment immediately,therefore mutiply*-1.
        self.update_debt(financed_by_debt) #update debt.
        
        # print('')
        # print('financed_by_debt: ',round(financed_by_debt/10**6,2))                            
        # print('financed_by_own_capital: ',round(financed_by_own_capital/10**6,2))                            
        # print('total debt: ',round(self.debt/10**6,2))                            
        # print('cash: ',round(self.cash/10**6,2))                            
        ##update the principle_payment payment
        outstanding_loan = financed_by_debt #outstanding_loan loan
        amortization = financed_by_debt * new_plant.CRF(self.interests_rate)
        #print('amortization',round(amortization/10**6,2))
        counting = 0
        
        for yr in range (year+1,year+new_plant.lifetime+1):
            principle_amount = amortization - outstanding_loan * self.interests_rate
            self.principle_payment[yr] += principle_amount #annuitized cost meanus interest payment
            outstanding_loan -= principle_amount 
        
        #print('principle_payment: ', self.principle_payment/10**6)    
                

    def my_plant_value(self):
        plant_value = 0
        for pp in list(PowerPlant.instances):
            if pp.owner == self:
                plant_value += pp.value
        return plant_value



    def pay_dividend(self):
        if self.cash - self.saveBuffer > 0 :
            self.cash -= self.dividend_fraction *  (self.cash - self.saveBuffer)

    def record_portfolio(self,tech_lst):
        for tech in tech_lst:
            self.portfolio_lst[tech].append(self.portfolio[tech])

####===================investment evaluation and decision processes===========####
    
    
    @classmethod
    def forecast_carbon_price(cls,data,possible_range):
        if len(data) < 5:
            past_average = sum(data) / len(data)
        else: 
            past_average = sum (data[-5:]) / 5 #data of the last 5 years
        
        past_average = data[-1]# set the price to last' year's data

        possible_carbon_price = [past_average * n for n in possible_range]
        return possible_carbon_price

    @classmethod
    def forecast_el_demand_change (cls):
        # el_demand_change_rate = {}
        # el_demand_change_rate ['high'] = 1.1
        # el_demand_change_rate ['medium'] = 1
        # el_demand_change_rate ['low'] = 0.9
        el_demand_change_rate = [0.9,1,0,1.1]
        return el_demand_change_rate
    
    @classmethod
    def forecast_fuel_price (cls):
        # fuel_price_change_rate = {}
        # fuel_price_change_rate ['high'] = 2
        # fuel_price_change_rate ['medium'] = 1
        # fuel_price_change_rate ['low'] = 0.55
        fuel_price_change_rate = [0.5, 1.0, 2.0]
        return fuel_price_change_rate
    


    
    adjust_value = 0.05
    max_aversion_level = 1
    mean_aversion_level = 0.1
    def update_risk_averse_level(self,carbon_price):
        ###adjust aversion level by the the development of one's equity##
        if len(self.equity_lst) > 3:
            equity_data = self.equity_lst[-3:]#last 3 years data
        else:
            equity_data = self.equity_lst

        equity_trend,_ = self.calculate_past_trend(equity_data)
        # # if self.name =='A6':
        # #     print('equity_data: ',equity_data)
        # #     print('equity_trend: ',equity_trend)

        if equity_trend < -1*10**(-6):## if equity has been decreasing, due to "technical reason", the number is not < 0.
            self.risk_averse_level = min (self.risk_averse_level + self.adjust_value, self.max_aversion_level) 
        elif -1*10**(-6) < equity_trend < 0 :## if equity no change,risk no change
            self.risk_averse_level += 0
        else:## if equity has been increasing: equity_trend >= 0
            self.risk_averse_level = max(self.risk_averse_level-self.adjust_value, self.mean_aversion_level) 
        
        self.risk_level_lst.append(self.risk_averse_level)
        
        #return

    @classmethod
    def calculate_past_trend (cls,data):
        #print(data)
        a,b = np.polyfit(list(range(1,len(data)+1)),data, deg=1) # linear fit.
        #print('data',data)
        #print('a,b',a,b)
        return a,b #a=the slope of the line/change_rate, b=residuals    


 
    def evaluate_only_portfolio_profits (self
                                        ,year
                                        ,tech_lst
                                        ,possible_carbon_price
                                        ,financial_module
                                        ,risk_adjust_method
                                        ,el_demand_change_rate = [1]
                                        ,fuel_price_change_rate = [1]
                                        ): 
        el_demand_change_rate = [1]    
        fuel_price_change_rate = [1]
        # mean = 1
        # delta= 0.25
        # fuel_price_change_rate = [mean-3*delta,mean-2*delta,mean-1*delta,mean, mean+1*delta, mean+2*delta,mean+3*delta ]
        # fuel_price_change_rate = [0.5,0.75,1, 1.25,1.5]
        scenario_lst = [possible_carbon_price,el_demand_change_rate,fuel_price_change_rate]
        possible_future_scenarios = list(itertools.product(*scenario_lst))
        investment_cadidate = []
        
        #print(possible_future_scenarios)
        for tech in tech_lst:# set to empty list
            #self.NPV_single_assessment[tech] = [] 
            tech.criteria = 0
            self.portfolio_revenue_no_investment = []
            self.portfolio_revenue_self_invest[tech] = []
            weighted_eq_price = {}
            
            for scenario_params in possible_future_scenarios:
                carbon_price = scenario_params [0]
                #print('carbon_price',carbon_price)
                coal_cost =  coal.fuel_cost * scenario_params [1]
                natural_gas_cost = natural_gas.fuel_cost * scenario_params [1]
                el_demand = electricity_demand * scenario_params [2]
                
                ## company runs a 'internal' profit estimation simulation.
                tech_order,cost_order = Power_Company.bid_el_price(carbon_price,coal_cost,natural_gas_cost)
                
                supply_lst = (list(zip(*Power_Company.offer_capacity(tech_order))))
                #print('cost_order',cost_order)
                slice_revuene,_,_ = zip(*map(func_revenue 
                                    ,el_demand
                                    ,supply_lst
                                    ,[cost_order]*len(slice_hours)
                                    ,slice_hours
                                    ))
                annual_tech_revuene = np.sum(slice_revuene,axis=0)
                #print('annual_tech_revuene ',annual_tech_revuene)
                PowerPlant.get_revenue_per_plant(annual_tech_revuene,tech_order)
                NPV_revenue_no_investment = npf.npv(rate=self.hr_homo, values= [0] +  [self.calculate_revenue()]* tech.lifetime)#tech.lifetime=40
                self.portfolio_revenue_no_investment.append(NPV_revenue_no_investment)
            #print('self.calculate_revenue()',self.calculate_revenue())
            #print('revenue_no_investment: ',round(self.calculate_revenue()/10**6,2))  
            #print('self.portfolio_revenue_no_investment',self.portfolio_revenue_no_investment)


            ##=====================assess revenues with new investment=================================##
                quantity_increase = 1/(500*10**6) #number of plant
                tech.quantity += quantity_increase
                #tech.intalled_capacity += 1
                
                supply_lst = (list(zip(*Power_Company.offer_capacity(tech_order))))
                slice_revuene,el_price,el_production = zip(*map(func_revenue 
                                ,el_demand
                                ,supply_lst
                                ,[cost_order]*len(slice_hours)
                                ,slice_hours
                                ))
                # tech.produce_price[carbon_price] = el_price
                # tech.produce_quantity[carbon_price] = el_production
                # tech.weighted_eq_price[carbon_price] = (sum(np.array(el_price)*np.array(el_production)*np.array(slice_hours))/sum(np.array(el_production)*np.array(slice_hours)))
                # print('electricity price : ',tech.weighted_eq_price)
                
                weighted_eq_price[str(carbon_price)]=(sum(np.array(el_price)*np.array(el_production)*np.array(slice_hours))/sum(np.array(el_production)*np.array(slice_hours)))
                
                annual_tech_revuene = np.sum(slice_revuene,axis=0)
                
                PowerPlant.get_revenue_per_plant(annual_tech_revuene,tech_order)
                
                portfolio_revenue_self_invest = self.calculate_revenue() + tech.revuene_per_plant#*quantity_increase
                NPV_portfolio_revenue_self_invest = npf.npv(rate=self.hr_homo, values= [0] + [portfolio_revenue_self_invest] * tech.lifetime) - tech.overnight_cost#+ tech.subsidy
                self.portfolio_revenue_self_invest[tech].append(NPV_portfolio_revenue_self_invest)
                
                continue #to next scenario

        
            ##=========adjust with risk-averse===========##
            if risk_adjust_method == 'mean-variance' or risk_adjust_method == 'mean-deviation':
                if risk_adjust_method == 'mean-variance':
                    risk_adjust_parameter_no_investment = pvariance(self.portfolio_revenue_no_investment) ##pvariance
                    risk_adjust_parameter_self_invest = pvariance(self.portfolio_revenue_self_invest[tech]) ##pvariance
                    
                # elif risk_adjust_method == 'mean-deviation':
                #     risk_adjust_parameter_no_investment = pstdev(self.portfolio_revenue_no_investment) ##pvariance
                #     risk_adjust_parameter_self_invest = pstdev(self.portfolio_revenue_self_invest[tech]) ##stanard deviation
               
            

                expected_portfolio_profit_no_investment = (sum(self.portfolio_revenue_no_investment)
                                                        /len(possible_future_scenarios)
                                                        - self.risk_averse_level * risk_adjust_parameter_no_investment)
            
            
                expected_portfolio_profit_self_invest = (sum(self.portfolio_revenue_self_invest[tech]) 
                                                        /len(possible_future_scenarios)
                                                        - self.risk_averse_level * risk_adjust_parameter_self_invest)
                
                tech.portfolio_pofitability = ((expected_portfolio_profit_self_invest - expected_portfolio_profit_no_investment)
                                                /tech.overnight_cost
                                                * tech.CRF (self.hr_homo))


                # if  (tech.portfolio_pofitability > 0) and (tech in self.tech_preference):
                if  (tech.portfolio_pofitability > 0):
                    investment_cadidate.append(tech)
                    tech.criteria = 1

            
                ##==================record assessment data==================###
                self.assessment_recods.append(
                                        [year
                                        ,self.name
                                        ,tech.__name__[0:-5]
                                        ,tech.criteria
                                        ,np.array(self.portfolio_revenue_no_investment) #sum(self.portfolio_revenue_no_investment)/len(possible_future_scenarios)
                                        ,np.array(self.portfolio_revenue_self_invest[tech])#sum(self.portfolio_revenue_self_invest[decision])/len(possible_future_scenarios)
                                        ,sum(self.portfolio_revenue_no_investment)
                                        ,sum(self.portfolio_revenue_self_invest[tech])
                                        ,pvariance(self.portfolio_revenue_no_investment)
                                        ,pvariance(self.portfolio_revenue_self_invest[tech])
                                        ,tech.portfolio_pofitability
                                        ,weighted_eq_price
                                        ])#
            
            elif risk_adjust_method == 'loss-aversion':
                difference = np.subtract(self.portfolio_revenue_self_invest[tech], self.portfolio_revenue_no_investment)

                tech.positive_cases = np.count_nonzero(difference > 0) ##positive case

                pofits = sum(difference) 
                #if tech == WindPlant:
                    #print(self.portfolio_revenue_self_invest[tech])
                    #print(self.portfolio_revenue_no_investment)
                    # print(tech.positive_cases)

                    #print(pofits)
                
                tech.portfolio_pofitability = (pofits/len(possible_future_scenarios)
                                                    /tech.overnight_cost* tech.CRF (self.hr_homo)
                                                    )

                if tech.positive_cases >= self.risk_averse_level and pofits > 0:
                    investment_cadidate.append(tech)
                    tech.criteria = 1
                
                self.assessment_recods.append([year
                                        ,self.name
                                        ,tech.__name__[0:-5]
                                        ,tech.criteria
                                        ,np.array(self.portfolio_revenue_no_investment) #sum(self.portfolio_revenue_no_investment)/len(possible_future_scenarios)
                                        ,np.array(self.portfolio_revenue_self_invest[tech])#sum(self.portfolio_revenue_self_invest[decision])/len(possible_future_scenarios)
                                        ,difference
                                        ,sum(self.portfolio_revenue_self_invest[tech])
                                        ,tech.positive_cases
                                        ,tech.portfolio_pofitability
                                        ,weighted_eq_price
                                        ])
                
                # print('\n'+tech.__name__[0:-5])
                # print('tech.positive_cases ',tech.positive_cases )
                # print('tech.positive_cases',tech.positive_cases)
            
            
            tech.quantity = int(tech.quantity - quantity_increase)
            continue # to evaluate next technology
            
        
        if len(investment_cadidate) == 0:
            return None
        else:# len(investment_cadidate)> 0:
            investment_cadidate.sort(key=lambda tech: tech.portfolio_pofitability, reverse=True)
            #print(investment_cadidate)

            if financial_module == "on" :
                decision = self.check_affordability(investment_cadidate[0],year)
            else:
                decision = investment_cadidate[0]
                 
            if decision != None:
                
                if risk_adjust_method == 'mean-variance':
                    self.investment_assessment_lst.append([year
                                                            ,decision.__name__[0:-5]
                                                            ,decision.criteria
                                                            ,np.array(self.portfolio_revenue_no_investment) #sum(self.portfolio_revenue_no_investment)/len(possible_future_scenarios)
                                                            ,risk_adjust_parameter_no_investment
                                                            ,np.array(self.portfolio_revenue_self_invest[decision])#sum(self.portfolio_revenue_self_invest[decision])/len(possible_future_scenarios)
                                                            ,pvariance(self.portfolio_revenue_self_invest[decision])
                                                            ])#for plotting

                elif risk_adjust_method == 'loss-aversion':
                    self.investment_assessment_lst.append([year
                                                            ,decision.__name__[0:-5]
                                                            ,decision.criteria
                                                            ,np.array(self.portfolio_revenue_no_investment) #sum(self.portfolio_revenue_no_investment)/len(possible_future_scenarios)
                                                            ,np.array(self.portfolio_revenue_self_invest[decision])#sum(self.portfolio_revenue_self_invest[decision])/len(possible_future_scenarios)
                                                            ,decision.positive_cases
                                                            ])#for plotting

            return decision


    # ##==END od the method==##