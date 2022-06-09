import cv2
from cv2 import TM_CCOEFF_NORMED
from cv2 import IMREAD_GRAYSCALE
from cv2 import IMREAD_ANYCOLOR
from cv2 import FONT_HERSHEY_PLAIN
from numpy import angle 
import kinematik
from sympy import *

def empty(a):                                                           #Leere Funktion für Einstellparameter
    pass
                                                                        #Importieren der Bilder die zuvor mit photo.py gemacht wurden
template = cv2.imread('C:/Users/CLEVO Computer/Documents/Python/RobotikProjekt/template2.jpg', IMREAD_GRAYSCALE)
rtemplate = cv2.imread('C:/Users/CLEVO Computer/Documents/Python/RobotikProjekt/template1.jpg', IMREAD_GRAYSCALE)
background = cv2.imread('C:/Users/CLEVO Computer/Documents/Python/RobotikProjekt/background.jpg', IMREAD_ANYCOLOR)
pixelsize = 1.0
score = 0.5
greifer = kinematik.d2r(20)
Z = 60
camera = cv2.VideoCapture(1)                                            #Kamerastream 2 öffnen

cv2.namedWindow("Bars")                                                 #Fenster mit Einstellparametern erstellen
cv2.resizeWindow("Bars", 640, 240)
cv2.createTrackbar("Pixel", "Bars", 86, 100, empty)
cv2.createTrackbar("Wert", "Bars", 75, 100, empty)
cv2.createTrackbar("Rahmen", "Bars", 43, 100, empty)
cv2.createTrackbar("X", "Bars", 311, 640, empty)
cv2.createTrackbar("Y", "Bars", 5, 480, empty)

while camera.isOpened():                                                #Programmloop
                                                                        #einlesen der Einstellparameter
    X = cv2.getTrackbarPos("X", "Bars")                                 #Position der Referenz
    Y = cv2.getTrackbarPos("Y", "Bars")
    parameter1 = cv2.getTrackbarPos("Pixel", "Bars")                    #mm pro Pixel
    parameter2 = cv2.getTrackbarPos("Wert", "Bars")                     #Mindestwert für die Markierung
    w = cv2.getTrackbarPos("Rahmen", "Bars")                            #Rahmengröße
    h = w
    pixelsize = parameter1 / 100
    score = parameter2 / 100

    ret, image = camera.read()                                          #Bild von Kamera lesen
    negimage = cv2.subtract(background, image)                          #Hintergrund subtrahieren
    posimage = cv2.bitwise_not(negimage)                                #Bild invertieren
    grayimage = cv2.cvtColor(posimage, cv2.COLOR_RGB2GRAY)              #in Graustufen umwandeln
    matches1 = cv2.matchTemplate(grayimage,template,TM_CCOEFF_NORMED)   #Template Matching
    matches2 = cv2.matchTemplate(grayimage,rtemplate,TM_CCOEFF_NORMED)

    min_val, max_val1, min_loc, max_loc1 = cv2.minMaxLoc(matches1)      
    min_val, max_val2, min_loc, max_loc2 = cv2.minMaxLoc(matches2)
    top_left = max(max_loc1, max_loc2)                                  #Position der besten Übereinstimmung
    match_score = max(max_val1, max_val2)                               #Bewertung der besten Übereinstimmung

    bottom_right = (top_left[0] + w, top_left[1] + h)                   #top_left und bottom_right werden zum zeichnen des Rechteckrahmens genutzt
    Xpos = int(top_left[0] + w/2)                                       #Xpos, Ypos geben den Mittelpunkt des Rechteckrahmens an
    Ypos = int(top_left[1] + h/2)
    newXpos = (Xpos - X)                                                #newXpos, newYpos geben die relative position zum neu definierten Null an
    newYpos = (Ypos - Y)                                                #Alle diese angaben sind in Pixeln gemessen!
    Xmm = round((newXpos * pixelsize),2)                                #Xmm, Ymm sind die relative Position in Millimetern
    Ymm = round((newYpos * pixelsize),2)

    cv2.drawMarker(image,(X,Y),(255,0,0),1,10,2)                        #Markierung der neuen Nullposition
    text = "X= " + str(Xmm) + " Y= " + str(Ymm) + " Score= " + str(round(match_score,2)) + " Scale= " + str(round(pixelsize,2)) + " Size= " + str(round((w * pixelsize),2))
    
    if match_score > score:                                             #Wird ein Objekt gefunden wird es markiert 
        cv2.drawMarker(image,(Xpos,Ypos),(0,255,0),1,10,2)              #Mittelpunkt
        cv2.rectangle(image,top_left, bottom_right, (0,0,255), 2)       #Rahmen um Objekt
    
    finalimage = cv2.putText(image, text, (5,20), FONT_HERSHEY_PLAIN, 1, (0,0,0), 2)
    
    cv2.imshow("frame", finalimage)                                     #Kamerabild mit Markierungen
    #cv2.imshow("process", grayimage)                                   #Vorverarbeitetes Bild ohne Hintergrund
    
    w = Matrix([0,0,0,0,0,0])
    key = cv2.waitKey(1) & 0xff                                         #Programm wartet 1ms auf einen Tastendruck
    if key == 13:                                                       #gibt die positionen aus wenn Enter gedrückt wird
        trying = 0
        approach = -1.00
        print("Versuche " + str(Xmm) + ", " + str(Ymm) + ", " + Z + " zu erreichen")
        while trying == 0:
            if approach < -0.02:                                        #Wenn Maximum nicht erreicht ist versuche den winkel zu erhöhen
                approach = approach + 0.05 
                print("Versuche Winkel " + str(round(approach),2))
            if approach > -0.02:                                        #Wenn Maximum erreicht ist brich diesen Versuch ab
                print("Keine mögliche Pose gefunden")
                break 
            w = Matrix([greifer,newXpos * pixelsize,newYpos * pixelsize,Z,approach*pi/2,pi/2])
            trying = kinematik.BraccioGo(w)                             #Pose wird überprüft und ausgeführt wenn sie möglich ist
        if trying == 1:
            print("Pose gefunden")

    if key == 49:                                                       #Taste 1 um den Greifer zu schließen
        greifer = kinematik.d2r(55)
        print("greifer zu")
    if key == 50:                                                       #Taste 2 um den greifer zu öffnen
        greifer = kinematik.d2r(20)
        print("greifer auf")
    if key == 51:                                                       #Taste 3 Höhe der Pose wird auf untere Position festgelegt
        Z = 10
        print("Position unten")
    if key == 52:                                                       #Taste 4 Höhe der Pose wird auf obere Position festgelegt
        Z = 60
        print("Position oben")
    if key == 53:                                                       #Taste 5 zurück in Ausgangsposition mit geschlossenem Greifer
        kinematik.s.write(b'P90,90,90,90,90,55,30')
    if key == 54:                                                       #Taste 6 zurück in Ausgangsposition mit offenem Greifer
        kinematik.s.write(b'P90,90,90,90,90,20,30')
    if key == 57:                                                       #Taste 9 Screenshot
        cv2.imwrite('C:/Users/CLEVO Computer/Documents/Python/RobotikProjekt/screenshot.jpg', finalimage)
    if key == 27:                                                       #ESC zum beenden
        kinematik.closecom()
        break