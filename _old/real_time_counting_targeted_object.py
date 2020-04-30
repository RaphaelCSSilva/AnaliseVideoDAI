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

import tensorflow as tf

# Object detection imports
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
args = vars(ap.parse_args())

fps = get_fps_from_camera()

buffer = int(round(fps * args["buffer_time"]))

print(fps, buffer)

output = args["output"]

confidence = args["confidence"]

numberToDetect = args["number_to_detect"]

operation = args["operation"]

cap = cv2.VideoCapture(0)

print("operation: {}".format(operation))
print("operation test: {}".format(operation == "eq"))


kcw = KeyClipWriter(bufSize=buffer)
consecFrames = 0

# By default I use an "SSD with Mobilenet" model here. See the detection model zoo (https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md) for a list of other models that can be run out-of-the-box with varying speeds and accuracies.
detection_graph, category_index = backbone.set_model('ssd_mobilenet_v1_coco_2018_01_28', 'mscoco_label_map.pbtxt')

# object_counting_api.object_counting(input_video, detection_graph, category_index, 0) # for counting all the objects, disabled color prediction

# object_counting_api.object_counting(input_video, detection_graph, category_index, 1) # for counting all the objects, enabled color prediction


targeted_object = "person"  # (for counting targeted objects) change it with your targeted objects
is_color_recognition_enabled = 0

#object_counting_api_altered.targeted_object_counting(cap, buffer, output, fps, confidence, detection_graph, category_index, is_color_recognition_enabled,
#                                             targeted_objects)  # targeted objects counting


#print(frame)


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
            ret, frame = cap.read()

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
                                                                                                   np.squeeze(boxes),
                                                                                                   np.squeeze(
                                                                                                       classes).astype(
                                                                                                       np.int32),
                                                                                                   np.squeeze(scores),
                                                                                                   category_index,
                                                                                                   targeted_objects=targeted_object,
                                                                                                   use_normalized_coordinates=True,
                                                                                                   line_thickness=4)
                if len(the_result) == 0:
                    cv2.putText(input_frame, "...", (10, 35), font, 0.8, (0, 255, 255), 2, cv2.FONT_HERSHEY_SIMPLEX)
                else:
                    cv2.putText(input_frame, the_result, (10, 35), font, 0.8, (0, 255, 255), 2,
                                cv2.FONT_HERSHEY_SIMPLEX)

            #if the_result[1:7] == 'person' and scores[0][0] >= confidence:
                if the_result[1:7] == 'person':
                    consecFrames = 0

                    # if we are not already recording, start recording
                    if not kcw.recording:
                        timestamp = datetime.datetime.now()
                        p = "{}/{}.avi".format(output,
                                               timestamp.strftime("%Y%m%d-%H%M%S"))
                        kcw.start(p, cv2.VideoWriter_fourcc(*'XVID'), fps)

                    if operation != "":
                        if operation == "eq":
                            if the_result[11:12] == str(numberToDetect):
                                print("Somos {}!".format(numberToDetect))

                        if operation == "gt":
                            if the_result[11:12] >= str(numberToDetect):
                                print("Somos mais do que {}!".format(numberToDetect))
                        if operation == "lt":
                            if the_result[11:12] <= str(numberToDetect):
                                print("Somos menos do que {}!".format(numberToDetect))

            # print(the_result)

            # print(the_result[1:7])
            # print(the_result[11:12])

            # if classes[1] == "person":
            #    print("Teste Person")

            cv2.imshow('object counting', input_frame)

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

            #cv2.imshow('object counting', input_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # if we are in the middle of recording a clip, wrap it up
        if kcw.recording:
            kcw.finish()

    cap.release()
    cv2.destroyAllWindows()

# # if we are in the middle of recording a clip, wrap it up
# if kcw.recording:
#     kcw.finish()
#
# cap.release()
# cv2.destroyAllWindows()

# object_counting_api.object_counting(input_video, detection_graph, category_index, is_color_recognition_enabled, fps, width, height) # counting all the objects
