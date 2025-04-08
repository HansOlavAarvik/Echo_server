import socket
from data_process import handle_json_data, handle_audio_data
from div import log_setup, log

def udp_start_json_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #IPv4,  User Datagram Protocol
    server_address =("0.0.0.0", 6002) #all ip's, port 6002
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) ## if already bound
    log(f"Binding to UDP port {server_address[1]} to receive JSON data")
    sock.bind(server_address)
    return sock, server_address

def udp_start_audio_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address =("0.0.0.0", 6001) #all ip's, port 6002
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) ## if already bound
    log(f"Binding to UDP port {server_address[1]} to receive Audio data")
    sock.bind(server_address)
    return sock, server_address

def UDP_main_json():
    sock_json, server_adress_json = udp_start_json_socket()

    log_setup()
    while True:
        try:
            json_data, address_json = sock_json.recvfrom(4096)
            #log(f"Received packet from {address[0]}:{address[1]}")
            #log(json_data)
            handle_json_data(json_data, address_json)
        except Exception as e:
            log(f"Error in UDP receiver: {str(e)}")

def UDP_main_audio():
    sock_audio, server_adress_audio = udp_start_audio_socket()
    while True:
        try:
            audio_data, address_audio = sock_audio.recvfrom(4096)
            #log(f"Received packet from {address_audio[0]}:{address_audio[1]}")
            #log(audio_data)
            handle_audio_data(audio_data, address_audio)
        except Exception as e:
            log(f"Error in UDP receiver: {str(e)}")