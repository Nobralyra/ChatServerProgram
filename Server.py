import re
import socket
import sys

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
sock.settimeout(10000)

"""
Function that sends an answer to the client, if the server receive a message from the client.
We need to add one to seg_number because of the protocol and have the address of the client as an parameter"""


def send_message(address):
    global seg_number
    seg_number += 1
    server_says = "res-" + str(seg_number) + " = " + "I am server"
    sock.sendto(server_says.encode(), address)
    print("S: " + server_says)


"""Function that receives a message from the client and have address as an parameter because we send a message to the 
client if there was an timeout """


def receive_message():
    """Try is for the exception that can happen and a finally that close the socket and give an exit code 1 that
    means something wrong happend """
    try:
        global seg_number
        first_message = True
        while True:
            receive_message_from_client, address = sock.recvfrom(bytes_to_be_read)
            print("C: " + receive_message_from_client.decode())

            do_msg_match = re.findall(r'msg', receive_message_from_client.decode())
            do_msg_match_join = ' '.join(do_msg_match)
            do_seg_number_match = re.findall(r'\d+', receive_message_from_client.decode())
            do_seg_number_match_join = ' '.join(do_seg_number_match)

            if do_msg_match_join.__eq__("msg") and do_seg_number_match_join.__eq__(str(seg_number)) and first_message:
                first_message = False
                send_message(address)

            elif do_msg_match_join.__eq__("msg") & do_seg_number_match_join.__eq__(str(seg_number + 1)) and not first_message:
                seg_number += 1
                send_message(address)

            else:
                error_with_message_client = "msg protocol has an error. Closing the server"
                print("S: " + error_with_message_client)
                sock.sendto(error_with_message_client.encode(), address)
                sock.gettimeout()
                return

    except socket.timeout:
        timeout_server = "No activity from client"
        print(timeout_server)


    except OSError as error:
        print("OS error: {0}".format(error))

    finally:
        sock.close()
        sys.exit(1)


def handshake():
    try:
        receive_syn, address = sock.recvfrom(bytes_to_be_read)
        print("C: " + receive_syn.decode())
        if receive_syn.decode() == "com-0 " + server_IP:
            syn_ack = "com-" + str(seg_number) + " accept " + server_IP
            print("S: " + syn_ack)
            sock.sendto(syn_ack.encode(), address)

            receive_ack, address = sock.recvfrom(bytes_to_be_read)
            print("C: " + receive_ack.decode())
            if receive_ack.decode() == "com-0 accept":
                receive_message()

            else:
                return
        else:
            error_with_handshake_client = "Invalid syn or ack request. Closing the server"
            print("S: " + error_with_handshake_client)
            sock.sendto(error_with_handshake_client.encode(), address)
            sock.gettimeout()

    # If there is no reply from the server or the handshake did not go well
    except socket.timeout:
        print("No activity from client in handshake")

    except OSError as error:
        print("OS error: {0}".format(error))

    finally:
        sock.close()
        sys.exit(1)


if handshake():
    receive_message()
