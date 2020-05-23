# Imports
import pytz
import requests
import json
from datetime import datetime

from real_time_counting_targeted_object_teste_zmq import detectionAlg


def main():
    ip = requests.get('https://api.ipify.org').text

    URL_AREAS = "http://" + ip + ":8181/services/eventos/api/areas"

    bearer_token = ""

    headers = {
        'Authorization': bearer_token}

    areas_json = requests.get(URL_AREAS, headers=headers).json()

    detectionAlg(areas_json, ip)


if __name__ == '__main__':
    main()
