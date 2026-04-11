# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**pycaruna** is a single-module Python library that wraps the Caruna+ API (Finnish energy company) to retrieve energy consumption data. The entire API surface lives in `pycaruna.py`.

## Dependencies

No `requirements.txt` exists. Dependencies must be installed manually:

```bash
pip install requests beautifulsoup4 lxml
```

The example script `caruna.py` additionally uses `awswrangler`, `keyring`, `pandas`, and `python-dateutil` for exporting data to AWS S3.

## Usage

```python
import pycaruna

(session, info) = pycaruna.login_caruna("username", "password")
customer = info['user']['ownCustomerNumbers'][0]
token = info['token']
metering_points = pycaruna.get_metering_points(session, token, customer)
consumption = pycaruna.get_cons_hours(session, token, customer, metering_points[0][0], "2023", "1", "3")
response = pycaruna.logout_caruna(session)
```

## Architecture

The library exposes four stateless functions that share a `requests.Session` object:

1. **`login_caruna(username, password)`** — The most complex function. Implements a multi-step authentication flow against `authentication2.caruna.fi` using Apache Wicket's AJAX form submission. Uses BeautifulSoup to scrape form fields and redirect URLs from HTML responses. Returns `(session, info)` where `info` contains `token` and `user.ownCustomerNumbers`.

2. **`get_metering_points(s, token, customer)`** — Calls `/api/customers/{customer}/assets` with Bearer auth. Returns list of `(assetId, streetName)` tuples.

3. **`get_cons_hours(s, token, customer, metering_point, year, month, day)`** — Calls `/api/customers/{customer}/assets/{metering_point}/energy?timespan=daily`. Returns raw JSON with hourly consumption and temperature data.

4. **`logout_caruna(s)`** — GET to `authentication2.caruna.fi/portal/`, returns `response.ok`.

All API endpoints are under `https://plus.caruna.fi/api/` except authentication which goes through `https://authentication2.caruna.fi/portal/`.
