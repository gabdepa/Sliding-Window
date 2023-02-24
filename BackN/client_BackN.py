import socket
import sys
import time

# Buffer Size
BUFFER_SIZE = 128

SERVER_ADDRESS = ('localhost', 5000) # Port and address of server

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket Creation

while True:
    try:
        sock.connect(SERVER_ADDRESS)
        print("=> Connection Established\n")
        break
    except ConnectionRefusedError:
        print("=> Connection refused by server")
        sys.exit(1)
    except BlockingIOError:
        time.sleep(1)
        pass
    except ConnectionResetError:
        print("=> Connection closed by server")

MAX_RETRIES = 3 # Maximum number of retries
TIMEOUT = 30  # 30 seconds
window_size = 3 # Size of the window
last_seq_num = seq_num = -1 # Initialization
start_time = time.time()  # Time of sending the window
retries = 0 # Initialization
data_size = 0 # Initialization
window_data = [] # List that hold the packets to send
flag = True # Auxiliar flag

filename = "./testMessage.txt" # Input file
with open(filename, 'rb') as f:
    while ((time.time() - start_time) < TIMEOUT) and flag == True :  # While there is data to be sent and time limit has not been reached
        for i in range(window_size): # Iterate from 0 to 2
            data = str(f.read(BUFFER_SIZE)) # Read the file until reaches BUFFER_SIZE as a string, and puts its result on "data"
            if (data == "b''"): # If read empty string, there is nothing more to read
                print("\nWINDOW PACKETS: ",window_data) # Print of the list of packets to be sent
                break
            else:
                seq_num = int(seq_num) + 1 # Increment the sequence number
                packet = str(seq_num) + " - " + data # Creating packet with sequence number
                packet = packet.encode() # Transform into bytes
                print(f"\n=> Sending Sequence Number: {seq_num} , Element {i} of window, Sending Data:\n {seq_num} - {data}") # Print of data in the window
                window_data.append(packet) # Append the packet to window
                data_size += len(packet) # Take its size and add to the total size sent
            
        if window_data != []: # Window still has packets to send
            for packet in window_data: # Send each packet in the window
                    try:
                        sock.send(packet) # Send the data
                        message = sock.recv(BUFFER_SIZE) # Store the server return message
                        if ":ACK".encode() in message: # Received ACK
                            print("\n=> Confirmation Received: ", message.decode('utf-8')) # Print of the confirmation
                            last_seq_num = seq_num # Last sequence is updated
                            rec_seq_num = message.decode().split(':')[0] # Take the received sequence number from message
                            print(f"RECEIVED ACK: {rec_seq_num}") # Print of the received sequence number
                            for i in window_data: # Iterate over the window packets
                                l = i.decode() # Decode the packet to see it's sequence number
                                if rec_seq_num in l.split(' - ')[0]: # If the number received in in the sequence number of the packet
                                    window_data.remove(i) # Here we take the packet that was ACK to server from the window
                            retries = 0  # Reset after success the retries
                            break # Ack received, break the loop
                        else: # Received NACK
                            retries += 1 # Increase the retrie of already sent packets
                            print("==> Receipt not confirmed: ", message.decode('utf-8')) # Print of NACK Received
                            rec_seq_num = message.decode().split(':')[0] # Take the received sequence number from message
                            for i in window_data: # Iterate over the window packets
                                seq_num = i.decode().split(' - ')[0] # Take the sequence number of the packet
                                if seq_num == rec_seq_num: # If it matches with the packet
                                    sock.send(i) # Send the packet again
                    except socket.timeout: # In case of timeout
                        retries += 1  # incrementa contador de tentativas
                        print(f"\nTimeout reached ({retries}/{MAX_RETRIES}), resending packet...") # Timeout reached, resend the packet
                        if retries > MAX_RETRIES:  # Reached the limit of retries
                            print("Maximum number of retries reached, connection lost.")
                            break  
        else: # Window lack of packets, there is nothing more to send
            print("\nWINDOW PACKETS: ",window_data)
            flag = False # Set the operation of sending to false  

print(f"Total Size of packages Sent: {data_size}")
print("All packets sent!\nClosing Socket")       
packet = '' # Empty String to be send
packet = packet.encode() # Transform packet to bytes
sock.send(packet) # Send packet
print("Signal to Close connection sent!") 
time.sleep(1)
sock.close() 
