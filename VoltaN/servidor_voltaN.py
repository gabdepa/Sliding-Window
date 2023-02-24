import socket
import time
import os

# Tamanho do buffer
BUFFER_SIZE = 128
SEQ_HEADER = 20

# Endereço e porta do servidor
SERVER_ADDRESS = ('localhost', 5000)

# Criação do socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Configura o socket como não bloqueante
sock.setblocking(False)

# Bind do socket com o endereço e porta do servidor
sock.bind(SERVER_ADDRESS)

# Escuta por conexões
sock.listen(1)

while True:
    try:
        conn, client_address = sock.accept()
        print("=> Conncection Established")
        break
    except BlockingIOError:
        pass
    except ConnectionResetError:
        print("Conexão encerrada pelo servidor.")

max_sequence = 7
expected_seq_num = 0
actual_seq = window_size = 3

# Recebimento dos dados
filename = 'arquivo_recebido.txt'
with open(filename, 'wb') as f:
    # Usada para monitorar a quantidade total de dados recebidos.
    received_data_size = 0
    data = conn.recv(BUFFER_SIZE*window_size + SEQ_HEADER) # Recebe os dados do cliente, eles serão armazenados na variável data.
    while True:
        try:         
            data_str = data.decode('utf-8') # Decode the data
            print("\n-------------------> ",data_str,"\n")
            if data_str != "":
                message = data_str.split(' - b')[1]
                # O tamanho do dado recebido é adicionado à variável received_data_size
                received_data_size += len(data)
                # dado recebido é gravado no arquivo criado anteriormente
                f.write(str(message).encode())
                # Imprime dados recebidos
                print(f"\n=> Expected Sequence Number: {int(expected_seq_num)} Data Received:\n {data_str}\n")
                print("MESSAGE: ", message)
                if b' - ' in data:
                    seq_num = data_str.split(' - ')[0]
                    seq_num = int(seq_num)
                    print("Sequence Number DECODED: ", seq_num)
                    if (seq_num > window_size):
                        actual_seq = seq_num+window_size
                        
                    if seq_num == expected_seq_num:
                        print(f"Sending {seq_num}:ACK, Expected={expected_seq_num}={seq_num}")
                        conn.send(f"{expected_seq_num}:ACK".encode('utf-8'))
                        expected_seq_num += 1
                    elif seq_num < expected_seq_num:
                        print(f"Sending {seq_num}:ACK, because {expected_seq_num}>{seq_num}")
                        conn.send(f"{seq_num}:ACK".encode('utf-8'))
                    else:
                        print(f"Sending {expected_seq_num}:NACK, received: {seq_num} | expected: {expected_seq_num}")
                        conn.send(f"{expected_seq_num}:NACK".encode('utf-8'))
            else: # Nenhum dado recebido, o loop é interrompido
                print(f"\n------> Received END of transmission, closing connection")
                break
            time.sleep(0.5)
            data = conn.recv(BUFFER_SIZE*window_size + SEQ_HEADER) # Recebe os dados do cliente, eles serão armazenados na variável data.
        # Caso ocorra uma exceção do tipo BlockingIOError ou KeyboardInterrupt, o código é direcionado para o bloco except
        except KeyboardInterrupt:
            # Nenhuma mensagem disponível no momento
            print("KeyBoard Interrupt toggled!")
            break
        except BlockingIOError:
            print("Blocking IO Error raised.")
            pass

    # Final dos dados, imprime tamanho total de dados recebidos.
    print(f"\nTotal received data size, without Sequence Headers: {received_data_size} bytes.")

# Finalização da conexão com o cliente
conn.close()
