#!/usr/bin/env python
import rospy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from std_msgs.msg import Float64MultiArray

dados = []
temp = []
flag=0
flagplot=0
def callback(data):        #callback do subscriber
    global dados,temp,flag,flagplot
    dados=data.data
    if flag==0 and flagplot==0:
        flag=1
        temp=dados
        flag=0

def animate(i):
    global temp,flagplot
    flagplot=1
    ax1.clear()
    ax1.set_ylim([-1.3, 1.3])
    ax1.plot(temp)
    flagplot=0

def fourth():
    rospy.init_node('fourth', anonymous=True)
    rospy.Subscriber("canal3",Float64MultiArray,callback,queue_size=1)
    ani = animation.FuncAnimation(fig, animate, interval=400)
    plt.show()
    
if __name__ == '__main__':
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)
    fourth()