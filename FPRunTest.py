'''
Created on Dec 12, 2014

@author: dustin
'''

#FPRun.py

import os
import time
import sys
import Fingerprint
import FPSconstants
import RPi.GPIO as GPIO

inputPinExit = 7
outputPin = 40

#Get ID # from operator and enroll
def enrollIDLoop():
    #userInput = input("ID # to store the finger as:")
    while(True):
        fID = input("ID # to store the finger or Q to quit:")
        
        if(fID.isdigit()):
            break
        elif((fID == 'q') or (fID == 'Q')):
            fID = ''
            main()
        else:
            print ("Must enter digit only")
    
    print ("Enrolling ID #" + fID)
    
    fRun = False
    while(not fRun):
        fRun = enrollFingerprint(fID)
        if(GPIO.input(inputPinExit) == False):
            main()
    
def enrollFingerprint(enrollID):
    print ("Waiting for valid finger to enroll")
    time.sleep(0.5)
    
    p = False
    while (not p):
        p = Fingerprint.getImage()
        if(p):
            print ("Image taken")
            break
        elif(not p):
            print (".")
        else:
            print ("Unknown Error")
    
    time.sleep(0.5)
    p = Fingerprint.image2Tz(1)
    
    if(p):
        print ("Image converted")
    elif(not p):
        print ("Image not converted")
        return p
    else:
        print ("Unknown Error")
        return p
    
    print ("Remove Finger")
    time.sleep(2.0)
    
    p = False
    print ("Place same finger again")
    time.sleep(1.0)
    while(not p):
        p = Fingerprint.getImage()
        
        if(p):
            print ("Image taken")
            break
        elif(not p):
            print (".")
        else:
            print ("Unknown Error")

    time.sleep(0.5)
    p = Fingerprint.image2Tz(2)
    
    if(p):
        print ("Image converted")
    elif(not p):
        print ("Image not converted")
        return p
    else:
        print ("Unknown Error")
        return p

    #Converted
    time.sleep(0.5)
    p = Fingerprint.createModel()
    
    if(p):
        print ("Fingerprints match")
    elif(not p):
        print ("Fingerprints did not match")
        return p
    else:
        print ("Unknown Error")
        return p
    
    time.sleep(0.5)
    enrollIDbytes = int(enrollID, 16)
    p = Fingerprint.storeModel(enrollIDbytes, 1)
    
    if(p):
        print ("Stored fingerprint template")
        enrollIDLoop()
    elif(not p):
        print ("Store Fingerprint Error")
        return p
    else:
        print ("Unknown Error")
        return p
    
#Run fingerprint sensor
def runLoop(outputTimeout):
    print ("Waiting for valid finger...")
    
    while(GPIO.input(inputPinExit) == True):
        if(getFingerprintIDez() == True):
            GPIO.output(outputPin, GPIO.HIGH)
            time.sleep(outputTimeout)
        else:
            GPIO.output(outputPin, GPIO.LOW)
            
    main()
#Get fingerprint
def getFingerprintID():
    p = False
    while(not p):
        p = Fingerprint.getImage()
        if(p):
            print ("Image Taken")
            break
        elif(not p):
            print ("No finger detected")
        else:
            print ("Unknown Error")
    
    p = Fingerprint.image2Tz(1)
    
    if(p):
        print ("Image converted")
    elif(not p):
        print ("Image not converted")
        return p
    else:
        print ("Unknown Error")
        return p
    
    p = Fingerprint.fingerSearch()
    
    if(p):
        print ("Found fingerprint")
    elif(not p):
        print ("No fingerprint found")
        return p
    else:
        print ("Unknown Error")
        return p
    
#Get fingerprint quick
def getFingerprintIDez():
    
    p = Fingerprint.getImage()
    if(not p):
        return 0
    
    p = Fingerprint.image2Tz(1)
    if(not p):
        return -1
    
    p = Fingerprint.fingerSearch()
    if(not p):
        return -1
    
    #print ("Found fingerprint")
    return (True)

#Upload fingerprint image to computer and save to file
def imageUpload():
    #userInput = input("ID # to store the finger as:")
    while(True):
        userID = input("ID # to store the finger or Q to quit:")
        
        if(userID.isdigit()):
            break
        elif((userID == 'q') or (userID == 'Q')):
            userID = ''
            main()
        else:
            print ("Must enter digit only")
    
    print ("Enrolling ID #" + userID)
    
    print ("Waiting for valid finger to enroll")
    time.sleep(0.5)
    
    p = False
    while (not p):
        p = Fingerprint.getImage()
        if(p):
            print ("Image taken")
            break
        elif(not p):
            print (".")
        else:
            print ("Unknown Error")
    
    #time.sleep(0.5)
    p = Fingerprint.uploadImage(userID)
    
    if(p):
        print ("Image downloaded and saved")
        return p
    elif(not p):
        print ("Image not downloaded or saved")
        return p
    else:
        print ("Unknown Error")
        return p

#Open image file and download to fingerprint sensor
def imageDownload():
    #userInput = input("ID # to store the finger as:")
    while(True):
        userID = input("ID # to download the finger or Q to quit:")
        
        if(userID.isdigit()):
            break
        elif((userID == 'q') or (userID == 'Q')):
            userID = ''
            main()
        else:
            print ("Must enter digit only")
    
    print ("Downloading ID #" + userID)
    
    p = Fingerprint.downloadImage(userID)
    time.sleep(.05)
    
    if(p):
        print ("Image downloaded to sensor")
    elif(not p):
        print ("Image not downloaded to sensor")
        return p
    else:
        print ("Unknown Error")
        return p

    p = Fingerprint.image2Tz(1)
    time.sleep(.05)
    if(p):
        print ("Image converted")
    elif(not p):
        print ("Image not converted")
        return p
    else:
        print ("Unknown Error")
        return p

    p = Fingerprint.downloadImage(userID)
    time.sleep(.05)
    if(p):
        print ("Image downloaded to sensor")
    elif(not p):
        print ("Image not downloaded to sensor")
        return p
    else:
        print ("Unknown Error")
        return p

    p = Fingerprint.image2Tz(2)
    time.sleep(.05)
    if(p):
        print ("Image converted")
    elif(not p):
        print ("Image not converted")
        return p
    else:
        print ("Unknown Error")
        return p

    #Converted
    p = Fingerprint.createModel()
    if(p):
        print ("Fingerprints match")
    elif(not p):
        print ("Fingerprints did not match")
        return p
    else:
        print ("Unknown Error")
        return p
    
    enrollIDbytes = int(userID, 16)
    p = Fingerprint.storeModel(enrollIDbytes, 1)
    if(p):
        print ("Stored fingerprint template")
        return p
    elif(not p):
        print ("Store Fingerprint Error")
        return p
    else:
        print ("Unknown Error")
        return p

#Main
def main():
    lockOnTime = 1
    #set-up output pin
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(outputPin, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(inputPinExit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    #Set serial port and baudrate
    Fingerprint.begin()
    
    if(Fingerprint.checkFPComms()):
        print ("Found Fingerprint Sensor")
    else:
        print ("Did not find Fingerprint Sensor")
        main()
    while(True):
        print("1 - Enroll Fingerprints")
        print("2 - Run Fingerprint Sensor")
        print("3 - Save Notepad to File")
        print("4 - Load Notepad from File")
        print("5 - Erase Library")
        print("6 - Upload Fingerprint Image to Computer")
        print("7 - Download Fingerprint Image to Sensor")
        print("E - Exit")
        menuInput = input ("Please select option ")
        
        if((menuInput.isdigit()) and (menuInput == '1')):
            enrollIDLoop()
            break
        elif((menuInput.isdigit()) and (menuInput == '2')):
            lockOnTime = 8
            runLoop(lockOnTime)
            break
        elif((menuInput.isdigit()) and (menuInput == '3')):
            totalCount = Fingerprint.getTemplateCount()
            print ("Template count is " + str(totalCount))
            for i in range(1, totalCount + 1):
                if(Fingerprint.getNotepad(i) == True):
                    print("Success Writing ID File for " + str(i))
                else:
                    print("Error Writing ID File")
                    break
        elif((menuInput.isdigit()) and (menuInput == '4')):
            #run Fingerprint.writeNotepad(ID) until False (returns false when no ID found)
            writeID = 1
            while((Fingerprint.writeNotepad(writeID)) == True):
                writeID += 1
            print("Total ID's entered " + str(writeID - 1))
        elif((menuInput.isdigit()) and (menuInput == '5')):
            if(Fingerprint.emptyDatabase() == True):
                pass
            else:
                print("Error erasing library")
        elif((menuInput.isdigit()) and (menuInput == '6')):
            if(imageUpload() == True):
                pass
            else:
                print("Error uploading image and saving to file")
        elif((menuInput.isdigit()) and (menuInput == '7')):
            if(imageDownload() == True):
                pass
            else:
                print("Error opening file and downloading to sensor")
        elif((menuInput == 'E') or (menuInput == 'e')):
            menuInput = ''
            GPIO.cleanup()
            sys.exit()
        else:
            print ("Must select from the menu")
    
    GPIO.cleanup()    
    return 0
   
if __name__ == '__main__':
    main()
    
#End
