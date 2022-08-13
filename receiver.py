from socket import *


# Defining Ack Function
def ack(seq_number, address):
    receiverSocket.sendto(('Ack ' + str(seq_number)).encode(), address)


# Create a UDP client socket
# (AF_INET is used for IPv4 protocols) (SOCK_DGRAM is used for UDP)
receiverSocket = socket(AF_INET, SOCK_DGRAM)

# Bind IP address and port number to the socket
receiverPort = 12000
receiverSocket.bind(('', receiverPort))

numberOfPackets = 0 # A variable to store the received number of  packets to be transmitted

# Loop to assure the reception of seq 0
while True:
    try:
        # Receiving the packet
        message, source = receiverSocket.recvfrom(2048)

        # Extracting the sequence number and the data
        seqNumber = int(message.decode().split('\r\n')[0])
        data = message.decode().split('\r\n')[1]
        print('Number of packets to be received is '+data)

        # Checking if it is the expected datagram
        if seqNumber == 0:
            # Storing the the received number of  packets to be transmitted
            numberOfPackets = int(data)
            # Acknowledging the received datagram
            ack(seqNumber, source)
            # Breaking the while loop to start the reception of the actual data
            break
        else:
            print('Seq 0 not received\n')
    except IOError:
        print('Error in receiving Seq 0\n')


counter = 1  # Counter to keep track of the expected sequence nuumber and to terminate the While Loop
data = ''   # A container to store the received text

# Loop to receive the file packets
while counter <= numberOfPackets:
    try:
        # Receiving the packet
        message, source = receiverSocket.recvfrom(2048)

        # Extracting the sequence number
        seqNumber = int(message.decode().split('\r\n')[0])

        # Checking if it is the expected datagram
        if seqNumber == counter:
            # Extracting the text
            data += '\r\n'.join(message.decode().split('\r\n')[1:])
            # Acknowledging the packet
            ack(counter, source)
            # incrementing the counter
            counter += 1
            print('Packet ' + str(seqNumber) + ' received successfully') # with payload: ' + '\r\n'.join(message.decode().split('\r\n')[1:]))
        else:  # If an out of order packet is received
            print('Packet ' + str(seqNumber) + ' arrived out of order')
            # Acknowledging the last in order packet received
            ack(counter - 1, source)
    except IOError:
        print('Error in receiving packet')

text_file = open("ReceivedText.txt", "a")
n = text_file.write(data)
text_file.close()
receiverSocket.close()