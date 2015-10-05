'''
Created on Dec 12, 2014

@author: dustin
'''

#FPRun.py

import os
import time
import Fingerprint
import FPSconstants

#Get ID # from operator and enroll
def enrollIDLoop():
    #userInput = input("ID # to store the finger as:")
    while(True):
        fID = input("ID # to store the finger or Q to quit:")
        
        if(fID.isdigit()):
            break
        elif((fID == 'q') or (fID == 'Q')):
            return
        else:
            print ("Must enter digit only")
    
    print ("Enrolling ID #" + fID)
    
    fRun = enrollFingerprint(fID)
    while(not fRun):
        fRun = enrollFingerprint(fID)
    
def enrollFingerprint(enrollID):
    print ("Waiting for valid finger to enroll")
    
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
    
    p = Fingerprint.image2Tz(0x01)

    if(p):
        print ("Image converted")
    elif(not p):
        print ("Image not converted")
        return p
    else:
        print ("Unknown Error")
        return p
    
    print ("Remove Finger")
    time.sleep(2)
    
    p = False
    print ("Place same finger again")
    while(not p):
        p = Fingerprint.getImage()
        
        if(p):
            print ("Image taken")
            break
        elif(not p):
            print (".")
        else:
            print ("Unknown Error")
        
    p = Fingerprint.image2Tz(0x02)
    
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
    
    enrollIDbytes = int(enrollID, 16)
    p = Fingerprint.storeModel(enrollIDbytes)
    
    if(p):
        print ("Stored fingerprint template")
        enrollIDLoop()
    elif(not p):
        print ("Store Fingerprint Error")
        return p
    else:
        print ("Unknown Error")
        return p
    

#Main
def main():
    #print "main function start"
    
    #Set serial port and baudrate
    Fingerprint.begin()
    
    if(Fingerprint.checkFPComms()):
        print ("Found Fingerprint Sensor")
    else:
        print ("Did not find Fingerprint Sensor")
        main()
    enrollIDLoop()
    
    return 0
   
if __name__ == '__main__':
    main()
    
#End
