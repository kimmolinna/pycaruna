# pycaruna
Caruna API for Python

The module includes the following functions:

- `login(username, password)`
- `getCurrent(session)`
- `getMeteringPoints(session, customer)`
- `getConsHours(session, customer, meteringPoint, start_day, end_day)`
- `logout(session)`


Sample use of code:

```python
import pycaruna
session = pycaruna.login("username", "password")
response = pycaruna.getConsHours(session, "0000000", "000000", "2018-04-01", "2020-04-30")
consumption = response.json()
response = pycaruna.logout(session)
```
