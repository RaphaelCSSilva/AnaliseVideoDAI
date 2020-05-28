# ----------------------------------------------
# --- Author         : Ahmet Ozlu
# --- Mail           : ahmetozlu93@gmail.com
# --- Date           : 27th January 2018
# ----------------------------------------------

# usage on linux: python3 real_time_counting_targeted_object.py
# usage on windows: python real_time_counting_targeted_object.py

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

# Imports
import argparse
import datetime
import time

import pytz
import requests
import json

import imagezmq
import tensorflow as tf

# Object detection imports
from imutils import build_montages

from utils import visualization_utils as vis_util
from utils.fpsGetter import get_fps_from_camera
from utils.keyclipwriter import KeyClipWriter
from utils.maxDetectionsBuffer import MaxDetectionBuffer
from utils import backbone
import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", default='output',
                help="path to output directory")
ap.add_argument("-b", "--buffer-time", type=int, default=10,
                help="time before and after the event to record, in seconds")
ap.add_argument("-c", "--confidence", type=float, default=0.25,
                help="minimum probability to filter weak detections")
ap.add_argument("-n", "--number-to-detect", type=int, default=0,
                help="number of people to do the specific detections")
ap.add_argument("-op", "--operation", type=str, default="",
                help="Operation to perform, it can be -gt for greater or equal than, -lt for less or equal than or -eq for equal to")
ap.add_argument("-mW", "--montageW", type=int,
                help="montage frame width")
ap.add_argument("-mH", "--montageH", type=int,
                help="montage frame height")
args = vars(ap.parse_args())


def detectionAlg(areas_json, ip, token):

    bearer_token = "Bearer " + token

    headersGet = {
        'Authorization': bearer_token
    }

    headersPost = {
        'Content-Type': "application/json",
        'Authorization': bearer_token,
        'cache-control': "no-cache",
    }

    first_detection = True

    #fps = get_fps_from_camera()
    fps = 30


    buffer = int(round(fps * args["buffer_time"]))

    print(fps, buffer)

    output = args["output"]

    confidence = args["confidence"]

    kcw = KeyClipWriter(bufSize=buffer)
    consecFrames = 0

    maxDetectionBuffer = MaxDetectionBuffer(buffSize=10)

    # By default I use an "SSD with Mobilenet" model here. See the detection model zoo (https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md) for a list of other models that can be run out-of-the-box with varying speeds and accuracies.
    detection_graph, category_index = backbone.set_model('ssd_mobilenet_v1_coco_2018_01_28', 'mscoco_label_map.pbtxt')

    targeted_object = "person"  # (for counting targeted objects) change it with your targeted objects
    is_color_recognition_enabled = 0

    # initialize the ImageHub object
    imageHub = imagezmq.ImageHub()

    frameDict = {}

    # initialize the dictionary which will contain  information regarding
    # when a device was last active, then store the last time the check
    # was made was now
    lastActive = {}
    lastActiveCheck = datetime.datetime.now()

    # stores the estimated number of Pis, active checking period, and
    # calculates the duration seconds to wait before making a check to
    # see if a device was active
    ESTIMATED_NUM_PIS = 1
    ACTIVE_CHECK_PERIOD = 10
    ACTIVE_CHECK_SECONDS = ESTIMATED_NUM_PIS * ACTIVE_CHECK_PERIOD

    # assign montage width and height so we can view all incoming frames
    # in a single "dashboard"
    mW = 1
    mH = 1

    firstConnection = True

    print("[INFO] detecting: persons...")

    updateConsecFrames = True

    total_passed_vehicle = 0
    speed = "waiting..."
    direction = "waiting..."
    size = "waiting..."
    color = "waiting..."
    the_result = "..."
    width_heigh_taken = True
    height = 0
    width = 0

    pessoas_det_final = 0

    cap = cv2.VideoCapture('HomeInvasionTest.mp4')

    with detection_graph.as_default():
        with tf.compat.v1.Session(graph=detection_graph) as sess:
            # Definite input and output Tensors for detection_graph
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

            # Each box represents a part of the image where a particular object was detected.
            detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
            detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')

            print("\nA entrar no while...")

            while True:

                #(rpiName, frame) = imageHub.recv_image()
                #imageHub.send_reply(b'OK')
                rpiName = "14:4f:8a:aa:22:d3"
                ret, frame = cap.read()


                # if a device is not in the last active dictionary then it means
                # that its a newly connected device
                if firstConnection:

                    print("[INFO] receiving data from {}...".format(rpiName))

                    id_area = None

                    id_cam = None

                    id_tipoevento = None

                    for i in range(len(areas_json)):
                        print(i)
                        for j in range(len(areas_json[i]['camaras'])):
                            mac_compare = areas_json[i]['camaras'][j]['enderecoMac']
                            if rpiName == mac_compare:
                                id_cam = areas_json[i]['camaras'][j]['id']

                                id_area = areas_json[i]['id']

                                id_tipoevento = areas_json[i]['tipoevento']['id']

                                print("Mac: {}  \nId_cam:  {}  \nId_area: {}  \nId_tipoevento: {}".format(mac_compare,
                                                                                                          id_cam,
                                                                                                          id_area,
                                                                                                          id_tipoevento))

                    url_camara = "http://" + ip + ":8181/services/eventos/api/camaras/" + str(id_cam)

                    url_area = "http://" + ip + ":8181/services/eventos/api/areas/" + str(id_area)

                    url_tipoevento = "http://" + ip + ":8181/services/eventos/api/tipoeventos/" + str(id_tipoevento)

                    url_eventos = "http://" + ip + ":8181/services/eventos/api/eventos"

                    area_json = requests.get(url_area, headers=headersGet).json()

                    print(area_json)

                    camara_json = requests.get(url_camara, headers=headersGet).json()

                    tipo_evento_json = requests.get(url_tipoevento, headers=headersGet).json()

                    numPessoasPerm = area_json['numPessoasPerm']

                    firstConnection = False

                # record the last active time for the device from which we just
                # received a frame
                #lastActive[rpiName] = datetime.datetime.now()

                # for all the frames that are extracted from input video

                frame = cv2.resize(frame, (800, 600))

                #input_frame = frame

                # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                image_np_expanded = np.expand_dims(frame, axis=0)

                # Actual detection.
                (boxes, scores, classes, num) = sess.run(
                    [detection_boxes, detection_scores, detection_classes, num_detections],
                    feed_dict={image_tensor: image_np_expanded})

                #print(scores)

                # insert information text to video frame
                font = cv2.FONT_HERSHEY_SIMPLEX

                #if scores[0][0] >= confidence:

                # Visualization of the results of a detection.
                counter, csv_line, the_result = vis_util.visualize_boxes_and_labels_on_image_array(-1,
                                                                                                   frame,
                                                                                                   1,
                                                                                                   is_color_recognition_enabled,
                                                                                                   np.squeeze(
                                                                                                       boxes),
                                                                                                   np.squeeze(
                                                                                                       classes).astype(
                                                                                                       np.int32),
                                                                                                   np.squeeze(
                                                                                                       scores),
                                                                                                   category_index,
                                                                                                   min_score_thresh = 0.35,
                                                                                                   targeted_objects=targeted_object,
                                                                                                   use_normalized_coordinates=True,
                                                                                                   line_thickness=4)
                if len(the_result) == 0:
                    cv2.putText(frame, "...", (10, 35), font, 0.8, (0, 255, 255), 2, cv2.FONT_HERSHEY_SIMPLEX)
                else:
                    cv2.putText(frame, the_result, (10, 35), font, 0.8, (0, 255, 255), 2,
                                cv2.FONT_HERSHEY_SIMPLEX)

                #tipo_detetado = the_result[1:7]

                # try:
                #     numPessoasDet = int(float(the_result[11:12]))
                #     print(the_result[11:12])
                # except ValueError:
                #     print("numPessoasDet deu ValueError")

                if len(the_result) != 0:
                    numPessoasDet = int(float(the_result[11:12]))
                    tipo_detetado = the_result[1:7]
                    maxDetectionBuffer.update(numPessoasDet)
                    print(the_result[11:12])
                else:
                    numPessoasDet = 0
                    tipo_detetado = ""
                    #print("Nao houve detecoes")

                #print(tipo_detetado)

                if tipo_detetado == 'person':
                    consecFrames = 0

                    # if we are not already recording, start recording
                    if not kcw.recording:
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%SZ")
                        p = "{}/{}.webm".format(output, timestamp)
                        kcw.start(p, cv2.VideoWriter_fourcc(*'VP80'), fps)

                        timestamp = timestamp.replace("_", ":")

                    print(tipo_evento_json['descricao'])

                    print("first_detection = {}".format(first_detection))

                    #if tipo_evento_json['descricao'] == "Maior" and maxDetectionBuffer.isFull():
                        #pessoas_det_final = numPessoasDet if numPessoasDet > pessoas_det_final else pessoas_det_final

                    #elif tipo_evento_json['descricao'] == "Menor" and maxDetectionsBuffer == fps:
                        #pessoas_det_final = numPessoasDet if numPessoasDet < pessoas_det_final else pessoas_det_final

                    if maxDetectionBuffer.isFull():
                        pessoas_det_final = maxDetectionBuffer.getMaxDetectionNum() if tipo_evento_json['descricao'] == "Maior" and maxDetectionBuffer.getMaxDetectionNum() > pessoas_det_final else pessoas_det_final
                        pessoas_det_final = maxDetectionBuffer.getMaxDetectionNum() if tipo_evento_json[
                                                                                           'descricao'] == "Menor" and maxDetectionBuffer.getMaxDetectionNum() < pessoas_det_final else pessoas_det_final

                        print("Pessoas_det_final: {}.".format(pessoas_det_final))
                        maxDetectionBuffer.clearBufferArray()


                    if tipo_evento_json['descricao'] != "" and first_detection:
                        if tipo_evento_json['descricao'] == "eq":
                            if numPessoasDet == numPessoasPerm:
                                print("Somos {}!".format(numPessoasPerm))

                        if tipo_evento_json['descricao'] == "Maior":
                            if numPessoasDet > numPessoasPerm:
                                print("Somos mais do que {}!".format(numPessoasPerm))

                                descricao = "Detetou-se " + str(
                                    numPessoasDet) + " pessoa(s), quando o maximo e de " + str(
                                    numPessoasPerm) + ' pessoa(s).'

                                current_video_name = p[7:]

                                dataHoraInicio = timestamp

                                dataHoraFim = timestamp

                                data = {
                                    "descricao": descricao,
                                    "numPessoasPerm": numPessoasPerm,
                                    "numPessoasDet": numPessoasDet,
                                    "dataHoraInicio": dataHoraInicio,
                                    "dataHoraFim": dataHoraFim,
                                    "path": "http://" + ip + ":5580/" + current_video_name,
                                    "formato": "webm",
                                    "area": area_json,
                                    "camara": camara_json,
                                    "tipoevento": tipo_evento_json
                                }

                                print("Data before json.dumps: {}".format(data))

                                dataToSend = json.dumps(data, indent=4, sort_keys=True, default=str)

                                print("Data after json.dumps: " + dataToSend)

                                response = requests.post(url_eventos, data=dataToSend, headers=headersPost).json()

                                print(response)

                                first_detection = False
                        if tipo_evento_json['descricao'] == "Menor":
                            if numPessoasDet < numPessoasPerm:
                                print("Somos menos do que {}!".format(numPessoasPerm))

                                descricao = "Detetou-se " + str(
                                    numPessoasDet) + " pessoa(s), quando o mínimo é de " + str(
                                    numPessoasPerm) + ' pessoa(s).'

                                current_video_name = p[7:]

                                dataHoraInicio = timestamp

                                dataHoraFim = timestamp

                                data = {
                                    "descricao": descricao,
                                    "numPessoasPerm": numPessoasPerm,
                                    "numPessoasDet": numPessoasDet,
                                    "dataHoraInicio": dataHoraInicio,
                                    "dataHoraFim": dataHoraFim,
                                    "path": "http://" + ip + ":5580/" + current_video_name,
                                    "formato": "webm",
                                    "area": area_json,
                                    "camara": camara_json,
                                    "tipoevento": tipo_evento_json
                                }

                                dataToSend = json.dumps(data, indent=4, sort_keys=True, default=str)

                                response = requests.post(url_eventos, data=dataToSend, headers=headersPost).json()

                                first_detection = False
                else:
                    maxDetectionsBuffer = 0

                # update the new frame in the frame dictionary
                #frameDict[rpiName] = frame

                # build a montage using images in the frame dictionary
                montages = build_montages(frameDict.values(), (800, 600), (mW, mH))

                # if current time *minus* last time when the active device check
                # was made is greater than the threshold set then do a check
                # if (datetime.datetime.now() - lastActiveCheck).seconds > ACTIVE_CHECK_SECONDS:
                #     # loop over all previously active devices
                #     for (rpiName, ts) in list(lastActive.items()):
                #         # remove the RPi from the last active and frame
                #         # dictionaries if the device hasn't been active recently
                #         if (datetime.datetime.now() - ts).seconds > ACTIVE_CHECK_SECONDS:
                #             print("[INFO] lost connection to {}".format(rpiName))
                #             lastActive.pop(rpiName)
                #             frameDict.pop(rpiName)
                #
                #     # set the last active check time as current time
                #     lastActiveCheck = datetime.datetime.now()

                # display the montage(s) on the screen
                # for (i, montage) in enumerate(montages):
                #     cv2.imshow("Home pet location monitor ({})".format(i),
                #                montage)

                cv2.imshow("Cam " + rpiName, frame)

                # otherwise, no action has taken place in this frame, so
                # increment the number of consecutive frames that contain
                # no action
                if updateConsecFrames:
                    consecFrames += 1

                # update the key frame clip buffer
                kcw.update(frame)

                # if we are recording and reached a threshold on consecutive
                # number of frames with no action, stop recording the clip
                if kcw.recording and consecFrames == buffer:
                    kcw.finish()
                    print("TesteFinish")
                    novaDataHoraFim = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                    response['dataHoraFim'] = novaDataHoraFim

                    response['descricao'] = "Detetou-se " + str(
                                    pessoas_det_final) + " pessoa(s), quando o maximo e de " + str(
                                    numPessoasPerm) + ' pessoa(s).'
                    
                    response['numPessoasDet'] = pessoas_det_final 

                    #dataToSend = json.dumps(response)

                    dataToSend = json.dumps(response, indent=4, sort_keys=True, default=str)

                    responseStopped = requests.put(url_eventos, data=dataToSend, headers=headersPost).json()

                    print(responseStopped)

                    first_detection = True

                    consecFrames = 0

                    pessoas_det_final = 0

                # cv2.imshow('object counting', input_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # if we are in the middle of recording a clip, wrap it up
            if kcw.recording:
                kcw.finish()
                print("TesteFinish")
                novaDataHoraFim = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                response['dataHoraFim'] = novaDataHoraFim
                response['numPessoasDet'] = pessoas_det_final
                response['descricao'] = "Detetou-se " + str(
                    pessoas_det_final) + " pessoa(s), quando o maximo e de " + str(
                    numPessoasPerm) + ' pessoa(s).'
                response['descricao'] += ' Este evento terminou de forma inesperada! (Erro)'

                #dataToSend = json.dumps(response)

                dataToSend = json.dumps(response, indent=4, sort_keys=True, default=str)

                responseError = requests.put(url_eventos, data=dataToSend, headers=headersPost).json()

                print(responseError)

                first_detection = True

                consecFrames = 0

                pessoas_det_final = 0

                cap.release()
                cv2.destroyAllWindows()
