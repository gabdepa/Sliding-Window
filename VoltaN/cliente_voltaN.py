import socket
import sys
import time

# Tamanho do buffer
BUFFER_SIZE = 512

# Endereço e porta do servidor
SERVER_ADDRESS = ('localhost', 5000)

# Criação do socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while True:
    try:
        # Tenta se conectar ao servidor
        sock.connect(SERVER_ADDRESS)
        print("=> Connection Established\n")
        break
    except ConnectionRefusedError:
        # Caso a conexão seja recusada pelo servidor, termina o loop e encerra o programa
        print("=> Connection refused by server")
        sys.exit(1)
    except BlockingIOError:
        # Se ainda não for possível conectar, espera 1 segundo e tenta novamente
        time.sleep(1)
        pass
    except ConnectionResetError:
        print("=> Connection closed by server")

MAX_RETRIES = 3
TIMEOUT = 30  # 30 segundos, meio minuto
window_size = 3
max_sequence = 7
last_seq_num = seq_num = -1
start_time = time.time()  # tempo de início do envio dos pacotes
retries = 0
data_size = 0
window_data = [] # List that hold the window data

# Abertura do arquivo
filename = "./testMessage.txt"
with open(filename, 'rb') as f:
    while (time.time() - start_time) < TIMEOUT:  # Enquanto houver dados a serem enviados e o tempo limite não foi atingido
        
        for i in range(window_size):
            data = str(f.read(BUFFER_SIZE))
            if (data == "b''"):
                # Send packet indicating the sequence has finished
                packet = ''
                packet = packet.encode()
                sock.send(packet)     
                break 
            seq_num = int(seq_num) + 1
            packet = str(seq_num) + " - " + data # Creating packet with sequence number
            packet = packet.encode()
            print(f"\n=> Sending Sequence Number: {seq_num} , Element {i} of window, Sending Data:\n {seq_num} - {data}")
            window_data.append(packet)            
            data_size += len(packet)              
            
        if (window_data != []):
            for packet in window_data: # Envia cada pacote da janela
                while True: # Espera pela confirmação de recebimento do servidor
                    try:
                        
                        sock.send(packet) # Envio dos dados
                        message = sock.recv(BUFFER_SIZE) # Armazena a mensagem recebida do servidor
                        if ":ACK".encode() in message:
                            print("\n=> Confirmation Received: ", message.decode('utf-8'))
                            last_seq_num = seq_num
                            rec_seq_num = message.decode().split(':')[0]
                            print(f"RECEIVED ACK: {rec_seq_num}")
                            print("SEQUENCE_NUMBER = ", seq_num)
                            for i in window_data:
                                l = i.decode()
                                if rec_seq_num in l.split(' - ')[0]:
                                    window_data.remove(i) 
                            retries = 0  # reseta contador de tentativas após sucesso
                            print("\n----------WINDOW PACKETS AFTER ACK: ",window_data, "\n")
                            break # Confirmação recebida, interrompe o loop
                        else:
                            print("==> Receipt not confirmed: ", message.decode('utf-8'))
                            rec_seq_num = message.decode().split(':')[0]
                            print(rec_seq_num)
                            for i in window_data:
                                seq_num = i.decode().split(' - ')[0]
                                if seq_num == rec_seq_num:
                                    sock.send(i) 
                            retries += 0  # reseta contador de tentativas após sucesso
                            print("\n---------WINDOW PACKETS AFTER NACK: ",window_data, "\n")

                        time.sleep(1)
                    except socket.timeout:
                        retries += 1  # incrementa contador de tentativas
                        print(f"\nTimeout reached ({retries}/{MAX_RETRIES}), resending packet...") # Timeout atingido, reenvia o pacote
                        if retries > MAX_RETRIES:  # atingiu o limite de tentativas
                            print("Maximum number of retries reached, connection lost.")
                            break  
        else:
            print("\nWINDOW PACKETS: ",window_data)
            print(f"Total Size of packages Sent: {data_size}")
            print("All packets sent!\nClosing Socket")
            sock.close() 
            break           
    

