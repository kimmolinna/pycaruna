import requests
import json 
from bs4 import BeautifulSoup
from urllib import parse

def login_caruna (username: str,password: str):
    """Login to Caruna+ as a registered user

    Arguments:
        username -- The username of the user for Caruna+\n
        password -- The password of the user for Caruna+
    Returns:
        The session object for the user and the user information
    """    

    s = requests.session()
    r = s.post("https://plus.caruna.fi/api/authorization/login",
        json = {"redirectAfterLogin":"https://plus.caruna.fi/","language":"fi"})
    url = json.loads(r.text)["loginRedirectUrl"]
    r = s.get(url)
    c = r.content
    soup = BeautifulSoup(c,'lxml')
    post_url = soup.find('meta')['content'][6:] # type: ignore
    r = s.get("https://authentication2.caruna.fi" + str(post_url))
    c = r.content
    soup = BeautifulSoup(c,'lxml')
    action=soup.find('form')['action'][1:][:17]+"IBehaviorListener.0-userIDPanel-usernameLogin-loginWithUserID"  # type: ignore
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
        'Wicket-Ajax-BaseURL': '.',
        'Wicket-FocusedElementId': 'loginWithUserID5',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://authentication2.caruna.fi',
        'Referer': 'https://authentication2.caruna.fi/portal/'
    }
    
    # Post a form
    r = s.post("https://authentication2.caruna.fi/portal"+action, data=svars, headers=extraHeaders)

    # AJAX-page/redirect #1
    text = r.text
    text = text[text.find('CDATA[')+7:]
    url = text[:text.find(']')]
    r = s.get("https://authentication2.caruna.fi/portal"+url)

    c = r.content
    soup = BeautifulSoup(c,'lxml')

    # change to a correct action
    url = soup.find('meta')['content'][6:]  # type: ignore
    r = s.get(str(url))

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
    r = s.post(action, data=svars,allow_redirects=False)  # type: ignore
    r = s.get(r.headers['Location'],allow_redirects=False)
    ids = r.headers['Location']
    caruna_query = parse.urlsplit(ids).query
    r = s.get(ids,headers=extraHeaders,allow_redirects=False)
    r = s.post("https://plus.caruna.fi/api/authorization/token",data = caruna_query)
    info = json.loads(r.text)
    return (s,info)    
def get_metering_points (s : requests.Session,customer : str,token : str):
    """Get the metering points for the user

    Arguments:
        s -- The session object for the user\n
        customer -- The customer number for the user\n
        token -- The token for the user\n
    Returns:
        The list of metering points[meteringPoinNumber,address] for the customer
    """
    r=s.get("https://plus.caruna.fi/api/customers/"+customer+"/assets",
        headers={'Authorization': 'Bearer '+token}).json()
    return [(c['assetId'],c['address']['streetName']) for c in r]
def get_cons_hours (s : requests.Session,token :str,
                    customer : str,metering_point : str,
                    year:str, month: str, day : str):
    """Get the consumption data for the specified metering point for one day

    Arguments:
        s -- Ths session object for the user\n
        token -- The token for the user\n
        customer -- The customer number for the user\n
        metering_point -- The metering point number for the customer\n
        day -- A day for the consumption data (DD)\n
        month -- A month for the consumption data (MM)\n
        year -- A year for the consumption data (YYYY)

    Returns:
        The list of Caruna data for the specified metering point (JSON)
    """ 
    r=s.get("https://plus.caruna.fi/api/customers/"+customer+"/assets/"+
        metering_point+"/energy?year="+year+"&month="+month+
        "&day="+day+"&timespan=hourly",
        headers={'Authorization': 'Bearer '+token})
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