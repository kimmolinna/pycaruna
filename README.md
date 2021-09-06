# pycaruna

Basic Python implementation for interfacing with Caruna's API. It supports only basic methods, 
but enough to extract electricity usage data for further processing.

Supported features:

* Get user profile information
* Get metering points
* Get consumption data (daily/hourly, optioanlly divided by tariffs)

## Usage

> TODO: Publish to PyPi

You can use this package by adding the following to your `requirements.txt`:

```
git+https://github.com/Jalle19/pycaruna.git@7289352ee5f0a829c21a71f131ad34df9f3c3c24#egg=pycaruna==0.0.2
```

The library can then be used like this:

```python
import json
from datetime import date, datetime
from pycaruna import Caruna, Resolution

if __name__ == '__main__':
    caruna = Caruna('you@example.com', 'password')
    caruna.login()

    customer = caruna.get_user_profile()
    metering_points = caruna.get_metering_points(customer['username'])

    end_time = datetime.combine(date.today(), datetime.min.time()).astimezone().isoformat()
    start_time = datetime.combine(date.today().replace(day=1), datetime.min.time()).astimezone().isoformat()
    metering_point = metering_points[0]['meteringPoint']['meteringPointNumber']

    consumption = caruna.get_consumption(customer['username'],
                                         metering_points[0]['meteringPoint']['meteringPointNumber'],
                                         Resolution.DAYS, True,
                                         start_time, end_time)
    print(json.dumps(consumption))
```

The resources directory has examples of API response structures.

Please note that the authentication procedure requires a lot of HTTP requests to be sent back and forth, so the 
script is relatively slow.

## Credits

https://github.com/kimmolinna/pycaruna

## License

MIT
