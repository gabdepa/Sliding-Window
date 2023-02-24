import socket
import sys
import time

# Tamanho do buffer
BUFFER_SIZE = 1024

# Endereço e porta do servidor
SERVER_ADDRESS = ('localhost', 5000)

# Criação do socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while True:
    try:
        # Tenta se conectar ao servidor
        sock.connect(SERVER_ADDRESS)
        print("=> Conncection Established\n")
        break
    except BlockingIOError:
        # Se ainda não for possível conectar, espera 1 segundo e tenta novamente
        time.sleep(1)
        pass
    except ConnectionResetError:
        print("Conexão encerrada pelo servidor.")


# Abertura do arquivo
filename = "./testMessage.txt"
seq_num = 0

with open(filename, 'rb') as f:
    data = f.read(BUFFER_SIZE) # Leitura do arquivo em pedaços de BUFFER_SIZE
    
    while data: # Enquanto houver dados a serem enviados
        try:
            packet = str(seq_num).encode() + b':' + data # Empacotamento dos dados com o número de sequência
            while True: # Espera pela confirmação de recebimento do servidor
                sock.settimeout(5) # Define o timeout como 2 segundo para que o loop possa ser interrompido para reenviar pacotes
                try:
                    print("\n=> Enviando dados:\n", data.decode())
                    sock.send(packet) # Envio dos dados         
                    confirmation = sock.recv(BUFFER_SIZE) # Armazena a mensagem recebida do servidor
                    if confirmation == str(seq_num).encode() + b':ACK':
                        print("\n=> Confirmação recebida: ", confirmation.decode())
                        last_seq_num = seq_num # Atualiza o último número de sequência confirmado
                        seq_num+=1 # Incrementa o número de sequência
                        break # Confirmação recebida, interrompe o loop
                    elif not confirmation:
                        print("Conexão encerrada pelo servidor.")
                        break
                except sock.timeout:
                    print("\nTimeout atingido, reenviando pacote...") # Timeout atingido, reenvia o pacote
        except BlockingIOError:
            print("Nenhuma mensagem disponível!") # Nenhuma mensagem disponível no momento
            time.sleep(1)
            pass
            
        data = f.read(BUFFER_SIZE)
    packet = b""
    sock.send(packet)
            
            
# Finalização da conexão com o servidor
time.sleep(1) # Espera 1 segundo antes de fechar a conexão
sock.close() # Fechamento da conexão

       

