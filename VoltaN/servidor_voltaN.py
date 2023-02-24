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
    except ConnectionResetError:
        print("Conexão encerrada pelo servidor.")


# Recebimento dos dados
filename = 'arquivo_recebido.txt'
with open(filename, 'wb') as f:
    # Usada para monitorar a quantidade total de dados recebidos.
    received_data_size = 0
    while True:
        try:
            # Recebe os dados do cliente, caso exista dados recebidos, eles serão armazenados na variável data.
            data = conn.recv(BUFFER_SIZE)

            if data:
                if b"" in data:
                    data = data.replace(b"", b"-")

                if b"-" in data:
                    lines = data.split(b"-")
                    for line in lines[:-1]:
                        # O tamanho do dado recebido é adicionado à variável received_data_size
                        received_data_size += len(line)
                        # dado recebido é gravado no arquivo criado anteriormente
                        f.write(line)
                        # Imprime dados recebidos
                        print("\n=> Recebendo dados:\n", line.decode())
                        seq_num, data = line.split(b':', 1)
                        # envia uma mensagem de confirmação de recebimento ao cliente usando o método send()
                        conn.send(seq_num + b':ACK')
                    data = lines[-1]

            else:
                # Nenhum dado recebido, o loop é interrompido
                break
        # Caso ocorra uma exceção do tipo BlockingIOError ou KeyboardInterrupt, o código é direcionado para o bloco except
        except (BlockingIOError, KeyboardInterrupt):
            # Nenhuma mensagem disponível no momento
            print("No message at the moment..!")
            pass

    # Final dos dados, imprime tamanho total de dados recebidos.
    print(f"\nTotal received data size: {received_data_size} bytes.")

# Finalização da conexão com o cliente
time.sleep(1)
conn.close()
