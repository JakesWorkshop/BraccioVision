import cv2

def empty(a):
    pass

camera = cv2.VideoCapture(1)                                #Kamerastream 2 öffnen
#Fenster für Einstellparameter erstellen
cv2.namedWindow("Bars")
cv2.resizeWindow("Bars", 640, 240)
cv2.createTrackbar("X", "Bars", 0, 635, empty)
cv2.createTrackbar("Y", "Bars", 0, 475, empty)
cv2.createTrackbar("W", "Bars", 5, 640, empty)
cv2.createTrackbar("H", "Bars", 5, 480, empty)

print("1= Hintergrund, 2= gerade Vorlage, 3= gedrehte Vorlage, Esc= Beenden")

while camera.isOpened():                                    #Programmloop
    ret, image = camera.read()
    X = cv2.getTrackbarPos("X", "Bars")                     #Position des Rahmens für Template
    Y = cv2.getTrackbarPos("Y", "Bars")
    Width = cv2.getTrackbarPos("W", "Bars")                 #Größe des Rahmens für Template
    Height = cv2.getTrackbarPos("H", "Bars") 
    W = X + Width
    H = Y + Height
    preview = image.copy()

    crop = image[Y:H, X:W]                                  #Zuschneiden auf eingestellte Größe
    cv2.rectangle(preview, (X, Y), (W, H), 255, 2)
    cv2.imshow('background', preview)                       #Sowohl das vollständige als auch das Zugeschnittene Bild werden angezeigt
    cv2.imshow('crop', crop)

    key = cv2.waitKey(1) & 0xff
    if key == 49:                                           #1 zum speichern des Hintergrunds
        cv2.imwrite('C:/Users/CLEVO Computer/Documents/Python/RobotikProjekt/background.jpg', image)
        print("Hintergrud gespeichert")
    if key == 50:                                           #2 zum speichern des ersten Template
        cv2.imwrite('C:/Users/CLEVO Computer/Documents/Python/RobotikProjekt/template1.jpg', crop)
        print("gerade Vorlage gespeichert")
    if key == 51:                                           #3 zum speichern des zweiten Template
        cv2.imwrite('C:/Users/CLEVO Computer/Documents/Python/RobotikProjekt/template2.jpg', crop)
        print("gedrehte vorlage gespeichert")
    if key == 27:                                           #ESC zum schließen
        break