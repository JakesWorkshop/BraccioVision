from sympy import *
import serial
import time
s = serial.Serial('COM3', 115200, timeout=5)                    #Sereiller Port für die Ansteuerung
time.sleep(3) 

def d2r(deg):                                                   #Umrechnung von Grad zu Rad
    return deg/180*pi

d1=70                                                           #IK Parameter des roboters
a2=125
a3=125
a4=0
d5=60+132

def BraccioInverse(w):                                          #Berechnung der Inversen Kinematik
    q=Matrix([0,0,0,0,0,0])                                     #Greifer,X,Y,Z,Handgelenk Pitch,Handgelenk Roll
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
    q_deg=N(q/pi*180)                                           # Umrechnung in Grad-Angaben

    go = True
    for angle in q_deg:                                         #Prüfen ob die winkel erreichbar sind
        if not 0 <= angle <= 180:
            go=False
            break
    if go:                                                      #Roboter-String erzeugen
        command="P"+str(int(q_deg[1]))+"," \
                +str(int(q_deg[2]))+"," \
                +str(int(q_deg[3]))+","\
                +str(int(q_deg[4]))+","\
                +str(int(q_deg[5]))+"," \
                +str(int(q_deg[0]))+",75\n"
    else: 
        command = None
    return command

def BraccioGo(w):                                               #Sendet Befehle an den Roboter
    angles = genBraccioString(BraccioInverse(w))
    if angles:
        s.write(angles.encode('ascii'))
        print(s.readline().decode())
        return(1)                                               #Rückgabewert 1 wenn Position möglich ist
    else:
        return(0)       

def closecom():                                                 #Funktion zum schließsen des Serial Port
    s.close()