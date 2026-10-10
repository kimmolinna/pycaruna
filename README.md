# pycaruna
Caruna API for Python

Reads electricity consumption from Caruna+. Login follows Caruna's web sign-in and parses the Wicket login page, so it breaks when Caruna changes that form.

## Install

```bash
pip install -r requirements.txt
```

Runtime dependencies:

- `requests`
- `beautifulsoup4`
- `lxml` — BeautifulSoup parser used by `login_caruna`. Login fails without it.

`caruna.py` is a separate example that also needs `keyring`, `pandas`, `python-dateutil`, and `awswrangler`. Those are not required to use the library.

## Functions

The module includes the following functions:

- `login_caruna (username: str,password: str)`
- `get_metering_points (s : requests.Session,token : str, customer : str)`
- `get_cons_hours (s : requests.Session,token : str,customer : str,metering_point : str,year : str,month : str, day : str)`
- `logout_caruna(s)`


Sample use of code:

```python
import pycaruna
(session,info) = pycaruna.login_caruna("username", "password")
customer = info['user']['ownCustomerNumbers'][0]
token = info['token']
metering_points = pycaruna.get_metering_points(session, token, customer)
consumption = pycaruna.get_cons_hours(session, token, customer, metering_points[0][0], "2023", "1", "3")
response = pycaruna.logout_caruna(session)
```
