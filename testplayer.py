# Simple example of reading the MCP3008 analog input channels and printing
# them all out.
# Author: Tony DiCola
# License: Public Domain
import time

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
from .enemy import Enemy
from .player import Player

# inport GPIO library
import numpy as np
import RPi.GPIO as GPIO  # import RPi.GPIO module
from time import sleep
import serial  # importa libreria serial lettura valori usb

# Software SPI configuration:
# CLK  = 23
# MISO = 21
# MOSI = 19
# CS   = 24
# mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# CS2 = 26
# mcp2 = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS2, miso=MISO, mosi=MOSI)

# Hardware SPI configuration: un bus, due MCP3008
SPI_PORT = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

SPI_DEVICE = 1
mcp2 = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD
GPIO.setup(22, GPIO.OUT)  # set GPIO24 as an output
GPIO.setup(17, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)  # aggiungere tutti gli altri pin: 15 totali finali

gpioPin = [22, 17, 24, 23]  # aggiungerli anche qua
ser = serial.Serial('/dev/ttyACM0', 9600)
print('Reading MCP3008 values, press Ctrl-C to quit...')
print('partenza del ciclo di lettura della posizione')
print('-' * 57)
# Main program loop.
num = 0
count = 0
posPlayerX = -1
posPlayerY = -1
playerOnBoard = False
playerEndTurn = False
player = None
nemico = None
initPosX = 7
initPosY = 14
try:
    # accende led
    ser.write(str(
        initPosY * 15 + initPosX) + ",3")  # inizializzazione del giocatore: deve venir posizionato sulla casella 217, e nemico
    # manca battito rilevato
    while not playerOnBoard:
        for n, p in enumerate(gpioPin):
            GPIO.output(p, 1)
            # Read all the ADC channel values in a list.
            values = [0] * 8
            values2 = [0] * 7
            for i in range(8):
                # The read_adc function will get the value of the specified channel (0-7).
                values[i] = mcp.read_adc(i)
            for i in range(7):
                values2[i] = mcp2.read_adc(i)
            # Print the ADC values.
            # results = np.append(values, values2, axis=0)
            #    			print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*values))
            for i in range(len(values)):
                if values[i] > 1000:
                    print('{}{}{}{}'.format('sei in posizione ', i, ' , ', n))
                    num = i * 4 + n
                    print(str(i * 4 + n + 1))
                    posPlayerX = i
                    posPlayerY = n
            for i in range(len(values2)):
                if values2[i] > 1000:
                    print('{}{}{}{}'.format('sei in posizione ', i , ' , ', n + 8))
                    num = i * 4 + n
                    print(str(i * 4 + n + 1))
                    posPlayerX = i
                    posPlayerY = n
            if posPlayerX == initPosX and posPlayerY == initPosY:
                playerOnBoard = True
                player = Player(posPlayerX, posPlayerY)
                nemico = Enemy(posPlayerX, posPlayerY)
                ser.write(str(initPosY * 15 + initPosX) + ",5")  # spegne led
            GPIO.output(p, 0)
        time.sleep(0.1)
    #####################################################
    #   inserire controllo battito cardiaco             #
    #####################################################
    while True:  # gestione del turno giocatore
        count += 1
        nodes = nemico.getNodes()
        for n in nodes:
            if n[player.getX()][player.getY()].getPortal():
                playerEndTurn = True
                nemico.destroyPortal(player.getX(), player.getY())
            elif n[player.getX()][player.getY()].getManifestazione():
                playerEndTurn = True
                ######################################################################################
                # inserire prova sensori per risoluzione manifestazione e gestione evento             #
                ######################################################################################
                nemico.risolviManifestazione(player.getX(), player.getY())
            else:
                oldPosx = player.getX()
                oldPosy = player.getY()
                playerOnBoard = False
                ######################################################################################
                # inserire caso uso oggetto, riposo, cosra                                            #
                ######################################################################################
                for n, p in enumerate(gpioPin):
                    GPIO.output(p, 1)
                    # Read all the ADC channel values in a list.
                    values = [0] * 8
                    values2 = [0] * 7
                    for i in range(8):
                        # The read_adc function will get the value of the specified channel (0-7).
                        values[i] = mcp.read_adc(i)
                    for i in range(7):
                        values2[i] = mcp2.read_adc(i)
                    # Print the ADC values.
                    # results = np.append(values, values2, axis=0)
                    #    			print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*values))
                    for i in range(len(values)):
                        if values[i] > 1000:
                            playerOnBoard = True
                            print('{}{}{}{}'.format('sei in posizione ', i, ' , ', n))
                            num = i * 4 + n
                            print(str(i * 4 + n + 1))
                            posPlayerX = i
                            posPlayerY = n
                    for i in range(len(values2)):
                        if values2[i] > 1000:
                            playerOnBoard = True
                            print('{}{}{}{}'.format('sei in posizione ', i, ' , ', n + 8))
                            num = i * 4 + n
                            print(str(i * 4 + n + 1))
                            posPlayerX = i
                            posPlayerY = n
                            # Pause for half a second.
                    if playerOnBoard and (posPlayerX != oldPosx or posPlayerY != oldPosy):

                        #####################################################
                        #   inserire controllo validità casella             #
                        #####################################################
                        playerEndTurn = True
                    else:
                        #####################################################
                        #   controllo uso oggetto? riposo?                  #
                        #####################################################
                        playerEndTurn = False
                    time.sleep(0.05)
                    GPIO.output(p, 0)
        if playerEndTurn:
            playerEndTurn = False
            player.setX(posPlayerX)
            player.setY(posPlayerY)
            nemico.setMove()
            nemico.updatePlayerPos(player.getX(), player.getY())
            nemico.update()
            ser.write(str(nemico.getPos()))
        if count == 100:
            ser.flushInput()
            count = 0
except KeyboardInterrupt:  # trap a CTRL+C keyboard interrupt
    GPIO.cleanup()