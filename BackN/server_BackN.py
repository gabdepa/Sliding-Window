import socket
import time
import os

# Buffer Size
BUFFER_SIZE = 128
SEQ_HEADER = 20

SERVER_ADDRESS = ('localhost', 5000) # Port and address of server

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket Creation

sock.setblocking(False) # Configure socket as non-blocking

sock.bind(SERVER_ADDRESS) # Bind of socket with port and server address

sock.listen(1) # Listen for connection

while True:
    try:
        conn, client_address = sock.accept()
        print("=> Conncection Established")
        break
    except BlockingIOError:
        pass
    except ConnectionResetError:
        print("Conexão encerrada pelo servidor.")

max_sequence = 7 # Initialization
expected_seq_num = 0 # Initialization
actual_seq = window_size = 3 # Initialization
received_data_size = 0 # Initialize the size of received data

filename = 'data_received.txt' # Output file
with open(filename, 'wb') as f:
    data = conn.recv(BUFFER_SIZE*window_size + SEQ_HEADER) # Receive the data send and stores it on data variable.
    while True:
        try:         
            data_str = data.decode('utf-8') # Decode the data to string
            if data_str != "": # If don't receive empty string
                message = data_str.split(' - b')[1] # Split the data to separate message from sequence number(seq_num), here we take the message
                received_data_size += len(data) # The size of data received is added to received_data_size
                f.write(str(message).encode()) # The data received is written to the file opened before
                print(f"\n=> Expected Sequence Number: {int(expected_seq_num)} Data Received:\n {data_str}\n") # Print of received Data
                seq_num = data_str.split(' - ')[0] # Split the data to separate message from sequence number(seq_num), here we take the sequence number
                seq_num = int(seq_num) # Convert it to a number
                print("Sequence Number DECODED: ", seq_num) # Print of the received sequence number
                if (seq_num > window_size): # If the received sequence number is higher than the window_size
                    actual_seq = seq_num  # We take the sequence number as window size
                    
                if seq_num == expected_seq_num: # If sequence number is equal to our expected sequence
                    print(f"Sending {expected_seq_num}:ACK, Expected={expected_seq_num}={seq_num}") # Print of Send ack
                    conn.send(f"{expected_seq_num}:ACK".encode('utf-8')) # Send ack
                    expected_seq_num += 1 # Increase the expected sequence number
                elif seq_num < expected_seq_num: # If sequence number is lower to our expected sequence
                    print(f"Sending {seq_num}:ACK, because {expected_seq_num}>{seq_num}") # Print of Send ack
                    conn.send(f"{seq_num}:ACK".encode('utf-8')) # Send ack
                else: # The sequence number is higher than our expected sequence
                    print(f"Sending {expected_seq_num}:NACK, received: {seq_num} | expected: {expected_seq_num}") # Print of send NACK
                    conn.send(f"{expected_seq_num}:NACK".encode('utf-8')) # Send Nack
            else: # Received empty string
                print(f"\n------> Received END of transmission, closing connection") 
                break # Breakout of the loop
            time.sleep(0.5)
            data = conn.recv(BUFFER_SIZE*window_size + SEQ_HEADER) # Receive the data send and stores it on data variable.
        except KeyboardInterrupt: # Exception of closing the program
            print("KeyBoard Interrupt toggled!")
            break
        except BlockingIOError: # Exception of blocking socket
            print("Blocking IO Error raised.")
            pass

    print(f"\nTotal received data size, without Sequence Headers: {received_data_size} bytes.") # Print the size of the total data received

conn.close() # Closing connection
