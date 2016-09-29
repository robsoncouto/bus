
import serial,time #You need the pyserial library
import struct

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0)
#time.sleep(10);#my arduino bugs if data is written to the port after opening it
#filename='sonic.bin'#name of the rom, bin format
#f=open(name,'rb');
#with open(filename,'rb') as f:
romsize=1024

def binary_mode():
    print("Entering binary mode\n")
    tries=0;
    while(tries<20):
        ser.flushInput()
        ser.write(b"\x00")
        time.sleep(0.01)
        response = ser.read(5)
        print(response)
        if (response == bytes("BBIO1","ASCII")):
            print("[*]Bus pirate now in binary mode")
            break
        else:
            print("Bus pirate not found after",tries,"tries")
        tries=tries+1
def set_i2c_mode():
    print("Setting I2C mode\n")
    tries=0;
    while(tries<20):
        ser.flushInput()
        ser.write(b"\x02")
        time.sleep(0.01)
        response = ser.read(4)
        print(response)
        if (response == bytes("I2C1","ASCII")):
            print("[*]Bus pirate now in I2C mode")
            break
        else:
            print("Problem in setting i2c mode after",tries,"tries")
        tries=tries+1
    tries=0;
    while(tries<20):
        ser.flushInput()
        ser.write(b"\x63")
        time.sleep(0.01)
        response = ser.read(1)
        print(response)
        if (response == struct.pack(">B",0x01)):
            print("[*]I2C speed set to 400kHz")
            break
        else:
            print("Problem in setting i2c speed after ",tries,"tries")
        tries=tries+1
    tries=0
    while(tries<20):
        ser.flushInput()
        ser.write(b"\x4C")
        time.sleep(0.01)
        response = ser.read(1)
        print(response)
        if (response == struct.pack(">B",0x01)):
            print("[*]Power supply and Pull ups activated")
            break
        else:
            print("Problem in setting i2c mode ",tries,"tries")
        tries=tries+1

def i2c_mem_set_address(address):
    print("Setting I2C mode\n")
    tries=0;
    while(tries<20):
        ser.flushInput()
        ser.write(b"\x02")
        time.sleep(0.01)
        response = ser.read(1)
        print(response)
        if (response == struct.pack(">B",0x01)):
            print("[*]Sent Start bit")
            break
        else:
            print("Problem in setting i2c mode after",tries,"tries")
        tries=tries+1
    tries=0;
    while(tries<20):
        ser.flushInput()
        ser.write(b"\x12")
        time.sleep(0.01)
        response = ser.read(1)
        print(response)
        if (response == struct.pack(">B",0x01)):
            print("[*]Sent bulk write comand")
            break
        else:
            print("Problem in setting i2c mode after",tries,"tries")
        tries=tries+1
    tries=0;
    while(tries<20):
        ser.flushInput()
        ser.write(b"\xA1")
        time.sleep(0.01)
        response = ser.read(1)
        print(response)
        if (response == struct.pack(">B",0x00)):
            print("[*]Sent memory write command")
            break
        else:
            print("Problem in setting i2c mode after",tries,"tries")
        tries=tries+1
    tries=0;
    while(tries<20):
        ser.flushInput()
        ser.write(struct.pack(">B",address>>8))
        time.sleep(0.01)
        response = ser.read(1)
        print(response)
        if (response == struct.pack(">B",0x00)):
            print("[*]Sent Address high byte,ok")
            break
        else:
            print("Problem in setting i2c mode after",tries,"tries")
        tries=tries+1
    tries=0;
    while(tries<20):
        ser.flushInput()
        ser.write(struct.pack(">B",address&0xFF))
        time.sleep(0.01)
        response = ser.read(1)
        print(response)
        if (response == struct.pack(">B",0x00)):
            print("[*]Sent address low byte,ok")
            break
        else:
            print("Problem in setting i2c mode after",tries,"tries")
        tries=tries+1

while True:
    print("===========================================")
    print("           What do you want do do?         ")
    print("                                           ")
    print("              1-dump                       ")
    print("              2-burn                       ")
    print("              3-info                       ")
    print("              4 -binary mode     2016      ")
    print("                                  Robson C ")
    print("===========================================")
    option=int(input())
    romsize=1*1024*1024
    block=0
    print(option)
    if(option==1):
        name=input("What the name of the file?")

        f = open(name, 'w')
        f.close()
        ser.flushInput()
        ser.write(b"\x00")
        ser.write(bytes("r","ASCII"))
        numBytes=0
        f = open(name, 'ab')#yes, that simple
        while (numBytes<romsize):
            while ser.inWaiting()==0:
                print("waiting...\n",numBytes)
                time.sleep(0.1)
            data = ser.read(1)#must read the bytes and put in a file
            f.write(data)
            numBytes=numBytes+1
            #if(numBytes%8192==0):
            #    //block=block+1
            #    f.close()
            #    f = open(name+str(block)+".bin", 'ab')
        f.close()
    if(option==2):
        name=input("What's the name of the file?")
        print(name)
        f = open(name, 'rb')

        for i in range(8192):
            ser.write(b"\x55")
            ser.write(bytes("w","ASCII" ))
            time.sleep(0.001)
            ser.write(struct.pack(">B",i>>8))
            CHK=i>>8
            #CHK=ord(CHK)
            time.sleep(0.001)
            ser.write(struct.pack(">B",i&0xFF))
            CHK^=i&0xFF
            time.sleep(0.001)
            data=f.read(128);
            print(data)
            #print("CHK:", CHK)
            for j in range(len(data)):
                 CHK=CHK^data[j]
            time.sleep(0.001)
            print("Sector:",i)
            print("CHK:", CHK)
            #ser.write(data)
            response=~CHK
            while response!=CHK:
                ser.write(data)
                ser.write(struct.pack(">B",CHK&0xFF))
                timeout=30
                while ser.inWaiting()==0:
                    time.sleep(0.1)
                    print("waiting for CHK response")
                response=ord(ser.read(1))
                print("rsp", response)
        f.close()
    if(option==4):
        binary_mode()
    if(option==5):
        binary_mode()
        set_i2c_mode()
        i2c_mem_set_address(0)
