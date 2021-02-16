#! /usr/bin/env python

# This code is a part of the LoCO AUV project.
# Copyright (C) The Regents of the University of Minnesota

# Maintainer: Junaed Sattar <junaed@umn.edu> and the Interactive Robotics and Vision Laboratory

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Maintainer: Jahid (email: islam034@umn.edu)
Interactive Robotics and Vision Lab
http://irvlab.cs.umn.edu/

Class for detecting diver using CNN-based model (we are usng ssd now)
"""

# ros/python/opencv/tensorflow libraries
import os
import sys
import cv2
import rospy
import roslib
import argparse
import numpy as np
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL']='2' #export TF_CPP_MIN_LOG_LEVEL=2


class DiverDetection:
    """
      class for driving the deep diver detection
      returns the target bounding boxe
    """

    def __init__(self):
        """
          initialize variables and flags
        """ 
        #self.data_dir = '/home/xahid/model_data_/diver_rcnn/'
        #self.data_dir = '/home/aqua/model_data_/diver_ssd/'
        self.data_dir = '/home/irvlab/catkin_ws/src/diver_detection/model_data/'
        self.min_score_thresh = 0.1
        self.CNN_init()
        

    def CNN_init(self):
        """
          load saved tensorflow graph and model parameters
          just load once, DONOT load every time for each frame
	    then it'll be too slow
        """ 
        frozen_model_path = self.data_dir+'frozen_inference_graph.pb'
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(frozen_model_path, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        ops = self.detection_graph.get_operations()
        all_tensor_names = {output.name for op in ops for output in op.outputs}
        self.tensor_dict = {}
        for key in ['detection_boxes', 'detection_scores','detection_classes']:
            tensor_name = key + ':0'
            if tensor_name in all_tensor_names:
                self.tensor_dict[key] = self.detection_graph.get_tensor_by_name(tensor_name)
        self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        self.sess = tf.Session(graph=self.detection_graph)


    
    def filter_box_normal(self, normalized_box, im_h, im_w):
        """
          given a normalized bounding box, returns the box coordinates in pixels
           if the numbers look right. 
           returned Bbox coordinate => {left, right, top, bottom}
        """
        ymin, xmin, ymax, xmax = tuple(normalized_box.tolist())
        BBox = (int(xmin*im_w), int(xmax*im_w), int(ymin*im_h), int(ymax*im_h))
        # check the Bbox numbers and the area make sense
        area_ = (BBox[1]-BBox[0])*(BBox[3]-BBox[2])
        if (BBox[0]>0 and BBox[2]>0 and BBox[1]<im_w and BBox[3]<im_h and area_>0.01*im_h*im_w):
            return BBox, True
        return BBox, False



    def Detect_diver(self, frame):
        """
          given an image, return the detected diver {bounding boxe, success_flag} 
        """
        im_height, im_width, _ = frame.shape
        image = cv2.cvtColor(cv2.resize(frame, (300, 300)), cv2.COLOR_BGR2RGB)
        output_dict = self.sess.run(self.tensor_dict, feed_dict={self.image_tensor: np.expand_dims(image, 0)})

        output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(np.uint8)
        output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
        output_dict['detection_scores'] = output_dict['detection_scores'][0]
        boxes, classes, scores = output_dict['detection_boxes'], output_dict['detection_classes'], output_dict['detection_scores']

        # filter detection and return output
        BBox, success_ = (-1, -1, -1, -1), False
        id_ = 0 # scores is sorted, most confident first (e.g., id_ = np.argmax(scores) = 0)
        if classes[id_] == 1 and scores[id_]>self.min_score_thresh:
            BBox, success_ = self.filter_box_normal(boxes[id_], im_height, im_width)

        return BBox, success_





