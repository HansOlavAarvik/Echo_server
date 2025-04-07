import socket
from data_process import handle_json_data
from div import log_setup, log

def udp_start_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #IPv4,  User Datagram Protocol
    server_address =("0.0.0.0", 6002) #all ip's, port 6002
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) ## if already bound
    log(f"Binding to UDP port {server_address[1]} to receive JSON data")
    sock.bind(server_address)
    return sock, server_address
    

def UDP_main():
    sock, server_adress = udp_start_socket()
    log_setup()
    while True:
        try:
            data, address = sock.recvfrom(4096)
            log(f"Received packet from {address[0]}:{address[1]}")
            log(data)
            handle_json_data(data, address)
        except Exception as e:
            log(f"Error in UDP receiver: {str(e)}")
            
