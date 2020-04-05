import socket
import sys

# Create a UDP socket
import self

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_IP = "127.0.0.1"
server_PORT = 9090
# Bind the socket to the port
server_address = (server_IP, server_PORT)
sock.bind(server_address)
bytes_to_be_read = 4096
# how many messages has been send
sequence_number = 0
sock.settimeout(4)

"""
The Server is listing after incoming connection request (SYN) from the Client. If the Client tries to connect, 
the Server and Client do the handshake. It checks if the Clients SYN and IP matches the SYN-protocol and IP on the 
socket and sends a SYN-ACK in return if it passed. It then gets a ACK from the Client where it checks if the incoming 
ACK's address matches the SYN address and if the ACK matches the ACK-protocol, if it pass the Server informs the 
Client that handshake is approved. The Server then starts to listen after incoming message from the Client. If the 
handshake fails either with SYN or ACK the Client gets notified, and the Server close the socket and exit the program 
with 1 (something unexpected happen). 
"""


def handshake():
    try:
        receive_syn, (ip, port) = sock.recvfrom(bytes_to_be_read)
        print("C: " + receive_syn.decode())

        if receive_syn.decode() == "com-0 " + ip:
            syn_ack = "com-" + str(sequence_number) + " accept " + server_IP
            print("S: " + syn_ack)
            sock.sendto(syn_ack.encode(), (ip, port))

            receive_ack, address = sock.recvfrom(bytes_to_be_read)
            if address == (ip, port) and receive_ack.decode() == "com-0 accept":
                print("C: " + receive_ack.decode())
                handshake_approved = "Handshake approved!"
                sock.sendto(handshake_approved.encode(), (ip, port))
                return True

            # If the SYN_ACK check failed at Client. Client sends error message before closing the socket.
            # The Server then also close the socket and exit the program with 1 (something unexpected happen)
            elif receive_ack.decode() == "Invalid SYN_ACK. Closing Client":
                error_with_syn_ack_handshake = "Invalid SYN_ACK. Closing Server and Client"
                print("C: " + error_with_syn_ack_handshake)
                return False

            # If the ACK check fails, Server print and sends an error message to Client and close the socket.
            else:
                error_with_handshake_client = "Invalid ACK request. Closing Server"
                print("S: " + error_with_handshake_client)
                sock.sendto(error_with_handshake_client.encode(), address)
                return False

        # If the SYN check fails, Server print and sends an error message to Client and close the socket.
        else:
            error_with_handshake_client = "Invalid SYN. Closing Server"
            print("S: " + error_with_handshake_client)
            sock.sendto(error_with_handshake_client.encode(), (ip, port))

    # If there is no incoming connection request, SYN or ACK from Client
    except socket.timeout:
        print("No activity from client in handshake")

    except OSError as error:
        print("OS error: {0}".format(error))


"""
Function that sends an answer to Client, if Server receive a message from Client.
We need to add one to sequence_number because of the protocol and have the address of Client as an parameter
"""


def send_message(address):
    global sequence_number
    sequence_number += 1
    server_says = "res-" + str(sequence_number) + " = " + "I am server"
    sock.sendto(server_says.encode(), address)
    print("S: " + server_says)


"""
Function that receives a message from the Client. It gets the message and split on "-" and index 0 and get "msg", 
and then we want the sequence number where we split on " " and index 0 and get "msg-X", then split again with "-" and 
index 1 and get the sequence number. The sequence number must only be 0 on the first message Client sent, 
and to secure that there is the variable (first_message) that is only true the first time the while loop run. 
Thereafter the sequence number from the Client should be one larger than the Server's sequence number.
In the elif there is needed to add 1 to the sequence number so it is not falling behind in the sequence number
"""


def receive_message():
    """Try is for the exception that can happen and a finally that close the socket and give an exit code 1 that
    means something wrong happen """

    global sequence_number
    first_message = True
    while True:
        receive_message_from_client, address = sock.recvfrom(bytes_to_be_read)
        print("C: " + receive_message_from_client.decode())

        do_msg_match = receive_message_from_client.decode().split("-")[0]

        do_seg_number_match = receive_message_from_client.decode().split(" ")[0].split("-")[1]

        if do_msg_match.__eq__("msg") and do_seg_number_match.__eq__(str(sequence_number)) and first_message:
            first_message = False
            send_message(address)

        elif do_msg_match.__eq__("msg") and do_seg_number_match.__eq__(str(sequence_number + 1)) and not first_message:
            sequence_number += 1
            send_message(address)

        else:
            error_with_message_client = "msg protocol has an error. Closing the server"
            print("S: " + error_with_message_client)
            sock.sendto(error_with_message_client.encode(), address)
            return address


def main():
    try:
        if handshake():
            while True:
                address = receive_message()
                send_message(address)

    # If there is no messages from Client
    except socket.timeout:
        error_with_message_client = "con-res 0xFE"
        print("S: " + error_with_message_client)
        sock.sendto(error_with_message_client.encode(), address)

    except OSError as error:
        print("OS error: {0}".format(error))

    finally:
        sock.close()
        sys.exit(1)


if __name__ == "__main__":
        main()
