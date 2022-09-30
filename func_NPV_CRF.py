#HAPPI version  July 2021, author Jinxi.
##first calculate the NPV-based revenueability, then rank the option
import numpy as np
import numpy_financial as npf

def func_NPV(hr,revenue_t1,revenue_t10,new_pp):
    #first interpolate revenues between year t+1 to t+10.
    years_in_between = 10 # 10 years
    revenues_t1_t10 = list(np.linspace(revenue_t1, revenue_t10, years_in_between))
    #then concatenate all annaul revenues to a singel list (revenue after t+10 is assumed to be equal to revenue(t+10).)
    revenues_t1_to_end = [0] + revenues_t1_t10 + [revenue_t10] * (new_pp.lifetime - years_in_between)    
    #calculate NPV of all revenue streams and minus the investment cost.
    NPV = npf.npv(rate=hr,values= revenues_t1_to_end)- new_pp.overnight_cost + new_pp.subsidy
    #check if NPV is positive
   # print(NPV)
    if NPV > 0 :
        return NPV
    else:
        return None    

# def func_CRF (r,pp_lifetime):
#     return r/(1 - (1 + r)**(-1 * pp_lifetime))