#HAPPI
#other params
import pandas as pd

##========= electricity market===========##
eps = -0.05
p0 = 3.25 #cent/kWh.
p0 *= 10**(-2) #euro/kWh. 
##===========slice data=============##
data_slice = pd.read_excel("param/slice_param.xlsx",engine='openpyxl',sheet_name="slice_params",header=0,index_col=0)
sliced_el_demand = data_slice.loc['demand_level'].values # MW(h)
slice_hours = data_slice.loc['slice_hours'].values
wind_availability = data_slice.loc['wind_level'].values
solar_availability = data_slice.loc['solar_level'].values
nonVER_availability = data_slice.loc['nonVER_level'].values
# print(sliced_el_demand)

similation_period = 200
extra_year = 40