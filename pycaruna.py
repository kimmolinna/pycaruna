import json

import requests
from bs4 import BeautifulSoup


def _hidden_fields(soup):
    """Return hidden form inputs. A missing value becomes an empty string."""
    fields = {}
    for field in soup.find_all("input", type="hidden"):
        fields[field["name"]] = field.get("value", "")
    return fields


def _meta_redirect(soup, step):
    """Return the target of a meta refresh. Content is ``0;url=<location>``."""
    meta = soup.find("meta")
    if meta is None or "content" not in meta.attrs:
        raise RuntimeError(f"Caruna login failed at {step}: no meta redirect")
    return meta["content"][6:]


def _form_action(soup, step):
    form = soup.find("form")
    if form is None or "action" not in form.attrs:
        raise RuntimeError(f"Caruna login failed at {step}: no login form")
    return form["action"]


def _wicket_redirect(text):
    """Read the relative URL from a Wicket AJAX ``<![CDATA[./<url>]]>`` redirect.

    The slice skips the ``CDATA[`` marker and the leading ``.``.
    """
    marker = "CDATA["
    start = text.find(marker)
    if start < 0:
        raise RuntimeError("Caruna login failed after credentials: no Wicket redirect")
    relative = text[start + len(marker) + 1:]
    end = relative.find("]")
    if end < 0:
        raise RuntimeError("Caruna login failed after credentials: Wicket redirect was truncated")
    return relative[:end]


def login_caruna(username: str, password: str):
    """Login to Caruna+ as a registered user.

    Arguments:
        username -- The username of the user for Caruna+
        password -- The password of the user for Caruna+

    Returns:
        The session object for the user and the user information
    """
    session = requests.Session()
    try:
        redirect_url = session.post(
            "https://plus.caruna.fi/api/authorization/login",
            json={"redirectAfterLogin": "https://plus.caruna.fi/", "language": "fi"},
        ).json()["loginRedirectUrl"]
    except (json.JSONDecodeError, KeyError) as exc:
        raise RuntimeError("Caruna login failed at authorization redirect") from exc

    soup = BeautifulSoup(session.get(redirect_url).content, "lxml")
    login_page = session.get("https://authentication2.caruna.fi" + _meta_redirect(soup, "login page"))
    soup = BeautifulSoup(login_page.content, "lxml")

    # Drop the leading character, keep the 11-character Wicket page id, and
    # target the username login component.
    action = _form_action(soup, "username form")[1:][:11] + "0-userIDPanel-usernameLogin-loginWithUserID"
    fields = _hidden_fields(soup)
    fields["ttqusername"] = username
    fields["userPassword"] = password
    submit = soup.find("input", type="submit")
    if submit is None or "name" not in submit.attrs:
        raise RuntimeError("Caruna login failed at username form: no submit button")
    fields[submit["name"]] = "1"

    ajax = session.post(
        "https://authentication2.caruna.fi/portal" + action,
        data=fields,
        headers={
            "Wicket-Ajax": "true",
            "Wicket-Ajax-BaseURL": ".",
            "Wicket-FocusedElementId": "loginWithUserID5",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://authentication2.caruna.fi",
            "Referer": "https://authentication2.caruna.fi/portal/",
        },
    )
    after_login = session.get("https://authentication2.caruna.fi/portal" + _wicket_redirect(ajax.text))
    soup = BeautifulSoup(after_login.content, "lxml")
    continue_page = session.get(_meta_redirect(soup, "post-login redirect"))
    soup = BeautifulSoup(continue_page.content, "lxml")

    submitted = session.post(_form_action(soup, "token form"), data=_hidden_fields(soup))
    if "?" not in submitted.request.path_url:
        raise RuntimeError("Caruna login failed at token exchange: redirect had no query")
    try:
        info = session.post(
            "https://plus.caruna.fi/api/authorization/token",
            data=submitted.request.path_url.split("?")[1],
        ).json()
    except json.JSONDecodeError as exc:
        raise RuntimeError("Caruna login failed at token exchange: response was not JSON") from exc
    return (session, info)


def get_metering_points(s: requests.Session, token: str, customer: str):
    """Get the metering points for the user.

    Arguments:
        s -- The session object for the user
        token -- The token for the user
        customer -- The customer number for the user

    Returns:
        The list of metering points (metering point number, address) for the customer
    """
    response = s.get(
        f"https://plus.caruna.fi/api/customers/{customer}/assets",
        headers={"Authorization": "Bearer " + token},
    )
    response.raise_for_status()
    return [(asset["assetId"], asset["address"]["streetName"]) for asset in response.json()]


def get_cons_hours(s: requests.Session, token: str, customer: str, metering_point: str,
                   year: str, month: str, day: str):
    """Get the consumption data for the specified metering point for one day.

    Arguments:
        s -- The session object for the user
        token -- The token for the user
        customer -- The customer number for the user
        metering_point -- The metering point number for the customer
        year -- A year for the consumption data (YYYY)
        month -- A month for the consumption data (MM)
        day -- A day for the consumption data (DD)

    Returns:
        The list of Caruna data for the specified metering point (JSON)
    """
    response = s.get(
        f"https://plus.caruna.fi/api/customers/{customer}/assets/{metering_point}/energy"
        f"?year={year}&month={month}&day={day}&timespan=daily",
        headers={"Authorization": "Bearer " + token},
    )
    response.raise_for_status()
    return response.json()


def logout_caruna(s: requests.Session):
    """Logout from Caruna+.

    Arguments:
        s -- The session object for the user

    Returns:
        Whether the logout request succeeded
    """
    return s.get("https://authentication2.caruna.fi/portal/").ok
