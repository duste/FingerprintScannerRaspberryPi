'''
Created on Dec 10, 2014

@author: dustin
'''
#Fingerprint.py

import FPSconstants
import serial
import struct
import time
import sys
import os

#Variables
thePassword = 0x00
theAddress = 0xFFFFFFFF
fingerID = 0
confidence = 0
templateCount = 0
shortTime = 0.5
usbport = '/dev/ttyAMA0'		#Change ttyAMA0 to ttyS0 or serial0 for Pi3
baudrate = 57600
parity = serial.PARITY_NONE
stopbits = serial.STOPBITS_ONE
bytesize = serial.EIGHTBITS
usbportTimeout = 5.0
xonxoff = 0
rtscts = 0
   
#Set-up serial communication
def begin():
	
	global ser
	ser = serial.Serial(
                        usbport,
                        baudrate,
                        bytesize,
                        parity,
                        stopbits,
                        usbportTimeout,
                        xonxoff,
                        rtscts)
     
	time.sleep(shortTime)
	print ("Serial port setup on " + ser.name)
	
	if(ser.isOpen() == True):
		print("Serial port is open")
		ser.flush()
	else:
		print("Serial port is closed")

#Verify password with the Fingerprint Sensor
def verifyPassword():
    rxPacket = bytearray()
    
    packet = bytearray([
			FPSconstants.FINGERPRINT_VERIFYPASSWORD,
			((thePassword >> 24) & 0xff), 
			((thePassword >> 16) & 0xff),
			((thePassword >> 8) & 0xff), 
			(thePassword & 0xff)
			])
    
    writePacket(theAddress, FPSconstants.FINGERPRINT_COMMANDPACKET, 0x0007, packet)
    rxPacket = receivePacket(12)
    
    rxLength = (rxpacket[8]) - 2

    if((rxLength == 1) and (str(rxpacket[6]) == '7') and (str(rxPacket[9]) == '0')):
        return True
    return False

#Return packet of detected Fingerprint image
def getImage():
    rxPacket = bytearray()
    packet = bytearray([FPSconstants.FINGERPRINT_GETIMAGE])
    
    writePacket(theAddress, FPSconstants.FINGERPRINT_COMMANDPACKET, (len(packet)+2), packet)
    rxPacket = receivePacket(12)
    
    if((len(rxPacket)) < 12):
        print ("Receive packet error - Rx'd:" + str(len(rxPacket)))
        return False
    
    rxLength = (rxPacket[8]) - 2

    if((rxLength == 1) and (str(rxPacket[6]) == '7')):
        #print ("Receive packet acknowledged")
        if(str(rxPacket[9]) == '0'):
            print ("Finger collection success")
            return True
        elif(str(rxPacket[9]) == '1'):
            print ("Error receiving packet")
            return False
        elif(str(rxPacket[9]) == '2'):
            print ("Can't detect finger")
            return False
        elif(str(rxPacket[9]) == '3'):
            print ("Failed to collect finger")
            return False
        else:
            print ("Unknown getImage error")
            return False
    
#Return packet of character file from original Fingerprint image
def image2Tz(image2TzBuffer):
    rxPacket = bytearray()
    packet = bytearray([
        FPSconstants.FINGERPRINT_IMAGE2TZ,
        (image2TzBuffer & 0xff)
        ])

    writePacket(theAddress, FPSconstants.FINGERPRINT_COMMANDPACKET, (len(packet)+2), packet)
    rxPacket = receivePacket(12)
    
    rxLength = (rxPacket[8]) - 2

    if((rxLength == 1) and (str(rxPacket[6]) == '7')):
        #print ("Receive packet acknowledged")
        if(str(rxPacket[9]) == '0'):
            print ("Generated character file complete")
            return True
        elif(str(rxPacket[9]) == '1'):
            print ("Error receiving packet")
            return False
        elif(str(rxPacket[9]) == '6'):
            print ("Failed to generate character file due to over-disorderly fingerprint image")
            return False
        elif(str(rxPacket[9]) == '7'):
            print ("Failed to generate character file due to lackness of character point or over smallness of fingerprint image")
            return False
        elif(str(rxPacket[9]) == '21'):
            print ("Failed to generate image for the lackness of valid primary image")
            return False
        else:
            print ("Unknown image2Tz error")
            return False

#Return acknowledge packet of RegModel
def createModel():
    rxPacket = bytearray()
    packet = bytearray([FPSconstants.FINGERPRINT_REGMODEL])

    writePacket(theAddress, FPSconstants.FINGERPRINT_COMMANDPACKET, (len(packet)+2), packet)
    rxPacket = receivePacket(12)
    
    rxLength = (rxPacket[8]) - 2

    if((rxLength == 1) and (str(rxPacket[6]) == '7')):
        #print ("Receive packet acknowledged")
        if(str(rxPacket[9]) == '0'):
            print ("Generate template success")
            return True
        elif(str(rxPacket[9]) == '1'):
            print ("Error receiving packet")
            return False
        elif(str(rxPacket[9]) == '10'):
            print ("Failed to combine character file")
            return False
        else:
            print ("Unknown createModel error")
            return False

#Return acknowledge packet of Store
def storeModel(storeModelID, storeModelBuffer):
    rxPacket = bytearray()
    packet = bytearray([
        FPSconstants.FINGERPRINT_STORE, 
        (storeModelBuffer & 0xff),
        ((storeModelID >> 8) & 0xff),
        (storeModelID & 0xff)
        ])

    writePacket(theAddress, FPSconstants.FINGERPRINT_COMMANDPACKET, (len(packet)+2), packet)
    rxPacket = receivePacket(12)
    
    rxLength = (rxPacket[8]) - 2

    if((rxLength == 1) and (str(rxPacket[6]) == '7')):
        #print ("Receive packet acknowledged")
        if(str(rxPacket[9]) == '0'):
            print ("Template stored success")
            return True
        elif(str(rxPacket[9]) == '1'):
            print ("Error receiving packet")
            return False
        elif(str(rxPacket[9]) == '11'):
            print ("Addressed PageID is beyond finger library")
            return False
        elif(str(rxPacket[9]) == '24'):
            print ("Error writing flash")
            return False
        else:
            print ("Unknown storeModel error")
            return False

#Return Fingerprint template from flash into Char Buffer 1
def loadModel(loadModelID, loadModelBuffer):
    rxPacket = bytearray()
    packet = bytearray([
        FPSconstants.FINGERPRINT_LOAD, 
        (loadModelBuffer & 0xff),
        ((loadModelID >> 8) & 0xff),
        (loadModelID & 0xff)
        ])

    writePacket(theAddress, FPSconstants.FINGERPRINT_COMMANDPACKET, (len(packet)+2), packet)
    rxPacket = receivePacket(12)
    
    rxLength = (rxPacket[8]) - 2

    if((rxLength == 1) and (str(rxPacket[6]) == '7')):
        #print ("Receive packet acknowledged")
        if(str(rxPacket[9]) == '0'):
            print ("Template load success")
            return True
        elif(str(rxPacket[9]) == '1'):
            print ("Error receiving packet")
            return False
        elif(str(rxPacket[9]) == '12'):
            print ("Error reading template from library or readout template is invalid")
            return False
        elif(str(rxPacket[9]) == '11'):
            print ("Addressed PageID is beyond finger library")
            return False
        else:
            print ("Unknown loadModel error")
            return False

#Transfer a Fingerprint template from the Char Buffer 1 to host computer
def getModel(getModelBuffer):
    rxPacket = bytearray()
    packet = bytearray([
        FPSconstants.FINGERPRINT_UPLOAD, 
        (getModelBuffer & 0xff)
        ])
    
    writePacket(theAddress, FPSconstants.FINGERPRINT_COMMANDPACKET, (len(packet)+2), packet)
    rxPacket = receivePacket(12)
    rxLength = (rxPacket[8]) - 2

    if((rxLength == 1) and (str(rxPacket[6]) == '7')):
        #print ("Receive packet acknowledged")
        if(str(rxPacket[9]) == '0'):
            print ("Ready to tansfer following data packet")
            return True
        elif(str(rxPacket[9]) == '1'):
            print ("Error receiving packet")
            return False
        elif(str(rxPacket[9]) == '13'):
            print ("Error uploading template")
            return False
        else:
            print ("Unknown getmodel error")
            return False

#Delete Fingerprint template
def deleteModel(deleteModelID):
    rxPacket = bytearray()
    packet = bytearray([
        FPSconstants.FINGERPRINT_DELETE, 
        ((deleteModelID >> 8) & 0xff), 
        (deleteModelID & 0xff), 
        0x00, 
        0x01
        ])

    writePacket(theAddress, FPSconstants.FINGERPRINT_COMMANDPACKET, (len(packet)+2), packet)
    rxPacket = receivePacket(12)

    rxLength = (rxPacket[8]) - 2
        
    if((rxLength == 1) and (str(rxPacket[6]) == '7')):
        #print ("Receive packet acknowledged")
        if(str(rxPacket[9]) == '0'):
            print ("ID template delete success")
            return True
        elif(str(rxPacket[9]) == '1'):
            print ("Error receiving packet")
            return False
        elif(str(rxPacket[9]) == '16'):
            print ("Failed to delete ID template")
            return False
        else:
            print ("Unknown deleteModel error")
            return False

#Empty Fingerprint sensor database
def emptyDatabase():
    rxPacket = bytearray()
    packet = bytearray([FPSconstants.FINGERPRINT_EMPTY])

    writePacket(theAddress, FPSconstants.FINGERPRINT_COMMANDPACKET, (len(packet)+2), packet)
    rxPacket = receivePacket(12)
        
    rxLength = (rxPacket[8]) - 2
        
    if((rxLength == 1) and (str(rxPacket[6]) == '7')):
        #print ("Receive packet acknowledged")
        if(str(rxPacket[9]) == '0'):
            print ("Empty library success")
            return True
        elif(str(rxPacket[9]) == '1'):
            print ("Error receiving packet")
            return False
        elif(str(rxPacket[9]) == '17'):
            print ("Failed to clear finger library")
            return False
        else:
            print ("Unknown emptyDatabase error")
            return False

#Fingerprint search
def fingerSearch():
    rxPacket = bytearray()
    packet = bytearray([
    FPSconstants.FINGERPRINT_SEARCH, 
    0x01, 
    0x00, 
    0x00
    ])

    writePacket(theAddress, FPSconstants.FINGERPRINT_COMMANDPACKET, (len(packet)+2), packet)
    rxPacket = receivePacket(16)
        
    rxLength = (rxPacket[8]) - 2
    
    if((rxLength == 5) and (str(rxPacket[6]) == '7')):
        #print ("Receive packet acknowledged")
        if(str(rxPacket[9]) == '0'):
            print ("Page ID:" + str(rxPacket[10]) + str(rxPacket[11]))
            print ("Match score:" + str(rxPacket[12]) + str(rxPacket[13]))
            return True
        elif(str(rxPacket[9]) == '1'):
            print ("Error receiving packet")
            return False
        elif(str(rxPacket[9]) == '9'):
            print ("No matching finger in the library")
            return False
        else:
            print ("Unknown fingerSearch error")
            return False    

#Get the template count of the Fingerprint sensor
def getTemplateCount():
    templateCount = 0
    rxPacket = bytearray()
    packet = bytearray([FPSconstants.FINGERPRINT_TEMPLATECOUNT])

    writePacket(theAddress, FPSconstants.FINGERPRINT_COMMANDPACKET, len(packet)+2, packet)
    rxPacket = receivePacket(14)
        
    rxLength = (rxPacket[8]) - 2
        
    if((rxLength == 3) and (str(rxPacket[6]) == '7')):
        #print ("Receive packet acknowledged")
        if(str(rxPacket[9]) == '0'):
            print ("Finger collection success")
        elif(str(rxPacket[9]) == '1'):
            print ("Error receiving packet")
            return -1
        else:
            print ("Unknown getTemplateCount error")
            return -1
    
    templateCount = (rxPacket[10] * 256) + rxPacket[11]
    
    return templateCount

#Verify communication with Fingerprint Sensor
def checkFPComms():
    rxPacket = bytearray()
    packet = bytearray([
        FPSconstants.FINGERPRINT_COMMLINK,
        0x00
        ])
    writePacket(theAddress, FPSconstants.FINGERPRINT_COMMANDPACKET, 0x0004, packet)
    rxPacket = receivePacket(12)
    
    if((len(rxPacket)) < 12):
        print ("Receive packet error - Rx'd:" + str(len(rxPacket)))
        return False
    
    #rxLength = (ord(rxPacket[8])) - 2
    rxLength = rxPacket[8] - 2
    
    if((rxLength == 1) and ((str(rxPacket[6])) == '7')):
        #print ("Receive packet acknowledged")
        if(str(rxPacket[9]) == '0'):
            print ("Communication success")
            return True
        elif(str(rxPacket[9]) == '1'):
            print ("Error receiving packet")
            return False
        elif(str(rxPacket[9]) == '29'):
            print ("Comm port error")
            return False
        else:
            print ("Unknown error")
            return False

#Read notepad for each ID
def getNotepad(pageID):
    fileName = 'FingerprintID' + str(pageID)
    rxPacket = bytearray()
    packet = bytearray([
        FPSconstants.FINGERPRINT_READNOTEPAD, 
        (pageID & 0xff),
        ])
    
    #Open file as write only
    try:
        f = open(fileName, "w")
    except:
        print("Error opening/creating file " + fileName)
        return False
    
    #Send command to read page ID
    writePacket(theAddress, FPSconstants.FINGERPRINT_COMMANDPACKET, (len(packet)+2), packet)
    rxPacket = receivePacket(44)
        
    rxLength = rxPacket[8] - 2
    
    if((rxLength == 33) and (str(rxPacket[6]) == '7')):
        #print ("Receive packet acknowledged")
        if(str(rxPacket[9]) == '0'):
            print("Notepad Read Success")
            #write Rx packet to file
            for i in range(10, (rxLength + 9)):
                f.write((str(rxPacket[i])) + '\n')
            f.write('EOF')
            f.close()
            return True
        elif(str(rxPacket[9]) == '1'):
            print ("Error receiving packet")
            f.close()
            return False
        else:
            print ("Unknown error")
            f.close()
            return False

#Write each ID to Notepad
def writeNotepad(pageID):
    rxPacket = bytearray()
    
    fileName = 'FingerprintID' + str(pageID)
    
    #Open file as read only
    try:
        f = open(fileName, "r")
    except:
        print("Error opening file " + fileName)
        return False
    
    packet = bytearray([
        FPSconstants.FINGERPRINT_WRITENOTEPAD, 
        (pageID & 0xff),
        ])
    
    #read file with new line for each value - 32 numbers
    lines = f.readlines()
    
    #get rid of EOF
    lines.pop(32)
    
    #get rid of '\n'
    for i in range(0, (len(lines))):
        lines[i] = lines[i].replace('\n', '')
    #print("length of lines " + str(len(lines)))
    #print(lines)
    
    #convert string to int then hex and append to packet
    for i in range(0, len(lines)):
        packet.append((int(lines[i]) & 0xff))
    
    #add values to packet and convert to hex
    
    writePacket(theAddress, FPSconstants.FINGERPRINT_COMMANDPACKET, (len(packet)+2), packet)
    rxPacket = receivePacket(12)
    
    rxLength = rxPacket[8] - 2
    
    if((rxLength == 1) and (str(rxPacket[6]) == '7')):
        #print ("Receive packet acknowledged")
        if(str(rxPacket[9]) == '0'):
            print("Notepad Write Success")
            f.close()
            if(loadModel(pageID, 1) == True):
                if(loadModel(pageID, 2) == True):
                    if(creatModel() == True):
                        if(storeModel(pageID, 1) == True):
                            return True
            return False
        elif(str(rxPacket[9]) == '1'):
            print ("Error receiving packet")
            f.close()
            return False
        else:
            print ("Unknown error")
            f.close()
            return False
    
#Upload fingerprint image to computer
def uploadImage(uploadImageID):
    fileName = 'FingerprintImage' + uploadImageID
    rxPacket = bytearray()
    imagePacket = bytearray()
    packet = bytearray([
        FPSconstants.FINGERPRINT_UPLOADIMAGE])
    
    #Open file as write only
    try:
        f = open(fileName, "w")
    except:
        print("Error opening/creating file " + fileName)
        return False

    writePacket(theAddress, FPSconstants.FINGERPRINT_COMMANDPACKET, (len(packet)+2), packet)
    rxPacket = receivePacket(12)
    rxLength = (rxPacket[8]) - 2

    if((rxLength == 1) and (str(rxPacket[6]) == '7')):
        #print ("Receive packet acknowledged")
        if(str(rxPacket[9]) == '0'):
            print ("Ready to tansfer following data packet")
            imagePacket = receivePacket(40032)
            for i in range(0, (len(imagePacket))):
                f.write(str(imagePacket[i]) + '\n')
            f.write('EOF')
            f.close
            return True
        elif(str(rxPacket[9]) == '1'):
            print ("Error receiving packet")
            return False
        elif(str(rxPacket[9]) == '16'):
            print ("Fail to transfer the following data packet")
            return False
        else:
            print ("Unknown uploadImage error")
            return False

#Download fingerprint image to Sensor
def downloadImage(downloadImageID):
    fileName = 'FingerprintImage' + downloadImageID
    rxPacket = bytearray()
    imagePacket = bytearray()
    packet = bytearray([
        FPSconstants.FINGERPRINT_DOWNLOADIMAGE])
    
    #Open file as write only
    try:
        f = open(fileName, "r")
    except:
        print("Error opening file " + fileName)
        return False
    #read lines of the file
    lines = f.readlines()
    print("Length of lines " + str(len(lines)))
    
    #Get rid of EOF
    lines.pop(len(lines)-1)
    
    #Get rid of '\n'
    for i in range(0, (len(lines))):
        lines[i] = lines[i].replace('\n', '')
        imagePacket.append((int(lines[i])) & 0xff)
    #print("length of lines " + str(len(lines)))
    #print(lines)
    
    writePacket(theAddress, FPSconstants.FINGERPRINT_COMMANDPACKET, (len(packet)+2), packet)
    rxPacket = receivePacket(12)
    rxLength = (rxPacket[8]) - 2

    if((rxLength == 1) and (str(rxPacket[6]) == '7')):
        #print ("Receive packet acknowledged")
        if(str(rxPacket[9]) == '0'):
            print ("Ready to tansfer following data packet")
            imageTX = ser.write(imagePacket)
            f.close
            return True
        elif(str(rxPacket[9]) == '1'):
            print ("Error receiving packet")
            return False
        elif(str(rxPacket[9]) == '15'):
            print ("Module can't receive the following data packet")
            return False
        else:
            print ("Unknown DownloadImage error")
            return False


#Write data to Fingerprint Sensor
def writePacket(addr, packetType, pLengthTX, packet):
    checksum = bytearray()
    dataToSend = bytearray([
        ((FPSconstants.FINGERPRINT_STARTCODE>>8) & 0xff),
        ((FPSconstants.FINGERPRINT_STARTCODE) & 0xff),
        ((addr>>24) & 0xff),
        ((addr>>16) & 0xff),
        ((addr>>8) & 0xff),
        ((addr) & 0xff),
        ((packetType) & 0xff),
        ((pLengthTX>>8) & 0xff),
        ((pLengthTX) & 0xff)
        ])

    #print ("dataToSend created")
    
    #packageSum is used as checksum (arithmatic sum of package id, package length and package contents
    packageSum = ((pLengthTX >>8) & 0xff) + (pLengthTX & 0xff) + packetType
    #print ("packageSum:" + str(packageSum))
    
    
    for i in range((len(packet))):
        packageSum = packageSum + (packet[i] & 0xff)
    
    #bytesTX = ser.write(checksum)
    #ser.flush()
    
    packet.append((packageSum >> 8) & 0xff)
    packet.append(packageSum & 0xff)
    
    bytesTX = ser.write(dataToSend)
    bytesTX = ser.write(packet)
    
#Fast Read data from Fingerprint Sensor and return with package length of 3 ONLY
def receivePacket(pLengthRx):
    timer = 0
    bArrayLoc = 0
    reply = [0]
    
    while(True):
        bArrayLoc = 0
        
        while(not ser.readable()):
            time.sleep(0.1)
            timer = timer + 1
            if timer >= ((int(usbportTimeout)) * 10):
                return int(FPSconstants.FINGERPRINT_TIMEOUT)
        #print ("read " + str(reply[0]))
        
        #Waiting for receive packet
        while(reply[bArrayLoc] == 0):
            reply[bArrayLoc] = ser.read(1)
            #Need to add timeout - times out then waits for user input? timeout and goes back to main?
        reply.extend(ser.read(pLengthRx - 1))
        reply[0] = 239
        '''
        #Display received packet
        print ("Display received packet")
        for i in range(0, pLengthRx):
            print ("reply:" + str(i) + " = " + str(reply[i]))
        '''
        
        return reply
