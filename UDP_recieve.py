import socket
#import json
#import random
from data_process import handle_json_data

def udp_start_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #IPv4,  User Datagram Protocol
    server_adress =("0.0.0.0", 6002) #all ip's, port 6002
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) ## if already bound
    print(f"starting UPD on {server_adress}")
    sock.bind(server_adress)
    return sock, server_adress
    

def UDP_main():
    sock, server_adress = udp_start_socket()
    while True:
        data, address = sock.recvfrom(4096)
        try:
            handle_json_data(data, address)
        except:
            print(f"Error processing sensor data")
            print(f"Raw data: {data}")

