##initialize existing (coal and gas) power plants.
#from cls_Power_Company import Power_Company#,old_company
from itertools import cycle

def func_initialize_plant (company_lst,tech_lst):
    for company in company_lst:
        for tech in tech_lst:
            lifespan = list(range(tech.lifetime,0,-1))#range backwards.
            # if tech_lst.index(tech) % 2 == 0: #even number
            #     lifespan = list(range(tech.lifetime,0,-1))#range backwards.
            # else:
            #     lifespan = list(range(1,tech.lifetime+1,1))#range forward.
                

            for x,y in zip(range(company.portfolio[tech]),cycle(lifespan)):
                tech(owner = company,lifespan = y) #evenly disribute lifespan.
            
    #return      
    
    
    
    
    # initial_coalPlant_nr = 128 #start with 128 coal plants = 64GW.
    # owner_name.portfolio['CoalPlant'] = initial_coalPlant_nr
    # ##======initilized initial coal plants==========###
    # ##the remaining lifespan of the initial plants are evenly distributed\
    # #\between 1 to 40. And there are 8 more plants with maximal lifespan.
    # repeat_value = initial_coalPlant_nr//CoalPlant.lifetime ##divisor 
    # remainder =  initial_coalPlant_nr % CoalPlant.lifetime #remainder
    # for remaining_year in range(1,CoalPlant.lifetime+1):
    #     for i in range(repeat_value):
    #         #creat several plants with the same remaining lifespan
    #         CoalPlant(lifespan=remaining_year,owner = owner_name)

    # for nr in range (remainder):
    #     #creat the rest of the plants with the maximal lifespan (40 years)
    #     CoalPlant(lifespan=CoalPlant.lifetime,owner = owner_name)

    # # print(CoalPlant.count)

    # ##======initilized initial NGCC plants==========###
    # initial_ngccPlant_nr = 4 #start with 4 NGCC plants = 2GW.
    # owner_name.portfolio['NgccPlant'] = initial_ngccPlant_nr
    # #arbitrarily set the lifespan of the 4 initial Ngcc plants to\
    # # [10,15,20,25]
    # lifespan_lst = [10,15,20,25]
    # for remaining_year in lifespan_lst:
    #     pp = NgccPlant(lifespan=remaining_year,owner=owner_name)
    # # print (NgccPlant.count)
    # #print('the initial capacity of coal is: ',CoalPlant.available_capacity())
    

# print(CoalPlant.quantity) #print out the final capacity mix.