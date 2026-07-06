import matplotlib.pyplot as plt
import datetime
import numpy as np
import pandas as pd

import os

# header with names
#/home/cjchandler/Git_Projects/incubator_public/incubator/pi_incubator/datalog
path = "./datalog/"

v = "_piV1"

#"2026-03-25_state

df = pd.read_csv( path + "2026-07-06_state"+ v+".csv")
df['datetime'] = pd.to_datetime(df['last_save_timestamp'], unit='s')
df = df.set_index('datetime')
print(df.columns)
df = df.drop(['last_save_timestamp'], axis=1)

df2 = df 



final_df = pd.concat([  df2 ] )
final_df = final_df.sort_index()
final_df.drop(final_df.index[:5], inplace=True)
# ~ final_df["deltaT"] = final_df["temperature_1_C"] - final_df["temperature_2_C"] 
# ~ final_df["deltaTthermocouple"] = final_df["thermocouple_1"] - final_df["thermocouple_2"] 
# ~ final_df = final_df[["temperature_1_C" , "humidity_1", "temperature_2_C" , "humidity_2" , "deltaT" , "deltaTthermocouple", "near_switch" , "far_switch"]].copy()

final_df = final_df[["temperature_1_C" , "humidity_1" , "heater_on","target_temperature", 'front_turn_switch', 'rear_turn_switch', 'top_switch']].copy()
# ~ final_df = final_df[["near_switch" ,  "far_switch"]].copy()

 # ~ state_dict['heating_proportional_Cf'] = 0.2
    # ~ state_dict['heating_integral_Cf'] = 0.00001 #2 p , 0.001i was too big perhaps 
    # ~ state_dict['heating_derivitive_Cf'] = 0.


final_df.plot()
plt.show()
