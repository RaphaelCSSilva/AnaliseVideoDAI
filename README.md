# AnaliseVideoDAI

Parte de análise de vídeo do projeto de DAI 2019/2020 MIEGSI UMinho.

Parte da WebApp: https://github.com/NunoVelosoMIEGSI/prisontech

# Preview

Ainda estamos a realizar o vídeo demonstrativo. 

# Instalação

Nota: Python versão 3.6 foi usada neste trabalho, sendo o python 3.5-3.7 requerido pelo tensorflow.

Nota2: Versão do tensorflow a instalar: 1.14.0

Para o funcionamento deste repositório será necessário instalar as seguintes dependências:

*   OpenCV
*   imutils
*   ImageZMQ
*   Tensorflow
*   Requests

Exemplo

```
pip install opencv-python
pip install imutils
...
```

Para instalação do Tensorflow ver: https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/installation.md


# Utilização

Depois de instalada todas as dependências é preciso correr o ficheiro ServersEngine.py.

Windows:

```
python ServersEngine.py
```

Linux:

```
python3 ServersEngine.py
```

É necessário também iniciar um servidor http na pasta de output.

Windows
```
python -m http.server
```

Linux:
```
python3 -m http.server
```

Finalmente apenas é necessário conectar com o cliente, usando o ficheiro client.py com o comando abaixo ou então através da imagem docker do cliente.

Com o ficheiro client.py

Windows
```
python client.py --server-ip <ip da máquina a correr o servidor (ServersEngine)>
```

Linux:
```
python3 client.py --server-ip <ip da máquina a correr o servidor (ServersEngine)>
```

Com a docker image (correr em Linux):

Primeiro dar pull da docker image:

```
docker pull dai1920/imagezmq
```

Verificar o id da imagem (IMAGE ID):
```
docker images
```

Depois correr a imagem:

```
docker run --device /dev/video0 -e mac=$(ip link show [INTERFACE DE REDE A UTILIZAR] | awk '/ether/ {print $2}') [IMAGEID da imagem vista em cima]
```

# Erros Comuns

De vez em quando o ServersEngine.py pode dar um erro na inicialização, fechar e voltar a correr normalmente resolve o problema.


Créditos:

https://github.com/ahmetozlu/tensorflow_object_counting_api

https://www.pyimagesearch.com/

