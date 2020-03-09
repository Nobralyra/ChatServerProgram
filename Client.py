import socket
import sys

# Create a UDP socket
sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp_IP = "127.0.0.1"
udp_PORT = 9090
server_address = (udp_IP, udp_PORT)
bytes_to_be_read = 4096
# how many messages has been send
sequence_number = 0


"""The Client starts the handshake with the Server with a connection request (SYN), and gets a SYN-ACK in return from 
Server. Client send a ACK to the Server and gets a handshake approved if it passed. Client then goes to send_message(
). If there is problem with one of the steps in the handshake the Client close the socket and exit the program with 1 
(something unexpected happen) """


def handshake():
    try:
        syn = "com-" + str(sequence_number) + " " + udp_IP
        print("C: " + syn)
        sock.sendto(syn.encode(), server_address)

        receive, address = sock.recvfrom(bytes_to_be_read)
        print("S: " + receive.decode())
        if receive.decode() == "com-0 accept " + udp_IP:
            ack = "com-" + str(sequence_number) + " accept"
            print("C: " + ack)
            sock.sendto(ack.encode(), server_address)

            receive_approved, address = sock.recvfrom(bytes_to_be_read)
            if receive_approved.decode() == "Handshake approved!":
                send_message()

            # If the ACK check fails at Server, Client print and sends an error message to the Server and close the
            # socket.
            else:
                error_with_ack_handshake = "Invalid ACK request. Closing Server and Client"
                print("S: " + error_with_ack_handshake)
                sock.close()
                sys.exit(1)

        # If the SYN check failed at Server. Server sends an error message to Client and close the socket. The Client
        # gets the error message and also close the socket
        elif receive.decode() == "Invalid SYN. Closing Server":
            error_with_syn_handshake = "Invalid SYN. Closing Server and Client"
            print("S: " + error_with_syn_handshake)
            return

        # If the SYN_ACK check fails, Client print and sends an error message to Server and close the socket.
        else:
            error_with_syn_ack_handshake = "Invalid SYN_ACK. Closing Client"
            print("S: " + error_with_syn_ack_handshake)
            sock.sendto(error_with_syn_ack_handshake.encode(), address)
            return


    #except socket.timeout: Not working as attended
        #raise RuntimeError("No activity from server")

    finally:
        sock.close()
        sys.exit(1)


"""
Function that reads the input from the console and sends a message to ServerWe need to add one to sequence_number because of the protocol and have the address of Client as an parameter
"""


def send_message():

    global sequence_number
    print("Write a message")
    message = input()
    message_to_server = "msg-" + str(sequence_number) + " = " + message
    sock.sendto(message_to_server.encode(), server_address)
    print("C: " + message_to_server)
    receive_message()


"""
Function that receives a message from the Server. It gets the message and split on "-" and index 0 and get "res", 
and then we want the sequence number where we split on " " and index 0 and get "res-X", then split again with "-" and 
index 1 and get the sequence number. The sequence number from the Server should be one larger than the Client's 
sequence number. 
Then it is needed to add 2 to the sequence number so it is not falling behind in the sequence number
"""


def receive_message():
    """Try is for the exception that can happen and a finally that close the socket and give an exit code 1 that
    means something wrong happen """
    try:
        global sequence_number
        while True:
            receive_message_from_server, server_address = sock.recvfrom(bytes_to_be_read)
            print("S: " + receive_message_from_server.decode())

            do_res_match = receive_message_from_server.decode().split("-")[0]

            do_seg_number_match = receive_message_from_server.decode().split(" ")[0].split("-")[1]

            if do_res_match.__eq__("res") and do_seg_number_match.__eq__(str(sequence_number + 1)):
                sequence_number += 2
                send_message()

            else:
                error_with_message_server = "Invalid message. Closing the client"
                print("C: " + error_with_message_server)
                sock.sendto(error_with_message_server.encode(), server_address)
                return

    finally:
        sock.close()
        sys.exit(1)


if handshake():
    send_message()
    receive_message()
