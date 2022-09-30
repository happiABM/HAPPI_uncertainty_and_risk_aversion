#CLASS consumer
from params import sliced_el_demand

class Consumer ():

    @classmethod
    def express_demand(cls,consumer_demand):
        if consumer_demand == 'electricity' or consumer_demand == 'el':
            return sliced_el_demand
        else: 
            raise ValueError ('We are sorry to inform you that HAPPI cannot provide ' +consumer_demand+ ' at the moment.')

# a = Consumer()
# a.express_demand('electricity')
