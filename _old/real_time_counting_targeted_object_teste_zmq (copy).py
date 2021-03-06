# ----------------------------------------------
# --- Author         : Ahmet Ozlu
# --- Mail           : ahmetozlu93@gmail.com
# --- Date           : 27th January 2018
# ----------------------------------------------

# usage on linux: python3 real_time_counting_targeted_object.py
# usage on windows: python real_time_counting_targeted_object.py

# Imports
import argparse
import datetime
import time

import pytz
import requests
import json
import glob
import os

import imagezmq
import tensorflow as tf

# Object detection imports
from imutils import build_montages

from utils import visualization_utils as vis_util
from utils.fpsGetter import get_fps_from_camera
from utils.keyclipwriter import KeyClipWriter
from utils import backbone
import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", default='output',
                help="path to output directory")
ap.add_argument("-b", "--buffer-time", type=int, default=10,
                help="time before and after the event to record, in seconds")
ap.add_argument("-c", "--confidence", type=float, default=0.8,
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


def detectionAlg(areas_json, ip):
    # ip = 'localhost'

    url_camara = "http://" + ip + ":8181/services/eventos/api/camaras/" + str(camaraId)

    url_area = "http://" + ip + ":8181/services/eventos/api/areas/" + str(areaId)

    url_tipoevento = "http://" + ip + ":8181/services/eventos/api/tipoeventos/" + str(tipoEventoId)

    url_eventos = "http://148.63.202.53:8181/services/eventos/api/eventos"

    url_eventos_get = "http://148.63.202.53:8181/services/eventos/api/eventos/"

    headersGet = {
        'Authorization': "Bearer eyJhbGciOiJIUzUxMiJ9"
                         ".eyJzdWIiOiJhZG1pbiIsImF1dGgiOiJST0xFX0FETUlOLFJPTEVfVVNFUiIsImV4cCI6MTU5MDE0ODUzM30"
                         ".MDFoVukkynl8xxdR7lzhYSNod6PvJSiCvGhpCyuwpUgSfS7hYiD37yUfIN8T_S_lPh11xUEo4TiLTkqsXxrqBg "
    }

    headersPost = {
        'Content-Type': "application/json",
        'Authorization': "Bearer eyJhbGciOiJIUzUxMiJ9"
                         ".eyJzdWIiOiJhZG1pbiIsImF1dGgiOiJST0xFX0FETUlOLFJPTEVfVVNFUiIsImV4cCI6MTU5MDE0ODUzM30"
                         ".MDFoVukkynl8xxdR7lzhYSNod6PvJSiCvGhpCyuwpUgSfS7hYiD37yUfIN8T_S_lPh11xUEo4TiLTkqsXxrqBg",
        'cache-control': "no-cache",
    }

    area_json = requests.get(url_area, headers=headersGet).json()

    # print(area_json)

    camara_json = requests.get(url_camara, headers=headersGet).json()

    tipo_evento_json = requests.get(url_tipoevento, headers=headersGet).json()

    current_video_name = ""

    dataHoraInicio = ""

    dataHoraFim = ""

    numPessoasPerm = area_json['numPessoasPerm']

    numPessoasDet = None

    descricao = ""

    descricoes = {
        "Maior": "Foram detetadas " + str(numPessoasDet) + " numa área onde o limite é de " + str(numPessoasPerm),
        "Menor": "Foram detetadas " + str(numPessoasDet) + " numa área onde o mínimo são " + str(numPessoasPerm)
    }

    dataToSend = json.dumps(data)

    is_detecting = False

    fps = get_fps_from_camera()

    buffer = int(round(fps * args["buffer_time"]))

    print(fps, buffer)

    output = args["output"]

    confidence = args["confidence"]

    # numberToDetect = args["number_to_detect"]

    # operation = args["operation"]

    # cap = cv2.VideoCapture(0)

    print("operation: {}".format(tipo_evento_json['descricao']))

    kcw = KeyClipWriter(bufSize=buffer)
    consecFrames = 0

    # By default I use an "SSD with Mobilenet" model here. See the detection model zoo (https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md) for a list of other models that can be run out-of-the-box with varying speeds and accuracies.
    detection_graph, category_index = backbone.set_model('ssd_mobilenet_v1_coco_2018_01_28', 'mscoco_label_map.pbtxt')

    # object_counting_api.object_counting(input_video, detection_graph, category_index, 0) # for counting all the objects, disabled color prediction

    # object_counting_api.object_counting(input_video, detection_graph, category_index, 1) # for counting all the objects, enabled color prediction

    targeted_object = "person"  # (for counting targeted objects) change it with your targeted objects
    is_color_recognition_enabled = 0

    # object_counting_api_altered.targeted_object_counting(cap, buffer, output, fps, confidence, detection_graph, category_index, is_color_recognition_enabled,
    #                                             targeted_objects)  # targeted objects counting

    # print(frame)

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
    # mW = args["montageW"]
    # mH = args["montageH"]

    mW = 1
    mH = 1

    print("[INFO] detecting: persons...")

    updateConsecFrames = True

    # height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    # height = 480
    # width = 640

    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # output_movie = cv2.VideoWriter('the_output.avi', fourcc, fps, (width, height))

    total_passed_vehicle = 0
    speed = "waiting..."
    direction = "waiting..."
    size = "waiting..."
    color = "waiting..."
    the_result = "..."
    width_heigh_taken = True
    height = 0
    width = 0

    while True:
        if imageHub.recv_image() is None:
            time.sleep(1)
        else:
            (mac, frame) = imageHub.recv_image()

            id_area = None

            id_cam = None

            id_tipoevento = None

            for i in range(len(areas_json)):
                print(i)
                for j in range(len(areas_json[i]['camaras'])):
                    mac_compare = areas_json[i]['camaras'][j]['enderecoIp']
                    if mac == mac_compare:
                        id_cam = areas_json[i]['camaras'][j]['id']

                        id_area = areas_json[i]['id']

                        id_tipoevento = areas_json[i]['tipoevento']['id']

                        print("Mac: {}  \nId_cam:  {}  \nId_area: {}  \nId_tipoevento: {}".format(mac_compare, id_cam,
                                                                                                  id_area,
                                                                                                  id_tipoevento))

            url_camara = "http://" + ip + ":8181/services/eventos/api/camaras/" + id_cam

            url_area = "http://" + ip + ":8181/services/eventos/api/areas/" + id_area

            url_tipoevento = "http://" + ip + ":8181/services/eventos/api/tipoeventos/" + id_tipoevento

            area_json = requests.get(url_area, headers=headersGet).json()

            camara_json = requests.get(url_camara, headers=headersGet).json()

            tipo_evento_json = requests.get(url_tipoevento, headers=headersGet).json()

            break

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

            while True:
                # ret, frame = cap.read()

                (rpiName, frame) = imageHub.recv_image()
                imageHub.send_reply(b'OK')

                # if a device is not in the last active dictionary then it means
                # that its a newly connected device
                if rpiName not in lastActive.keys():
                    print("[INFO] receiving data from {}...".format(rpiName))

                # record the last active time for the device from which we just
                # received a frame
                lastActive[rpiName] = datetime.datetime.now()

                # for all the frames that are extracted from input video

                # ret, frame = cap.read()

                # if not ret:
                #    print("end of the video file...")
                #    break

                frame = cv2.resize(frame, (800, 600))

                input_frame = frame

                # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                image_np_expanded = np.expand_dims(input_frame, axis=0)

                # Actual detection.
                (boxes, scores, classes, num) = sess.run(
                    [detection_boxes, detection_scores, detection_classes, num_detections],
                    feed_dict={image_tensor: image_np_expanded})

                # insert information text to video frame
                font = cv2.FONT_HERSHEY_SIMPLEX

                # print(cap.get(1))

                if scores[0][0] >= confidence:

                    # Visualization of the results of a detection.
                    counter, csv_line, the_result = vis_util.visualize_boxes_and_labels_on_image_array(-1,
                                                                                                       input_frame,
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
                                                                                                       targeted_objects=targeted_object,
                                                                                                       use_normalized_coordinates=True,
                                                                                                       line_thickness=4)
                    if len(the_result) == 0:
                        cv2.putText(input_frame, "...", (10, 35), font, 0.8, (0, 255, 255), 2, cv2.FONT_HERSHEY_SIMPLEX)
                    else:
                        cv2.putText(input_frame, the_result, (10, 35), font, 0.8, (0, 255, 255), 2,
                                    cv2.FONT_HERSHEY_SIMPLEX)

                    tipo_detetado = the_result[1:7]

                    # print(the_result[11:12])

                    try:
                        numPessoasDet = int(float(the_result[11:12]))
                    except ValueError:
                        print(numPessoasDet)

                    # if tipo_detetado == 'person' and scores[0][0] >= confidence:
                    if tipo_detetado == 'person':
                        consecFrames = 0

                        # if we are not already recording, start recording
                        if not kcw.recording:
                            timestamp = datetime.datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                            p = "{}/{}.webm".format(output, timestamp)
                            kcw.start(p, cv2.VideoWriter_fourcc(*'VP80'), fps)

                        if tipo_evento_json['descricao'] != "" and is_detecting == False:
                            if tipo_evento_json['descricao'] == "eq":
                                if numPessoasDet == numPessoasPerm:
                                    print("Somos {}!".format(numPessoasPerm))

                            if tipo_evento_json['descricao'] == "Maior":
                                if numPessoasDet > numPessoasPerm:
                                    print("Somos mais do que {}!".format(numPessoasPerm))

                                    descricao = "Foram detetadas " + str(
                                        numPessoasDet) + " numa área onde o limite é de " + str(numPessoasPerm)

                                    # current_video_name = latest_file[9:]

                                    current_video_name = p[7:]

                                    dataHoraInicio = timestamp

                                    dataHoraFim = timestamp

                                    data = {
                                        "descricao": descricao,
                                        "numPessoasPerm": numPessoasPerm,
                                        "numPessoasDet": numPessoasDet,
                                        "dataHoraInicio": dataHoraInicio,
                                        "dataHoraFim": dataHoraFim,
                                        "path": "http://" + ip + ":8000/" + current_video_name,
                                        "formato": "webm",
                                        "area": area_json,
                                        "camara": camara_json,
                                        "tipoevento": tipo_evento_json
                                    }

                                    dataToSend = json.dumps(data, indent=4, sort_keys=True, default=str)

                                    response = requests.post(url_eventos, data=dataToSend, headers=headersPost).json()

                                    # response_id = response['id']

                                    # response_post_evento = requests.get(url_eventos_get + response_id, headers=headersGet)

                                    print(response)
                            if tipo_evento_json['descricao'] == "Menor":
                                if numPessoasDet < numPessoasPerm:
                                    print("Somos menos do que {}!".format(numPessoasPerm))

                    is_detecting = True

                # print(the_result)

                # print(tipo_detetado)
                # print(numPessoasDet)

                # if classes[1] == "person":
                #    print("Teste Person")

                # update the new frame in the frame dictionary
                frameDict[rpiName] = frame

                # build a montage using images in the frame dictionary
                montages = build_montages(frameDict.values(), (800, 600), (mW, mH))

                # cv2.imshow('object counting', input_frame)

                # if current time *minus* last time when the active device check
                # was made is greater than the threshold set then do a check
                if (datetime.datetime.now() - lastActiveCheck).seconds > ACTIVE_CHECK_SECONDS:
                    # loop over all previously active devices
                    for (rpiName, ts) in list(lastActive.items()):
                        # remove the RPi from the last active and frame
                        # dictionaries if the device hasn't been active recently
                        if (datetime.datetime.now() - ts).seconds > ACTIVE_CHECK_SECONDS:
                            print("[INFO] lost connection to {}".format(rpiName))
                            lastActive.pop(rpiName)
                            frameDict.pop(rpiName)

                    # set the last active check time as current time
                    lastActiveCheck = datetime.datetime.now()

                # display the montage(s) on the screen
                for (i, montage) in enumerate(montages):
                    cv2.imshow("Home pet location monitor ({})".format(i),
                               montage)

                # output_movie.write(input_frame)
                # print("writing frame")

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

                    dataToSend = json.dumps(response)

                    response = requests.put(url_eventos, data=dataToSend, headers=headersPost).json()

                    print(response)

                    is_detecting = False

                # cv2.imshow('object counting', input_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # if we are in the middle of recording a clip, wrap it up
            if kcw.recording:
                kcw.finish()

        # cap.release()
        # cv2.destroyAllWindows()

# # if we are in the middle of recording a clip, wrap it up
# if kcw.recording:
#     kcw.finish()
#
# cap.release()
# cv2.destroyAllWindows()

# object_counting_api.object_counting(input_video, detection_graph, category_index, is_color_recognition_enabled, fps, width, height) # counting all the objects
