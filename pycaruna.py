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
    url = json.loads(s.post("https://plus.caruna.fi/api/authorization/login",
        json = {"redirectAfterLogin":"https://plus.caruna.fi/",
        "language":"fi"}).content)["loginRedirectUrl"]
    soup = BeautifulSoup(s.get(url).content,'lxml')
    post_url = soup.find('meta')['content'][6:] # type: ignore
    r = s.get("https://authentication2.caruna.fi" + str(post_url))
    soup = BeautifulSoup(r.content,'lxml')
    action=soup.find('form')['action'][1:][:17]+"0-userIDPanel-usernameLogin-loginWithUserID"  # type: ignore
    svars = {}
    for var in soup.findAll('input',type="hidden"):
        try:
            svars[var['name']] = var['value']
        except:
            svars[var['name']] = ''    
    svars['ttqusername']=username
    svars['userPassword']=password
    svars[soup.find('input',type="submit")['name']]="1"  # type: ignore
    extraHeaders = { 
        'Wicket-Ajax': 'true',
        'Wicket-Ajax-BaseURL': '.',
        'Wicket-FocusedElementId': 'loginWithUserID5',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://authentication2.caruna.fi',
        'Referer': 'https://authentication2.caruna.fi/portal/'
    }
    text = s.post("https://authentication2.caruna.fi/portal"+action, 
        data=svars, headers=extraHeaders).text
    text = text[text.find('CDATA[')+7:]
    url = text[:text.find(']')]
    r = s.get("https://authentication2.caruna.fi/portal"+url)
    soup = BeautifulSoup(r.content,'lxml')
    url = soup.find('meta')['content'][6:]  # type: ignore
    soup = BeautifulSoup(s.get(str(url)).content,'lxml')
    action =soup.find('form')['action']  # type: ignore
    svars = {}
    for var in soup.findAll('input',type="hidden"):
        try:
            svars[var['name']] = var['value']
        except:
            svars[var['name']] = ''
    r = s.post(action, data=svars)  # type: ignore
    r = s.post("https://plus.caruna.fi/api/authorization/token",data = r.request.path_url.split("?")[1])
    info = json.loads(r.text)
    return (s,info)    
def get_metering_points (s : requests.Session,token : str,customer : str):
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
        "&day="+day+"&timespan=daily",
        headers={'Authorization': 'Bearer '+token})
    return r.json()
def logout_caruna(s : requests.Session):
    """Logout from Caruna+

    Arguments:
        s -- The session object for the user

    Returns:
        The response from the logout
    """
    return s.get('https://authentication2.caruna.fi/portal/').ok