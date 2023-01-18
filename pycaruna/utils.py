CARUNA_PLUS_API_BASE_URL = 'https://plus.caruna.fi/api'
PYCARUNA_USER_AGENT = 'pycaruna'


def create_caruna_plus_url(path):
    return f'{CARUNA_PLUS_API_BASE_URL}{path}'


def create_caruna_plus_headers(token):
    return {
        'Authorization': f'Bearer {token}',
        'User-Agent': PYCARUNA_USER_AGENT,
    }


def get_hidden_form_vars(soup):
    vars = {}

    for var in soup.findAll('input', type="hidden"):
        try:
            vars[var['name']] = var['value']
        except KeyError:
            vars[var['name']] = ''

    return vars
