import sys
import config
import network
from time import sleep

connection = network.WLAN(network.STA_IF)


def connect():

    if connection.isconnected():
        print("Already connected")
        return
    
    try:
        connection.active(True)
        connection.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

        retry = 0
        while not connection.isconnected():  # wait until connection is complete
            if retry == 15:  # try 10 times
                sys.exit("Could not establish connection, check your settings")
            retry += 1

            print(retry)

            sleep(1)  # check again in a sec

        # no exit, we have a connection!
        print("Connection established")

    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    connect()