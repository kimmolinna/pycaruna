import requests
import pycaruna.utils as utils
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

        # Start page. We can't go straight to the login page, we have to start here.
        # Will perform some 302 redirects including some OAuth initiation until we get to a HTTP 200 (ng2Responder)
        r = s.get("https://energiaseuranta.caruna.fi/mobile/")

        # Parse the <meta http-equiv="refresh"> URL and request it (ng2Postresponder)
        url = BeautifulSoup(r.content, 'lxml').findAll('meta')[0]['content'][6:]
        r = s.get("https://authentication2.caruna.fi" + url)

        # Now we're at the actual login page. We need to find the <form>, get its "action" attribute, then modify it
        # so it actually posts to the correct place. Normally the form submission and action mangling is done by
        # JavaScript.
        c = r.content
        soup = BeautifulSoup(c, 'lxml')
        action = soup.find('form')['action'][1:][:11] + "IBehaviorListener.0-userIDPanel-usernameLogin-loginWithUserID"

        # Build form variables (all hidden variables must always be included)
        svars = utils.get_hidden_form_vars(soup)
        svars['ttqusername'] = self.username
        svars['userPassword'] = self.password
        svars[soup.find('input', type="submit")['name']] = "1"

        # Post the form, with some extra headers that are required for proper response
        r = s.post("https://authentication2.caruna.fi/portal" + action, data=svars, headers={
            'Wicket-Ajax': 'true',
            'Wicket-Ajax-BaseURL': 'login',
            'Wicket-FocusedElementId': 'loginWithUserID5',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://authentication2.caruna.fi',
            'Referer': 'https://authentication2.caruna.fi/portal/login'
        })

        # Redirect to the location indicated by the Ajax-Location header
        location = r.headers['Ajax-Location'][1:]
        r = s.get("https://authentication2.caruna.fi/portal" + location)

        # Parse the <meta http-equiv="refresh"> URL and request it (ngPostResponder)
        url = BeautifulSoup(r.content, 'lxml').findAll('meta')[0]['content'][6:]
        r = s.get(url)

        # Parse the form and submit it (would normally be done by JavaScript). This will then finally redirect through
        # some OAuth endpoints and in the end you'll be authenticated.
        soup = BeautifulSoup(r.content, 'lxml')
        action = soup.find('form')['action']
        s.post(action, data=utils.get_hidden_form_vars(soup))

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
