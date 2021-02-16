#!/usr/bin/env python2
# -*- coding: utf-8 -*-


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

Class for Kalman Filter-based bounding box tracker
"""

import numpy as np
from numpy import dot
from scipy.linalg import inv, block_diag


class BoxTrackerKF(): 
    """ class for Kalman Filter-based tracker
    """
    def __init__(self):
        # Parameters for Kalman Filtering
        self.init_tracker() 
        self.dt = 1.   # time interval
        self.iou_thr = 0.25 # min overlap between old-new detections
        self.max_age = 20 # max # of missed detection before clearing track
        # Process matrix, assuming constant velocity model
        self.F = np.array([[1, self.dt, 0,  0,  0,  0,  0, 0],
                           [0, 1,  0,  0,  0,  0,  0, 0],
                           [0, 0,  1,  self.dt, 0,  0,  0, 0],
                           [0, 0,  0,  1,  0,  0,  0, 0],
                           [0, 0,  0,  0,  1,  self.dt, 0, 0],
                           [0, 0,  0,  0,  0,  1,  0, 0],
                           [0, 0,  0,  0,  0,  0,  1, self.dt],
                           [0, 0,  0,  0,  0,  0,  0,  1]])
        # Measurement matrix, assuming we can only measure the coordinates
        self.H = np.array([[1, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 1, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 1, 0, 0, 0], 
                           [0, 0, 0, 0, 0, 0, 1, 0]])
        # Initialize the state covariance
        self.L = 10.0
        self.P = np.diag(self.L*np.ones(8))
        # Initialize the process covariance
        self.Q_comp_mat = np.array([[self.dt**4/4., self.dt**3/2.],
                                    [self.dt**3/2., self.dt**2]])
        self.Q = block_diag(self.Q_comp_mat, self.Q_comp_mat, 
                            self.Q_comp_mat, self.Q_comp_mat)
        # Initialize the measurement covariance
        self.R_scaler = 1.0
        R_diag = self.R_scaler * np.array([self.L, self.L, self.L, self.L])
        self.R = np.diag(R_diag)
        


    def init_tracker(self):
        # initialize and clear data for next tracking
        # state: {left, left_dot, right, right_dot, top, top_dot, bottom, bottom_dot}
        self.x_state=[] 
        self.box = [] # list to store the coordinates for a bounding box 
        self.missed_dets = 0 # no.of missed detections

    
        
    def kalman_filter(self, z): 
        '''
        Implementation of the Kalman Filter
        '''
        # Prediction
        x = dot(self.F, self.x_state)
        self.P = dot(self.F, self.P).dot(self.F.T) + self.Q

        # Update
        S = dot(self.H, self.P).dot(self.H.T) + self.R
        K = dot(self.P, self.H.T).dot(inv(S)) # Kalman gain
        y = z - dot(self.H, x) # residual
        x += dot(K, y)
        self.P = self.P - dot(K, self.H).dot(self.P)
        self.x_state = x.astype(int) # integer coordinates 

        

    def predict_only(self):  
        '''
        Only the prediction stage (for missed/unmatched detections)
        '''
        x = dot(self.F, self.x_state)
        self.P = dot(self.F, self.P).dot(self.F.T) + self.Q
        self.x_state = x.astype(int)



    def estimateTrackedBbox(self, z):
        '''
        Handles all kinds of estimation: 
            unmatched detections (new detection)
            unmatched tracking (no confident detections)
            matched detection (general tracking)
        '''
        z = np.expand_dims(z, axis=0).T
        if self.box==[] or self.x_state==[]:   
            # unmatched detection
            self.x_state = np.array([[z[0], 0, z[1], 0, z[2], 0, z[3], 0]]).T
            self.predict_only()
            self.missed_dets=0
        else:
            iou = box_iou(self.box, z)
            if iou > self.iou_thr:
                # matched tracking
                self.kalman_filter(z)
                self.missed_dets=0
            else:
                if self.missed_dets>self.max_age:
                    return False
                self.missed_dets += 1
                self.predict_only()

        xx = self.x_state.T[0].tolist()
        self.box =[xx[0], xx[2], xx[4], xx[6]] 
        return True                   
                   





def box_iou(a, b):
    '''
    Helper funciton to calculate intersection over the union of two boxes a and b
     Bbox coordinates =>> {left, right, top, bottom}
    '''
    w_intsec = np.maximum (0, (np.minimum(a[1], b[1]) - np.maximum(a[0], b[0])))
    h_intsec = np.maximum (0, (np.minimum(a[3], b[3]) - np.maximum(a[2], b[2])))
    s_intsec = w_intsec * h_intsec
    s_a = (a[1] - a[0])*(a[3] - a[2])
    s_b = (b[1] - b[0])*(b[3] - b[2])
  
    return float(s_intsec)/(s_a + s_b -s_intsec)



             










