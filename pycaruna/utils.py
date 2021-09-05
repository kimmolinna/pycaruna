def get_hidden_form_vars(soup):
    vars = {}

    for var in soup.findAll('input', type="hidden"):
        try:
            vars[var['name']] = var['value']
        except KeyError:
            vars[var['name']] = ''

    return vars
