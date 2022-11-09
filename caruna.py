from datetime import datetime

import awswrangler as wr
import keyring
import pandas as pd
from dateutil.relativedelta import relativedelta

import pycaruna

start_day = datetime.now().strftime("%Y-%m")+"-01"
end_day = (datetime.now() + relativedelta(months=1)).strftime("%Y-%m")+"-01"
session = pycaruna.login_caruna("kimmo.linna@gmail.com",keyring.get_password("caruna", "kimmo.linna@gmail.com"))
customer = pycaruna.get_current(session)
metering_points = pycaruna.get_metering_points(session, customer)
consumption = pycaruna.get_cons_hours(session, customer, metering_points[1][0], start_day, end_day)
timestamps=[]
consumption_values=[]
for hour in consumption:
    measure = hour["values"].get("EL_ENERGY_CONSUMPTION#0")
    if measure is not None:
        timestamps.append(hour["timestamp"])
        consumption_values.append(measure["value"])
df = pd.DataFrame.from_dict({"timestamp":timestamps,"consumption":consumption_values})
month = timestamps[len(timestamps)-1][:7].replace("-","") 
wr.s3.to_parquet(df, "s3://linna/caruna/caruna_"+ month +".parquet")
pycaruna.logout_caruna(session)

#Kimmo Linna