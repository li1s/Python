
import urllib3
urllib3.disable_warnings()

import requests
import json

TDSK_API_URL="https://192.168.3.160"
TDSK_LOGIN_URL="{}/api/auth/v1/legacy/login".format(TDSK_API_URL)
TDSK_CONNECTION_URL="{}/rest/connection".format(TDSK_API_URL)
TDSK_CONNECTION_INFO_URL="{}/api/client/v1/connectionInfo".format(TDSK_API_URL)
TDSK_PRECONNECTION_INFO_URL="{}/api/client/draft/preconnectionInfo".format(TDSK_API_URL)
TDSK_ENABLE_URL="{}/rest/termidesk/enable".format(TDSK_API_URL)

TDSK_RDS_LOGIN="user1"
TDSK_RDS_PASSWORD="user1"
TDSK_RDS_AUTH="main"

TDSK_STAL_LOGIN="test1"
TDSK_STAL_PASSWORD="test1"
TDSK_STAL_AUTH="main"

TDSK_LOGIN=TDSK_STAL_LOGIN
TDSK_PASSWORD=TDSK_STAL_PASSWORD
TDSK_AUTH=TDSK_STAL_AUTH

TDSK_LOGIN=TDSK_RDS_LOGIN
TDSK_PASSWORD=TDSK_RDS_PASSWORD
TDSK_AUTH=TDSK_RDS_AUTH

hostname="abcde"
version="4.1.0.23017-dev-578d2d5"
user_agent="User-Agent: Mozilla/5.0 (FreeBSD) AppleWebKit/537.21 (KHTML, like Gecko) Termidesk Client/{VERSION} (QtWebKitWidgets)".format(
        VERSION=version)

# login
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'}
url = TDSK_LOGIN_URL
print("POST url: {}".format(url))
print("Headers: {}".format(headers))
jsn = {'username':TDSK_LOGIN, 'password':TDSK_PASSWORD, 'auth':TDSK_AUTH}
r = requests.post(TDSK_LOGIN_URL, verify=False, headers=headers, json=jsn)
if r.status_code != 200:
    raise Exception("Fail auth: {}".format(r.text))
print("Login result: {}".format(json.dumps(r.json(), indent=2)))
result=r.json().get('result')
token=r.json().get('token')

# connection
headers = {
    'accept': 'application/json',
    'X-Auth-Token': token}
url = TDSK_CONNECTION_URL
print("GET url: {}".format(url))
print("Headers: {}".format(headers))
r = requests.get(url, verify=False, headers=headers)
if r.status_code != 200:
    raise Exception("Fail connection: {}".format(r.text))
print("Login connection: {}".format(json.dumps(r.json(), indent=2)))
result = r.json().get('result')

conn0 = result[0]
for transport in conn0.get('transports'):
    # enable
    headers = {
        'accept': 'application/json',
        'X-Auth-Token': token}
    url = "{}/{}/{}".format(
        TDSK_ENABLE_URL, conn0.get('id'), transport.get('id'))
    print("GET url: {}".format(url))
    print("Headers: {}".format(headers))
    r = requests.get(url, verify=False, headers=headers)
    if r.status_code != 200:
        raise Exception("Fail connection: {}".format(r.text))
    print("Transport connection: {}".format(json.dumps(r.json(), indent=2)))
    ticket= r.json().get('result').get('ticket')

    # preconnection info
    headers = {
        'accept': 'application/json'}
    url = "{}/{}?hostname={}&version={}".format(
        TDSK_PRECONNECTION_INFO_URL, ticket, hostname, version)
    print("GET url: {}".format(url))
    print("Headers: {}".format(headers))
    r = requests.get(url, verify=False, headers=headers)
    if r.status_code != 200:
        raise Exception("Fail connection: {}".format(r.text))
    print("Transport Info: {}".format(json.dumps(r.json(), indent=2))) 

    # connection info
    headers = {
        'accept': 'application/json'}
    url = "{}/{}?hostname={}&version={}".format(
        TDSK_CONNECTION_INFO_URL, ticket, hostname, version)
    print("GET url: {}".format(url))
    print("Headers: {}".format(headers))
    r = requests.get(url, verify=False, headers=headers)
    if r.status_code != 200:
        raise Exception("Fail connection: {}".format(r.text))
    print("Connection info: {}".format(json.dumps(r.json(), indent=2)))

