# pycaruna

Basic Python implementation for interfacing with Caruna Plus (sometimes called _Caruna+_). It supports only basic 
methods, but enough to extract electricity usage data for further processing.

Supported features:

* Get user profile information
* Get metering points ("assets")
* Get consumption data (daily/hourly)

## Usage

> TODO: Publish to PyPi

You can use this package by adding the following to your `requirements.txt`:

```
git+https://github.com/Jalle19/pycaruna.git@7289352ee5f0a829c21a71f131ad34df9f3c3c24#egg=pycaruna==0.0.2
```

The `assets/` directory has example Python programs illustrrating how to use the library.

The `resources/` directory has examples of API response structures.

Please note that the authentication procedure requires a lot of HTTP requests to be sent back and forth, so the 
script is relatively slow. It's best to store the token produced by it and reusing that instead of doing the 
authentication process all over again.

## Credits

https://github.com/kimmolinna/pycaruna

## License

MIT
