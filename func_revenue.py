import numpy as np
from params import eps,p0

def func_revenue(q0,supply_lst,running_costs,slice_hours):##q0 = demand
    #print('running_costs: ',running_costs)
    #print('supply_lst: ',supply_lst)

    total_avail_capacity = sum(supply_lst)
    #print('\n' + 'The total_avail_capacity is: ' + str(total_avail_capacity))
    eq_production = 0
# =============================================================================
    for pos, pp_capacity in enumerate(supply_lst, start=0):
        eq_production += pp_capacity
        if eq_production == 0: continue
        demand_price = p0 * q0 ** (-1 / eps) * eq_production ** (1 / eps)
        
        if demand_price <= running_costs[pos]:
            eq_price = running_costs[pos]## means price will be the running cost of first type.
            eq_production = q0 * (eq_price / p0) ** eps 
            break
            
        else: ##if demand_price > run_costs[i]
            eq_price = demand_price
            if total_avail_capacity - eq_production > 0 and demand_price > running_costs[pos+1]: continue
                ## first if :## if there is still remaining/unruned production/plants.second if: check if on the vertical line
            else: break ## if demand_price <= run_costs[i+1] or total_avail_capacity=max
    
    hour_revuene =(eq_price - np.asarray(running_costs)) * supply_lst * 1000 #convert to Kw.
    hour_revuene = np.where(hour_revuene < 0, 0, hour_revuene)
    # annual revuene.
    slice_revuene = hour_revuene * slice_hours
    #print('eq_price',eq_price)
    #print('eq_production',eq_production)
    return slice_revuene,eq_price,eq_production