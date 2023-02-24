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

# Abertura do arquivo
filename = "./testMessage.txt"

with open(filename, 'rb') as f:
    # Leitura do arquivo em pedaços
    data = f.read(BUFFER_SIZE)
    while data: # Enquanto houver dados a serem enviados
        try:
            sock.send(data) # Envio dos dados
            print("\n=> Enviando dados:\n", data.decode())

            confirmation = ""
            while confirmation != b"ACK": # Enquanto não receber a confirmação de recebimento
                confirmation = sock.recv(BUFFER_SIZE) # Armazena a mensagem recebida do servidor
                print("\n=> Confirmação recebida: ", confirmation.decode())

        except BlockingIOError:
            # Nenhuma mensagem disponível no momento
            print("Blocking Error!")
            pass

        # Leitura do próximo pedaço do arquivo
        data = f.read(BUFFER_SIZE)

    # Envio de um pacote vazio para indicar que todos os dados foram enviados
    sock.send(b"")


# Finalização da conexão com o servidor
time.sleep(1) # Espera 1 segundo antes de fechar a conexão
sock.close() # Fechamento da conexão
