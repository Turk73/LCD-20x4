#!/usr/bin/python

# HD44780 20x4 LCD Test Script per
# Raspberry Pi
# Author	: Coge & Turk
# Site		: http://rpy-italia.org/
# Date		: 22/04/2013
# Versione	:	2.0.1

# I contatti dell LCD sono i seguenti
# 1 : GND
# 2 : 5V
# 3 : Contrast (0-5V)*
# 4 : RS (Register Select)
# 5 : R/W (Read Write)       - GROUND THIS PIN
# 6 : Enable or Strobe
# 7 : Data Bit 0              
# 8 : Data Bit 1             
# 9 : Data Bit 2             
# 10: Data Bit 3             
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Retroilluminazione +5V**
# 16: LCD Retroilluminazione GND

import RPi.GPIO as GPIO
import time
import subprocess
import os

# Define GPIO to LCD mapping
LCD_RS = 17
LCD_E  = 4
LCD_D0 = 25 # per 16 bit
LCD_D1 = 8  # per 16 bit
LCD_D2 = 9  # per 16 bit
LCD_D3 = 11 # per 16 bit
LCD_D4 = 22 
LCD_D5 = 23
LCD_D6 = 24
LCD_D7 = 27
LED_ON = 7

# Definizione di qualche costante
LCD_WIDTH = 20    # Caratteri massimi per linea
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line 

# Costanti di Tempo
E_PULSE = 0.00005
E_DELAY = 0.00005

GPIO.setwarnings (False)     # Non avverte se i canali sono occupati
GPIO.setmode(GPIO.BCM)       # Usa la numerazione BCM per la GPIO
GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT) # RS
GPIO.setup(LCD_D0, GPIO.OUT) # DB0
GPIO.setup(LCD_D1, GPIO.OUT) # DB1
GPIO.setup(LCD_D2, GPIO.OUT) # DB2
GPIO.setup(LCD_D3, GPIO.OUT) # DB3
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7
GPIO.setup(LED_ON, GPIO.OUT) # Retroilluminazione abililtata

# Calcolo file scaricati
directory = 3

try:
	hdd = subprocess.check_output(["df -h | grep sda1 | awk '{print $4}'"], shell=True)[:-2]
	hdd1 = str (100-int(subprocess.check_output(["df -h | grep sda1 | awk '{print $5}'"], shell=True)[:-2]))
	file_scaricati = str(int(subprocess.check_output(["ls /mnt/Mulo | wc -l"], shell=True)[:-1]) - directory)

except:
	data = subprocess.check_output(["date | awk '{ print $1,$2,$3,$4,$5}'"], shell=True)[:-2]
	out_file = open ("/home/pi/display/ripristini.log","a")
	out_file.write (data + ": HDD Smontato\n")
	out_file.close ()
	os.system("sudo reboot")
	
##  VARIABILI  ##
ora = subprocess.check_output(["date | awk '{ print $5 }' | cut -c1-5"], shell=True)[:-1]
cpu_temp = subprocess.check_output(["/opt/vc/bin/vcgencmd measure_temp | cut -c6-9"], shell=True)[:-1]
try:
	download = subprocess.check_output(["amulecmd -P amule -c status | grep Download:"], shell=True)[13:-1]
except: download = "NON DISP."
# Controllo impostazione velocita di aMule
vel = open('/home/pi/.aMule/amule.conf','r')
vel.seek(81,0)
velocita1 = vel.readline()
velocita = velocita1.split('=')
vel.close()
if int(velocita[1]) == 0: velocita = "Max"
else: velocita = "Min"

# Blocco principale del programma
def main():
# Inizializza il display
	lcd_init()
# Spegne e riaccende retroillu.ne
	GPIO.output(LED_ON, False)
	GPIO.output(LED_ON, True)

	lcd_byte(LCD_LINE_1, LCD_CMD)
	lcd_string("CPU: " + cpu_temp + chr(223) +  "C    " + ora , 1)
	lcd_byte(LCD_LINE_2, LCD_CMD)
	lcd_string("HDD Lib. " + hdd1 + "% = "  + hdd + "Gb" , 1)
	lcd_byte(LCD_LINE_3, LCD_CMD)
	lcd_string("Vel: " + download + " " + velocita , 1)
	lcd_byte(LCD_LINE_4, LCD_CMD)
	lcd_string(file_scaricati + " File Completi" , 2)
# Controlli su Samba e aMule
	statoamule = subprocess.check_output(["sudo service amule-daemon status | awk '{print $2}'"], shell=True)[:-1]
	statosamba = subprocess.check_output(["sudo service samba status | grep smbd | awk '{print $3}'"], shell=True)[:-1]
	if statoamule=="not":msg1="aMule ";os.system("sudo service amule-daemon start")
	else: msg1=""
	if statosamba=="not":msg2="Samba";os.system("sudo service samba start")
	else: msg2=""
	if msg1!="" or msg2!="":
		data = subprocess.check_output(["date | awk '{ print $1,$2,$3,$4,$5}'"], shell=True)[:-2]
		out_file = open ("/home/pi/display/ripristini.log","a")
		out_file.write (data+" Ripristinato: "+msg1+msg2+"\n")
		out_file.close ()
		lcd_string("CPU: " + cpu_temp + chr(223) +  "C " + msg1 + msg2, 1)
	time.sleep(3) # attende x secondi

# Spegne retroilluminazione
	GPIO.output(LED_ON, False)
 
#  GPIO.cleanup()

def lcd_init():
	# Inizializza display
	lcd_byte(0x33,LCD_CMD)
	lcd_byte(0x32,LCD_CMD)
	lcd_byte(0x28,LCD_CMD)
	lcd_byte(0x0C,LCD_CMD)  
	lcd_byte(0x06,LCD_CMD)
	lcd_byte(0x01,LCD_CMD)  

def lcd_string(message,style):
  # Invia al display la stringa
  # style=1 Giustificata a SX
  # style=2 Centrata
  # style=3 Giustificata a DX

  if style==1:
    message = message.ljust(LCD_WIDTH," ")  
  elif style==2:
    message = message.center(LCD_WIDTH," ")
  elif style==3:
    message = message.rjust(LCD_WIDTH," ")

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D0, False)
  GPIO.output(LCD_D1, False)
  GPIO.output(LCD_D2, False)
  GPIO.output(LCD_D3, False)
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
#  if bits&0x10==0x10:
#    GPIO.output(LCD_D0, True)
#  if bits&0x01==0x01:
#    GPIO.output(LCD_D1, True)
#  if bits&0x02==0x02:
#    GPIO.output(LCD_D2, True)
#  if bits&0x04==0x04:
#    GPIO.output(LCD_D3, True)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  time.sleep(E_DELAY)    
  GPIO.output(LCD_E, True)  
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)  
  time.sleep(E_DELAY)      

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  time.sleep(E_DELAY)    
  GPIO.output(LCD_E, True)  
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)  
  time.sleep(E_DELAY)   

if __name__ == '__main__':
  main()
