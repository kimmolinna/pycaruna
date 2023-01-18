import requests
import pycaruna.utils as utils
from enum import Enum


class TimeSpan(Enum):
    DAILY = 'daily'
    MONTHLY = 'monthly'
    YEARLY = 'yearly'


class CarunaPlus:
    def __init__(self, token):
        self.token = token

    def get_user_profile(self, customer_id):
        """
        Returns the user's profile information
        :param customer_id: the customer number
        :return: the user information
        """
        r = requests.get(url=utils.create_caruna_plus_url(f'/customers/{customer_id}/info'),
                         headers=utils.create_caruna_plus_headers(self.token))

        return r.json()

    def get_assets(self, customer_id):
        """
        Returns the metering points available for the specified customer
        :param customer_id: the customer ID
        :return: the metering points, including a lot of metadata about them
        """
        r = requests.get(url=utils.create_caruna_plus_url(f'/customers/{customer_id}/assets'),
                         headers=utils.create_caruna_plus_headers(self.token))

        return r.json()

    def get_contracts(self, customer_id):
        """
        Returns the contracts available for the specified customer
        :param customer_id: the customer ID
        :return: the contracts
        """
        r = requests.get(url=utils.create_caruna_plus_url(f'/customers/{customer_id}/contracts'),
                         headers=utils.create_caruna_plus_headers(self.token))

        return r.json()

    def get_energy(self, customer_id, asset_id, timespan, year, month, day):
        """
        Returns energy consumption for the specified metering point
        :param customer_id: the customer ID
        :param asset_id: the asset ID
        :param timespan: the time span (a TimeSpan enum)
        :param year: the year
        :param month: the month
        :param day: the day
        :return: the consumption data
        """
        r = requests.get(url=utils.create_caruna_plus_url(f'/customers/{customer_id}/assets/{asset_id}/energy'),
                         params={
                             'year': year,
                             'month': month,
                             'day': day,
                             'timespan': timespan.value,
                         },
                         headers=utils.create_caruna_plus_headers(self.token))

        return r.json()
