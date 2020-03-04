import re
import socket
import sys

# Create a UDP socket
sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

udp_IP = "127.0.0.1"
udp_PORT = 9090
server_address = (udp_IP, udp_PORT)
bytes_to_be_read = 4096
# how many messages has been send
seg_number = 0


def send_message():
    global seg_number
    print("Write a message")
    message = input()
    message_to_server = "msg-" + str(seg_number) + " = " + message
    sock.sendto(message_to_server.encode(), server_address)
    print("C: " + message_to_server)
    receive_message()


def receive_message():
    try:
        global seg_number
        while True:
            receive_message_from_server, server_address = sock.recvfrom(bytes_to_be_read)
            print("S: " + receive_message_from_server.decode())

            do_res_match = re.findall(r'res', receive_message_from_server.decode())
            do_res_match_join = ' '.join(do_res_match)

            do_seg_number_match = re.findall(r'\d+', receive_message_from_server.decode())
            do_seg_number_match_join = ' '.join(do_seg_number_match)

            if do_res_match_join.__eq__("res") & do_seg_number_match_join.__eq__(str(seg_number + 1)):
                seg_number += 2
                send_message()

            else:
                error_with_message_server = "Invalid message. Closing the client"
                print("C: " + error_with_message_server)
                sock.sendto(error_with_message_server.encode(), server_address)
                return

    finally:
        sock.close()
        sys.exit(1)


def handshake():
    try:
        syn = "com-" + str(seg_number) + " " + udp_IP
        print("C: " + syn)
        sock.sendto(syn.encode(), server_address)

        receive, address = sock.recvfrom(bytes_to_be_read)
        print("S: " + receive.decode())
        if receive.decode() == "com-0 accept " + udp_IP:
            ack = "com-" + str(seg_number) + " accept"
            print("C: " + ack)
            sock.sendto(ack.encode(), server_address)
            send_message()

        else:
            error_with_handshake_server = "Invalid syn_ack. Closing the client"
            print("S: " + error_with_handshake_server)
            sock.sendto(error_with_handshake_server.encode(), address)
            return

    except socket.timeout:
        raise RuntimeError("No activity from server")

    finally:
        sock.close()
        sys.exit(1)


if handshake():
    send_message()
    receive_message()
