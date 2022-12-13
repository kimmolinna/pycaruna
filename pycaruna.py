import requests
from bs4 import BeautifulSoup


def login_caruna (username: str,password: str)->requests.Session:
    """Login to Caruna+ as a registered user

    Arguments:
        username -- The username of the user for Caruna+\n
        password -- The password of the user for Caruna+
    Returns:
        The session object for the user
    """    

    s = requests.session()

    # start page
    r = s.get("https://energiaseuranta.caruna.fi/mobile/")

    # first redirect
    url = BeautifulSoup(r.content,'lxml').findAll('meta')[0]['content'][6:]
    r = s.get ("https://authentication2.caruna.fi"+ url)

    # login page
    c = r.content
    soup = BeautifulSoup(c,'lxml')

    # change to a correct action

    action=soup.find('form')['action'][1:][:11]+"IBehaviorListener.0-userIDPanel-usernameLogin-loginWithUserID"  # type: ignore

    # get hidden inputs for the form
    svars = {}
    for var in soup.findAll('input',type="hidden"):
        try:
            svars[var['name']] = var['value']
        except:
            svars[var['name']] = ''
    
    svars['ttqusername']=username
    svars['userPassword']=password
    svars[soup.find('input',type="submit")['name']]="1"  # type: ignore

    # Headers for Ajax and Wicket
    extraHeaders = { 
        'Wicket-Ajax': 'true',
        'Wicket-Ajax-BaseURL': 'login',
        'Wicket-FocusedElementId': 'loginWithUserID5',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://authentication2.caruna.fi',
        'Referer': 'https://authentication2.caruna.fi/portal/login'
    }
    
    # Post a form
    r = s.post("https://authentication2.caruna.fi/portal"+action, data=svars, headers=extraHeaders)

    # AJAX-page/redirect #1
    text = r.text
    text = text[text.find('CDATA[')+7:]
    url = text[:text.find(']')]
    r = s.get("https://authentication2.caruna.fi/portal"+url)

    # Redirect #2
    url = BeautifulSoup(r.content,'lxml').findAll('meta')[0]['content'][6:]
    r = s.get(url)

    # Authorization/redirect #3
    soup = BeautifulSoup(r.content,'lxml')
    action =soup.find('form')['action']  # type: ignore
    svars = {}
    for var in soup.findAll('input',type="hidden"):
        try:
            svars[var['name']] = var['value']
        except:
            svars[var['name']] = ''
    extraHeaders = { 
        'Origin': 'https://authentication2.caruna.fi',
        'Referer': 'https://authentication2.caruna.fi/portal/login'
    } 
    r = s.post(action, data=svars, headers=extraHeaders)  # type: ignore
    return s
def get_current(s : requests.Session)->str:
    """Get the current user information

    Arguments:
        s -- The session object for the user

    Returns:
        The customer number for the user
    """
    r=s.get("https://energiaseuranta.caruna.fi/api/users?current")
    return r.json()["username"]
def get_metering_points (s : requests.Session,customer : str)->list[dict]:
    """Get the metering points for the user

    Arguments:
        s -- The session object for the user\n
        customer -- The customer number for the user
    Returns:
        The list of metering points[meteringPoinNumber,address] for the customer
    """
    r=s.get("https://energiaseuranta.caruna.fi/api/customers/"+customer+"/meteringPointInformationWrappers").json()
    mps = []
    for e in r["entities"]:
        mps.append([e["meteringPoint"][key] for key in ["meteringPointNumber","address"]])
    return mps 
def get_cons_hours (s : requests.Session,
                    customer : str,metering_point : str,
                    start_day : str,end_day : str)->list[dict]:
    """Get the consumption data for the specified metering point

    Arguments:
        s -- Ths session object for the user\n
        customer -- The customer number for the user\n
        metering_point -- The metering point number for the customer\n
        start_day -- Start day for the consumption data (YYYY-MM-DD)\n
        end_day -- End day for the consumption data (YYYY-MM-DD)

    Returns:
        The list of consumption data for the specified metering point (JSON)
    """ 
    r=s.get("https://energiaseuranta.caruna.fi/api/meteringPoints/ELECTRICITY/"+metering_point+"/series?products=EL_ENERGY_CONSUMPTION&resolution=MONTHS_AS_HOURS&customerNumber="+customer+"&startDate="+start_day+"T00:00:00-0000&endDate="+end_day+"T00:00:00-0000")
    return r.json()
def logout_caruna(s)->requests.Response:
    """Logout from Caruna+

    Arguments:
        s -- The session object for the user

    Returns:
        The response from the logout
    """
    r=s.get("https://authentication2.caruna.fi/portal/logout")
    return r 