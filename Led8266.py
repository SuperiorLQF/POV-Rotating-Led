#Led rotate display by ESP8266-NodeMCU and SK9822 with POV principle
#all right reserved @Superior 2021.6
#this procedure worked as a UDP client
#if this procedure work well, then delete Led_test from ESP8266 by webrepl
from machine import Pin,SPI,ADC
import machine
import socket
import ujson
import utime
'''
************************Hard Ware Connection:****************************************************************
ESP8266             Sk9822                battery1(5VDC)      battery2(3.7VDC)         
D7(MOSI)          Data(D,green wire)
D5(HSPI_CLK)      CLK(C,yellow wire)
GND               GND                       -                        -  (COMMON)           
                  VCC                       +
3V3                                                                  +
**************************************************************************************************************

****************SK9822 buf data structure:************************************
|****|****|****|****|       <- 4Byte or 2word
|111|brightness(5 bits)|Blue(8 bits)|Green(8 bits)|Red(8 bits)|
start frame:0000 0000 0000 0000
end frame:1111 1111 1111 1111
******************************************************************************

*****************************How to use it ?**********************************
1.connect the ESP8266 through webrepl
2.input  from Led8266 import *,and you 'll find 15Led trun on with white light
3.turn on the electrical motor to enable it to spin
4.as spinning stably, input Led_start(), the counter'll count and detect
5.run the ocv_test1 to send the picture，and it will shinning automatically
******************************************************************************

'''
machine.freq(160000000)#set the CPU frequency to 160MHz
hspi=SPI(1,baudrate=30000000,polarity=0,phase=0)#baudrate max30M,18.133us to 15SK9822LED


ESP_PORT = 8081#UDP initialize
ESP_IP=''
ESP_addr = (ESP_IP, ESP_PORT)


'''
****************SPI send method or principle in MicroPython:******************
save the data in a list, for instance, LED_buf. Every object in list represents a Led(4Byte data structure).
Note*: the first and last elements in list must be start frame and end frame
       the LED_buf[x] corresponds to the xth Led in Sk9822
'''

#open n lights with the brightest white color
def Led_open(n):
    LED_buf=[b'\xff'*4 for i in range(n+2)]
    LED_buf[0]=b'\x00'*4#The start frame must be \x00\x00\x00\x00 in 2word or 4Byte
    LED_buf[-1]=b'\xff'*4#The end frame must be \xff\xff\xff\xff in 2word or 4Byte
    for i in range(n+2):
        hspi.write(LED_buf[i])

#close all the Led_lights
def Led_close():
    n=20
    LED_buf=[b'\xe0\00\00\00' for i in range(n+2)]
    LED_buf[0]=b'\x00'*4#start frame
    LED_buf[-1]=b'\xff'*4#end frame
    for i in range(n+2):
        hspi.write(LED_buf[i])


#to convert the BGR_list to the standard SK9822 bytes format
def BGR2sixteen(BGR_list):
    my_bytes=b'\xff'+bytearray(BGR_list) #to make the arrytype be b'' not bytearray(b'') though they are equalvalent in sometime, but they'll cause some problem
    return my_bytes


'''
****************************Led15object***********************
function:define a string lights with 15Led
class variable:startframe/endframe
object property:rpmspeed
object method:shine/close  (containning delay)
**************************************************************
'''
#Led object
class Led15:
    __startframe__ = b'\x00' * 4
    __endframe__ = b'\xff' * 4
    __segment_num__=45#we divide the circle into 45 pieces
    def __init__(self,rpmspeed):
        self.delay=1000000/(rpmspeed/60)/Led15.__segment_num__-32*15/30 #if rpmspeed=3000,then a position 'll cost 444.444us
    #15Led shining，time cost ：18.133us（with high spi）

    #make the Led15 shining
    def shine(self,Ledbuf):
        hspi.write(Led15.__startframe__)
        for i in range(15):
            hspi.write(Ledbuf[i])
        hspi.write(Led15.__endframe__)
        utime.sleep_us(int(self.delay))

    #make the Led15 extinguish
    def close(self):
        Ledbuf = [b'\xff\00\00\00' for i in range(15)]
        hspi.write(Led15.__startframe__)
        for i in range(15):
            hspi.write(Ledbuf[i])
        hspi.write(Led15.__endframe__)



#UDP receive function
def udpServer_recv(udp_server):
    recv_data, server_addr = udp_server.recvfrom(1024)  # 接受数据，等待对方反应......
    recv_result= ujson.loads(recv_data.decode('utf-8'))
    #print(recv_result)
    return recv_result


'''
*************************rpmspeed detection module*****************
to detect the rpmspeed before turn on the light 
you shold make your eletric motor run first!
test method:use an Led to make the detector detect it while spinning
*******************************************************************
'''
def rpm_detect():
    my_adc=ADC(0)
    lst=[]
    while my_adc.read() < 1000:  # 阻塞直至电平升高
        pass
    for i in range(100):#get average rpm
        t1=utime.tick_us()
        while my_adc.read()>1000:#阻塞直至电平降低
            pass
        while my_adc.read()<1000:#阻塞直至电平升高
            pass
        t2=utime.tick_us()
        lst.append(t2-t1)
        print(i)
    AVRG=sum(lst)/100
    rpmspeed=60*1000000/AVRG
    return rpmspeed


'''**************************image receive function****************************
corresponding with ocv_test.py on PC
you should run that proceure first!
*******************************************************************************
'''
def Led_start(rpmspeed=7000):
    print('start!')
    #rpmspeed=rpm_detect()    #detect the rpmspeed

    #print('rpmspeed = {}'.format(rpmspeed))
    string_lights = Led15(rpmspeed)#create Led15 object实例化对象

    #UDP receive image
    lst=[]
    for i in range(45):
        print('{}:'.format(i),end='')
        a=udpServer_recv(udp_server)
        a=list(map(BGR2sixteen,a))
        print(a)
        lst.append(a)


    while True:
        for i in range(45):
            string_lights.shine(lst[i])

def Led_try(rpm1,rpm2,n):
    print('start!')
    lst=[]
    for i in range(45):
        print('{}:'.format(i),end='')
        a=udpServer_recv(udp_server)
        a=list(map(BGR2sixteen,a))
        print(a)
        lst.append(a)
    if rpm1<=rpm2:
        for rpmspeed in range(rpm1,rpm2+1):
            string_lights = Led15(rpmspeed)
            for i in range(n):
                for i in range(45):
                    string_lights.shine(lst[i])
            print(rpmspeed)
    else:
        for rpmspeed in range(rpm1,rpm2-1,-1):
            string_lights = Led15(rpmspeed)
            for i in range(n):
                for i in range(45):
                    string_lights.shine(lst[i])
            print(rpmspeed)

#test function to test if work well
def test():
    BGR_list_all=[[255,0,0],[0,255,0],[0,0,255],[255,255,255],[0,255,255],[255,0,0],[0,255,0],[0,0,255],[255,255,255],[0,255,255],[255,0,0],[0,255,0],[0,0,255],[255,255,255],[0,255,255]]
    print('15 lights blue green red white yellow')
    hspi.write('\x00\x00\x00\x00')
    for i in range(15):
        hspi.write(BGR2sixteen(BGR_list_all[i]))
    hspi.write('\xff\xff\xff\xff')


#open the socket,prepare for UDP
udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server.bind(ESP_addr)





