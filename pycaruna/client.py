from urllib.parse import urlparse, parse_qs
import requests
import pycaruna.utils as utils
from bs4 import BeautifulSoup
from enum import Enum


class Resolution(Enum):
    DAYS = 'MONTHS_AS_DAYS'
    HOURS = 'MONTHS_AS_HOURS'


CARUNA_PLUS_API_BASE_URL = 'https://plus.caruna.fi/api'


class Caruna:

    def __init__(self, username, password):
        """
        :param username: your e-mail address
        :param password: your password
        """
        self.username = username
        self.password = password
        self.session = None
        self.token = None
        self.user = None
        pass

    def login(self):
        """
        Performs the login dance required to obtain cookies etc. for further API communication
        """
        s = requests.session()

        # Start the authentication flow. This page will do some redirects and finally return a JSON object containing
        # a URL we have to visit manually
        r = s.post(CARUNA_PLUS_API_BASE_URL + '/authorization/login', json={
            'language': 'fi',
            'redirectAfterLogin': 'https://plus.caruna.fi/',
        })

        r = s.get(r.json()['loginRedirectUrl'])

        # Parse the <meta http-equiv="refresh"> URL and request it (ng2Postresponder)
        url = BeautifulSoup(r.content, 'lxml').findAll('meta')[0]['content'][6:]
        r = s.get("https://authentication2.caruna.fi" + url)

        # Now we're at the actual login page. We need to find the <form>, get its "action" attribute, then modify it
        # so it actually posts to the correct place. Normally the form submission and action mangling is done by
        # JavaScript.
        c = r.content
        soup = BeautifulSoup(c, 'lxml')
        action = "/wicket/page?3-1.IBehaviorListener.0-userIDPanel-usernameLogin-loginWithUserID"

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

        # Parse the form and submit it (would normally be done by JavaScript). Normally it would be enough to have it
        # automatically redirect through all the intermediate URLs, but we need to intercept a particular one in order
        # to grab the Connect2id callback parameters
        soup = BeautifulSoup(r.content, 'lxml')
        action = soup.find('form')['action']
        r = s.post(action, data=utils.get_hidden_form_vars(soup), allow_redirects=False)
        r = s.get(r.headers['Location'], allow_redirects=False)
        openid_login_return_url = r.headers['Location']

        # Extract code, state and session_state
        parsed_url = urlparse(openid_login_return_url)
        parsed_query = parse_qs(parsed_url.query)
        connect2id_params = {
            'code': parsed_query['code'][0],
            'state': parsed_query['state'][0],
            'session_state': parsed_query['session_state'][0],
        }

        # Okay, we now have the Connect2id stuff. Now we can get an OAuth token which is needed for the actual API
        # requests...
        r = s.post(CARUNA_PLUS_API_BASE_URL + '/authorization/token', data=connect2id_params)
        json_r = r.json()
        self.token = json_r['token']

        return json_r['user']

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
