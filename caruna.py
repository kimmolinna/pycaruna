from datetime import datetime

import awswrangler as wr
import keyring
import pandas as pd
from dateutil.relativedelta import relativedelta

import pycaruna

(year,month,day) = (datetime.now() - relativedelta(days=3)).strftime("%Y %m %d").split()
(session,info) = pycaruna.login_caruna("kimmo.linna@gmail.com",str(keyring.get_password("caruna", "kimmo.linna@gmail.com")))
customer = info['user']['ownCustomerNumbers'][0]
token = info['token']
metering_points = pycaruna.get_metering_points(session, token, customer)
consumption = pycaruna.get_cons_hours(session, token, customer, metering_points[1][0], year, month, day)
values = [(hour['timestamp'],hour['temperature'],hour['totalConsumption']) for hour in consumption]
(timestamp_values,temperature_values,consumption_values) = [[row[i]for row in values] for i in range(3)]
df = pd.DataFrame.from_dict({"timestamp":timestamp_values,
    "temperature":temperature_values,
    "consumption":consumption_values})
wr.s3.to_parquet(df, "s3://linna/caruna/caruna_"+ year + month + day +".parquet")
pycaruna.logout_caruna(session)