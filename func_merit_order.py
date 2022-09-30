#merit_order
from operator import itemgetter#, attrgetter
from cls_Power_Plant import PowerPlant#, tech_lst

def func_merit_order(tax,tech_lst):
    merit_order =[]
    for tech in tech_lst:
        print(tech)
        merit_order.append((tech,tech.running_cost(tax)))
    # print(merit_order)
    merit_order = sorted(merit_order, key=itemgetter(1))
    tech_order = list(map(itemgetter(0), merit_order))
    cost_order = list(map(itemgetter(1), merit_order))
    # print(f'tech_order',tech_order)
    # print(f'cost_order',cost_order)
    # print(f'merit_order_full',merit_order)
    return tech_order,cost_order
# tech_order,cost_order = func_merit_order(10)
# print(tech_order)
# print(cost_order)

