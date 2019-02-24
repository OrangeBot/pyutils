import requests


CONNECTION_CHECK_DEFAULT_SERVER = "https://www.google.com"
CONNECTION_CHECK_TIMEOUT = 2


def is_connected(hostname, timeout=CONNECTION_CHECK_TIMEOUT):
    try:
        requests.get(hostname, timeout=timeout)
        return True
    except requests.ConnectionError:
        return False


def connected_to_internet(chosen_server=CONNECTION_CHECK_DEFAULT_SERVER):
    return is_connected(chosen_server)
