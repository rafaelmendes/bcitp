#!/usr/bin/env python
from __future__ import division
import rospy
import numpy as np
import scipy.signal as sg
from std_msgs.msg import Float64MultiArray
num_channels=4

W_csp = np.matrix([1,1,1,1])

msg_to_send = Float64MultiArray()

def callback(msg_received):
	X_csp = np.matrix(msg_received.data)
	X_csp.shape = (num_channels,X_csp.size/num_channels)
	Y_csp = W_csp*X_csp
	msg_to_send.data=Y_csp.A1
	pub.publish(msg_to_send)
	
def csp():
	global pub
	rospy.init_node('csp', anonymous=True)
	rospy.Subscriber('canal3',Float64MultiArray,callback,queue_size=1)
	pub=rospy.Publisher('canal4', Float64MultiArray, queue_size=1)
	rospy.spin()

csp()



