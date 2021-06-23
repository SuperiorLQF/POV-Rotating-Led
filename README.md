# POV-Rotating-Led
 This project can display as a screen by rotating the Led series to cause POV phonomenon  
POV Rotating Led using ***Esp8266-Node MCU*** and ***SK9822 Led series***  
The electrical motors is using a 12V motor which has rpm around 3000  
This project contents the wire connection map, python code run on computer and micropython code run on ESP8266.  
Then you shold make simple mechanical connection by yourself, and make sure to be safe***!!!

## Hard Ware Connection:  
|ESP8266| Sk9822|battery1(5VDC)|battery2(3.7VDC)|
|----|----|----|----|
|D7(MOSI)|Data(D,green wire)|
|D5(HSPI_CLK)|CLK(C,yellow wire)|
|GND|GND|COMMON|COMMON|          
|   |VCC|+||                   
|3V3|||+| 


## SK9822 buf data structure:  
|structure|15 to 13|12 to 8|7 to 4|3 to 0|       
|----|----|----|----|----|
|impilication|brightness(5 bits)|Blue(8 bits)|Green(8 bits)|Red(8 bits)|
|start frame|000|00000|0000|0000|
|end frame|111|11111|1111|1111|

## How to use it ?  
1.connect the ESP8266 through webrepl  
2.input  from Led8266 import *,and you 'll find 15Led trun on with white light  
3.turn on the electrical motor to enable it to spin  
4.as spinning stably, input Led_start(), the counter'll count and detect  
5.run the ocv_test1 to send the picture，and it will shinning automatically  
