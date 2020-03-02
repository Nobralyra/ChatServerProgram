import socket

# Create a UDP socket
sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

udp_IP = "127.0.0.1"
udp_PORT = 9090
server_address = (udp_IP, udp_PORT)
message = ""
bytes_to_be_read = 4096
# how many messages has been send
seg_number = 0


try:

    # Send data
    print('sending {!r}'.format(message))
    # uses sendto() to send messages to the server’s address.
    # sent = sock.sendto(message, server_address)

    # Receive response
    print('waiting to receive')
    # data, server = sock.recvfrom(bytes_to_be_read)
    # print('received {!r}'.format(data))

finally:
    print('closing socket')
    #sock.close()


def send_message():
    print("Write a message")
    message = input()
    message_to_server = "msg-" + str(seg_number) + "=" + message
    sock.sendto(message_to_server, server_address)


def receive_message():
    receive_message_server = sock.recvfrom(bytes_to_be_read)
    return receive_message_server


def handshake():
    while True:
        syn = "com-" + str(seg_number) + " " + udp_IP
        print("C: " + syn)
        syn_to_server = str.encode(syn)
        sock.sendto(syn_to_server, server_address)
        #print(syn.str.encode)

        receive = receive_message()
        if receive:
            message_from_server = receive[0].decode().split(" ", 1)


if handshake():
    send_message()
