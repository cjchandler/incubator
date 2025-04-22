import matplotlib.pyplot as plt
import datetime
import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from pytz import timezone
utc = timezone('UTC')
from pysolar.solar import *
import os

# header with names

df = pd.read_csv("/home/carl/Git_Projects/growth_chamber_data_2024/2024-09-11_state.csv")
df['datetime'] = pd.to_datetime(df['last_save_timestamp'], unit='s')
df = df.set_index('datetime')
print(df)
df = df.drop(['last_save_timestamp'], axis=1)

df1 = df

df = pd.read_csv("/home/carl/Git_Projects/growth_chamber_data_2024/2024-09-11_state.csv")
df['datetime'] = pd.to_datetime(df['last_save_timestamp'], unit='s')
df = df.set_index('datetime')
print(df)
df = df.drop(['last_save_timestamp'], axis=1)

df2 = df 

df = pd.read_csv("/home/carl/Git_Projects/growth_chamber_data_2024/2024-09-11_state.csv")
df['datetime'] = pd.to_datetime(df['last_save_timestamp'], unit='s')
df = df.set_index('datetime')
print(df)
df = df.drop(['last_save_timestamp'], axis=1)

df3 = df 

final_df = pd.concat([ df1 , df2, df3] )
final_df.drop(final_df.index[:3], inplace=True)
final_df = final_df[["temperature_C" , "humidity"]].copy()


final_df.plot()
plt.show()
