# Imports
import pytz
import requests
import json
from datetime import datetime

from algoritmoAnaliseParaFicheirosVideo import detectionAlg


def main():
    ip = requests.get('https://api.ipify.org').text

    URL_AREAS = "http://" + ip + ":8181/services/eventos/api/areas"

    header_authentication = {
        "Content-Type": "application/json"
    }

    body_authentication = {
        "password": "admin",
        "username": "admin"
    }

    token = requests.post("http://localhost:8181/api/authenticate", headers=header_authentication, data=json.dumps(body_authentication)).json()

    print(token['id_token'])

    bearer_token = "Bearer " + token['id_token']

    headers = {
        'Authorization': bearer_token}

    areas_json = requests.get(URL_AREAS, headers=headers).json()

    print(areas_json)

    detectionAlg(areas_json, ip, token['id_token'])


if __name__ == '__main__':
    main()
