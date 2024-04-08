# Uncomment this to pass the first stage
import socket


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client_socket, client_address = server_socket.accept() # wait for client

    print(client_socket, client_address)
    with client_socket:
        data = client_socket.recvmsg(1024)
        print(data)
        client_socket.sendmsg([("HTTP/1.1 200 OK\r\n\r\n").encode()])


if __name__ == "__main__":
    main()
