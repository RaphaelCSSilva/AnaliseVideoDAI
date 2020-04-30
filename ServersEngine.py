# Imports
import pytz
import requests
import json
from datetime import datetime

from real_time_counting_targeted_object_teste_zmq import detectionAlg


def main():
    ip = requests.get('https://api.ipify.org').text

    URL_AREAS = "http://" + ip + ":8181/services/eventos/api/areas"

    headers = {
        'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9'
                         '.eyJzdWIiOiJhZG1pbiIsImF1dGgiOiJST0xFX0FETUlOLFJPTEVfVVNFUiIsImV4cCI6MTU5MDE0ODUzM30'
                         '.MDFoVukkynl8xxdR7lzhYSNod6PvJSiCvGhpCyuwpUgSfS7hYiD37yUfIN8T_S_lPh11xUEo4TiLTkqsXxrqBg'}

    areas_json = requests.get(URL_AREAS, headers=headers).json()

    detectionAlg(areas_json, ip)


if __name__ == '__main__':
    main()
