#Led rotate display by ESP8266-NodeMCU and SK9822 with POV principle
#all right reserved @Superior 2021.6
#this procedure worked as a UDP sever
import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
import json
import socket
import time

IMAGE_LENGTH=300#图像的边长
CUBE_LENGTH = 10#像素块的边长
Rotate_direction=1#电机旋转方向，逆旋转为1，顺时针为-1
DIVIDE=45

#UDP client  IP
ESP_PORT = 8081
ESP_IP='192.168.43.38'
ESP_addr = (ESP_IP, ESP_PORT)

#UDP server  IP
PC_PORT=8081
PC_IP=''
PC_addr=(PC_IP,PC_PORT)

def list_add(a,b):#BGR数列相加函数
    return  [x+y for x,y in zip(a,b)]

def pixelate(cropped_img):#将裁剪后的图片进行像素化
    global IMAGE_LENGTH
    global CUBE_LENGTH
    for m in range(IMAGE_LENGTH // CUBE_LENGTH):
        for k in range(IMAGE_LENGTH // CUBE_LENGTH):
            SUM_BGR = [0, 0, 0]
            for i in range(CUBE_LENGTH):
                for j in range(CUBE_LENGTH):
                    SUM_BGR = list_add(SUM_BGR, cropped_img[i + k * 10, j + m * 10])
            AVG_BGR = [int(x / CUBE_LENGTH ** 2) for x in SUM_BGR]
            for i in range(CUBE_LENGTH):
                for j in range(CUBE_LENGTH):
                    cropped_img[i + k * 10, j + m * 10] = AVG_BGR

def get_BGR(xita,cropped_img):#获取某个角度上一系列的BGR数值，img是裁剪后的图像
    global IMAGE_LENGTH
    global CUBE_LENGTH
    center_point = [IMAGE_LENGTH//2, IMAGE_LENGTH//2]
    show_list = []
    for i in range(IMAGE_LENGTH // CUBE_LENGTH//2):
        lst_temp=list(map(int,cropped_img[int(center_point[0]+CUBE_LENGTH*i*math.cos(xita*math.pi/180)),int(center_point[1]-CUBE_LENGTH*i*math.sin(xita*math.pi/180))]))
        #str=BGR2sixteen(lst_temp)
        show_list.append(lst_temp)
    return show_list
def BGR2sixteen(BGR_list):#把BGR转换成SK9822标准格式'utf-8'的byte模式
    str=b'\xff'+bytearray(BGR_list) #to make the arrytype be b'' not bytearray(b'') though they are equalvalent in sometime, but they'll cause some problem
    return str
def get_rotate_bytematrix(cropped_img):
    image_bytearray=[]
    for i in range(DIVIDE):
        image_bytearray.append(get_BGR(Rotate_direction*8*i,cropped_img))
    return image_bytearray
def udpServer_send(udp_server,send_data):#UDP发送函数
    print('发送')
    send_data=json.dumps(send_data)
    udp_server.sendto(send_data.encode('utf-8'),ESP_addr) #发送数据

udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server.bind(PC_addr)#建立连接
pkq=cv2.imread('C:\\Users\\Lenovo\\Desktop\\ESP8266_POV\\MY_IMAGE\QSY.jpg')
center_point=[int(pkq.shape[0]/2),int(pkq.shape[1]/2)]
cropped_pkq = pkq[center_point[1]-IMAGE_LENGTH//2:center_point[1]+IMAGE_LENGTH//2, center_point[0]-IMAGE_LENGTH//2:center_point[0]+IMAGE_LENGTH//2]#H/WIDTH
pixelate(cropped_pkq)
cropped_pkq_bytematrix=get_rotate_bytematrix(cropped_pkq)

print('现在开始发送数据')
for i in range(DIVIDE):
    udpServer_send(udp_server,cropped_pkq_bytematrix[i])
    time.sleep(0.1)


#cv2.imwrite("C:\\Users\\Lenovo\\Desktop\\ESP8266_POV\\MY_IMAGE\\pkq.jpg", cropped)
cv2.imshow('pkq1',cropped_pkq)
cv2.waitKey(0)
'''
point_RGB=pkq[center_point[0],center_point[1]]#BGR
#print(*point_RGB)
image_length=min(center_point[0]-10,center_point[0]-10)
print(image_length)'''
