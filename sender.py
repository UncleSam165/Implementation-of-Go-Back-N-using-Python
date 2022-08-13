import sys
import time
import random
from statistics import mean
from socket import *
import math
from matplotlib import pyplot as plt

pack_id = [0]

# Get the filename, receiver (host) IP address and receiver port as command line arguments
argv = sys.argv
filename = argv[1]
host = argv[2]
port = argv[3]

# test file 1 parameters: MSS = 604, N = 18, timeout = 0.1

MSS = 1460     # Maximum Segment Size (in bytes)
N = 10        # Window size (number of packets to send each time)
timeout = 0.1  # Timeout interval (in second)

# read from file
with open(filename, 'rb') as f:
    data = []
    # print("length of the file".format(len(f.read())))
    print('number of packets is ' + str(math.ceil(len(f.read()) / MSS)))
    f.seek(0)

    while True:
        buf = f.read(MSS)
        if not buf:
            break
        data.append(buf.decode("utf-8"))

# Create UDP client socket
# The use of SOCK_DGRAM for UDP datagram packet
startTime = time.time()
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Set socket timeout
clientSocket.settimeout(timeout)

# Command line argument is a string, change the port into integer
port = int(port)

# Send base and next sequence number
send_base = 0
next_seq_num = 0
print('number of packets is '+ str(len(data)))


while send_base <= len(data):

    # If the next_seq_num is within the window of size N
    if next_seq_num < send_base + N:   # send packet next_seq_num

        # Simulating packet loss with a 10% probability
        nm = random.randint(1, 10)

        if nm == 1:   # The packet will 100% get lost
            next_seq_num += 1
            continue

        # The number of packets
        payload = len(data)

        # If it's not the first packet (containing the number of packets)
        if next_seq_num != 0:

            # If next_seq_num overflows, make it equal to len(data)
            if next_seq_num > len(data):
                next_seq_num = len(data)

            payload = data[next_seq_num-1]

        # If it's the first packet: payload = len(data) ,
        # if not: payload =  data[next_seq_num-1]
        packet = str(next_seq_num) + '\r\n' + str(payload)

        # Send the packet
        clientSocket.sendto(packet.encode(), (host, port))
        print('packet # ' + str(next_seq_num) +' sent successfully')
        next_seq_num += 1

        #time.sleep(0.010)

    try:
        # Receive the ACK

        #timeout_start = time.time()
        #time.sleep(0.1)
        message, address = clientSocket.recvfrom(2048)
        n = message.decode().split(" ")[1]
        pack_id.extend(list(range(pack_id[-1], int(n)+1)))
        # i = 1
        # while time.time() < timeout_start + 0.01:
        #    message, address = clientSocket.recvfrom(2048)
        #    n = message.decode().split(" ")[1]
        #    i += 1

        print('ack # '+ n +' received successfully')
        send_base = int(n) + 1

    except OSError:
        print("Request timed out.")
        # send packet send_base
        # send packet send_base+1
        # send packet next_seq_num-1
        for i in range(send_base, next_seq_num):
            payload = len(data)
            if i != 0:
                payload = data[i-1]

            packet = str(i) +'\r\n'+ str(payload)
            clientSocket.sendto(packet.encode(), (host, port))
            print('packet # ' +str(i)+' sent successfully')
        continue

# Close the client socket
clientSocket.close()
transmissionDuration = time.time() - startTime
rate = len(open(filename, 'r').read())/transmissionDuration;
print('Transmission of ' + filename + ' took: ' + str(transmissionDuration) + ' second')
print('Transmission rate = ' + str(rate/1000) + ' KB/s')
plt.plot(pack_id)
plt.xlabel("Time Step")
plt.ylabel("Received Packet")
plt.title("Transmission Timeline")
plt.show()
