import socket


# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_IP = "127.0.0.1"
server_PORT = 9090
# Bind the socket to the port
server_address = (server_IP, server_PORT)
sock.bind(server_address)
bytes_to_be_read = 4096
# how many messages has been send
seg_number = 0

print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

def receive_syn_message():

    receive_message_server = sock.recvfrom(bytes_to_be_read)
    return receive_message_server


def receive_message():
    while True:
        receive = receive_syn_message()
        if receive:
            message_from_client = receive[0].decode().split(" ", 1)




def handshake():
    while True:
        receive = receive_syn_message()

        if receive:
            message_from_client = receive[0].decode().split(" ", 1)


    # When a message arrives, we proceed to read it with recvfrom(4096) , where 4096 is the number of bytes to be
    # read, and unpack the return value in to data and address
    data, address = sock.recvfrom(bytes_to_be_read)

    print('received {} bytes from {}'.format(len(data), address))
    print(data)

    if data:
        serverSays = b"I am server"
        sent = sock.sendto(serverSays, address)
        print('sent {} bytes back to {}'.format(sent, address))


if(handshake()):
    receive_message()
