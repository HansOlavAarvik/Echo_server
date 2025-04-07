import socket

def receive_udp_data(ip_address="0.0.0.0", port=6000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (ip_address, port)
    print(f"Starting UDP server on {ip_address}:{port}")
    sock.bind(server_address)
    
    try:
        while True:
            # Receive data
            print("\nWaiting to receive message...")
            data, address = sock.recvfrom(4096)
            
            print(f"Received {len(data)} bytes from {address}")
            print(f"Data: {data.decode('utf-8', errors='replace')}")
    except KeyboardInterrupt:
        print("Server stopped by user")
    finally:
        sock.close()
        print("Socket closed")

if __name__ == "__main__":

    stm32_ip = "192.168.1.111"  # Replace with your STM32's static IP
    listen_port = 6002  # Replace with the port your STM32 is sending to

    receive_udp_data("0.0.0.0", listen_port)