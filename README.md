# pycaruna
Caruna API for Python

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
