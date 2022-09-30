#HAPPI code Version_July 2021, author: Jinxi
#class Power plant
#available_technology = {'coal_fired','coal_fired_CCS','NGCC','NGCC_CCS','nuclear','wind','solar'}
import random
from collections import defaultdict
from cls_Fuel import coal,natural_gas,biogas,uranium,air,sun
from params import wind_availability,solar_availability,\
    nonVER_availability,similation_period,extra_year
import numpy as np
#from tax_profile import tax_profile

#=================================================##
#=================================================##
#super class
class PowerPlant():

    instances = [] #track all "alive" plants.
    def append_instance(self):
        PowerPlant.instances.append(self)

    subsidy = 0


    @property
    def value(self,interests_rate = 0.04):
        return self.overnight_cost * (1-(1+interests_rate)**(-self.lifespan))/(1-(1+interests_rate)**(-self.lifetime))


    # @classmethod
    # def running_cost(cls,tax):
    #     if cls == GccPlant:#natural gas or biogas
    #         return min (natural_gas.fuel_cost+tax*natural_gas.emission_intensity,biogas.fuel_cost)
    #     else:
    #         fuel_cost = cls.fuel_type.fuel_cost
    #         emission_cost = tax * cls.fuel_type.emission_intensity
    #         return fuel_cost + emission_cost #cent/kWh el

    @classmethod
    #@property
    def intalled_capacity(cls):
        intalled_capacity = cls.quantity * cls.size
        return intalled_capacity

    def record_data(techLst):
        for tech in techLst:
            tech.capacity_record.append(tech.intalled_capacity())
            tech.cost_record.append(tech.overnight_cost)
            tech.estimated_NPV_records.append(dict(tech.estimated_NPV))
            tech.estimated_NPV = defaultdict(list)#reset the dict to empty



    @classmethod
    def record_annual_investment(cls,year):#record how many new plants are invested per year
        cls.annual_investment[year] += 1

    @classmethod
    def available_capacity(cls):
        #intalled_capacity = intalled_capacity(cls)
        if cls == WindPlant:
            available_capacity = WindPlant.intalled_capacity()* wind_availability
        elif cls == SolarPlant:
            available_capacity = SolarPlant.intalled_capacity() * solar_availability
        else:
            available_capacity = cls.intalled_capacity() * nonVER_availability
        return available_capacity


    def lifespan_minus_1(PowerPlant):
        decommission_lst =[]
        for pp in list(PowerPlant.instances):
            # print('check here')
            pp.lifespan -=1 #a plant's lifespan minus by 1
            if pp.lifespan == 0:
                decommission_lst.append(pp)
        return decommission_lst

    def decommission_one_plant(decommission_lst):
        # remove a plant (at a random position in the list), and retuen "the plant".
        the_plant = decommission_lst.pop(random.randrange(len(decommission_lst)))
        plant_type = type(the_plant) #get the Class type.
        plant_type.quantity -= 1 #numbers of this type of plant minus 1.
        the_plant.owner.portfolio[plant_type] -= 1 # also delete from its owner's protfolio.
        the_plant.owner = 'avfall' # 'send' the plant to 'garbage'.
        #delete the object, even though Python cannot delet an object.
        list(PowerPlant.instances).remove(the_plant)#remove it from the whole pp_lst.
        del the_plant #delete the instance, but seems python cannot delete instance

    @classmethod
    def CRF (cls,r):
        #"r" is the discount_rate
        return r/(1 - (1 + r)**(-1 * cls.lifetime))

    @classmethod
    def get_revenue_per_plant(cls,annual_tech_revuene,tech_order,Real_lifeMode = 'False'):
        for tech in tech_order:
            if tech.quantity == 0:
                tech.revuene_per_plant = 0
            else:
                tech.revuene_per_plant = annual_tech_revuene[tech_order.index(tech)] / tech.quantity
            if Real_lifeMode == 'True':#'real-life production',not in evaluation mode
                tech.annual_revenue_records.append (tech.revuene_per_plant)
      

    # @classmethod
    # def annuitized_cost(cls,financed_by_debt,i):
    #     #f: fraction borrowed from the bank.
    #     #: interest rate of the borrowed money.
    #     return financed_by_debt * cls.CRF(i) #annuitized cost,euro.

    # @classmethod
    # def investment_cost(cls):
    #     from cls_Power_Company import fraction_f
    #     return fraction_f * cls.overnight_cost \
    #         + (1-fraction_f) * cls.CRF * cls.lifetime

    maximal_reduction = 0.5 #maximal redction of the original cost
    learning_method = 'exdogenous'
    learning_method = 'endogenous'
    @classmethod
    def technology_learning(cls,year,policy='no_policy'):
        #for cls in tech_lst:
        for tech in PowerPlant.__subclasses__():
            if tech == SolarPlant and year < 10 and policy=='subsidy':
                continue #if subsidy, the price is determined by subsidy.
            if tech == NuclearPlant: maximal_reduction = 0.2
            #if tech == Ngcc_ccsPlant: maximal_reduction = 0.18#only CCS part can reduce to max.50%
            if tech.learning_method == 'endogenous':
                if tech.learning_rate_en == 0 or tech.overnight_cost <= tech.investment_cost_per_kw * tech.size * 1000 * tech.maximal_reduction:
                    continue
                else:
                    tech.overnight_cost *= (tech.total_experience/tech.previous_experience)**tech.learning_rate_en

            if tech.learning_method == 'exdogenous':
                if tech.learning_rate_ex == 0 or tech.overnight_cost <= tech.investment_cost_per_kw * tech.size * 1000 * tech.maximal_reduction:
                    continue
                else:
                    tech.overnight_cost *= (1-tech.learning_rate_ex)

            tech.previous_experience = tech.total_experience ##update experience benchmark


#1. coal-fired plants (without CCS).
class CoalPlant (PowerPlant):
    ##define varaibles
    color = 'sienna'
    size = 500 #Mw
    quantity = 0 #number of plants.
    #initial_experience = 64*10**3#MW
    # previous_experience = initial_experience
    # total_experience = previous_experience
    fuel_type = coal #
    running_cost = coal.fuel_cost #+ 0 * coal.emission_intensity #0 =carbon price
    investment_cost_per_kw = 1500 # euro/kW
    lifetime = 40 #years
    efficiency = 1 #100%
    availability = nonVER_availability
    #financial variables:
    overnight_cost = investment_cost_per_kw * size * 1000 #size: Mw to Kw
    capacity_record = []
    cost_record = []
    annual_revenue_records = []
    annual_investment = [0]*(similation_period+extra_year)
    ##new investment assessment
    positive_cases = 0
    average_pofitability = 0
    average_pofitability_lst = defaultdict(list)
    estimated_NPV = defaultdict(list)
    estimated_NPV_records = []
    dev_pofitability = 0
    revuene_per_plant = 0
    portfolio_pofitability = 0
    criteria = 0
    
    produce_quantity = []
    
    price_produce = []




    def __init__(self,owner,lifespan = lifetime,value=overnight_cost):
        self.owner = owner
        self.lifespan = lifespan
        #CoalPlant.total_experience += CoalPlant.size
        CoalPlant.quantity +=1
        #PowerPlant.instances.add(self)
        PowerPlant.append_instance(self) #record all plants



#3. gas-fired plants (without CCS).
class GccPlant(PowerPlant):
    color = 'lightcoral'
    #size = 100 #MW
    size = 500 #MW
    quantity = 0 # the initial number of plants
    # initial_experience = 2*10**3 #MW
    # previous_experience = initial_experience
    # total_experience = previous_experience
    # learning_rate_en = 0
    # learning_rate_ex = 0
    fuel_type = natural_gas or biogas# or biogas, need to add
    running_cost = fuel_type.fuel_cost #+ 0 * fuel_type.emission_intensity # 0 =carbon price
    investment_cost_per_kw = 900 # euro/kW
    lifetime = 30 #years
    efficiency = 1 #100%
    overnight_cost = investment_cost_per_kw * size * 1000 #size: Mw to Kw
    capacity_record = []
    cost_record = []
    annual_revenue_records = []
    annual_investment = [0]*(similation_period+extra_year)
    availability = nonVER_availability
    positive_cases = 0
    average_pofitability = 0
    average_pofitability_lst = defaultdict(list)
    estimated_NPV = defaultdict(list)
    estimated_NPV_records = []
    dev_pofitability = 0
    revuene_per_plant = 0
    portfolio_pofitability = 0
    criteria = 0
    
    produce_quantity = []
    price_produce = []
    


    def __init__(self,owner,lifespan=lifetime,value=overnight_cost):
        self.owner = owner
        self.lifespan = lifespan
        # GccPlant.total_experience += GccPlant.size
        GccPlant.quantity+=1
        PowerPlant.append_instance(self)

#4. gas-fired plants with CCS.
# class Ngcc_ccsPlant(PowerPlant):
#     size = 500 #MW
#     quantity = 0 # the initial number of plants
#     initial_experience = 2*10**3
#     previous_experience = initial_experience
#     total_experience = previous_experience
#     learning_rate_en = -0.322
#     learning_rate_ex = 0.0
#     fuel_type = natural_gasCCS
#     lifetime = 30 #years
#     investment_cost_per_kw = 1400 # euro/kW
#     efficiency = 0.85 #85%
#     overnight_cost = investment_cost_per_kw * size * 1000 #size: Mw to Kw
#     capacity_record = []
#     cost_record = []
#     annual_revenue_records = []
#     annual_investment = [0]*(similation_period+extra_year)
#     availability = nonVER_availability

#     def __init__(self,owner,lifespan=lifetime,value=overnight_cost):
#         self.owner = owner
#         self.lifespan = lifespan
#         Ngcc_ccsPlant.total_experience += Ngcc_ccsPlant.size
#         Ngcc_ccsPlant.quantity+=1
#         PowerPlant.append_instance(self)

#5.nuclear plants.
class NuclearPlant(PowerPlant):
    color = 'darkgrey' #for plotting purpose
    #size = 1000 #MW
    size = 500 #MW
    quantity = 0
    #initial_experience = 20*10**3#MW
    #previous_experience = initial_experience
    #total_experience = previous_experience
    #learning_rate_en = -0.00
    #learning_rate_ex = 0.00
    fuel_type = uranium
    running_cost = uranium.fuel_cost
    investment_cost_per_kw = 6000 # euro/kW
    # investment_cost_per_kw = 60000000 # euro/kW
    lifetime = 40 #years
    efficiency = 1 #100%
    overnight_cost = investment_cost_per_kw * size * 1000 #size: Mw to Kw
    capacity_record = []
    cost_record = []
    annual_revenue_records = []
    annual_investment = [0]*(similation_period+extra_year)
    availability = nonVER_availability
    positive_cases = 0
    average_pofitability = 0
    average_pofitability_lst = defaultdict(list)
    estimated_NPV = defaultdict(list)
    estimated_NPV_records = []
    dev_pofitability = 0
    revuene_per_plant = 0
    portfolio_pofitability = 0
    criteria = 0
    
    produce_quantity = []
    
    price_produce = []


    def __init__(self,owner,lifespan=lifetime,value=overnight_cost):
        self.owner = owner
        self.lifespan=lifespan
        # NuclearPlant.total_experience += NuclearPlant.size
        NuclearPlant.quantity+=1
        PowerPlant.append_instance(self)

class WindPlant(PowerPlant):
    color = 'deepskyblue' #for plotting purpose
    size = 100 #MW
    size = 500 #MW
    quantity = 0
    # initial_experience = 54938#MW, Germany 2020
    # previous_experience = initial_experience
    # total_experience = previous_experience
    # learning_rate_en = -0.322
    # learning_rate_ex = 0.02
    technology = 'wind'
    fuel_type = air
    running_cost = 0
    investment_cost_per_kw = 1500 # euro/kW
    lifetime = 25 #years
    efficiency = 1 #100%
    overnight_cost = investment_cost_per_kw * size * 1000 #size: Mw to Kw
    capacity_record = []
    cost_record = []
    annual_revenue_records = []
    annual_investment = [0]*(similation_period+extra_year)
    availability = wind_availability
    positive_cases = 0
    average_pofitability = 0
    average_pofitability_lst = defaultdict(list)
    estimated_NPV = defaultdict(list)
    estimated_NPV_records = []
    dev_pofitability = 0
    revuene_per_plant = 0
    portfolio_pofitability = 0
    criteria = 0
    
    produce_quantity = []
    
    price_produce = []


    def __init__(self,owner,lifespan=lifetime,value=overnight_cost):
        self.owner = owner
        self.lifespan=lifespan
        # WindPlant.total_experience += WindPlant.size
        WindPlant.quantity+=1
        PowerPlant.append_instance(self)

class SolarPlant(PowerPlant):
    color = 'gold'
    size = 100 #MW
    size = 500 #MW
    quantity = 0
    # initial_experience = 49096#MW, Germany 2019.
    # previous_experience = initial_experience
    # total_experience = previous_experience
    # learning_rate_en = -0.322
    # learning_rate_ex = 0.01
    technology = 'solar'
    fuel_type = sun
    running_cost = 0
    investment_cost_per_kw = 800 # euro/kW
    lifetime = 25 #years
    efficiency = 1 #100%
    overnight_cost = investment_cost_per_kw * size * 1000 #size: Mw to Kw
    capacity_record = []
    cost_record = []
    annual_revenue_records = []
    annual_investment = [0]*(similation_period+extra_year)
    availability = solar_availability
    positive_cases = 0
    average_pofitability = 0
    average_pofitability_lst = defaultdict(list)
    estimated_NPV = defaultdict(list)
    estimated_NPV_records = []
    dev_pofitability = 0
    revuene_per_plant = 0
    portfolio_pofitability = 0
    criteria = 0
    
    produce_quantity = []
    
    price_produce = []




    def __init__(self,owner,lifespan=lifetime,value=overnight_cost):
        self.owner = owner
        self.lifespan = lifespan
        #self.value = value
        # SolarPlant.total_experience += SolarPlant.size
        SolarPlant.quantity+=1
        PowerPlant.append_instance(self)

#2. coal-fired plants with CCS.
# class Coal_ccsPlant (CoalPlant):

# print(CoalPlant.running_cost(tax=2))

# c1=CoalPlant(owner='test')
# print(CoalPlant.quantity)
# print(list(c1.instances))