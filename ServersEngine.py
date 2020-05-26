# Imports
import pytz
import requests
import json
from datetime import datetime

from algoritmoAnalise import detectionAlg


def main():
    ip = requests.get('https://api.ipify.org').text

    URL_AREAS = "http://" + ip + ":8181/services/eventos/api/areas"

    bearer_token = "eyJhbGciOiJIUzUxMiJ9" \
                   ".eyJzdWIiOiJhZG1pbiIsImF1dGgiOiJST0xFX0FETUlOLFJPTEVfVVNFUiIsImV4cCI6MTU5Mjc3NzM3OX0" \
                   ".TrBopLe1_Qh3tQFIUDYn_R_0oX-3aqCehUDsLo1poUcvkfb5oFQYBdD7-Ht4P_JPGBJdV41K4LjUOZ4dXxxyOw "

    headers = {
        'Authorization': bearer_token}

    areas_json = requests.get(URL_AREAS, headers=headers).json()

    detectionAlg(areas_json, ip)


if __name__ == '__main__':
    main()
