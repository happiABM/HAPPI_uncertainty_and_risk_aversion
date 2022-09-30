## model initialization
## set up beginning conditions
import itertools
from cls_Power_Company import Power_Company
from cls_Power_Plant import PowerPlant,CoalPlant,GccPlant,\
    NuclearPlant,WindPlant,SolarPlant
from cls_system import El_System
from tax_profile import func_tax
from func_initialize_plants import func_initialize_plant
from params import similation_period
##===========initializa agents/Power Company==========##
old_company = Power_Company(name='old',risk_averse_level=1)

# #homogeneous risk avers
homo_risk = 0#* 10 ** -10
#A1 = Power_Company(name='A1',risk_averse_level = homo_risk)#,,tech_preference = [CoalPlant]#
# A2 = Power_Company(name='A2',risk_averse_level = homo_risk)#,tech_preference = [],tech_preference = [NgccPlant]
# A3 = Power_Company(name='A3',risk_averse_level = homo_risk)#,tech_preference = [WindPlant,SolarPlant]
# A4 = Power_Company(name='A4',risk_averse_level = homo_risk)
# A5 = Power_Company(name='A5',risk_averse_level = homo_risk)#,tech_preference = [CoalPlant,NgccPlant]
# A6 = Power_Company(name='A6',risk_averse_level = homo_risk)#,tech_preference = [NuclearPlant]
# A7 = Power_Company(name='A7',risk_averse_level = homo_risk)#
# A8 = Power_Company(name='A8',risk_averse_level = homo_risk)
# A9 = Power_Company(name='A9',risk_averse_level = homo_risk)
# A10 = Power_Company(name='A10',risk_averse_level = homo_risk)


#====assign initial plants to agents====###
##initial condition with 0 carbon price
old_company.portfolio[CoalPlant]= 128
old_company.portfolio[GccPlant]= 4
# old_company.portfolio[NuclearPlant]= 128##*10#*50
# A1.portfolio[NgccPlant]= 4#*10#*50

##===========initializa agents/Power Company==========##
func_initialize_plant(Power_Company.lst,PowerPlant.__subclasses__())
#Power_Company.lst.pop(0)#remove the "old_company" from the list for future investments.

##===========initializa the electricity system==========##
Happi = El_System()
Happi.capacity_mix = {pp: pp.quantity * pp.size for pp in PowerPlant.__subclasses__()}
#print('capaicity mix (MW)',Happi.capacity_mix)
##=============== real tax scenario=============##
tax_scenario ='grow' #'grow','no_tax','constant'
initial_tax = 0 #euro/ton CO2
real_carbon_price_profile = func_tax(similation_period,tax_scenario,initial_tax,start_year=10,max_tax= 100)
# print(real_carbon_price_profile[40])


###===========design cases===========###
case_lst = []
evaluate_method = ['portfolio_assessment'] #,'individual_assessment'
risk_adjust_method = ['loss-aversion']#['mean-variance','loss-aversion']
risk_averse_level = [0]#0.13*10**(-10),0.1*10**(-10)
loss_averse_level = [0]#[0,3,5,7,15]
assessment_method_combo = list(itertools.product(*[evaluate_method,risk_adjust_method]))

for i in range(len(assessment_method_combo)):
    #evaluate_method = assessment_method_combo[i][0]#'portfolio_assessment'#individual_assessment
    risk_adjust_method = assessment_method_combo[i][1] #'mean-variance','loss-aversion'
    if risk_adjust_method == 'mean-variance':
        assessment_method_combo[i] = list(itertools.product(*[[assessment_method_combo[i]],risk_averse_level]))
        #A1.risk_averse_level = assessment_method_combo[i][2]
        #continue
    elif risk_adjust_method == 'loss-aversion':
        assessment_method_combo[i] = list(itertools.product(*[[assessment_method_combo[i]],loss_averse_level]))
        #A1.risk_averse_level = assessment_method_combo[i][2]
        #continue
    
    for sublist in assessment_method_combo[i]:
        case_lst.append(sublist)
    continue

##======================