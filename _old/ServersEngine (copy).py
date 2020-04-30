# Imports
import pytz
import requests
import json
from datetime import datetime


from Evento.Area import Area

#from real_time_counting_targeted_object_teste_zmq import detectionAlg


def main():
    #area1 = Area('area1', 2, 0, 2, {'Teste': 'Teste'})
    #detectionAlg(1, 1, 1)

    URL_CAMARA = "http://148.63.202.53:8181/services/eventos/api/camaras/1"

    URL_AREA = "http://148.63.202.53:8181/services/eventos/api/areas/1"

    URL_TIPOEVENTO = "http://148.63.202.53:8181/services/eventos/api/tipoeventos/1"

    headers = {'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhZG1pbiIsImF1dGgiOiJST0xFX0FETUlOLFJPTEVfVVNFUiIsImV4cCI6MTU5MDE0ODUzM30.MDFoVukkynl8xxdR7lzhYSNod6PvJSiCvGhpCyuwpUgSfS7hYiD37yUfIN8T_S_lPh11xUEo4TiLTkqsXxrqBg'}

    area_json = requests.get(URL_AREA, headers=headers).json()

    camara_json = requests.get(URL_CAMARA, headers=headers).json()

    tipo_evento_json = requests.get(URL_TIPOEVENTO, headers=headers).json()

    print(tipo_evento_json['descricao'])

    data = {
        "descricao": "Teste Timeouts Resolvidos?10",
        "numPessoasPerm": 2,
        "numPessoasDet": 3,
        "dataHoraInicio": "2020-04-17T15:25:00Z",
        "dataHoraFim": "2020-04-17T15:25:00Z",
        "path": "http://148.63.202.53:8000/20200418-185126.webm",
        "formato": "webm",
        "area": area_json,
        "camara": camara_json,
        "tipoevento": tipo_evento_json
    }


    #null = None

    # data = {
    #     "descricao": "Maior",
    #     "eventos": None
    # }

    #json.load(data)
    #json.dumps(data)

    data_toSend = json.dumps(data)

    #print(json.dumps(data))

    #r = requests.post("http://148.63.202.53:8181/services/eventos/api/tipoeventos", headers=headers, json=data_toSend)

    #r = requests.post("https://httpbin.org/post", json=data_toSend)

    #json_response = r.json()

    #print(json_response)

    # sending get request and saving the response as response object
    #response = requests.get(URL, headers=headers)

    #json_response = response.json()

    #print(json_response)

    url = "http://148.63.202.53:8181/services/eventos/api/areas"

    payload = "{\n        \"descricao\": \"TestePython4\",\n        \"eventos\": null\n    }"
    #headers = {
    #    'Content-Type': "application/json",
    #    'Authorization': "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhZG1pbiIsImF1dGgiOiJST0xFX0FETUlOLFJPTEVfVVNFUiIsImV4cCI6MTU5MDE0ODUzM30.MDFoVukkynl8xxdR7lzhYSNod6PvJSiCvGhpCyuwpUgSfS7hYiD37yUfIN8T_S_lPh11xUEo4TiLTkqsXxrqBg",
    #    'cache-control': "no-cache",
    #}

    response = requests.get(url, headers=headers).json()

    #response = json.dumps(response)

    print(type(response))

    print(response[0]['camaras'])

    print(type(response[0]['camaras']))

    print(response[0]['camaras'][0]['enderecoIp'])

    mac = "148.63.202.53"

    id_cam = None

    for i in range(len(response)):
        print(i)
        for j in range(len(response[i]['camaras'])):
            mac_compare = response[i]['camaras'][j]['enderecoIp']
            if mac == mac_compare:
                id_cam = response[i]['camaras'][j]['id']
                print("Mac: {}  \nId_cam:  {}  \nId_area: {}  \nId_tipoevento: {}".format(mac_compare, id_cam, response[i]['id'], response[i]['tipoevento']['id']))


    print(len(response))

    #response['descricao'] = "teste"

    print(response)

    ip = requests.get('https://api.ipify.org').text
    print('My public IP address is:', ip)

    #print(datetime.strftime(datetime.now()))

    # timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    #
    # timestamp2 = datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    #
    # print("1 " + timestamp)
    #
    # print("2 " + timestamp2)

    #print(timestamp.strftime('%y-%m-%d %H:%M:%S'))




if __name__ == '__main__':
    main()