# pycaruna
Caruna API for Python

The module includes the following functions:

- `login_caruna (username: str,password: str)`
- `get_current(s : requests.Session)->str`
- `get_metering_points (s : requests.Session,customer : str)->list[dict]`
- `get_cons_hours (s : requests.Session,customer : str,metering_point : str,start_day : str,end_day : str)->list[dict]`
- `logout_caruna(s)`


Sample use of code:

```python
import pycaruna
session = pycaruna.login("username", "password")
customer = pycaruna.get_current(session)
metering_points = pycaruna.get_metering_points(session, customer)
consumption = pycaruna.get_cons_hours(session, customer, metering_point, "2022-11-01", "2022-11-30")
response = pycaruna.logout(session)
```
