import multiprocessing
import socket
import sys

import yaml
from timeloop import Timeloop
from datetime import timedelta

# Create a UDP socket
sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp_IP = "127.0.0.1"
udp_PORT = 9090
server_address = (udp_IP, udp_PORT)
bytes_to_be_read = 4096
# how many messages has been send
sequence_number = 0
true_or_false = None
value_from_config = None
is_send_message = False

"""The Client starts the handshake with the Server with a connection request (SYN), and gets a SYN-ACK in return from 
Server. Client send a ACK to the Server and gets a handshake approved if it passed. Client then goes to send_message(
). If there is problem with one of the steps in the handshake the Client close the socket and exit the program with 1 
(something unexpected happen) """


def handshake():
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
            return True

        # If the ACK check fails at Server, Client print and sends an error message to the Server and close the
        # socket.
        else:
            error_with_ack_handshake = "Invalid ACK request. Closing Server and Client"
            print("S: " + error_with_ack_handshake)
            return False

    # If the SYN check failed at Server. Server sends an error message to Client and close the socket. The Client
    # gets the error message and also close the socket
    elif receive.decode() == "Invalid SYN. Closing Server":
        error_with_syn_handshake = "Invalid SYN. Closing Server and Client"
        print("S: " + error_with_syn_handshake)
        return False

    # If the SYN_ACK check fails, Client print and sends an error message to Server and close the socket.
    else:
        error_with_syn_ack_handshake = "Invalid SYN_ACK. Closing Client"
        print("S: " + error_with_syn_ack_handshake)
        sock.sendto(error_with_syn_ack_handshake.encode(), address)
        return False


"""
Function that reads the input from the console and sends a message to Server. We need to add one to sequence_number
because of the protocol and have the address of Client as an parameter
Sets the is_send_message to True because there has been send a manual message
"""


def send_message():
    global sequence_number
    global is_send_message
    print("Write a message")
    message = input()
    message_to_server = "msg-" + str(sequence_number) + " = " + message
    sock.sendto(message_to_server.encode(), server_address)
    print("C: " + message_to_server)
    is_send_message = True
    return


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

    global sequence_number

    while True:
        receive_message_from_server, server_address = sock.recvfrom(bytes_to_be_read)
        print("S: " + receive_message_from_server.decode())

        do_res_match = receive_message_from_server.decode().split("-")[0]

        # When the server is closing it sends af 0xFe
        if receive_message_from_server.decode().__eq__("0xFE"):
            tolerance_message = "0xFF"
            print("C: " + tolerance_message)
            sock.sendto(tolerance_message.encode(), server_address)
            return False

        # If it the server closes because of to many packages
        if receive_message_from_server.decode().__eq__("Limit exceeded with maximum packages per seconds"):
            return False

        # If it the server closes because msg protocol is wrong or heartbeat
        if receive_message_from_server.decode().__eq__("msg protocol has an error. Closing the server"):
            raise ConnectionResetError

        do_seg_number_match = receive_message_from_server.decode().split(" ")[0].split("-")[1]

        if receive_message_from_server.decode().__eq__("con-a"):
            return True

        if do_res_match.__eq__("res") and do_seg_number_match.__eq__(str(sequence_number + 1)):
            sequence_number += 2
            return True

        else:
            error_with_message_server = "Invalid message. Closing the client"
            print("C: " + error_with_message_server)
            sock.sendto(error_with_message_server.encode(), server_address)
            return False


def main():
    """Try is for the exception that can happen and a finally that close the socket and give an exit code 1 that
    means something wrong happen """
    try:
        read_heartbeat()

        """If the KeepALive value is None then raise ValueError"""
        if true_or_false is None:
            raise ValueError

        """Check if the heartbeat should start or not"""
        if true_or_false.__eq__("True"):
            time_loop_heartbeat.start(block=False)

        read_DDoS()
        """If the package_per_seconds value is bigger than 0 then run DDOS"""
        if isinstance(package_per_seconds, int) and not None and package_per_seconds > 0:
            DDoS_job(package_per_seconds)

        while True:
            send_message()

            """When we get the 0xFE from the server and sends a 0xFF back, we do not receive an answer 
            because the server already has closed the socket"""
            if not receive_message():
                break

    except OSError as oSError:
        print("OS error: {0}".format(oSError))

    except yaml.YAMLError as yamlError:
        if hasattr(yamlError, 'problem_mark'):
            mark = yamlError.problem_mark
            print("YAML error: {0}".format(yamlError))
            print("Error position: (%s:%s)" % (mark.line + 1, mark.column + 1))

    except KeyError as keyError:
        print("Key error: {0}".format(keyError))

    except ValueError as valueError:
        print("Value error: {0}".format(valueError))

    except TypeError as typeError:
        print("Type error: {0}".format(typeError))

    except ConnectionResetError as connectionResetError:
        print("ConnectionReset error: {0}".format(connectionResetError))

    except RuntimeError as runTimeError:
        print("RuntimeError error: {0}".format(runTimeError))

    finally:
        time_loop_heartbeat.stop()
        sock.close()
        sys.exit(1)


""" Reads the config file and return the values from it"""


def load_config_file():
    global value_from_config
    with open('opt.conf') as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        value_from_config = yaml.load(file, Loader=yaml.FullLoader)
        return value_from_config


"""Gets the value of KeepALive value from the load_config_file"""


def read_heartbeat():
    global true_or_false
    load_config_file()
    true_or_false = value_from_config["Heartbeat"]["KeepALive"]
    print(true_or_false)
    return true_or_false


"""Gets the value of PackagePerSeconds value from the load_config_file"""


def read_DDoS():
    global package_per_seconds
    load_config_file()
    package_per_seconds = value_from_config["DDoS"]["PackagePerSeconds"]
    print(package_per_seconds)
    return package_per_seconds

time_loop_heartbeat = Timeloop()

"""Make the DDOS with multiprocessing"""

def DDoS_job(package_per_seconds):
    global sequence_number
    global server_address

    """For loop that iterates over the number of package_per_seconds"""
    for i in range(package_per_seconds):
        ddos_to_server = "msg-" + str(sequence_number) + " = " + "message"
        print("C: " + ddos_to_server)

        p = multiprocessing.Process(target=sock.sendto, args=(ddos_to_server.encode(), server_address))
        p.start()

        """Get the answer back from server - if receive_message return False then the server has shutdown"""
        if not receive_message():
            return


"""Timeloop of heartbeat that every 3 seconds checks if there has been send a message, and if not, then sends a heartbeat"""

@time_loop_heartbeat.job(interval=timedelta(seconds=3))
def heartbeat_job_every_3s():
    global server_address
    global is_send_message

    if is_send_message.__eq__(False):
        heartbeat = "con-h 0x00"
        print("C: " + heartbeat)
        sock.sendto(heartbeat.encode(), server_address)

        """Get the answer back from server - if receive_message return False then the server has shutdown"""
        if not receive_message():
            raise

        """Resets the is_send_message after 3 seconds if there has been send a manual messages"""
    else:
        is_send_message = False


if __name__ == "__main__":
    if handshake():
        main()

"""
     configParser = configparser.RawConfigParser()
     configParser.read('opt.ini')
     true_or_false = configParser.get('HEARTBEAT', 'KeepALive')
     if true_or_false.__eq__("True"):
         time_loop.start(block=False)
"""
