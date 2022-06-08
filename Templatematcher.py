import cv2
from cv2 import TM_CCOEFF_NORMED
from cv2 import IMREAD_GRAYSCALE
from cv2 import IMREAD_ANYCOLOR
from cv2 import FONT_HERSHEY_PLAIN

def empty(a):
    pass

#Wir importieren die Bilder die zuvor mit photo.py gemacht wurden
template = cv2.imread('C:/Users/CLEVO Computer/Documents/Python/RobotikProjekt/template2.jpg', IMREAD_GRAYSCALE)
rtemplate = cv2.imread('C:/Users/CLEVO Computer/Documents/Python/RobotikProjekt/template1.jpg', IMREAD_GRAYSCALE)
background = cv2.imread('C:/Users/CLEVO Computer/Documents/Python/RobotikProjekt/background.jpg', IMREAD_ANYCOLOR)
pixelsize = 1.0
score = 0.5
camera = cv2.VideoCapture(1)                                            #camerastream 2 öffnen
#Fenster mit Einstellparametern erstellen
cv2.namedWindow("Bars")
cv2.resizeWindow("Bars", 640, 240)
cv2.createTrackbar("Pixel", "Bars", 74, 100, empty)
cv2.createTrackbar("Wert", "Bars", 75, 100, empty)
cv2.createTrackbar("Rahmen", "Bars", 50, 100, empty)
cv2.createTrackbar("X", "Bars", 0, 640, empty)
cv2.createTrackbar("Y", "Bars", 0, 480, empty)

while camera.isOpened():                                                #Programmloop
    #einlesen der Einstellparameter
    X = cv2.getTrackbarPos("X", "Bars")                                 #X Position der Referenz
    Y = cv2.getTrackbarPos("Y", "Bars")                                 #Y Position der Referenz
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
    match_score = max(max_val1, max_val2)                               #Bewertung der bestern Übereinstimmung

    bottom_right = (top_left[0] + w, top_left[1] + h)
    Xpos = int(top_left[0] + w/2)
    newXpos = Xpos - X
    Ypos = int(top_left[1] + h/2)
    newYpos = (Ypos - Y) * (-1)

    cv2.drawMarker(image,(X,Y),(255,0,0),1,10,2)                        #Markierung der neuen Nullposition
    text = "X= " + str(round((newXpos * pixelsize),2)) + " Y= " + str(round((newYpos * pixelsize),2)) + " Score= " + str(round(match_score,2)) + " Scale= " + str(round(pixelsize,2)) + " Size= " + str(w * pixelsize)
    
    if match_score > score:                                             #Wird ein Objekt gefunden wird es markiert 
        cv2.drawMarker(image,(Xpos,Ypos),(0,255,0),1,10,2)      
        cv2.rectangle(image,top_left, bottom_right, (0,0,255), 2)
    
    finalimage = cv2.putText(image, text, (5,20), FONT_HERSHEY_PLAIN, 1, (0,0,0), 2)
    
    cv2.imshow("frame", finalimage)                                     #Kamerabild mit Markierungen
    #cv2.imshow("process", grayimage)                                   #Vorverarbeitetes Bild ohne Hintergrund
    
    key = cv2.waitKey(1) & 0xff
    if key == 13:                                                       #gibt die positionen aus wenn Enter gedrückt wird
        print("Relative X Position = " + str(round((newXpos * pixelsize),2)))
        print("Relative Y Position = " + str(round((newYpos * pixelsize),2)))
    if key == 57:                                                       #Screenshot wenn 9 gedrückt wid
        cv2.imwrite('C:/Users/CLEVO Computer/Documents/Python/RobotikProjekt/screenshot.jpg', finalimage)
    if key == 27:                                                       #ESC zum beenden
        break