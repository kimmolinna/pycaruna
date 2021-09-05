import sys

sys.path.append('../pycaruna')

import json
import os
from datetime import date, datetime, timedelta
from pycaruna import Caruna, Resolution


def make_min_hour_datetime(date):
    return datetime.combine(date, datetime.min.time())


def make_max_hour_datetime(date):
    return datetime.combine(date, datetime.max.time()).replace(microsecond=0)


if __name__ == '__main__':
    username = os.getenv('CARUNA_USERNAME')
    password = os.getenv('CARUNA_PASSWORD')

    if username is None or password is None:
        raise Exception('CARUNA_USERNAME and CARUNA_PASSWORD must be defined')

    client = Caruna(username, password)
    client.login()

    # Get customer details and metering points so we can get the required identifiers
    customer = client.get_user_profile()
    metering_points = client.get_metering_points(customer['username'])

    # Fetch data from midnight 00:00 7 days ago to 23:59 today
    start_time = make_min_hour_datetime(date.today() - timedelta(days=7)).astimezone().isoformat()
    end_time = make_max_hour_datetime(date.today()).astimezone().isoformat()

    metering_point = metering_points[0]['meteringPoint']['meteringPointNumber']

    consumption = client.get_consumption(customer['username'],
                                         metering_points[0]['meteringPoint']['meteringPointNumber'],
                                         Resolution.DAYS, True,
                                         start_time, end_time)

    # Extract the relevant data, filter out days without values (usually the most recent datapoint)
    filtered_consumption = [item for item in consumption if item['values']]
    mapped_consumption = list(map(lambda item: {
        'date': make_max_hour_datetime(
            date.today().replace(year=item['year'], month=item['month'], day=item['day'])).isoformat(),
        'kwh_total': item['values']['EL_ENERGY_CONSUMPTION#0']['value'],
        'kwh_night': item['values']['EL_ENERGY_CONSUMPTION#2']['value'],
        'kwh_day': item['values']['EL_ENERGY_CONSUMPTION#3']['value'],
    }, filtered_consumption))

    print(json.dumps(mapped_consumption))
