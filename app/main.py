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
        data, _, _, _  = client_socket.recvmsg(1024)
        data = data.decode()
        request_path = extract_headers(data)
        print("Request path: ", request_path)
        if(request_path=="/"):
            client_socket.sendmsg([("HTTP/1.1 200 OK\r\n\r\n").encode()])
        else:
            client_socket.sendmsg([("HTTP/1.1 404 Not Found\r\n\r\n").encode()])

def extract_headers(header_string:str) -> str:
    header_lines = header_string.split("\r\n")
    start_line = header_lines[0].split(" ")
    method, path, version = start_line
    return path


if __name__ == "__main__":
    main()
