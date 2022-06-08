from sympy import *
import serial
import time
s = serial.Serial('COM3', 115200, timeout=5)
time.sleep(3) 

def d2r(deg):
    return deg/180*pi

d1=70
a2=125
a3=125
a4=0
d5=60+132
greifer = 60

def BraccioInverse(w):
    q=Matrix([0,0,0,0,0,0])
    # Basisgelenk
    q[1]= atan2(w[2],w[1])
    q234 = w[4]
    b1 = w[1]*cos(q[1]) + w[2]*sin(q[1]) - a4*cos(q234) + d5*sin(q234)
    b2 = d1 - a4*sin(q234) - d5*cos(q234) - w[3]
    bb = (b1**2) + (b2**2)
    q[3] = acos((bb - (a2**2) - (a3**2)) / (2*a2*a3))
    q[2] = atan2((a2 + a3*cos(q[3]))*b2 - a3*sin(q[3])*b1,
                  (a2+a3*cos(q[3]))*b1 + a3*sin(q[3])*b2)
    q[4] = (q234 - q[2] - q[3] ) 
    q[5] = w[5]
    q[0] = w[0]
    q[1] = q[1] 
    q[2] = -q[2] 
    q[3] = -q[3] + pi/2
    q[4] = -q[4] - 0*pi/2
    q[5] = q[5] - 0*pi/2
    return q

def genBraccioString(q):
    # Umrechnung in Grad-Angaben
    q_deg=N(q/pi*180)

    # Roboter-String erzeugen
    go = True
    for angle in q_deg:
        if not 0 <= angle <= 180:
            print(angle)
            go=False
            break
    if go:
        command="P"+str(int(q_deg[1]))+"," \
                +str(int(q_deg[2]))+"," \
                +str(int(q_deg[3]))+","\
                +str(int(q_deg[4]))+","\
                +str(int(q_deg[5]))+"," + str(int(q_deg[0])) + ",50\n"
        # print(angles)
    else: 
        # print("not in range")
        command = None
    return command

def BraccioGo(w):
    angles = genBraccioString(BraccioInverse(w))
    if angles:
        s.write(angles.encode('ascii'))
        print(s.readline().decode())
        return(1)    
    else:
        return(0)       

def closecom():
    s.close()