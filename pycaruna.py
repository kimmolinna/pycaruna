import sys
import requests
from bs4 import BeautifulSoup

def login (username,password):
    # login to Caruna+ as a registered user
    # ("username","password") 
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

    action=soup.find('form')['action'][1:][:11]+"IBehaviorListener.0-userIDPanel-loginWithUserID"

    # get hidden inputs for the form
    svars = {}
    for var in soup.findAll('input',type="hidden"):
        try:
            svars[var['name']] = var['value']
        except:
            svars[var['name']] = ''
    
    svars['ttqusername']=username
    svars['userPassword']=password
    svars[soup.find('input',type="submit")['name']]="1"

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
    url = BeautifulSoup(r.content,'lxml').findAll('meta')[0]['content'][6:]
    r = s.get(url)
    return s  # session out
def getCurrent(s):
    # get current user infromation
    # s as session
    r=s.get("https://energiaseuranta.caruna.fi/api/users?current")
    return r    # response out
def getMeteringPoints (s,customer):
    # get Metering point information
    # s as session
    # "customer" as customer number (string) 
    r=s.get("https://energiaseuranta.caruna.fi/api/customers/"+customer+"/meteringPointInformationWrappers")
    return r
def getConsHours (s,customer,meteringPoint,start_day,end_day):
    # get consumption per hour
    # s as session
    # "customer" as customer number (string)
    # "meteringPoint" as metering poin number (string)
    # "start_day" as "2020-04-01"
    # "end_day as "2020-04-30" 
    r=s.get("https://energiaseuranta.caruna.fi/api/meteringPoints/ELECTRICITY/"+meteringPoint+"/series?products=EL_ENERGY_CONSUMPTION&resolution=MONTHS_AS_HOURS&customerNumber="+customer+"&startDate="+start_day+"T00:00:00-0700&endDate="+end_day+"T00:00:00-0700")
    return r    # response out
def logout(s):
    # logout
    # s as session
    r=s.get("https://authentication2.caruna.fi/portal/logout")
    return r    #response out   