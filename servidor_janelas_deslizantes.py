import socket
import time
import os

# Tamanho do buffer
BUFFER_SIZE = 1024

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


# Recebimento dos dados
filename = 'arquivo_recebido.txt'
with open(filename, 'wb') as f:
    received_data_size = 0 # Usada para monitorar a quantidade total de dados recebidos.
    while True:
        try:
            # Recebe os dados do cliente, caso exista dados recebidos, eles serão armazenados na variável data.
            data = conn.recv(BUFFER_SIZE)

            if data:
                received_data_size += len(data) # O tamanho do dado recebido é adicionado à variável received_data_size
                f.write(data) # dado recebido é gravado no arquivo criado anteriormente
                print("\n=> Recebendo dados:\n", data.decode()) # Imprime dados recebidos

                conn.send(b"ACK") # envia uma mensagem de confirmação de recebimento ao cliente usando o método send()

            else: # Nenhum dado recebido, o loop é interrompido
                break
        
        except BlockingIOError: # Caso ocorra uma exceção do tipo BlockingIOError, o código é direcionado para o bloco except 
            # Nenhuma mensagem disponível no momento
            print("No message at the moment..!")
            pass
    
    print(f"->> Total de dados recebidos: {received_data_size}") # Final dos dados, imprime tamanho total de dados recebidos


# Arquivo a ser recebido
file_to_send = "./testMessage.txt"

# Verifica se o tamanho do arquivo recebido é o mesmo que o tamanho do arquivo enviado
if os.path.getsize(filename) == os.path.getsize(file_to_send):
    print('->> Arquivo recebido com sucesso.')
else:
    print(f'->> Erro ao receber arquivo. Size: {os.path.getsize(filename)}')

# Fechamento da conexão
conn.close()
# Finalização da conexão com o cliente
sock.close()
