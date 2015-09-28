#!/usr/bin/env python
from __future__ import division
import rospy
import numpy as np
from std_msgs.msg import Float64MultiArray, MultiArrayDimension, String

num_channels=4

on_control=False

def control(msg_received):
	global on_control
	if msg_received.data == "on_bloco1":
		on_control=True		
	
def bloco1():
	rospy.init_node('Samples', anonymous=True)
	pub=rospy.Publisher('canal1', Float64MultiArray, queue_size=1)
	rospy.Subscriber('controle', String, control,queue_size=1)
	msg=Float64MultiArray()
	msg.data=np.arange(num_channels)
#	while not on_control and not rospy.is_shutdown():
		#pass

	print('Bloco1')	
	t=np.float64(0.0)
	rate = rospy.Rate(100)
	while not rospy.is_shutdown():
		sinal = np.sin(24*np.pi*t)+20
		msg.data=np.array([sinal]*num_channels)
		t=t + 1/100
		pub.publish(msg)
		rate.sleep()

bloco1()