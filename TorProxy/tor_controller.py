import time
import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 9088
BUFFER_SIZE = 1024


def start_tor():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(b'start')
    data = s.recv(BUFFER_SIZE)
    s.close()
    print(str(data))


def restart_tor():
    stop_tor()
    time.sleep(1)
    start_tor()
    time.sleep(10)


def stop_tor():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(b'stop')
    data = s.recv(BUFFER_SIZE)
    s.close()
    print(str(data))
