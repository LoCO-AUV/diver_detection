#!/usr/bin/env python

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

import rospy 
import sys
import argparse
from diver_detection import FollowerPipeline

"""
Maintainer: Jahid (email: islam034@umn.edu)
Interactive Robotics and Vision Lab
http://irvlab.cs.umn.edu/

>> This project contain code for CNN-based diver detection and publishing the target bounding box
  > the target bounding box is used by yaw_pitch_controller for generating actual commands 
    for following the diver (see target detection project, bbox_yaw_pitch_controller.py)  
  
>> relevant papers: 
    >> https://ieeexplore.ieee.org/document/8543168
    >> https://onlinelibrary.wiley.com/doi/full/10.1002/rob.21837

>> how to run:
    >> the whole diver following module:
	> launch: roslaunch diver_detection diver_follow_xahid.launch

    >> only the diver detection module:
	> launch: roslaunch diver_detection diver_detection_xahid.launch
	> rosrun: rosrun diver_detection follow_go.py
"""

# for aqua
go = FollowerPipeline(real_time=True)

''''
# rosrun diver_detection follow_go.py --im_dir=/home/xahid/datasets/diver_robot_test/diver/oliv09/
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--im_dir', required=False, dest='im_dir', type=str, default=None, help='Full path of image sequences')

    args = parser.parse_args()
    if (args.im_dir is not None):
        go = FollowerPipeline()
        go.image_streamimg(args.im_dir)
    else:
    	go = FollowerPipeline(real_time=True)
'''
