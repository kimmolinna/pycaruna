import requests
from bs4 import BeautifulSoup
from enum import Enum


class Resolution(Enum):
    DAYS = 'MONTHS_AS_DAYS'
    HOURS = 'MONTHS_AS_HOURS'


class Caruna:

    def __init__(self, username, password):
        """
        :param username: your e-mail address
        :param password: your password
        """
        self.username = username
        self.password = password
        self.session = None
        pass

    def login(self):
        """
        Performs the login dance required to obtain cookies etc. for further API communication
        """
        s = requests.session()

        # start page
        r = s.get("https://energiaseuranta.caruna.fi/mobile/")

        # first redirect
        url = BeautifulSoup(r.content, 'lxml').findAll('meta')[0]['content'][6:]
        r = s.get("https://authentication2.caruna.fi" + url)

        # login page
        c = r.content
        soup = BeautifulSoup(c, 'lxml')

        # change to a correct action

        action = soup.find('form')['action'][1:][:11] + "IBehaviorListener.0-userIDPanel-loginWithUserID"

        # get hidden inputs for the form
        svars = {}
        for var in soup.findAll('input', type="hidden"):
            try:
                svars[var['name']] = var['value']
            except KeyError:
                svars[var['name']] = ''

        svars['ttqusername'] = self.username
        svars['userPassword'] = self.password
        svars[soup.find('input', type="submit")['name']] = "1"

        # Headers for Ajax and Wicket
        extra_headers = {
            'Wicket-Ajax': 'true',
            'Wicket-Ajax-BaseURL': 'login',
            'Wicket-FocusedElementId': 'loginWithUserID5',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://authentication2.caruna.fi',
            'Referer': 'https://authentication2.caruna.fi/portal/login'
        }

        # Post a form
        r = s.post("https://authentication2.caruna.fi/portal" + action, data=svars, headers=extra_headers)

        # AJAX-page/redirect #1
        text = r.text
        text = text[text.find('CDATA[') + 7:]
        url = text[:text.find(']')]
        r = s.get("https://authentication2.caruna.fi/portal" + url)

        # Redirect #2
        url = BeautifulSoup(r.content, 'lxml').findAll('meta')[0]['content'][6:]
        r = s.get(url)

        # Authorization/redirect #3
        url = BeautifulSoup(r.content, 'lxml').findAll('meta')[0]['content'][6:]
        s.get(url)

        self.session = s

    def logout(self):
        """
        Closes the session by logging out
        :return: the response object
        """
        r = self.session.get("https://authentication2.caruna.fi/portal/logout")
        return r

    def get_user_profile(self):
        """
        Returns the current user's profile information
        :return: the user details
        """
        r = self.session.get("https://energiaseuranta.caruna.fi/api/users?current")
        return r.json()

    def get_metering_points(self, customer):
        """
        Returns the metering points available for the specified customer
        :param customer: the customer ID
        :return: the metering points, including a lot of metadata about them
        """
        r = self.session.get(
            "https://energiaseuranta.caruna.fi/api/customers/" + str(customer) + "/meteringPointInformationWrappers")
        response = r.json()
        return response['entities']

    def get_consumption(self, customer, metering_point, resolution, tariff_division, start_time, end_time):
        """
        Returns consumption statistics for the specified metering point
        :param customer: the customer ID
        :param metering_point: the metering point ID
        :param resolution: the resolution (a Resolution enum)
        :param tariff_division: whether to divide consumption into tariffs
        :param start_time: a datetime object
        :param end_time: a datetime object
        :return: the consumption data
        """
        params = {
            'products': 'EL_ENERGY_CONSUMPTION',
            'resolution': resolution.value,
            'tariffDivision': 'true' if tariff_division else 'false',
            'customerNumber': str(customer),
            'startDate': start_time,
            'endDate': end_time,
        }

        r = self.session.get(
            "https://energiaseuranta.caruna.fi/api/meteringPoints/ELECTRICITY/" + str(metering_point) + "/series",
            params=params)
        return r.json()
